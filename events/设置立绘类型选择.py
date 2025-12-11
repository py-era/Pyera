def event_设置立绘类型选择(self):
    """
    为每个角色选择并设置draw_type
    如果角色有多个draw_type选项，会询问用户选择哪一个
    """
    import random
    imgdict = {}
    
    for key in self.console.image_data:
        chara_id = self.console.image_data[key].get('chara_id')
        draw_type = self.console.image_data[key].get('draw_type')
        # 如果chara_id不在字典中，先创建空列表
        if chara_id not in imgdict:
            imgdict[chara_id] = []
        
        # 如果draw_type存在且不在列表中，则添加
        if draw_type and draw_type not in imgdict[chara_id]:
            imgdict[chara_id].append(draw_type)
    
    # 遍历角色字典
    for chara_id, chara_info in self.console.init.charaters_key.items():
        # 获取该角色的所有draw_type
        draw_types = imgdict.get(chara_id, [])
        
        if not draw_types:
            # 如果没有可用的draw_type，跳过或设置默认值
            chara_info['draw_type'] = None
            continue
        
        if len(draw_types) == 1:
            # 只有一个draw_type，直接设置
            chara_info['draw_type'] = draw_types[0]
        else:
            # 有多个draw_type，询问用户选择哪一个
            self.console.PRINT(f"角色 {chara_id} ({self.console.init.charaters_key[chara_id].get('名前', '未命名')}) 有多个立绘类型可选：")
            
            # 显示选项

            
            # 获取用户选择
            while True:
                for i, draw_type in enumerate(draw_types, 1):
                    listimg=self.console.chara_images[chara_id][draw_type]
                    self.console.PRINTIMG(random.choice(listimg))
                    self.console.PRINT(f"[{i}] {draw_type}",click=f'{i}')
                choice = self.console.INPUT()
                
                try:
                    choice_num = int(choice)
                    if 1 <= choice_num <= len(draw_types):
                        # 选择有效，设置对应的draw_type
                        chara_info['draw_type'] = draw_types[choice_num - 1]
                        break
                    else:
                        self.console.PRINT(f"请输入 1 到 {len(draw_types)} 之间的数字")
                except ValueError:
                    self.console.PRINT("请输入有效的数字")
    for i in self.console.init.chara_ids:
        try:
            listimg=self.console.chara_images[i][self.console.init.charaters_key[i].get('draw_type')]
            self.console.PRINTIMG(random.choice(listimg))
            self.console.PRINT(f"[{i}] {self.console.init.charaters_key[i].get('draw_type')}",click=f'{i}')
        except KeyError:
            self.console.PRINT(f"角色 {i} ({self.console.init.charaters_key[i].get('名前', '未命名')}) 不存在立绘文件或没有设置立绘类型")
    self.console.PRINT("所有角色的立绘类型已设置完成！")
    return self.console.init.charaters_key

# 设置事件属性
event_设置立绘类型选择.event_id = "draw_type_setup"
event_设置立绘类型选择.event_name = "设置角色立绘类型"
event_设置立绘类型选择.event_trigger = "on_start"  # 游戏开始时触发