def event_start(this):
    loadidlist=['1','2','3','4','5','99','10','8']#这是一个示例，如果你们也有这种需要进入的循环的话请把每一个循环中需要使用的事件id加入这种列表中并初始化
    start_eventid={}
    for i in this.event_manager.eventid:
        if i in loadidlist:
            start_eventid[i]=this.event_manager.eventid[i]
    if this.input == '0':
        running = True
        while running:
            this.input = this.console.INPUT()
            this.console.PRINT("[1]测试文本         [2]查询位置         [3]商店         [4]音乐控制")
            this.console.PRINT(f"[5]显示当前音乐     [99]退出            [10]查看当前加载事件           [8]helloworld！")
            if this.input == '99':
                running = False
            elif this.input:
                if this.input == '1':
                    this.event_manager.trigger_event('text',this)
                elif this.input == '2':
                    this.event_manager.trigger_event('getpwd',this)
                elif this.input == '3':
                    this.event_manager.trigger_event('shop',this)
                elif this.input == '4':
                    this.event_manager.trigger_event('music_control',this)
                elif this.input == '5':
                    if this.console.music_box:
                        status = this.console.music_box.get_status()
                        current_volume = this.console.music_box.get_volume()
                        this.console.PRINT(f"音乐状态: {status}")
                        this.console.PRINT(f"当前音量: {current_volume:.2f}")
                        if this.console.current_music_name:
                            this.console.PRINT(f"当前音乐: {this.console.current_music_name}")
                        elif this.console.music_box.url:
                            music_name = os.path.basename(this.console.music_box.url)
                            this.console.PRINT(f"当前音乐: {music_name}")
                    else:
                        this.console.PRINT("音乐系统未初始化", colors=(255, 200, 200))
                    this.console.PRINT("按任意键继续...")
                    this.console.INPUT()
                elif this.input == '10':
                    this.event_manager.trigger_event('logevent',this)
                elif this.input=='8':
                    this.event_manager.trigger_event('helloworld',this)
                this.console.PRINT("")
event_start.event_id = "start"
event_start.event_name = "开始"
event_start.event_trigger = "0"