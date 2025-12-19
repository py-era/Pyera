import json
import subprocess
import sys
import os

def event_open_kojo_maker(this):
    """
    启动口上制作器 GUI (独立进程版)
    trigger: kojo_maker
    """
    this.console.PRINT("正在启动口上制作工坊 (独立进程)...", colors=(100, 255, 100))
    
    init = this.console.init

    # --- 数据提取函数 ---
    def get_data_list(key_hint, default_list=None):
        target_data = None
        if key_hint in init.global_key:
            target_data = init.global_key[key_hint]
        else:
            for k in init.global_key:
                if k.upper() == key_hint.upper():
                    target_data = init.global_key[k]
                    break
        
        if not target_data:
            return default_list if default_list else []

        result_list = []
        for val in target_data.values():
            if isinstance(val, dict):
                if 'name' in val: result_list.append(str(val['name']))
                elif '名前' in val: result_list.append(str(val['名前']))
            else:
                result_list.append(str(val))
        return list(result_list)
    # --------------------

    # 1. 准备元数据
    events_meta = {}
    for event_key, event_func in this.event_manager.events.items():
        events_meta[event_key] = {
            'is_main': getattr(event_func, 'is_main_event', False)
        }
    
    chara_names = []
    if init.chara_ids:
        for i in init.chara_ids:
            name = init.charaters_key[i].get('名前', i)
            chara_names.append(name)
    else:
        chara_names = ['0']

    game_meta = {
        'ABL': get_data_list('Abl', ['C感觉', '顺从']),
        'TALENT': get_data_list('Talent', ['恋慕']),
        'BASE': get_data_list('Base', ['体力']),
        'EXP': get_data_list('Exp', []),
        'MARK': get_data_list('Mark', []),
        'CFLAG': ['好感度', '信赖度', '睡眠深度'], 
        'TEQUIP': ['眼罩', '绳子', '跳蛋'],
        'PALAM': ['润滑', '恭顺', '欲情'],
        'CHARAS': chara_names,
        'IMAGES': list(this.console.image_data.keys()),
        'EVENTS': list(this.event_manager.events.keys()),
        'EVENTS_META': events_meta,
    }
    
    # 2. [核心修改] 将数据转储到临时 JSON 文件
    temp_meta_path = 'temp_kojo_meta.json'
    try:
        with open(temp_meta_path, 'w', encoding='utf-8') as f:
            json.dump(game_meta, f, ensure_ascii=False)
    except Exception as e:
        this.console.PRINT(f"元数据导出失败: {e}", colors=(255, 0, 0))
        return

    # 3. [核心修改] 启动独立子进程
    # 这会开启一个新的 Python 窗口运行 kojo_gui.py，不受主游戏 DPI 影响
    tool_path = os.path.join('tools', '口上制作器.py')
    
    try:
        # 使用当前的 python 解释器启动工具脚本，并传入临时文件路径作为参数
        subprocess.Popen([sys.executable, tool_path, temp_meta_path])
        this.console.PRINT("制作器已在并列窗口启动，请查看任务栏。", colors=(150, 150, 150))
    except Exception as e:
        this.console.PRINT(f"启动制作器失败: {e}", colors=(255, 0, 0))

event_open_kojo_maker.event_trigger = "kojo_maker"
event_open_kojo_maker.is_main_event = False