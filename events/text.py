def event_text(this):
    this.console.PRINT('[1]测试文本')
    if this.input == '1':
        this.console.PRINT("GREEN",colors=(0, 255, 0))
        this.console.PRINT("BLUE",colors=(0, 0, 255))
        this.console.PRINT("RED",colors=(255, 0, 0))
event_text.event_id = "text"
event_text.event_name = "测试事件"
event_text.event_trigger = "1"