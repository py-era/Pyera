def event_logevent(this):
    import os
    """显示当前已加载的事件"""
    this.console.PRINT("════════════ 已加载事件列表 ════════════", (100, 150, 255))
    
    if not this.event_manager.events:
        this.console.PRINT("未加载任何事件", colors=(255, 200, 200))
        this.console.PRINT(f"事件目录: {os.path.abspath('./events')}", (150, 150, 150))
    else:
        events_count = len(this.event_manager.events)
        this.console.PRINT(f"已加载 {events_count} 个事件:", (200, 255, 200))
        this.console.PRINT_DIVIDER("-", 35, (100, 100, 150))
        
        # 显示所有事件
        for i, (event_name, event_func) in enumerate(this.event_manager.events.items(), 1):
            # 获取函数信息
            func_name = event_func.__name__
            func_module = event_func.__module__ if hasattr(event_func, '__module__') else "未知"
            func_doc = event_func.__doc__ or "无描述"
            
            # 显示事件信息
            this.console.PRINT(f"[{i:2d}] {event_name}", (200, 200, 255))
            this.console.PRINT(f"     函数: {func_name}()", (150, 150, 200))
            this.console.PRINT(f"     模块: {func_module}", (150, 150, 200))
            
            # 显示函数文档（简要说明）
            doc_lines = func_doc.strip().split('\n')
            if doc_lines:
                brief_doc = doc_lines[0].strip()[:60]  # 取第一行，最多60字符
                this.console.PRINT(f"     说明: {brief_doc}...", (180, 180, 180))
            
            # 检查是否有触发条件属性
            if hasattr(event_func, 'event_trigger') and event_func.event_trigger:
                trigger = event_func.event_trigger
                this.console.PRINT(f"     触发: 输入 '{trigger}'", (100, 255, 100))
            
            this.console.PRINT("")
    
    this.console.PRINT_DIVIDER("=", 40, (100, 150, 255))
    
    # 添加事件使用提示
    this.console.PRINT("事件使用说明:", (200, 200, 255))
    this.console.PRINT("  1. 在 events/ 目录下创建 .py 文件", (150, 150, 200))
    this.console.PRINT("  2. 定义以 'event_' 开头的函数", (150, 150, 200))
    this.console.PRINT("  3. 函数接受一个参数: thethings实例", (150, 150, 200))
    this.console.PRINT("  4. 可以使用 console.PRINT() 等方法", (150, 150, 200))
    this.console.PRINT_DIVIDER("-", 35, (100, 100, 150))
    this.console.PRINT("示例事件文件 (events/example.py):", (200, 200, 255))
    this.console.PRINT("  def event_myevent(things):", (150, 150, 255))
    this.console.PRINT("      things.console.PRINT('你好！')", (180, 180, 180))
    this.console.PRINT("      things.console.PRINT('输入 test:')", (180, 180, 180))
    this.console.PRINT("      if things.input == 'test':", (180, 180, 180))
    this.console.PRINT("          things.console.PRINT('测试成功！')", (180, 180, 180))
    
    this.console.PRINT("")
    this.console.PRINT("按任意键返回主菜单...")
    this.console.INPUT()
event_logevent.event_id = "logevent"
event_logevent.event_name = "查看加载事件"
event_logevent.event_trigger = "10"