class EventManager:
    def __init__(self, console_instance):
        self.console = console_instance
        self.events = {}
        self.eventid = {}
        self.call_stack = []
        
        # [新增] 存储事件的元数据（比如是否为主事件）
        # 结构: {'事件名': {'is_main': True, ...}}
        self.events_meta = {} 
        
        self.load_events()

    def load_events(self, is_reload=False):
            """动态加载事件文件 (兼容 PyInstaller 打包)"""
            import importlib
            import os
            import sys
            
            # 1. 获取程序的根目录 (兼容源码运行和打包后的 exe)
            if getattr(sys, 'frozen', False):
                # 如果是打包后的 exe，根目录是 exe 所在的文件夹
                root_dir = os.path.dirname(sys.executable)
            else:
                # 如果是源码运行，根目录是当前文件所在文件夹
                root_dir = os.path.dirname(os.path.abspath(__file__))

            # 2. 定位 events 文件夹
            events_dir = os.path.join(root_dir, "events")
            
            # [核心修复] 将根目录加入 sys.path，这样才能识别 "import events.xxx"
            if root_dir not in sys.path:
                sys.path.insert(0, root_dir)

            if not os.path.exists(events_dir):
                self.console.PRINT(f"警告: 未找到事件目录 {events_dir}", colors=(255, 100, 100))
                return # 或者 os.makedirs(events_dir)

            # [修改] 重载清理逻辑
            if is_reload:
                self.events = {}
                self.eventid = {}
                # 清理 sys.modules 中的旧缓存，强制重新读取文件
                # 这一步对于热重载非常重要
                modules_to_remove = [m for m in sys.modules if m.startswith('events.')]
                for m in modules_to_remove:
                    del sys.modules[m]
                
                self.console.PRINT("正在清理旧事件缓存...", colors=(150, 150, 150))

            # 3. 遍历文件
            for root, dirs, files in os.walk(events_dir):
                for file in files:
                    if file.endswith(".py") and file != "__init__.py":
                        # 计算相对路径，用于构建模块名
                        # 例如: root=D:\Game\events, file=start.py -> relative_path=.
                        try:
                            relative_path = os.path.relpath(root, events_dir)
                        except ValueError:
                            continue

                        if relative_path == ".":
                            module_name = f"events.{file[:-3]}"
                        else:
                            # 处理子文件夹情况
                            sub_pkg = relative_path.replace(os.sep, ".")
                            module_name = f"events.{sub_pkg}.{file[:-3]}"
                        
                        try:
                            # 4. 动态导入
                            if module_name in sys.modules:
                                module = importlib.reload(sys.modules[module_name])
                            else:
                                module = importlib.import_module(module_name)
                            
                            # 5. 注册事件
                            for attr_name in dir(module):
                                if attr_name.startswith("event_"):
                                    event_func = getattr(module, attr_name)
                                    event_key = attr_name[6:]
                                    # 兼容没有定义 event_trigger 的情况
                                    event_id = getattr(event_func, 'event_trigger', event_key)
                                    
                                    # 读取是否为主事件标记
                                    is_main = getattr(event_func, 'is_main_event', False)
                                    
                                    self.events[event_key] = event_func
                                    self.eventid[event_id] = event_key
                                    
                                    # 存入元数据
                                    self.events_meta[event_key] = {'is_main': is_main}
                                    
                                    if not is_reload:
                                        tag = "[主]" if is_main else ""
                                        self.console.PRINT(f"已加载事件: {event_key} {tag}")
                                        
                        except Exception as e:
                            # 打印详细错误方便调试
                            print(f"Failed to load {module_name}: {e}") 
                            self.console.PRINT(f"加载失败 {module_name}: {e}", colors=(255, 200, 200))
            
            if is_reload:
                self.console.PRINT(f"重载完成，当前共有 {len(self.events)} 个事件。", colors=(100, 255, 100))

    def trigger_event(self, event_name, things_instance,silent=False):
            if event_name in self.events:
                try:
                    # 记录调用栈
                    self.call_stack.append(event_name)
                    return self.events[event_name](things_instance)
                except Exception as e:
                    # [关键] 打印详细堆栈，而不是简单的“未找到”
                    import traceback
                    error_msg = traceback.format_exc()
                    print(f"❌ 事件 [{event_name}] 运行崩溃:\n{error_msg}") # 打印到终端
                    self.console.PRINT(f"事件运行出错: {e}", colors=(255, 0, 0)) # 打印到游戏
                    return None
                finally:
                    if self.call_stack: self.call_stack.pop()
            else:
                # 只有真的不在字典里，才报未找到
                if not silent:
                    self.console.PRINT(f"未找到事件: {event_name}", colors=(255, 100, 100))
                return None
    def get_save_stack(self):
        """
        [新增] 获取用于存档的事件栈
        只返回那些被标记为 is_main_event=True 的事件
        """
        # 使用列表推导式进行过滤
        # 只有在 events_meta 中记录为 is_main 的事件才会被保留
        return [
            evt for evt in self.call_stack 
            if self.events_meta.get(evt, {}).get('is_main', False)
        ]