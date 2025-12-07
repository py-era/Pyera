def event_showme(things):
    console = things.console
    if things.input=='debug':
        console.PRINT_DIVIDER("=", 60, (255, 200, 100))
        console.PRINT("调试信息：图片数据字典", (255, 255, 200))
        console.PRINT_DIVIDER("-", 40, (200, 200, 200))
        
        # 1. 显示 image_data 字典信息
        console.PRINT("image_data 字典统计:", (200, 220, 255))
        console.PRINT(f"  总图片数: {len(console.image_data)}", (200, 200, 200))
        
        # 按角色ID分组统计
        chara_counts = {}
        for img_ref, img_info in console.image_data.items():
            chara_id = img_info.get('chara_id', 'unknown')
            chara_counts[chara_id] = chara_counts.get(chara_id, 0) + 1
        
        console.PRINT("按角色ID分组:", (200, 220, 255))
        for chara_id, count in chara_counts.items():
            console.PRINT(f"  角色 {chara_id}: {count}张图片", (200, 200, 200))
        
        console.PRINT_DIVIDER("-", 40, (150, 150, 150))
        
        # 显示前20个图片数据
        console.PRINT("image_data 前20个条目:", (200, 220, 255))
        count = 0
        for img_ref, img_info in console.image_data.items():
            if count >= 20:
                console.PRINT(f"  ... 还有{len(console.image_data)-20}个条目未显示", (200, 200, 200))
                break
            
            source_file = img_info.get('source_file', '未知')
            chara_id = img_info.get('chara_id', '未知')
            x = img_info.get('x', 0)
            y = img_info.get('y', 0)
            width = img_info.get('width', 270)
            height = img_info.get('height', 270)
            
            console.PRINT(f"  [{count}] {img_ref}", (220, 220, 255))
            console.PRINT(f"      源文件: {source_file}", (180, 200, 220))
            console.PRINT(f"      角色ID: {chara_id}, 裁剪: [{x},{y},{width},{height}]", (180, 200, 220))
            count += 1
        
        console.PRINT_DIVIDER("=", 60, (200, 150, 255))
        console.PRINT("chara_images 字典信息", (255, 255, 200))
        console.PRINT_DIVIDER("-", 40, (200, 200, 200))
        
        # 2. 显示 chara_images 字典信息
        console.PRINT("chara_images 字典统计:", (200, 220, 255))
        console.PRINT(f"  总角色数: {len(console.chara_images)}", (200, 200, 200))
        
        # 显示每个角色的图片列表
        for chara_id, img_list in console.chara_images.items():
            chara_name = console.init.charaters_key.get(chara_id, {}).get('名前', f'角色{chara_id}')
            console.PRINT(f"角色 {chara_name}({chara_id}): {len(img_list)}张图片", (220, 200, 255))
            
            # 显示前10个图片引用名
            for i in range(min(10, len(img_list))):
                img_ref = img_list[i]
                img_info = console.image_data.get(img_ref, {})
                source_file = img_info.get('source_file', '未知')
                console.PRINT(f"  [{i}] {img_ref}", (200, 220, 220))
                console.PRINT(f"      -> 源文件: {source_file}", (180, 200, 200))
            
            if len(img_list) > 10:
                console.PRINT(f"  ... 还有{len(img_list)-10}张图片未显示", (200, 200, 200))
            
            console.PRINT("")  # 空行
        
        # 3. 显示图片缓存信息
        console.PRINT_DIVIDER("=", 60, (150, 200, 255))
        console.PRINT("图片缓存信息", (255, 255, 200))
        console.PRINT_DIVIDER("-", 40, (200, 200, 200))
        
        if hasattr(console, 'image_cache'):
            console.PRINT(f"已缓存的源图片文件数: {len(console.image_cache)}", (200, 200, 200))
            
            count = 0
            for source_file, surface in console.image_cache.items():
                if count >= 10:
                    console.PRINT(f"  ... 还有{len(console.image_cache)-10}个缓存文件未显示", (200, 200, 200))
                    break
                
                # 获取图片尺寸
                width, height = surface.get_size() if surface else (0, 0)
                console.PRINT(f"  [{count}] {source_file}: {width}x{height}", (200, 220, 220))
                count += 1
        else:
            console.PRINT("未找到 image_cache 属性", (255, 200, 200))
        
        # 4. 搜索特定图片的功能（可选）
        console.PRINT_DIVIDER("=", 60, (100, 200, 100))
        console.PRINT("搜索功能：输入图片引用名或部分名称进行搜索", (200, 255, 200))
        console.PRINT("输入 'exit' 退出搜索", (200, 255, 200))
        
        while True:
            console.PRINT("请输入搜索关键词:", (200, 220, 255))
            keyword = console.INPUT()
            
            if not keyword or keyword.lower() == 'exit':
                break
            
            # 搜索图片
            results = []
            for img_ref, img_info in console.image_data.items():
                if keyword.lower() in img_ref.lower() or keyword.lower() in img_info.get('source_file', '').lower():
                    results.append((img_ref, img_info))
            
            if results:
                console.PRINT(f"找到 {len(results)} 个匹配结果:", (200, 255, 200))
                for i, (img_ref, img_info) in enumerate(results[:10]):  # 只显示前10个
                    source_file = img_info.get('source_file', '未知')
                    chara_id = img_info.get('chara_id', '未知')
                    console.PRINT(f"  [{i}] {img_ref}", (220, 220, 255))
                    console.PRINT(f"      源文件: {source_file}, 角色ID: {chara_id}", (180, 200, 220))
                
                if len(results) > 10:
                    console.PRINT(f"  ... 还有{len(results)-10}个结果未显示", (200, 200, 200))
            else:
                console.PRINT("未找到匹配的图片", (255, 200, 200))
            
            console.PRINT_DIVIDER("-", 30, (150, 150, 150))
        
        console.PRINT_DIVIDER("=", 60, (255, 100, 100))
        console.PRINT("调试信息显示完毕", (255, 200, 100))

event_showme.event_id = "showme"
event_showme.event_name = "让我看看字典"
event_showme.event_trigger = "debug"