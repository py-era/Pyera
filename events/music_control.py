# events/music_control.py
"""
音乐控制系统模块
"""

def event_music_control(things):
    import os
    """
    音乐控制事件 - 提供音乐播放控制界面
    :param things: thethings实例，用于访问音乐盒和控制台
    """
    if not things.console.music_box:
        things.console.PRINT(things.cs("音乐系统未初始化").set_color((255, 200, 200)))
        things.console.PRINT(things.cs("按任意键继续..."))
        things.console.INPUT()
        return
    
    running = True
    while running:
        things.console.loader.add_divider("=", 40, (100, 200, 255))
        things.console.loader.add_text("════════════ 音乐控制 ════════════", (100, 150, 255))
        
        # 显示当前音乐状态
        status = things.console.music_box.get_status()
        current_volume = things.console.music_box.get_volume()
        current_pos = things.console.music_box.get_position()
        
        things.console.PRINT(f"状态: {status}")
        if things.console.current_music_name:
            things.console.PRINT(f"当前音乐: {things.console.current_music_name}")
        elif things.console.music_box.url:
            music_name = os.path.basename(things.console.music_box.url)
            things.console.PRINT(f"当前音乐: {music_name}")
        else:
            things.console.PRINT("当前音乐: 无")
        
        things.console.PRINT(f"音量: {current_volume:.2f}")
        if things.console.music_box.is_playing and not things.console.music_box.is_paused:
            things.console.PRINT(f"播放位置: {current_pos:.1f}秒")
        
        things.console.PRINT("─" * 40)
        things.console.PRINT(
            things.cs("[1] 播放音乐").click("1"), "        ",
            things.cs("[2] 暂停音乐").click("2"), "        ",
            things.cs("[3] 继续播放").click("3"), "        ",
            things.cs("[4] 停止音乐").click("4")
        )
        things.console.PRINT(
            things.cs("[5] 选择音乐").click("5"), "        ",
            things.cs("[6] 增大音量").click("6"), "        ",
            things.cs("[7] 减小音量").click("7"), "        ",
            things.cs("[8] 设置音量").click("8")
        )
        things.console.PRINT(
            things.cs("[9] 显示音乐列表").click("9"), "        ",
            things.cs("[0] 返回").click("0")
        )
        things.console.PRINT(things.cs("请输入选择:"))
        
        choice = things.console.INPUT()
        
        if choice == '0':
            running = False
        elif choice == '1':
            if things.console.music_box.url:
                things.console.music_box.play(loops=-1, fade_in=1000)
                things.console.PRINT(things.cs("音乐开始播放"))
            else:
                things.console.PRINT(things.cs("请先选择音乐文件").set_color((255, 200, 200)))
            things.console.PRINT(things.cs("按任意键继续..."))
            things.console.INPUT()
        elif choice == '2':
            things.console.music_box.pause()
            things.console.PRINT(things.cs("音乐已暂停"))
            things.console.PRINT(things.cs("按任意键继续..."))
            things.console.INPUT()
        elif choice == '3':
            things.console.music_box.countion()
            things.console.PRINT(things.cs("音乐继续播放"))
            things.console.PRINT(things.cs("按任意键继续..."))
            things.console.INPUT()
        elif choice == '4':
            things.console.music_box.stop()
            things.console.PRINT(things.cs("音乐已停止"))
            things.console.PRINT(things.cs("按任意键继续..."))
            things.console.INPUT()
        elif choice == '5':
            # 显示音乐列表供选择
            if not things.console.music_list:
                things.console.PRINT(things.cs("音乐列表为空").set_color((255, 200, 200)))
                things.console.PRINT(things.cs("按任意键继续..."))
                things.console.INPUT()
                continue
            
            things.console.loader.add_divider("=", 40, (100, 200, 255))
            things.console.loader.add_text("════════════ 音乐列表 ════════════", (100, 150, 255))
            
            music_names = list(things.console.music_list.keys())
            for i, music_name in enumerate(music_names, 1):
                things.console.PRINT(things.cs(f"[{i}] {music_name}").click(str(i)))
            
            things.console.PRINT("─" * 40)
            things.console.PRINT(things.cs("[0] 返回").click("0"))
            things.console.PRINT(things.cs("请输入要播放的音乐编号:"))
            
            music_choice = things.console.INPUT()
            if music_choice and music_choice.isdigit():
                choice_num = int(music_choice)
                if 1 <= choice_num <= len(music_names):
                    selected_music_name = music_names[choice_num - 1]
                    selected_music_path = things.console.music_list[selected_music_name]
                    
                    if os.path.exists(selected_music_path):
                        success = things.console.music_box.newurl(selected_music_path)
                        if success:
                            things.console.current_music_name = selected_music_name
                            things.console.music_box.play(loops=-1)
                            things.console.PRINT(things.cs(f"已切换到: {selected_music_name}"))
                        else:
                            things.console.PRINT(things.cs("切换音乐失败").set_color((255, 200, 200)))
                    else:
                        things.console.PRINT(things.cs(f"音乐文件不存在: {selected_music_path}").set_color((255, 200, 200)))
                elif choice_num == 0:
                    pass  # 返回
                else:
                    things.console.PRINT(things.cs("无效的选择").set_color((255, 200, 200)))
            else:
                things.console.PRINT(things.cs("无效的输入").set_color((255, 200, 200)))
            
            things.console.PRINT(things.cs("按任意键继续..."))
            things.console.INPUT()
        elif choice == '6':
            new_volume = min(1.0, current_volume + 0.1)
            things.console.music_box.set_volume(new_volume)
            things.console.PRINT(things.cs(f"音量增大到 {new_volume:.2f}"))
            things.console.PRINT(things.cs("按任意键继续..."))
            things.console.INPUT()
        elif choice == '7':
            new_volume = max(0.0, current_volume - 0.1)
            things.console.music_box.set_volume(new_volume)
            things.console.PRINT(things.cs(f"音量减小到 {new_volume:.2f}"))
            things.console.PRINT(things.cs("按任意键继续..."))
            things.console.INPUT()
        elif choice == '8':
            things.console.PRINT(things.cs("请输入音量 (0.0-1.0):"))
            vol_input = things.console.INPUT()
            try:
                vol_value = float(vol_input)
                if 0.0 <= vol_value <= 1.0:
                    things.console.music_box.set_volume(vol_value)
                    things.console.PRINT(things.cs(f"音量已设置为 {vol_value:.2f}"))
                else:
                    things.console.PRINT(things.cs("音量值必须在0.0到1.0之间").set_color((255, 200, 200)))
            except ValueError:
                things.console.PRINT(things.cs("请输入有效的数字").set_color((255, 200, 200)))
            things.console.PRINT(things.cs("按任意键继续..."))
            things.console.INPUT()
        elif choice == '9':
            # 显示音乐列表
            things.console.loader.add_divider("=", 40, (100, 200, 255))
            things.console.loader.add_text("════════════ 全部音乐 ════════════", (100, 150, 255))
            
            if not things.console.music_list:
                things.console.PRINT(things.cs("音乐列表为空").set_color((255, 200, 200)))
            else:
                music_names = list(things.console.music_list.keys())
                for i, music_name in enumerate(music_names, 1):
                    path = things.console.music_list[music_name]
                    exists = "✓" if os.path.exists(path) else "✗"
                    things.console.PRINT(things.cs(f"[{i}] {music_name} [{exists}]").click(str(i)))
            
            things.console.PRINT("─" * 40)
            things.console.PRINT(things.cs("按任意键继续..."))
            things.console.INPUT()
        else:
            things.console.PRINT(things.cs("无效的选择").set_color((255, 200, 200)))
            things.console.PRINT(things.cs("按任意键继续..."))
            things.console.INPUT()
    
    # 退出音乐控制界面
    things.console.PRINT(things.cs("已离开音乐控制"))
    things.console.loader.add_divider("=", 40, (100, 200, 255))

# 为事件函数添加元数据
event_music_control.event_id = "music_control"
event_music_control.event_name = "音乐控制"
event_music_control.event_trigger = "4"