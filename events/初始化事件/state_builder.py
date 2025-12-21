import datetime

def event_build_allstate(this):
    """
    初始化构建所有角色的状态字典 (allstate) - 全量同步版 (含 Base, Abl, Talent, Exp, Mark, Cflag, Ex)
    """
    init = this.console.init
    allstate = {}

    # --- 0. 辅助函数：创建默认模板 ---
    def create_template(csv_name):
        template = {}
        # 尝试获取全局定义 (兼容大小写及首字母大写)
        def_dict = init.global_key.get(csv_name, {}) or \
                   init.global_key.get(csv_name.upper(), {}) or \
                   init.global_key.get(csv_name.capitalize(), {})

        for key, val in def_dict.items():
            # 获取属性名
            prop_name = str(val)
            if isinstance(val, dict):
                prop_name = val.get('name') or val.get('全名') or str(key)
            
            if prop_name:
                template[str(prop_name)] = 0 # 默认值 0
        return template

    # [预生成所有模板]
    base_template = create_template('Base')
    abl_template = create_template('Abl')
    talent_template = create_template('Talent')
    exp_template = create_template('exp')
    mark_template = create_template('Mark')
    cflag_template = create_template('Cflag') 
    ex_template = create_template('ex') # [新增] 对应 ex.csv
    # 获取装备定义
    equip_slots_def = init.global_key.get('Equip', {})
    clothing_db = init.global_key.get('Tequip', {})
    # 获取地牢属性定义
    #dungeon_stat_template = create_template('角色地牢属性')

    # --- 遍历所有已注册的角色 ---
    for chara_id in init.chara_ids:
        raw_data = init.charaters_key.get(chara_id, {})
        print(raw_data)
        # 1. 基础信息
        char_state = {
            'id': chara_id,
            'name': raw_data.get('全名', '未命名'),
            'callname': raw_data.get('小名', raw_data.get('全名', '未命名')),
            'fullname': raw_data.get('全名', ''), 
            'data': raw_data, 
        }

        # 2. 才能 (Talent)
        talents = talent_template.copy()
        if '素质' in raw_data:
            for k, v in raw_data['素质'].items():
                try: talents[k] = int(v)
                except: talents[k] = v 
        char_state['talents'] = talents

        # 3. [核心修改] 属性值校准 (Base + Abl -> attributes)
        # 逻辑：遍历所有可能的属性，如果角色CSV里有定义，就设为CSV里的值(最大值)；否则设为0
        attributes = {}
        
        # --- 处理 Base (基础数值：体力、气力等) ---
        # 1. 获取源数据 (兼容多种写法：基础/基础/BASE)
        # 这一步非常关键，解决了"体力为0"的 Bug
        source_base = raw_data.get('基础') or raw_data.get('基础') or raw_data.get('BASE') or {}
        
        # 2. 遍历全局定义的模板 (base_template 包含所有可能的属性名)
        for key in base_template.keys():
            # 检查角色是否有这个属性
            if key in source_base:
                try:
                    # [校准] 将当前值(attributes) 初始化为 CSV中的设定值(最大值)
                    attributes[key] = int(source_base[key])
                except ValueError:
                    attributes[key] = 0
            else:
                # 没定义则默认为 0
                attributes[key] = 0

        # --- 处理 Abl (能力等级：技巧、顺从等) ---
        # 1. 获取源数据 (兼容多种写法：能力/ABL)
        source_abl = raw_data.get('能力') or raw_data.get('ABL') or {}
        
        # 2. 遍历全局定义
        for key in abl_template.keys():
            if key in source_abl:
                try:
                    # [校准] 等级初始化为 CSV 中的设定值
                    attributes[key] = int(source_abl[key])
                except ValueError:
                    attributes[key] = 0
            else:
                attributes[key] = 0
        
        char_state['attributes'] = attributes

        # 4. [核心修改] 经验 (Exp)
        # 使用模板补全，防止 KeyError
        exps = exp_template.copy()
        source_exp = raw_data.get('经验') or raw_data.get('EXP') or {}
        for k, v in source_exp.items():
            try: exps[k] = int(v)
            except: pass
        char_state['exp'] = exps

        # 5. [核心修改] 绝顶/EX (Ex)
        # 通常用于记录当前的绝顶次数或积累值
        exs = ex_template.copy()
        source_ex = raw_data.get('EX') or raw_data.get('绝顶') or {}
        for k, v in source_ex.items():
            try: exs[k] = int(v)
            except: pass
        char_state['ex'] = exs

        # 6. 刻印 (Mark)
        marks = mark_template.copy()
        source_mark = raw_data.get('刻印') or raw_data.get('MARK') or {}
        for k, v in source_mark.items():
            try: marks[k] = int(v)
            except: pass
        char_state['mark'] = marks

        # 7. CFLAG 系统同步
        cflags = cflag_template.copy()
        if 'CFLAG' in raw_data:
            for k, v in raw_data['CFLAG'].items():
                key = int(k) if k.isdigit() else k
                try:
                    cflags[key] = int(v)
                except ValueError:
                    cflags[key] = v
        char_state['cflags'] = cflags

        # 8. 装备状态
        equip_state = {}
        chara_init_equip = raw_data.get('装备') or raw_data.get('EQUIP') or {}
        
        for slot_id, slot_val in equip_slots_def.items():
            slot_name = str(slot_val)
            if isinstance(slot_val, dict):
                slot_name = slot_val.get('name', str(slot_id))
            
            item_id = str(chara_init_equip.get(str(slot_id), '0'))
            item_name = "无"
            if item_id != '0' and item_id in clothing_db:
                item_data = clothing_db[item_id]
                if isinstance(item_data, dict):
                    item_name = item_data.get('name', '未知服装')
                else:
                    item_name = str(item_data)
            
            equip_state[str(slot_id)] = {
                'slot_name': slot_name,
                'item_id': item_id,
                'item_name': item_name
            }
        char_state['equip'] = equip_state

        # 9. 特殊状态 (运行时)
        char_state['states'] = {'怀孕': 0, '妊娠': 0, '発情': 0, '绝顶': 0}

        # 10. 立绘信息
        loaded_images = this.console.chara_images.get(chara_id, {})
        available_types = list(loaded_images.keys())
        if not available_types: available_types = ['初始绘']

        draw_type = raw_data.get('draw_type')
        if draw_type not in available_types:
            draw_type = available_types[0]
            raw_data['draw_type'] = draw_type
            
        default_face = '顔絵_服_通常' if draw_type == '初始绘' else '别颜_服_通常'
        face_name = raw_data.get('DrawName', default_face)
        if not face_name: face_name = default_face

        full_img_key = f"{chara_id}_{draw_type}_{face_name}_{chara_id}"

        char_state['portrait'] = {
            'current_type': draw_type,
            'current_face': face_name,
            'full_key': full_img_key,
            'available': available_types, 
        }

        # 11. 物品栏
        inventory = {}
        raw_items = raw_data.get('物品栏')
        if raw_items:
            if isinstance(raw_items, list):
                item_str = "".join(str(x) for x in raw_items)
            else:
                item_str = str(raw_items)
            
            clean_str = item_str.replace('[', '').replace(']', '').replace("'", "").replace('"', '').strip()
            if clean_str:
                if '|' not in clean_str and ',' in clean_str:
                    clean_str = clean_str.replace(',', '|')
                for group in clean_str.split('|'):
                    group = group.strip()
                    if not group: continue
                    if ':' in group:
                        parts = group.split(':')
                        item_id = parts[0].strip()
                        try: count = int(parts[1].strip())
                        except: count = 1
                    else:
                        item_id = group.strip()
                        count = 1
                    if item_id:
                        inventory[item_id] = inventory.get(item_id, 0) + count
        char_state['inventory'] = inventory

        # 12. 历史
        char_state['location_history'] = []
        allstate[chara_id]=char_state
    this.console.allstate = allstate
    return allstate

def event_get_context_state(this):
    """
    获取当前的完整上下文快照
    trigger: get_context
    """
    # 如果 console.allstate 是 None，说明还没构建过
    if not getattr(this.console, 'allstate', None):
        event_build_allstate(this)

    # 快捷引用
    init = this.console.init
    all_chars = this.console.allstate # 现在肯定有了
    
    target_id = init.charaters_key['0'].get('选择对象')
    if not target_id:
        target_id = '0'
    
    master_id = '0'
    now = datetime.datetime.now()
    # 构建大字典
    context = {
        # --- 核心引用 (不可存档) ---
        'console': this.console,
        'init': init,
        'event_manager': this.event_manager,
        'loader': this.console.loader,
        # =======================================================
        # [核心修改] 这里就是保存"所有角色数据"的关键！
        # 把整个 allstate 字典放进去，存档时 SaveSystem 会把它递归写入 JSON
        # =======================================================
        'world_state': this.console.allstate,
        # [新增] 存档时，把当前的地图状态存进去
        # 这包含了 'status': 'corrupted' 这种动态变化
        'map_state': getattr(this.console, 'map_data', {}), 
        # --- 会话状态 ---
        'session': {
            'chara_id': target_id,
            'master_id': master_id,
            'location': init.charaters_key['0'].get('小地图', '未知'),
            # 这里假设 global_key 里有这些变量，如果没有会返回默认值
            'scene_type': init.global_key.get('System', {}).get('SCENE', '日常'),
            'time_of_day': init.global_key.get('System', {}).get('TIME', '昼'),
        },

        # --- 角色数据 (引用) ---
        'master': all_chars.get(master_id, {}),
        'chara': all_chars.get(target_id, {}),

        # --- 全局数据 ---
        'globals': {
            'variables': init.global_key.get('Variable', {}), 
            'flags': init.global_key.get('Flag', {}),
            'settings': init.global_key.get('System', {}),
        },

        # --- 系统状态 ---
        'system': {
            'time': {'year': now.year, 'month': now.month, 'day': now.day},
            'ui': {'width': this.console.screen_width, 'height': this.console.screen_height},
            # 使用 list() 或 copy() 创建副本，防止后续变化影响快照
            'event_stack': list(this.event_manager.get_save_stack()),
        }
    }

    return context

def event_apply_save_data(this):
    """
    [读档注入器 - 最终一致性版]
    流程：读取存档 -> 覆盖全局变量 -> 恢复世界状态 -> 反向绑定 init -> 更新上下文
    trigger: apply_save
    """
    save_data = getattr(this, 'temp_save_data', None)
    # [核心校准逻辑]
    if 'map_state' in save_data:
        # 1. 用存档里的地图（包含腐化状态）覆盖内存
        this.console.map_data = save_data['map_state']
        
        # 2. 重新触发 map 事件
        # 因为 map_data 变了，我们需要重新计算 charater_pwds
        # 这一步就是"校准"：让角色位置与载入的地图状态对齐
        this.event_manager.trigger_event('map', this)
        
        this.console.PRINT(">>> 地图状态已校准。", colors=(100, 255, 100))
    if not save_data: return None

    # 1. 获取基础模板 (用于填充那些存档里没有的临时数据)
    new_ctx = event_get_context_state(this)

    # ---------------------------------------------------------
    # 核心步骤 A: 恢复全局变量 (Global Key)
    # ---------------------------------------------------------
    if 'globals' in save_data:
        # 1. 更新上下文引用
        new_ctx['globals'] = save_data['globals']
        
        # 2. [反向映射] 将读出的数据写回 init.global_key
        # 这样以后调用 init.global_key['Variable'] 拿到的就是存档里的数据
        if 'variables' in save_data['globals']:
            this.console.init.global_key['Variable'] = save_data['globals']['variables']
        if 'flags' in save_data['globals']:
            this.console.init.global_key['Flag'] = save_data['globals']['flags']
        if 'settings' in save_data['globals']:
            this.console.init.global_key['System'] = save_data['globals']['settings']

    # ---------------------------------------------------------
    # 核心步骤 B: 恢复世界状态 (AllState) & 重建引用连接
    # ---------------------------------------------------------
    if 'world_state' in save_data:
        loaded_allstate = save_data['world_state']
        
        # [核心修复] 增强的连接逻辑
        for chara_id, chara_state in loaded_allstate.items():
            
            # 情况 A: 存档里有 data (正常情况，修复 save_system 后)
            if 'data' in chara_state:
                # 将存档里的数据覆盖到底层 init
                this.console.init.charaters_key[chara_id] = chara_state['data']
            
            # 情况 B: 存档里没 data (旧存档/坏档)
            # 我们必须手动补上这个键，否则后续代码会 KeyError
            else:
                # 指回游戏的初始数据，防止崩溃
                # 虽然会丢失存档里的初会面记录，但至少游戏能跑了
                chara_state['data'] = this.console.init.charaters_key.get(chara_id, {})
                # print(f"警告: 修复了角色 {chara_id} 缺失的 data 引用")

        # 3. [赋值] 将 console.allstate 指向这个加载好的大字典
        this.console.allstate = loaded_allstate
        new_ctx['world_state'] = loaded_allstate

        # 4. 更新当前 Context 里的快捷引用
        # 确保 new_ctx['master'] 指向的是新加载的 loaded_allstate 里的对象
        master_id = str(new_ctx['session'].get('master_id', '0'))
        chara_id = str(new_ctx['session'].get('chara_id', '0'))
        
        new_ctx['master'] = loaded_allstate.get(master_id, {})
        new_ctx['chara'] = loaded_allstate.get(chara_id, {})

        this.console.PRINT(">>> 数据流重定向完成 (Save -> Allstate -> Init)", colors=(100, 255, 100))

    # ---------------------------------------------------------
    # 核心步骤 C: 恢复其他 Session 信息
    # ---------------------------------------------------------
    for key in save_data:
        # 排除掉我们已经手动处理过的 key，剩下的直接覆盖
        if key not in ['console', 'init', 'event_manager', 'loader', 'world_state', 'globals']:
            new_ctx[key] = save_data[key]
            
    return new_ctx

# 注册触发器
event_build_allstate.event_trigger = "build_allstate"
event_get_context_state.event_trigger = "get_context_state"
event_apply_save_data.event_trigger = "apply_save"