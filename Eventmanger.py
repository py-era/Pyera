class EventManager:
    def __init__(self, console_instance):
        self.console = console_instance
        self.events = {}  # 存储事件函数
        self.eventid = {}  # 存事件的对应id
        self.load_events()
    
    def load_events(self):
        """动态加载事件文件"""
        import importlib
        import os
        import sys
        
        events_dir = "./events"  # 事件文件目录
        if not os.path.exists(events_dir):
            os.makedirs(events_dir)
        
        # 将events目录添加到Python路径，确保可以导入
        if events_dir not in sys.path:
            sys.path.insert(0, events_dir)
        
        # 使用os.walk遍历所有子文件夹
        for root, dirs, files in os.walk(events_dir):
            for file in files:
                if file.endswith(".py") and file != "__init__.py":
                    # 构建模块路径：将文件路径转换为模块导入路径
                    relative_path = os.path.relpath(root, events_dir)
                    
                    if relative_path == ".":
                        # 根目录下的文件
                        module_name = f"events.{file[:-3]}"
                    else:
                        # 子目录下的文件，需要将路径分隔符替换为点
                        module_path = relative_path.replace(os.sep, ".")
                        module_name = f"events.{module_path}.{file[:-3]}"
                    
                    try:
                        module = importlib.import_module(module_name)
                        
                        # 查找事件函数（以 event_ 开头的函数）
                        for attr_name in dir(module):
                            if attr_name.startswith("event_"):
                                event_func = getattr(module, attr_name)
                                event_key = attr_name[6:]  # 去掉 "event_"
                                event_id = getattr(event_func, 'event_trigger', event_key)
                                self.events[event_key] = event_func
                                self.eventid[event_id] = event_key
                                self.console.PRINT(f"已加载事件: {event_key} (来自: {module_name})")
                    except Exception as e:
                        self.console.PRINT(f"加载事件失败 {module_name}: {e}", (255, 200, 200))
    
    def trigger_event(self, event_name, things_instance):
        """触发指定事件"""
        try:
            if event_name in self.events:
                # 传递 thethings 实例给事件函数
                self.events[event_name](things_instance)
        except Exception as e:
            self.console.PRINT(f"触发事件失败 {event_name}: {e}", (255, 200, 200))