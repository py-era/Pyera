def event_init_data_adapters(this):
    """
    [数据二次加工事件]
    用于将 init.py 读取的原始数据（String/List）转换为游戏系统所需的复杂结构（Dict）。
    这样 shop.py 等系统就可以直接使用标准化的数据，而不用关心 CSV 原始格式。
    trigger: init_data
    """
    init = this.console.init
    
    # ========================================================
    # 1. Item (物品) 数据适配
    # 原始数据可能是 List: ['苹果', '100', '好吃']
    # 目标格式: {'name': '苹果', 'price': 100, 'idn': '好吃', 'ex': ''}
    # ========================================================
    if 'Item' in init.global_key:
        raw_items = init.global_key['Item']
        formatted_items = {}
        
        # 遍历原始数据
        for key, val in raw_items.items():
            # A. 初始化全字段默认值 (保底策略)
            item_data = {
                'name': '未知物品',
                'price': 0,
                'idn': '暂无简介',
                'ex': ''
            }
            
            # B. 根据原始数据的类型进行填充
            if isinstance(val, list):
                # 列表结构: [Name, Price, Desc, Ex]
                # 使用 len 判断防止索引越界
                if len(val) > 0: item_data['name'] = str(val[0])
                if len(val) > 1: item_data['price'] = val[1]
                if len(val) > 2: item_data['idn'] = str(val[2])
                if len(val) > 3: item_data['ex'] = str(val[3])
                
            elif isinstance(val, str):
                # 只有一列字符串的情况: "物品名"
                if val.strip():
                    item_data['name'] = val.strip()
            
            # C. 类型转换 (确保价格是 Int)
            try:
                # 转为字符串并去空格，防止 " 100 " 报错
                p_str = str(item_data['price']).strip()
                # 简单的数字检查
                if p_str.lstrip('-').isdigit(): 
                    item_data['price'] = int(p_str)
                else:
                    item_data['price'] = 0
            except:
                item_data['price'] = 0

            # D. 存入结果
            formatted_items[key] = item_data
            
        # E. 将加工后的数据写回 global_key，替换原始数据
        init.global_key['Item'] = formatted_items
        this.console.PRINT(f">>> [System] Item 数据适配完成，加载了 {len(formatted_items)} 个物品。")

    # ==========================
    # 这里以后可以添加 Monster, Skill 等其他数据的适配逻辑
    # ==========================

event_init_data_adapters.event_trigger = "init_data"