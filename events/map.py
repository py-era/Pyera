def event_map(this):
    import json
    try:
        with open('./json/map/map.json', 'r', encoding='utf-8') as f:
            map_data = json.load(f)
        
        # 先为所有角色设置默认位置
        for i in this.console.init.chara_ids:
            this.charater_pwds[i] = {
                '大地图': '10000',
                '小地图': '10001'
            }
        
        # 根据map.json更新角色位置
        for big_map, small_maps in map_data.items():
            for small_map, charater_list in small_maps.items():
                for charater_id in charater_list:
                    if charater_id in this.charater_pwds:
                        this.charater_pwds[charater_id] = {
                            '大地图': big_map,
                            '小地图': small_map
                        }
    except Exception as e:
        this.console.PRINT(f"加载地图数据失败: {e}", colors=(255, 200, 200))

event_map.event_id = "map"
event_map.event_name = "地图初始化"