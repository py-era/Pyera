def event_text(this):
    this.console.PRINT('[1]测试文本')
    if this.input == '1':
        this.console.PRINT("GREEN", (0, 255, 0))
        this.console.PRINT("BLUE", (0, 0, 255))
        this.console.PRINT("RED", (255, 0, 0))
event_text.event_id = "text"
event_text.event_name = "测试事件"
event_text.event_trigger = "1"