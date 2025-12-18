import tkinter as tk
from tkinter import ttk, messagebox, filedialog, Menu
import json

class KojoEditorApp:
    def __init__(self, root, game_meta):
        self.root = root
        self.meta = game_meta 
        self.root.title("Pera 口上制作工坊 v6.0 (节点约束优化版)")
        self.root.geometry("1300x850")
        
        # 数据模型
        self.project_data = [] 
        self.node_map = {} 
        self.parent_map = {}
        
        # [新增] 记录展开状态的集合 {ui_id}
        self.expanded_nodes = set()
        
        self.setup_ui()
        self.new_project() 

    def setup_ui(self):
        # --- 工具栏 ---
        toolbar = tk.Frame(self.root, bd=1, relief=tk.RAISED)
        toolbar.pack(side=tk.TOP, fill=tk.X)
        
        tk.Button(toolbar, text="📄 新建", command=self.new_project).pack(side=tk.LEFT, padx=2)
        tk.Button(toolbar, text="💾 保存JSON", command=self.save_project).pack(side=tk.LEFT, padx=2)
        tk.Button(toolbar, text="📂 打开JSON", command=self.load_project).pack(side=tk.LEFT, padx=2)
        
        tk.Button(toolbar, text="➕ 新建差分 (Root)", command=self.add_root_node, bg="#fff9c4").pack(side=tk.LEFT, padx=10)
        tk.Button(toolbar, text="🚀 导出脚本 (.py)", command=self.export_py, bg="#c8e6c9").pack(side=tk.RIGHT, padx=10)

        # --- 主体 ---
        paned = tk.PanedWindow(self.root, orient=tk.HORIZONTAL)
        paned.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        frame_left = tk.LabelFrame(paned, text="口上结构树")
        paned.add(frame_left, width=350)
        
        self.tree_widget = ttk.Treeview(frame_left)
        self.tree_widget.pack(fill=tk.BOTH, expand=True)
        
        # 绑定事件：记录展开/折叠状态
        self.tree_widget.bind("<<TreeviewOpen>>", self.on_tree_open)
        self.tree_widget.bind("<<TreeviewClose>>", self.on_tree_close)
        self.tree_widget.bind("<<TreeviewSelect>>", self.on_tree_select)
        self.tree_widget.bind("<Button-3>", self.show_context_menu)

        # 属性编辑区
        self.frame_right = tk.LabelFrame(paned, text="节点属性编辑")
        paned.add(self.frame_right)
        self.lbl_info = tk.Label(self.frame_right, text="请在左侧选择一个节点进行编辑", fg="gray")
        self.lbl_info.pack(pady=50)
        
        # --- 右键菜单 ---
        self.context_menu = Menu(self.root, tearoff=0)
        
        # 子菜单：添加逻辑
        self.menu_add = Menu(self.context_menu, tearoff=0)
        self.menu_add.add_command(label="🔷 分支判断 (IF)", command=self.add_branch)
        self.menu_add.add_command(label="🔘 选项菜单 (MENU)", command=self.add_menu_node)
        self.menu_add.add_command(label="✏️ 修改属性 (SET)", command=self.add_set_node)
        self.menu_add.add_separator()
        self.menu_add.add_command(label="💬 文本 (PRINT)", command=self.add_text_node)
        self.menu_add.add_command(label="🖼️ 图片 (PRINTIMG)", command=self.add_image_node)
        self.menu_add.add_command(label="🔗 调用事件 (CALL)", command=self.add_call_node)
        
        self.context_menu.add_cascade(label="➕ 添加子节点", menu=self.menu_add)
        self.context_menu.add_separator()
        self.context_menu.add_command(label="🧩 插入模板", command=self.insert_template)
        self.context_menu.add_command(label="❌ 删除节点", command=self.delete_node, foreground="red")

    # ================= 树的构建与状态保持 =================

    def on_tree_open(self, event):
        """记录展开的节点"""
        item_id = self.tree_widget.focus()
        self.expanded_nodes.add(item_id)

    def on_tree_close(self, event):
        """记录折叠的节点"""
        item_id = self.tree_widget.focus()
        if item_id in self.expanded_nodes:
            self.expanded_nodes.remove(item_id)

    def refresh_tree_view(self):
        # 1. 记录当前选中的节点和滚动位置 (如果能做到的话，这里简化为只保留展开状态)
        selected = self.tree_widget.selection()
        selected_id = selected[0] if selected else None
        
        # 2. 清空重建
        self.tree_widget.delete(*self.tree_widget.get_children())
        self.node_map = {}
        self.parent_map = {}
        
        # 递归构建
        # 注意：这里我们使用内存对象的 id() 作为 key 来追踪展开状态
        # 因为 UI 的 item_id 每次重建都会变，无法用来持久化状态
        # 所以我们需要维护一个 {data_node_id} 的集合
        
        for root_node in self.project_data:
            self._build_tree_recursive("", root_node)
            
        # 3. 恢复选中状态 (如果可能)
        # 由于 ID 变了，这里很难完美恢复选中，但可以尝试恢复展开
        # 下面的 _build_tree_recursive 已经处理了展开逻辑

    def _build_tree_recursive(self, parent_id, node_data):
        display_text = node_data.get('name', '未命名')
        tags = (node_data['type'],)
        
        # 优化显示文本
        if node_data['type'] == 'root':
            display_text = f"📦 差分: {node_data.get('event_id', '')}"
        elif node_data['type'] == 'branch':
            display_text = f"🔷 [IF] {node_data.get('condition', '?')}"
        elif node_data['type'] == 'text':
            display_text = f"💬 {node_data.get('content', '')[:20]}"
        elif node_data['type'] == 'menu':
            display_text = f"🔘 [MENU]"
        elif node_data['type'] == 'menu_case':
            display_text = f"↳ 选中 [{node_data.get('value')}]"
            
        # 插入节点
        item_id = self.tree_widget.insert(parent_id, 'end', text=display_text, tags=tags)
        self.node_map[item_id] = node_data
        self.parent_map[item_id] = parent_id
        
        # [关键优化] 根据内存对象的标记恢复展开状态
        # 我们在 node_data 里存一个临时标记 '_expanded'
        if node_data.get('_expanded', False):
            self.tree_widget.item(item_id, open=True)
            
        # 默认展开所有根节点
        if node_data['type'] == 'root':
            self.tree_widget.item(item_id, open=True)
            node_data['_expanded'] = True

        if 'children' in node_data:
            for child in node_data['children']:
                self._build_tree_recursive(item_id, child)

    def toggle_expand_state(self, node, is_open):
        """手动更新数据的展开状态标记"""
        node['_expanded'] = is_open

    # ================= 交互逻辑 =================

    def on_tree_select(self, event):
        selected = self.tree_widget.selection()
        if not selected: return
        ui_id = selected[0]
        if ui_id not in self.node_map: return
        node = self.node_map[ui_id]
        
        # 同步展开状态到数据
        # 其实 Treeview 的 Open 事件更好，但 Select 也能辅助
        self.render_editor(node, ui_id)

    def show_context_menu(self, event):
        ui_id = self.tree_widget.identify_row(event.y)
        if ui_id:
            self.tree_widget.selection_set(ui_id)
            node = self.node_map.get(ui_id)
            
            # [核心约束] 只有容器节点才能添加子节点
            # 容器类型：root, branch, menu_case
            # 叶子类型：text, image, call, set, menu(menu比较特殊，它的子节点是自动生成的)
            is_container = node['type'] in ['root', 'branch', 'menu_case']
            
            # 动态启用/禁用菜单项
            if is_container:
                self.context_menu.entryconfig("➕ 添加子节点", state="normal")
                self.context_menu.entryconfig("🧩 插入模板", state="normal")
            else:
                self.context_menu.entryconfig("➕ 添加子节点", state="disabled")
                self.context_menu.entryconfig("🧩 插入模板", state="disabled")

            self.context_menu.post(event.x_root, event.y_root)

    # ================= 节点操作 (增删改) =================

    def add_child_node(self, new_node):
        parent, ui_id = self.get_selected_node()
        if not parent: return
        
        # [双重保险] 再次检查类型
        if parent['type'] not in ['root', 'branch', 'menu_case']:
            messagebox.showwarning("操作无效", "该节点类型不支持添加子节点！")
            return
        
        if 'children' not in parent: parent['children'] = []
        parent['children'].append(new_node)
        
        # 标记父节点为展开
        parent['_expanded'] = True
        
        self.refresh_tree_view()
        
        # 选中新节点 (可选)
        # self.tree_widget.selection_set(new_item_id) 

    # 包装各个添加方法
    def add_branch(self): self.add_child_node({'type': 'branch', 'name': 'IF', 'children': [], 'condition': 'True'})
    def add_text_node(self): self.add_child_node({'type': 'text', 'content': '...'})
    def add_call_node(self): self.add_child_node({'type': 'call', 'target_event': ''})
    def add_image_node(self): self.add_child_node({'type': 'image', 'img_key': ''})
    def add_set_node(self): self.add_child_node({'type': 'set', 'var_name': '?', 'operator': '=', 'value': '0'})
    
    def add_menu_node(self):
        # Menu 比较特殊，初始化时自动带 children
        new_node = {
            'type': 'menu',
            'variable': 'res',
            'options': [{'label': 'Yes', 'value': '1'}, {'label': 'No', 'value': '0'}],
            'children': []
        }
        # 初始化 menu_case
        for opt in new_node['options']:
            new_node['children'].append({
                'type': 'menu_case', 'value': opt['value'], 'children': []
            })
        self.add_child_node(new_node)

    # 监听展开事件来更新数据
    def on_tree_open(self, event):
        item_id = self.tree_widget.focus() # 获取当前操作的节点
        if item_id in self.node_map:
            self.node_map[item_id]['_expanded'] = True

    def on_tree_close(self, event):
        item_id = self.tree_widget.focus()
        if item_id in self.node_map:
            self.node_map[item_id]['_expanded'] = False

    # ... (Render Editor, Save, Load, Export 等方法保持不变，直接复制即可) ...
    # 为了完整性，下面把之前的 render_editor 等复制过来
    def get_selected_node(self):
            selected = self.tree_widget.selection()
            if not selected:
                messagebox.showwarning("提示", "请先右键点击一个节点")
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
            'children': [],
            '_expanded': True # 默认展开
        }
        self.project_data.append(new_node)
        self.refresh_tree_view()
    
    def delete_node(self):
        node, ui_id = self.get_selected_node()
        if not node: return
        if node['type'] == 'root':
            if messagebox.askyesno("确认", "删除此根节点？"):
                self.project_data.remove(node)
                self.refresh_tree_view()
            return
        
        parent_ui = self.parent_map.get(ui_id)
        if parent_ui:
            parent = self.node_map[parent_ui]
            if node in parent['children']:
                parent['children'].remove(node)
                self.refresh_tree_view()

    # (Export, Save, Load, Insert Template 同前)
    # ...
    def render_editor(self, node,ui_id):
        # 清空右侧旧控件
        for widget in self.frame_right.winfo_children():
            widget.destroy()
            
        # [核心优化] 根据节点类型生成更直观的标题，而不是只显示"未命名"
        node_type = node.get('type', 'unknown')
        title_text = "未知节点"
        title_bg = "#f0f0f0" # 默认背景色
        title_fg = "#333"    # 默认前景色

        if node_type == 'root':
            evt_id = node.get('event_id', '未设置')
            title_text = f"📦 差分编辑器 (ID: {evt_id})"
            title_bg = "#fff9c4" # 淡黄
            
        elif node_type == 'branch':
            cond = node.get('condition', '未设置')
            title_text = f"🔷 逻辑判断: {cond}"
            title_bg = "#e3f2fd" # 淡蓝
            
        elif node_type == 'text':
            title_text = "💬 文本对话编辑器"
            
        elif node_type == 'menu':
            title_text = "🔘 选项菜单配置"
            title_bg = "#e8f5e9" # 淡绿
            
        elif node_type == 'menu_case':
            val = node.get('value', '?')
            title_text = f"↳ 分支逻辑: 当玩家选择 [{val}] 时"
            title_bg = "#f1f8e9"
            
        elif node_type == 'call':
            target = node.get('target_event', '未选择')
            title_text = f"🔗 事件调用: {target}"
            
        elif node_type == 'image':
            img = node.get('img_key', '未选择')
            title_text = f"🖼️ 图片显示: {img}"
            
        elif node_type == 'set':
            var = node.get('var_name', '??')
            title_text = f"✏️ 属性修改: {var}"
            title_bg = "#fff3e0" # 淡橙

        # 渲染优化后的标题栏
        header_frame = tk.Frame(self.frame_right, bg=title_bg, pady=5, padx=5)
        header_frame.pack(fill=tk.X, pady=(0, 10))
        
        tk.Label(header_frame, text=title_text, bg=title_bg, fg=title_fg, 
                font=("微软雅黑", 11, "bold")).pack(anchor=tk.W)

        # ---------------- 下面是原本的编辑器逻辑 ----------------
        # 请保留原来 if node['type'] == 'root': 之后的所有代码...
        

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
        elif node['type'] == 'menu':
            tk.Label(self.frame_right, text="[选项菜单设置]", font=('bold', 12)).pack(pady=5)
            
            # 选项列表容器
            self.frame_opts = tk.Frame(self.frame_right)
            self.frame_opts.pack(fill=tk.BOTH, expand=True, padx=5)
            
            tk.Label(self.frame_opts, text="选项列表 (显示文本 | 返回值):").pack(anchor=tk.W)
            
            # 动态生成输入框
            self.opt_entries = []
            options = node.get('options', [])
            
            for i, opt in enumerate(options):
                f = tk.Frame(self.frame_opts)
                f.pack(fill=tk.X, pady=2)
                
                tk.Label(f, text=f"选项 {i+1}:").pack(side=tk.LEFT)
                e_lbl = tk.Entry(f, width=15)
                e_lbl.insert(0, opt['label'])
                e_lbl.pack(side=tk.LEFT, padx=2)
                
                tk.Label(f, text="值:").pack(side=tk.LEFT)
                e_val = tk.Entry(f, width=5)
                e_val.insert(0, opt['value'])
                e_val.pack(side=tk.LEFT, padx=2)
                
                self.opt_entries.append((e_lbl, e_val))
            
            # 操作按钮
            btn_frame = tk.Frame(self.frame_right)
            btn_frame.pack(fill=tk.X, pady=10)
            
            tk.Button(btn_frame, text="+ 增加选项", command=lambda: self.modify_menu_opts(node, 1)).pack(side=tk.LEFT, padx=5)
            tk.Button(btn_frame, text="- 减少选项", command=lambda: self.modify_menu_opts(node, -1)).pack(side=tk.LEFT, padx=5)
            tk.Button(btn_frame, text="保存并刷新结构", command=lambda: self.save_menu_data(node), bg="#c8e6c9").pack(side=tk.RIGHT, padx=5)

        elif node['type'] == 'menu_case':
            tk.Label(self.frame_right, text="这是由菜单自动生成的分支节点", fg="gray").pack(pady=20)
            tk.Label(self.frame_right, text=f"当用户输入 '{node.get('value')}' 时执行此处逻辑").pack()
        elif node['type'] == 'set':
            tk.Label(self.frame_right, text="属性修改设定", font=('bold', 10)).pack(pady=5)
            
            frame_set = tk.Frame(self.frame_right)
            frame_set.pack(fill=tk.X, padx=5)
            
            # 1. 变量类型 (去掉 SYS，因为 SYS 通常不可写)
            valid_types = [k for k in self.meta.keys() if k not in ['CHARAS', 'IMAGES', 'EVENTS', 'SYS']]
            if not valid_types: valid_types = ['CFLAG']
            
            self.cmb_var_type = ttk.Combobox(frame_set, values=valid_types, width=8, state="readonly")
            self.cmb_var_type.set(node.get('var_type', valid_types[0]))
            self.cmb_var_type.pack(side=tk.LEFT)
            self.cmb_var_type.bind("<<ComboboxSelected>>", self.on_type_changed)
            
            # 2. 对象 (Scope)
            self.frame_scope = tk.Frame(frame_set)
            self.frame_scope.pack(side=tk.LEFT)
            tk.Label(self.frame_scope, text=":").pack(side=tk.LEFT)
            
            scope_opts = ['TARGET', 'MASTER', 'PLAYER'] + self.meta.get('CHARAS', [])
            self.cmb_var_scope = ttk.Combobox(self.frame_scope, values=scope_opts, width=8, state="readonly")
            self.cmb_var_scope.set(node.get('var_scope', 'TARGET'))
            self.cmb_var_scope.pack(side=tk.LEFT)
            
            # 3. 变量名
            tk.Label(frame_set, text=":").pack(side=tk.LEFT)
            self.cmb_var_name = ttk.Combobox(frame_set, width=12)
            self.cmb_var_name.pack(side=tk.LEFT)
            
            # 4. 运算符 (+=, -=, =)
            self.cmb_op = ttk.Combobox(frame_set, values=['=', '+=', '-='], width=3, state="readonly")
            self.cmb_op.set(node.get('operator', '+='))
            self.cmb_op.pack(side=tk.LEFT, padx=5)
            
            # 5. 数值
            self.entry_val = tk.Entry(frame_set, width=5)
            self.entry_val.insert(0, node.get('value', '0'))
            self.entry_val.pack(side=tk.LEFT)
            
            # 预览
            self.lbl_preview = tk.Label(self.frame_right, text="", fg="green", bg="#eee")
            self.lbl_preview.pack(fill=tk.X, padx=5, pady=5)
            
            tk.Button(self.frame_right, text="保存修改", command=lambda: self.save_node_data(node)).pack(pady=5)
            
            # 初始化联动
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
            
            # [新增] 根据类型生成不同的 Python 代码
            if node['var_type'] == 'SYS':
                if node['var_name'] in ['NAME', 'CALLNAME']:
                    val = node['value']
                    if not val.isdigit(): val = f"'{val}'"
                    node['condition'] = f"kojo.{node['var_name']} {node['operator']} {val}"
                else:
                    node['condition'] = f"int(kojo.{node['var_name']}) {node['operator']} {node['value']}"
            else:
                # 原有的字典访问逻辑
                v_scope = node.get('var_scope', 'TARGET')
                
                if v_scope == 'TARGET':
                    code_scope = ""
                elif v_scope in ['MASTER', 'PLAYER']:
                    code_scope = f"[kojo.{v_scope}]"
                else:
                    code_scope = f"['{v_scope}']"
                
                # 兼容 EraDataProxy 索引访问
                # 如果 scope 为空 (TARGET), data_proxy['TARGET'] 等同于 data_proxy.get
                # 但为了统一，我们这里生成 kojo.ABL[kojo.TARGET].get
                if not code_scope:
                    node['condition'] = f"int(kojo.{node['var_type']}.get('{node['var_name']}', 0)) {node['operator']} {node['value']}"
                else:
                    node['condition'] = f"int(kojo.{node['var_type']}{code_scope}.get('{node['var_name']}', 0)) {node['operator']} {node['value']}"
                    
            self.lbl_preview.config(text=node['condition'])
        elif node['type'] == 'text':
            node['content'] = self.txt_content.get(1.0, tk.END).strip()
            node['color'] = self.entry_color.get()
        elif node['type'] == 'call':
            node['target_event'] = self.cmb_event.get()
            node['event_type_filter'] = self.event_type_var.get() if hasattr(self, 'event_type_var') else "所有事件"
        elif node['type'] == 'image':
            node['img_key'] = self.cmb_img.get()
        elif node['type'] == 'set':
                    node['var_type'] = self.cmb_var_type.get()
                    node['var_scope'] = self.cmb_var_scope.get()
                    node['var_name'] = self.cmb_var_name.get()
                    node['operator'] = self.cmb_op.get()
                    node['value'] = self.entry_val.get()
                    
                    v_type = node['var_type']
                    v_scope = node['var_scope']
                    v_name = node['var_name']
                    op = node['operator']
                    val = node['value']
                    
                    # 构建代码预览
                    if v_scope == 'TARGET':
                        target_code = "" # 默认
                    elif v_scope in ['MASTER', 'PLAYER']:
                        target_code = f", chara_id=kojo.{v_scope}"
                    else:
                        target_code = f", chara_id='{v_scope}'"

                    if op == '=':
                        code = f"kojo.{v_type}.set('{v_name}', {val}{target_code})"
                    else:
                        code = f"# {v_type}:{v_name} {op} {val}"
                        
                    self.lbl_preview.config(text=code)
        self.refresh_tree_view()
        messagebox.showinfo("提示", "节点已更新")

    def modify_menu_opts(self, node, delta):
        """增加或减少选项数量"""
        options = node.get('options', [])
        if delta > 0:
            new_val = str(len(options) + 1)
            options.append({'label': '新选项', 'value': new_val})
            # 同时增加子节点
            node['children'].append({
                'type': 'menu_case', 
                'name': f"当选择 [{new_val}] 时", 
                'value': new_val, 
                'children': []
            })
        elif delta < 0 and options:
            options.pop()
            if node['children']: node['children'].pop()
            
        self.render_editor(node, self.node_map.keys().__iter__().__next__()) # 这里的刷新逻辑有点hack，实际应该传正确id
        # 为了修复刷新问题，我们直接调用 render_editor(node, 当前选中ID)
        # 获取当前选中的ID
        sel = self.tree_widget.selection()
        if sel: self.render_editor(node, sel[0])

    def save_menu_data(self, node):
        """保存菜单配置"""
        new_options = []
        # 读取输入框
        for i, (e_lbl, e_val) in enumerate(self.opt_entries):
            val = e_val.get()
            label = e_lbl.get()
            new_options.append({'label': label, 'value': val})
            
            # 同步更新对应的子节点名称
            if i < len(node['children']):
                node['children'][i]['value'] = val
                node['children'][i]['name'] = f"当选择 [{val}] 时"

        node['options'] = new_options
        self.refresh_tree_view()
        messagebox.showinfo("提示", "菜单结构已更新")

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
            elif node['type'] == 'menu':
                # 1. 生成显示代码
                menu_code_parts = []
                for opt in node.get('options', []):
                    label = opt['label']
                    val = opt['value']
                    btn_text = f"[{val}] {label}"
                    menu_code_parts.append(f'this.cs("{btn_text}").click("{val}")')
                
                menu_args = ', "   ", '.join(menu_code_parts)
                lines.append(f'{prefix}this.console.PRINT({menu_args})')
                
                # 2. 生成输入代码
                var_name = "menu_res" # 临时变量名
                lines.append(f'{prefix}{var_name} = this.console.INPUT()')
                
                # 3. 生成分支逻辑
                for i, child in enumerate(node.get('children', [])):
                    val = child.get('value', '')
                    if i == 0:
                        lines.append(f'{prefix}if {var_name} == "{val}":')
                    else:
                        lines.append(f'{prefix}elif {var_name} == "{val}":')
                    
                    if 'children' in child and child['children']:
                        for grand_child in child['children']:
                            self._compile_node(grand_child, lines, indent + 1)
                    else:
                        lines.append(f'{prefix}    pass')
                        
            elif node['type'] == 'text':
                color = node.get('color', 'COL_TALK')
                content_raw = node.get('content', '')
                
                content_lines = content_raw.splitlines()
                if not content_lines: content_lines = [""]
                    
                for i, line_text in enumerate(content_lines):
                    lines.append(f'{prefix}this.console.PRINT(f"{line_text}", colors={color})')
                
                lines.append(f'{prefix}this.console.INPUT()')
                
            elif node['type'] == 'call':
                evt = node.get('target_event', '')
                lines.append(f"{prefix}this.event_manager.trigger_event('{evt}', this)")
                
            elif node['type'] == 'image':
                img = node.get('img_key', '')
                lines.append(f'{prefix}this.console.PRINTIMG("{img}")')
                
            elif node['type'] == 'set':
                v_type = node['var_type']
                v_scope = node['var_scope']
                v_name = node['var_name']
                op = node['operator']
                val = node['value']
                
                if v_scope == 'TARGET':
                    target_id_code = "kojo.TARGET"
                elif v_scope in ['MASTER', 'PLAYER']:
                    target_id_code = f"kojo.{v_scope}"
                else:
                    target_id_code = f"'{v_scope}'"

                if op == '=':
                    lines.append(f"{prefix}kojo.{v_type}.set('{v_name}', {val}, chara_id={target_id_code})")
                else:
                    math_op = '+' if op == '+=' else '-'
                    lines.append(f"{prefix}current_val = int(kojo.{v_type}[{target_id_code}].get('{v_name}', 0))")
                    lines.append(f"{prefix}new_val = current_val {math_op} int({val})")
                    lines.append(f"{prefix}kojo.{v_type}.set('{v_name}', new_val, chara_id={target_id_code})")

    # ================= 项目存取 =================
    
    def new_project(self):
        # 初始化为一个空的列表 (包含一个默认的根)
        self.project_data = [{'type': 'root', 'name': '默认差分', 'event_id': '1_初期_未命名', 'children': [], '_expanded': True}]
        self.refresh_tree_view()

    def save_project(self):
        file_path = filedialog.asksaveasfilename(defaultextension=".json")
        if file_path:
            with open(file_path, 'w', encoding='utf-8') as f:
                # 保存前把 _expanded 这种临时属性清理掉？其实留着也没事，方便下次打开
                json.dump(self.project_data, f, indent=4) 

    def load_project(self):
        file_path = filedialog.askopenfilename(filetypes=[("JSON Files", "*.json")])
        if file_path:
            try:
                with open(file_path, 'r', encoding='utf-8') as f:
                    data = json.load(f)
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