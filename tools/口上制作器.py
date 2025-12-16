import tkinter as tk
from tkinter import ttk, messagebox, filedialog, Menu
import json

class KojoEditorApp:
    def __init__(self, root, game_meta):
        self.root = root
        self.meta = game_meta 
        
        # [调试] 检查数据
        print("\n=== GUI DEBUG: Received Meta Keys ===")
        print(list(self.meta.keys()))
        print("=====================================\n")

        self.root.title("Pera 口上制作工坊 v3.3 (多差分整合版)")
        self.root.geometry("1300x850")
        
        # [核心变更] 数据模型现在是一个列表，存储多个 Root 节点
        self.project_data = [] 
        
        self.node_map = {} 
        self.parent_map = {}
        
        self.setup_ui()
        self.new_project() # 初始化一个空项目
    def filter_events(self):
        """根据选择的类型过滤事件列表"""
        if not hasattr(self, 'all_events'):
            return
            
        event_type = getattr(self, 'event_type_var', tk.StringVar(value="所有事件")).get()
        
        if event_type == "所有事件":
            filtered_events = self.all_events
        elif event_type == "仅主事件":
            # 过滤主事件
            filtered_events = [
                event for event in self.all_events 
                if self.events_meta.get(event, {}).get('is_main', False)
            ]
        else:  # "仅普通事件"
            # 过滤普通事件
            filtered_events = [
                event for event in self.all_events 
                if not self.events_meta.get(event, {}).get('is_main', True)
            ]
        
        # 更新下拉框选项
        if hasattr(self, 'cmb_event'):
            self.cmb_event['values'] = filtered_events
            if filtered_events and not self.cmb_event.get():
                self.cmb_event.current(0)
    def on_event_search(self, event):
        """事件搜索功能"""
        if not hasattr(self, 'cmb_event') or not hasattr(self, 'all_events'):
            return
        
        search_text = self.cmb_event.get().lower()
        filtered = [evt for evt in self.all_events if search_text in evt.lower()]
        
        # 限制显示数量
        if len(filtered) > 50:
            filtered = filtered[:50] + [f"...等 {len(filtered)-50} 个事件"]
        
        self.cmb_event['values'] = filtered
    def setup_ui(self):
        # --- 顶部工具栏 ---
        toolbar = tk.Frame(self.root, bd=1, relief=tk.RAISED)
        toolbar.pack(side=tk.TOP, fill=tk.X)
        
        tk.Button(toolbar, text="📄 新建工程", command=self.new_project).pack(side=tk.LEFT, padx=2)
        tk.Button(toolbar, text="💾 保存工程 (JSON)", command=self.save_project).pack(side=tk.LEFT, padx=2)
        tk.Button(toolbar, text="📂 打开工程 (JSON)", command=self.load_project).pack(side=tk.LEFT, padx=2)
        
        # 核心操作按钮
        tk.Button(toolbar, text="➕ 新建差分 (Root)", command=self.add_root_node, bg="#fff9c4").pack(side=tk.LEFT, padx=10)
        
        tk.Button(toolbar, text="🚀 导出完整脚本 (.py)", command=self.export_py, bg="#c8e6c9").pack(side=tk.RIGHT, padx=10)

        # --- 主体区域 ---
        paned = tk.PanedWindow(self.root, orient=tk.HORIZONTAL)
        paned.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        # 左侧：逻辑树
        frame_left = tk.LabelFrame(paned, text="口上差分结构树")
        paned.add(frame_left, width=350)
        
        self.tree_widget = ttk.Treeview(frame_left)
        self.tree_widget.pack(fill=tk.BOTH, expand=True)
        
        scrollbar = ttk.Scrollbar(frame_left, orient="vertical", command=self.tree_widget.yview)
        scrollbar.place(relx=1, rely=0, relheight=1, anchor='ne')
        self.tree_widget.configure(yscrollcommand=scrollbar.set)

        self.tree_widget.bind("<<TreeviewSelect>>", self.on_tree_select)
        self.tree_widget.bind("<Button-3>", self.show_context_menu)

        # 右侧：属性编辑
        self.frame_right = tk.LabelFrame(paned, text="节点属性编辑")
        paned.add(self.frame_right)
        
        self.lbl_info = tk.Label(self.frame_right, text="请在左侧选择一个节点进行编辑", fg="gray")
        self.lbl_info.pack(pady=50)
        
        # --- 右键菜单 ---
        self.context_menu = Menu(self.root, tearoff=0)
        self.context_menu.add_command(label="➕ 添加分支判断 (IF)", command=self.add_branch)
        self.context_menu.add_command(label="📝 添加文本 (PRINT)", command=self.add_text_node)
        self.context_menu.add_command(label="🔗 调用其他事件 (CALL)", command=self.add_call_node)
        self.context_menu.add_command(label="🖼️ 添加图片 (PRINTIMG)", command=self.add_image_node)
        self.context_menu.add_separator()
        self.context_menu.add_command(label="🧩 插入模板 (JSON)", command=self.insert_template)
        self.context_menu.add_separator()
        self.context_menu.add_command(label="❌ 删除此节点", command=self.delete_node, foreground="red")

    # ================= 核心逻辑：树的构建 =================

    def refresh_tree_view(self):
        self.tree_widget.delete(*self.tree_widget.get_children())
        self.node_map = {}
        self.parent_map = {}
        
        # 遍历所有根节点 (差分)
        for root_node in self.project_data:
            self._build_tree_recursive("", root_node)
            
        # 默认展开所有根节点
        for item in self.tree_widget.get_children():
            self.tree_widget.item(item, open=True)

    def _build_tree_recursive(self, parent_id, node_data):
        display_text = node_data.get('name', '未命名')
        tags = ()
        
        if node_data['type'] == 'root':
            # 根节点显示更醒目
            evt_id = node_data.get('event_id', '未设置ID')
            display_text = f"📦 差分: {evt_id} ({display_text})"
            tags = ('root',)
        elif node_data['type'] == 'branch':
            cond = node_data.get('condition', 'True')
            display_text = f"🔷 [IF] {cond}"
            tags = ('branch',)
        elif node_data['type'] == 'text':
            content = node_data.get('content', '')
            display_text = f"💬 {content[:20]}"
            tags = ('text',)
        elif node_data['type'] == 'call':
            evt = node_data.get('target_event', '未选择')
            # 获取事件类型标记
            event_type = "⭐" if node_data.get('is_main_event', False) else "○"
            display_text = f"🔗 [CALL] {event_type} {evt}"
            tags = ('call',)
        elif node_data['type'] == 'image':
            img = node_data.get('img_key', '未选择')
            display_text = f"🖼️ [立绘] {img}"
            tags = ('image',)
        
        item_id = self.tree_widget.insert(parent_id, 'end', text=display_text, tags=tags)
        self.node_map[item_id] = node_data
        self.parent_map[item_id] = parent_id
        
        if 'children' in node_data:
            for child in node_data['children']:
                self._build_tree_recursive(item_id, child)

    # ================= 交互逻辑 =================

    def on_tree_select(self, event):
        selected = self.tree_widget.selection()
        if not selected: return
        ui_id = selected[0]
        if ui_id not in self.node_map: return
        node = self.node_map[ui_id]
        self.render_editor(node, ui_id)

    def show_context_menu(self, event):
        ui_id = self.tree_widget.identify_row(event.y)
        if ui_id:
            self.tree_widget.selection_set(ui_id)
            # 获取节点类型，如果是 root，禁用某些操作
            node = self.node_map.get(ui_id)
            if node:
                # 根节点上不能再加根节点，但可以加内容
                self.context_menu.post(event.x_root, event.y_root)

    # ================= 编辑器渲染 =================

    def render_editor(self, node, ui_id):
        for widget in self.frame_right.winfo_children():
            widget.destroy()
            
        tk.Label(self.frame_right, text=f"正在编辑: {self.tree_widget.item(ui_id)['text']}", fg="#555").pack(pady=5)

        if node['type'] == 'root':
            tk.Label(self.frame_right, text="[差分事件设置]", font=('bold', 12)).pack(pady=5)
            
            tk.Label(self.frame_right, text="事件触发ID (如 1_初期_聊天_H):").pack(anchor=tk.W, padx=5)
            self.entry_event_id = tk.Entry(self.frame_right)
            self.entry_event_id.insert(0, node.get('event_id', ''))
            self.entry_event_id.pack(fill=tk.X, padx=5)
            
            tk.Label(self.frame_right, text="备注名称 (仅编辑器可见):").pack(anchor=tk.W, padx=5)
            self.entry_name = tk.Entry(self.frame_right)
            self.entry_name.insert(0, node.get('name', ''))
            self.entry_name.pack(fill=tk.X, padx=5)
            
            tk.Button(self.frame_right, text="保存设置", command=lambda: self.save_node_data(node)).pack(pady=10)

        elif node['type'] == 'branch':
            tk.Label(self.frame_right, text="条件设定", font=('bold', 10)).pack(pady=5)
            
            frame_cond = tk.Frame(self.frame_right)
            frame_cond.pack(fill=tk.X, padx=5)
            
            # 1. 变量类型 [Box 1]
            valid_types = [k for k in self.meta.keys() if k not in ['CHARAS', 'IMAGES', 'EVENTS']]
            if not valid_types: valid_types = ['ABL']
            if 'SYS' not in valid_types: valid_types.insert(0, 'SYS')
            
            self.cmb_var_type = ttk.Combobox(frame_cond, values=valid_types, width=8, state="readonly")
            
            current_type = node.get('var_type', '')
            if current_type not in valid_types and valid_types: current_type = valid_types[0]
            self.cmb_var_type.set(current_type)
            self.cmb_var_type.pack(side=tk.LEFT)
            
            # 2. [新增] 对象/作用域选择 [Box 2]
            # 只有当类型不是 SYS 时才需要选对象
            self.frame_scope = tk.Frame(frame_cond) # 包一层frame方便隐藏
            self.frame_scope.pack(side=tk.LEFT)
            
            tk.Label(self.frame_scope, text=":").pack(side=tk.LEFT)
            self.cmb_var_scope = ttk.Combobox(self.frame_scope, width=8, state="readonly")
            # 作用域选项：TARGET, MASTER, PLAYER, ASSI + 具体角色ID
            scope_opts = ['TARGET', 'MASTER', 'PLAYER', 'ASSI'] + self.meta.get('CHARAS', [])
            self.cmb_var_scope['values'] = scope_opts
            self.cmb_var_scope.set(node.get('var_scope', 'TARGET')) # 默认 TARGET
            self.cmb_var_scope.pack(side=tk.LEFT)

            # 3. 变量名 [Box 3]
            tk.Label(frame_cond, text=":").pack(side=tk.LEFT)
            self.cmb_var_name = ttk.Combobox(frame_cond, width=12)
            self.cmb_var_name.pack(side=tk.LEFT)
            
            # 绑定事件：类型改变时 -> 更新变量名列表 + 决定是否显示对象框
            self.cmb_var_type.bind("<<ComboboxSelected>>", self.on_type_changed)
            
            # 4. 运算符 [Box 4]
            self.cmb_op = ttk.Combobox(frame_cond, values=['==', '!=', '>', '<', '>='], width=3, state="readonly")
            self.cmb_op.set(node.get('operator', '>'))
            self.cmb_op.pack(side=tk.LEFT, padx=5)
            
            # 5. 数值 [Box 5]
            self.entry_val = tk.Entry(frame_cond, width=5)
            self.entry_val.insert(0, node.get('value', '0'))
            self.entry_val.pack(side=tk.LEFT)
            
            self.lbl_preview = tk.Label(self.frame_right, text=node.get('condition', ''), fg="blue", bg="#eee")
            self.lbl_preview.pack(fill=tk.X, padx=5, pady=5)
            
            tk.Button(self.frame_right, text="保存条件", command=lambda: self.save_node_data(node)).pack(pady=5)
            
            # 初始化界面状态
            self.on_type_changed(None, initial_value=node.get('var_name', ''))

        elif node['type'] == 'text':
            tk.Label(self.frame_right, text="文本内容", font=('bold', 10)).pack(pady=5)
            
            # 快捷标签
            frame_tags = tk.Frame(self.frame_right)
            frame_tags.pack(fill=tk.X, padx=5, pady=2)
            tk.Label(frame_tags, text="插入: ").pack(side=tk.LEFT)
            quick_tags = [("主角", "{master_name}"), ("对象", "{target_name}"), ("称呼", "{call_name}"), ("❤", "❤")]
            for label, tag in quick_tags:
                tk.Button(frame_tags, text=label, command=lambda t=tag: self.insert_tag(t), font=("Arial", 8), pady=0).pack(side=tk.LEFT, padx=2)

            self.txt_content = tk.Text(self.frame_right, height=8)
            self.txt_content.insert(1.0, node.get('content', ''))
            self.txt_content.pack(fill=tk.X, padx=5)
            
            tk.Label(self.frame_right, text="颜色 (如 COL_TALK):").pack(anchor=tk.W, padx=5)
            self.entry_color = tk.Entry(self.frame_right)
            self.entry_color.insert(0, node.get('color', 'COL_TALK'))
            self.entry_color.pack(fill=tk.X, padx=5)
            
            tk.Button(self.frame_right, text="保存文本", command=lambda: self.save_node_data(node)).pack(pady=10)
            
        elif node['type'] == 'call':
            tk.Label(self.frame_right, text="调用其他事件", font=('bold', 12)).pack(pady=5)
            
            # 添加事件类型说明
            tk.Label(self.frame_right, text="⭐ = 主事件 (影响存档) | ○ = 普通事件", 
                    fg="gray", font=('Arial', 9)).pack(pady=(0, 10))
            
            # 添加事件类型过滤选项
            tk.Label(self.frame_right, text="事件类型筛选:").pack(anchor=tk.W, padx=5)
            event_types_frame = tk.Frame(self.frame_right)
            event_types_frame.pack(fill=tk.X, padx=5)
            
            # 创建事件类型变量
            self.event_type_var = tk.StringVar(value=node.get('event_type_filter', "所有事件"))
            
            # 事件类型选项
            event_type_options = ["所有事件", "仅主事件", "仅普通事件"]
            for i, option in enumerate(event_type_options):
                tk.Radiobutton(event_types_frame, text=option, variable=self.event_type_var, 
                            value=option, command=self.filter_events).pack(side=tk.LEFT, padx=5)
            
            # 下拉框选择事件（带搜索功能）
            tk.Label(self.frame_right, text="选择要调用的事件 (支持输入搜索):").pack(anchor=tk.W, padx=5, pady=(10,0))
            
            # 创建带搜索功能的Combobox
            self.cmb_event = ttk.Combobox(self.frame_right)
            self.cmb_event.pack(fill=tk.X, padx=5)
            
            # 添加搜索绑定
            self.cmb_event.bind('<KeyRelease>', self.on_event_search)
            
            # 保存当前事件列表（用于过滤和搜索）
            self.all_events = self.meta.get('EVENTS', [])
            self.events_meta = self.meta.get('EVENTS_META', {})
            
            # 初始化事件列表
            self.filter_events()
            
            # 设置选中的事件
            current_event = node.get('target_event', '')
            if current_event and current_event in self.all_events:
                self.cmb_event.set(current_event)
            
            # 显示事件详情
            if current_event in self.events_meta:
                meta = self.events_meta[current_event]
                event_info = f"事件类型: {'⭐ 主事件' if meta.get('is_main', False) else '○ 普通事件'}"
                tk.Label(self.frame_right, text=event_info, fg="blue").pack(pady=5)
            
            tk.Button(self.frame_right, text="保存设置", 
                    command=lambda: self.save_node_data(node)).pack(pady=10)

        elif node['type'] == 'image':
            tk.Label(self.frame_right, text="显示图片", font=('bold', 12)).pack(pady=5)
            
            tk.Label(self.frame_right, text="选择图片 (支持搜索):").pack(anchor=tk.W)
            # 自定义搜索过滤功能的 Combobox 比较复杂，这里先用原生
            self.cmb_img = ttk.Combobox(self.frame_right, values=self.meta.get('IMAGES', []), width=40)
            self.cmb_img.set(node.get('img_key', ''))
            self.cmb_img.pack(fill=tk.X, padx=5)
            
            tk.Button(self.frame_right, text="保存设置", command=lambda: self.save_node_data(node)).pack(pady=10)
    def on_type_changed(self, event, initial_value=None):
            """类型改变时触发：1.更新变量名列表 2.控制对象框显隐"""
            v_type = self.cmb_var_type.get()
            
            # --- 显隐控制 ---
            if v_type == 'SYS':
                self.frame_scope.pack_forget() # 隐藏对象框
            else:
                self.frame_scope.pack(side=tk.LEFT, before=self.cmb_var_name) # 显示对象框
                # 重新 pack 可能会乱序，这里只是简单演示，严谨做法是用 grid 或者固定位置
                # 由于我们包在 frame_scope 里，pack 顺序由外层 frame_cond 控制，应该没问题
                
            # --- 更新变量名列表 (同之前逻辑) ---
            if v_type == 'SYS':
                values = ['SELECTCOM', 'PREVCOM', 'TARGET', 'PLAYER', 'MASTER', 'CHARANUM', 'NO', 'NAME']
            else:
                raw_values = self.meta.get(v_type, [])
                values = [str(v) for v in raw_values]
            
            self.cmb_var_name['values'] = values
            
            if values:
                if initial_value and initial_value in values:
                    self.cmb_var_name.set(initial_value)
                elif not self.cmb_var_name.get():
                    self.cmb_var_name.current(0)
            else:
                self.cmb_var_name.set('')
    def insert_tag(self, tag):
        if hasattr(self, 'txt_content'):
            self.txt_content.insert(tk.INSERT, tag)
            self.txt_content.focus_set()

    def update_var_names(self, event, initial_value=None):
        v_type = self.cmb_var_type.get()
        
        # [新增] 处理 SYS 类型的硬编码列表
        if v_type == 'SYS':
            # 这些是 EraKojoHandler 直接支持的属性
            values = [
                'SELECTCOM', 'PREVCOM', 'TARGET', 'PLAYER', 'MASTER', 
                'ASSI', 'ASSIPLAY', 'CHARANUM', 'NO', 'NAME', 'CALLNAME'
            ]
        else:
            # 原有的逻辑：从 meta 读取
            raw_values = self.meta.get(v_type, [])
            values = [str(v) for v in raw_values]
        
        self.cmb_var_name['values'] = values
        
        if values:
            if initial_value and initial_value in values:
                self.cmb_var_name.set(initial_value)
            elif not self.cmb_var_name.get():
                self.cmb_var_name.current(0)
        else:
            self.cmb_var_name.set('')

    def save_node_data(self, node):
        if node['type'] == 'root':
            node['event_id'] = self.entry_event_id.get()
            node['name'] = self.entry_name.get() # 更新显示名
        elif node['type'] == 'branch':
            node['var_type'] = self.cmb_var_type.get()
            node['var_name'] = self.cmb_var_name.get()
            node['operator'] = self.cmb_op.get()
            node['value'] = self.entry_val.get()
            
            v_type = node['var_type']
            v_name = node['var_name']
            
            # [新增] 根据类型生成不同的 Python 代码
            if v_type == 'SYS':
                # 系统变量直接访问属性
                # 例如: kojo.SELECTCOM
                # 注意：有些属性可能返回字符串，最好转 int 比较安全，或者根据情况处理
                # 这里假设 SELECTCOM 等都是可以比较的
                # 为了稳健，我们可以统一转 int (如果是 ID 类除外)
                
                # 特殊处理：如果是字符串类变量 (NAME, CALLNAME)
                if v_name in ['NAME', 'CALLNAME']:
                    var_code = f"kojo.{v_name}"
                    # 字符串比较时，用户输入的值需要加引号，这里简单处理
                    # 如果用户输入的是数字，就不加引号；如果是文本，加引号
                    val = node['value']
                    if not val.isdigit():
                        val = f"'{val}'"
                    node['condition'] = f"{var_code} {node['operator']} {val}"
                    # 跳过后面的通用逻辑，直接 return 或 continue
                    # 但为了结构简单，我们这里只生成 var_code
                else:
                    # 数值类 (SELECTCOM, TARGET等)
                    var_code = f"int(kojo.{v_name})"
                    node['condition'] = f"{var_code} {node['operator']} {node['value']}"

            else:
                # 原有的字典访问逻辑
                # int(kojo.ABL.get('xxx', 0))
                var_code = f"int(kojo.{v_type}.get('{v_name}', 0))"
                node['condition'] = f"{var_code} {node['operator']} {node['value']}"
                
            self.lbl_preview.config(text=node['condition'])
        elif node['type'] == 'text':
            node['content'] = self.txt_content.get(1.0, tk.END).strip()
            node['color'] = self.entry_color.get()
        elif node['type'] == 'call':
            node['target_event'] = self.cmb_event.get()
            node['event_type_filter'] = self.event_type_var.get() if hasattr(self, 'event_type_var') else "所有事件"
        elif node['type'] == 'image':
            node['img_key'] = self.cmb_img.get()
            
        self.refresh_tree_view()
        messagebox.showinfo("提示", "节点已更新")

    # ================= 节点操作 =================

    def get_selected_node(self):
        selected = self.tree_widget.selection()
        if not selected:
            # 如果没选中，看是否有根节点，默认选中最后一个根节点，或者提示
            return None, None
        ui_id = selected[0]
        return self.node_map[ui_id], ui_id

    def add_root_node(self):
        """[新增] 添加一个新的根节点(差分)"""
        count = len(self.project_data) + 1
        new_node = {
            'type': 'root', 
            'name': f'差分_{count}', 
            'event_id': f'event_id_{count}',
            'children': []
        }
        self.project_data.append(new_node)
        self.refresh_tree_view()

    def add_child_node(self, new_node):
        parent, ui_id = self.get_selected_node()
        if not parent:
            messagebox.showwarning("提示", "请先在左侧选择一个插入位置（父节点）")
            return
        
        # 确保 parent 有 children 列表
        if 'children' not in parent: parent['children'] = []
        parent['children'].append(new_node)
        
        self.refresh_tree_view()
        if ui_id and self.tree_widget.exists(ui_id):
            self.tree_widget.item(ui_id, open=True)

    def add_branch(self):
        self.add_child_node({'type': 'branch', 'name': '新分支', 'children': [], 'var_type': 'ABL', 'var_name': '', 'operator': '>', 'value': '0'})

    def add_text_node(self):
        self.add_child_node({'type': 'text', 'name': '新对话', 'content': '...', 'color': 'COL_TALK'})

    def add_call_node(self):
        self.add_child_node({'type': 'call', 'name': '调用事件', 'target_event': ''})

    def add_image_node(self):
        self.add_child_node({'type': 'image', 'name': '图片', 'img_key': ''})

    def delete_node(self):
        node, ui_id = self.get_selected_node()
        if not node: return
        
        # 如果是根节点，从 project_data 删除
        if node['type'] == 'root':
            if messagebox.askyesno("确认", "确定要删除这个差分及其所有内容吗？"):
                self.project_data.remove(node)
                self.refresh_tree_view()
            return

        # 如果是子节点，从父节点删除
        parent_ui_id = self.parent_map.get(ui_id)
        if parent_ui_id and parent_ui_id in self.node_map:
            parent_node = self.node_map[parent_ui_id]
            if node in parent_node['children']:
                parent_node['children'].remove(node)
                self.refresh_tree_view()

    # ================= 模板导入 =================
    
    def insert_template(self):
        # 逻辑：把外部 JSON 的所有 Root 加到当前 Project，或者把外部 Root 的 Children 加到当前 Node
        target_node, ui_id = self.get_selected_node()
        file_path = filedialog.askopenfilename(filetypes=[("JSON Files", "*.json")])
        if not file_path: return
        
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                template_data = json.load(f) # 这是一个 list
            
            # 如果没选中节点，视为合并项目（追加根节点）
            if not target_node:
                if isinstance(template_data, list):
                    self.project_data.extend(template_data)
                else: # 旧版兼容
                    self.project_data.append(template_data)
            else:
                # 选中了节点，尝试提取模板里的第一个根节点的 children 追加进去
                source_children = []
                if isinstance(template_data, list) and template_data:
                    source_children = template_data[0].get('children', [])
                elif isinstance(template_data, dict):
                    source_children = template_data.get('children', [])
                
                if 'children' not in target_node: target_node['children'] = []
                target_node['children'].extend(source_children)
                
            self.refresh_tree_view()
            messagebox.showinfo("成功", "模板已插入")
        except Exception as e:
            messagebox.showerror("错误", f"导入失败: {e}")

    # ================= 导出逻辑 (多函数版) =================
    
    def export_py(self):
        lines = []
        lines.append("from utils.era_handler import EraKojoHandler")
        lines.append("")
        
        # 遍历所有根节点，生成多个函数
        for root_node in self.project_data:
            func_name = f"event_{root_node.get('event_id', 'temp')}"
            
            lines.append(f"def {func_name}(this):")
            lines.append(f'    """ {root_node.get("name", "")} """')
            lines.append("    context = getattr(this, 'current_kojo_context', {})")
            lines.append("    kojo = EraKojoHandler(this.console, context)")
            lines.append("")
            
            # 自动注入常用变量 (更新版)
            lines.append("    # --- 常用变量定义 ---")
            lines.append("    master_name = '你'")
            lines.append("    if kojo.MASTER:")
            lines.append("        master_name = this.console.init.charaters_key.get(kojo.MASTER, {}).get('名前', '你')")
            lines.append("    target_name = kojo.NAME")
            lines.append("    call_name = kojo.CALLNAME")
            lines.append("    # --------------------")
            lines.append("")
            
            lines.append("    COL_TALK = (255, 255, 255)")
            lines.append("    COL_DESC = (170, 170, 170)")
            lines.append("")
            
            # 编译子节点
            if 'children' in root_node:
                for child in root_node['children']:
                    self._compile_node(child, lines, indent=1)
            else:
                lines.append("    pass")
            
            lines.append("")
            # 注册触发器
            lines.append(f"{func_name}.event_trigger = '{root_node.get('event_id', 'temp')}'")
            lines.append("")
            lines.append("# " + "-"*40)
            lines.append("")
        
        file_path = filedialog.asksaveasfilename(defaultextension=".py", filetypes=[("Python Files", "*.py")])
        if file_path:
            with open(file_path, "w", encoding="utf-8") as f:
                f.write("\n".join(lines))
            messagebox.showinfo("成功", "多差分脚本已生成！")

    def _compile_node(self, node, lines, indent):
            prefix = "    " * indent
            
            if node['type'] == 'branch':
                cond = node.get('condition', 'True')
                lines.append(f"{prefix}if {cond}:")
                if 'children' in node and node['children']:
                    for child in node['children']:
                        self._compile_node(child, lines, indent + 1)
                else:
                    lines.append(f"{prefix}    pass")
                
            elif node['type'] == 'text':
                color = node.get('color', 'COL_TALK')
                content_raw = node.get('content', '')
                
                # [核心改进] 按换行符切割文本，生成多个 PRINT 语句
                # splitlines() 会自动处理 \r\n, \n 等各种换行符
                content_lines = content_raw.splitlines()
                
                # 如果内容为空，或者只有空行，至少输出一个空行
                if not content_lines:
                    content_lines = [""]
                    
                for i, line_text in enumerate(content_lines):
                    # 只有最后一行才添加 INPUT (等待)，前面的行只负责显示
                    # 除非你希望每行都等待，那就在这里改逻辑
                    
                    # 清理首尾空格 (可选，取决于你想不想要保留缩进)
                    # line_text = line_text.strip() 
                    
                    lines.append(f'{prefix}this.console.PRINT(f"{line_text}", colors={color})')
                
                # 在所有文本打印完后，添加一次 INPUT
                lines.append(f'{prefix}this.console.INPUT()')
                
            elif node['type'] == 'call':
                evt = node.get('target_event', '')
                lines.append(f"{prefix}this.event_manager.trigger_event('{evt}', this)")
                
            elif node['type'] == 'image':
                img = node.get('img_key', '')
                lines.append(f'{prefix}this.console.PRINTIMG("{img}")')

    # ================= 项目存取 =================
    
    def new_project(self):
        # 初始化为一个空的列表 (包含一个默认的根)
        self.project_data = [{'type': 'root', 'name': '默认差分', 'event_id': '1_初期_未命名', 'children': []}]
        self.refresh_tree_view()

    def save_project(self):
        file_path = filedialog.asksaveasfilename(defaultextension=".json")
        if file_path:
            with open(file_path, 'w', encoding='utf-8') as f:
                json.dump(self.project_data, f, indent=4) # 存的是 List

    def load_project(self):
        file_path = filedialog.askopenfilename(filetypes=[("JSON Files", "*.json")])
        if file_path:
            try:
                with open(file_path, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    # 兼容旧版 (如果是 dict，转为 list)
                    if isinstance(data, dict):
                        self.project_data = [data]
                    else:
                        self.project_data = data
                self.refresh_tree_view()
            except Exception as e:
                messagebox.showerror("错误", f"读取失败: {e}")

if __name__ == "__main__":
    root = tk.Tk()
    meta = {'ABL': ['C感觉'], 'CHARAS': ['0'], 'IMAGES': []}
    app = KojoEditorApp(root, meta)
    root.mainloop()