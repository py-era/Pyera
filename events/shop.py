# shop.py
"""
商店系统模块
独立于主程序的事件模块
"""

def event_shop(things):
    """
    商店事件 - 提供物品购买界面
    :param things: thethings实例，用于访问游戏数据和控制台
    """
    running = True
    page = 0
    items_per_page = 12
    
    # 检查是否有物品数据
    if not hasattr(things.console.init, 'global_key') or 'Item' not in things.console.init.global_key:
        things.console.PRINT("商店数据未加载", colors=(255, 200, 200))
        things.console.PRINT("按任意键继续...")
        things.console.INPUT()
        return
    
    items_data = things.console.init.global_key['Item']
    item_ids = list(items_data.keys())
    
    while running:
        # 清空输出（如果需要）
        things.console.loader.add_divider("=", 40, (100, 200, 255))
        things.console.loader.add_text("════════════ 商店 ════════════", (100, 150, 255))
        
        if len(item_ids) == 0:
            things.console.PRINT("商店目前没有商品")
            things.console.PRINT("按任意键返回...")
            things.console.INPUT()
            running = False
        else:
            total_pages = (len(item_ids) + items_per_page - 1) // items_per_page
            start_idx = page * items_per_page
            end_idx = min(start_idx + items_per_page, len(item_ids))
            
            things.console.PRINT(f"第 {page + 1}/{total_pages} 页")
            things.console.PRINT("─" * 40)
            
            # 显示当前页的商品
            for i in range(start_idx, end_idx):
                item_id = item_ids[i]
                item_info = items_data[item_id]
                
                item_name = item_info.get('name', f'物品{item_id}')
                price = item_info.get('price', 0)
                
                display_num = i - start_idx + 1
                things.console.PRINT(f"{display_num:2d}. {item_name:<20} {price:>5}金币")
            
            things.console.PRINT("─" * 40)
            things.console.PRINT("n:下一页  p:上一页  数字:查看详情  e:退出")
            things.console.PRINT("请输入选择:")
            
            thisinput = things.console.INPUT().lower()
            
            if thisinput == 'e':
                running = False
            elif thisinput == 'n':
                if page < total_pages - 1:
                    page += 1
                else:
                    things.console.PRINT("已经是最后一页了")
                    things.console.PRINT("按任意键继续...")
                    things.console.INPUT()
            elif thisinput == 'p':
                if page > 0:
                    page -= 1
                else:
                    things.console.PRINT("已经是第一页了")
                    things.console.PRINT("按任意键继续...")
                    things.console.INPUT()
            elif thisinput.isdigit():
                selected = int(thisinput)
                if 1 <= selected <= (end_idx - start_idx):
                    actual_index = start_idx + selected - 1
                    item_id = item_ids[actual_index]
                    item_info = items_data[item_id]
                    
                    # 显示商品详情
                    things.console.loader.add_divider("=", 40, (100, 200, 255))
                    
                    item_name = item_info.get('name', f'物品{item_id}')
                    price = item_info.get('price', 0)
                    description = item_info.get('idn', '暂无简介')
                    
                    things.console.PRINT(f"════════════ 物品详情 ════════════")
                    things.console.PRINT(f"名称: {item_name}")
                    things.console.PRINT(f"价格: {price}金币")
                    things.console.PRINT("")
                    things.console.PRINT("简介:")
                    things.console.PRINT(f"  {description}")
                    things.console.PRINT("")
                    
                    # 显示其他属性
                    other_keys = [k for k in item_info.keys() if k not in ['name', 'price', 'idn']]
                    if other_keys:
                        things.console.PRINT("其他属性:")
                        for key in other_keys:
                            things.console.PRINT(f"  {key}: {item_info[key]}")
                    
                    things.console.PRINT("")
                    things.console.PRINT("1. 购买")
                    things.console.PRINT("2. 返回商店")
                    things.console.PRINT("请选择:")
                    
                    choice = things.console.INPUT()
                    
                    if choice == '1':
                        things.console.PRINT(f"购买了 {item_name}，花费 {price} 金币！")
                        # 这里可以添加实际的购买逻辑
                        things.console.PRINT("按任意键继续...")
                        things.console.INPUT()
                else:
                    things.console.PRINT("无效的选择")
                    things.console.PRINT("按任意键继续...")
                    things.console.INPUT()
            else:
                things.console.PRINT("无效的命令")
                things.console.PRINT("按任意键继续...")
                things.console.INPUT()
    
    # 商店退出时显示消息
    things.console.PRINT("已离开商店")
    things.console.loader.add_divider("=", 40, (100, 200, 255))

# 为事件函数添加元数据
event_shop.event_id = "shop"
event_shop.event_name = "商店系统"
event_shop.event_trigger = "3"