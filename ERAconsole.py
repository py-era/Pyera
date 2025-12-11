import pygame
import sys
import time
import json
import os
from Musicbox import MusicBox
from dynamic_loader import DynamicLoader, ContentType,InlineFragment  # 导入动态加载器
from clickable import ClickableString
class SimpleERAConsole:
    from init import initall
    def __init__(self):
        pygame.init()
        self.screen_width = 1600
        self.screen_height = 1000
        self.screen = pygame.display.set_mode((self.screen_width, self.screen_height))
        pygame.display.set_caption("ERA Console")
        
        # 字体设置
        self.font = pygame.font.Font('./font/luoli.ttf', 24)
        self.line_height = 30
        
        # 输入区域高度
        self.input_area_height = 40
        
        # 初始化动态加载器
        self.loader = DynamicLoader(
            screen_width=self.screen_width,
            screen_height=self.screen_height,
            font=self.font,
            input_area_height=self.input_area_height,
            log_file="./logs/game_log.txt"
        )
        
        # 输入相关
        self.input_text = ""
        self.input_history = []  # 输入历史记录
        self.input_history_index = -1  # 当前输入历史索引
        self.cursor_visible = True
        self.cursor_timer = 0
        self.running = True
        
        # 初始化音乐盒和音乐列表
        self.music_box = None
        self.music_list = {}
        self.current_music_name = None
        self.clickable_regions = []  # 存储所有可点击区域
        self.clickable_region_counter = 0  # 可点击区域计数器
        
        # 图片数据相关
        self.image_data = {}  # 图片数据字典，键为"角色ID_图片名"，值为图片信息
        self.chara_images = {}  # 角色立绘字典，键为角色ID，值为该角色下的图片列表
        # 添加示例文本用于测试滚动
        #self._add_test_content()
    def set_font(self, font_path, font_size=24):
        """
        更改字体文件，只影响后续的输出
        
        Args:
            font_path: 字体文件路径
            font_size: 字体大小，默认为24
        """
        try:
            # 加载新字体
            new_font = pygame.font.Font(font_path, font_size)
            
            # 更新控制台字体
            self.font = new_font
            
            # 更新动态加载器中的字体，确保后续输出使用新字体
            self.loader.set_font(new_font)
            
            # 更新行高（如果需要）
            self.line_height = font_size + 6  # 可根据需要调整
            
            self.PRINT(f"字体已更改为: {os.path.basename(font_path)} (大小: {font_size})",colors= (200, 255, 200))
            
            # 刷新显示
            self._draw_display()
            pygame.display.flip()
            
        except FileNotFoundError:
            self.PRINT(f"字体文件未找到: {font_path}",colors= (255, 200, 200))
        except Exception as e:
            self.PRINT(f"更改字体失败: {e}", colors=(255, 200, 200))
    # main.py - 修改 PRINTIMG 方法
    def PRINTIMG(self, url, clip_pos=None, size=None, click=None, chara_id=None, draw_type=None, img_list=None,offset=None):
        """
        显示图片到控制台 - 增强版，支持单张图片或图片列表叠加
        
        Args:
            url: 单张图片名，或当使用img_list时的默认图片
            clip_pos: 裁剪位置 (x, y)，可选
            size: 调整大小 (width, height)，可选
            click: 点击回调函数，可选
            chara_id: 角色ID，可选
            draw_type: 立绘类型，可选
            img_list: 图片列表，用于叠加显示。可以是：
                    1. 图片名列表 [img1, img2, ...]
                    2. 字典列表 [{"img": img1, "draw_type": type1}, ...]
                    3. 混合列表
        """
        try:
            # 如果传入了img_list，则使用列表模式
            if img_list and isinstance(img_list, list):
                # 创建图片列表叠加标记
                return self._print_image_stack(img_list, clip_pos, size, click, chara_id, draw_type)
            
            # 以下是原有的单张图片处理逻辑
            img_info = self._find_image_info(url, chara_id, draw_type)
            if not img_info:
                return
            
            # 构建图片标记
            params = []
            
            if clip_pos:
                params.append(f"clip={clip_pos[0]},{clip_pos[1]}")
            
            if size:
                params.append(f"size={size[0]},{size[1]}")
            
            if click:
                params.append(f"click={click}")
            
            if chara_id:
                params.append(f"chara={chara_id}")
            
            if draw_type:
                params.append(f"type={draw_type}")
            
            # 构建标记字符串
            param_str = "|".join(params)
            img_mark = f"[IMG:{url}"
            if param_str:
                img_mark += f"|{param_str}"
            img_mark += "]"
            
            # 注册图片信息到动态加载器
            self.loader.register_image_info(url, img_info)
            
            # 使用动态加载器添加图片标记
            if click:
                self.loader.add_image_mark(img_mark, click)
            else:
                self.loader.add_image_mark(img_mark)
            
            # 刷新显示
            self._draw_display()
            pygame.display.flip()
            
        except Exception as e:
            self.PRINT(f"显示图片失败 {url}: {e}", colors=(255, 200, 200))

    def _find_image_info(self, img_url, chara_id=None, draw_type=None):
        """根据图片名、角色ID和立绘类型查找图片信息"""
        actual_url = img_url
        
        # 尝试直接查找
        if actual_url in self.image_data:
            return self._get_image_info_dict(actual_url)
        
        # 如果有角色ID，尝试加上前缀查找
        if chara_id:
            # 如果有立绘类型，优先在指定类型中查找
            if draw_type and draw_type in self.chara_images.get(chara_id, {}):
                prefixed_url = f"{chara_id}_{draw_type}_{img_url}"
                if prefixed_url in self.image_data:
                    return self._get_image_info_dict(prefixed_url)
                
                # 尝试查找原始名称匹配的图片
                for img_name in self.chara_images[chara_id][draw_type]:
                    if self.image_data[img_name].get('original_name') == img_url:
                        return self._get_image_info_dict(img_name)
            
            # 如果没有指定立绘类型，在所有立绘类型中查找
            else:
                for draw_type_key, img_list_data in self.chara_images.get(chara_id, {}).items():
                    prefixed_url = f"{chara_id}_{draw_type_key}_{img_url}"
                    if prefixed_url in self.image_data:
                        return self._get_image_info_dict(prefixed_url)
                    
                    for img_name in img_list_data:
                        if self.image_data[img_name].get('original_name') == img_url:
                            return self._get_image_info_dict(img_name)
        
        # 尝试全局查找原始名称匹配的图片
        for img_name, img_info in self.image_data.items():
            if img_info.get('original_name') == img_url:
                return self._get_image_info_dict(img_name)
        
        self.PRINT(f"图片 {img_url} 不存在于数据中", colors=(255, 200, 200))
        return None

    def _get_image_info_dict(self, img_name):
        """获取图片信息字典"""
        if img_name not in self.image_data:
            return None
        
        img_info = self.image_data[img_name]
        return {
            'path': os.path.join(img_info['base_dir'], img_info['filename']),
            'original_width': img_info['width'],
            'original_height': img_info['height'],
            'chara_id': img_info.get('chara_id'),
            'draw_type': img_info.get('draw_type'),
            'original_name': img_info.get('original_name')
        }

    def _print_image_stack(self, img_list, clip_pos=None, size=None, click=None, chara_id=None, draw_type=None,offset=None):
        """
        处理图片列表叠加显示
        
        Args:
            img_list: 图片列表，可以是：
                    1. 字符串列表：["img1", "img2", ...]
                    2. 字典列表：[{"img": "img1", "draw_type": "type1"}, ...]
        """
        try:
            processed_images = []
            
            for img_item in img_list:
                # 处理不同类型的图片项
                if isinstance(img_item, dict):
                    # 字典格式：{"img": 图片名, "draw_type": 立绘类型, "chara_id": 角色ID}
                    img_url = img_item.get('img')
                    item_draw_type = img_item.get('draw_type', draw_type)
                    item_chara_id = img_item.get('chara_id', chara_id)
                    item_click = img_item.get('click',click)
                    item_size = img_item.get('size',size)
                    item_offset=img_item.get('offset',offset)
                else:
                    # 字符串格式：直接是图片名
                    img_url = img_item
                    item_draw_type = draw_type
                    item_chara_id = chara_id
                
                # 查找图片信息
                img_info = self._find_image_info(img_url, item_chara_id, item_draw_type)
                if not img_info:
                    self.PRINT(f"图片 {img_url} 不存在于数据中", colors=(255, 200, 200))
                    continue
                
                # 使用图片名作为唯一标识
                img_name = img_info.get('original_name', img_url)
                if item_chara_id and item_draw_type:
                    img_name = f"{item_chara_id}_{item_draw_type}_{img_name}"
                
                # 注册图片信息
                self.loader.register_image_info(img_name, img_info)
                processed_images.append(img_name)
            
            if not processed_images:
                self.PRINT("图片列表为空或所有图片都不存在", colors=(255, 200, 200))
                return
            
            # 构建图片叠加标记
            # 格式: [IMG_STACK:img1,{clip:{x,x},size:{x,y},click:click_value,chara:chara_id,type:draw_type}|img2.....]
            #渲染底层透明模板时高取最高图片的高，宽取屏幕的宽
            param_str = f"img_list={','.join(processed_images)}"
            
            if clip_pos:
                param_str += f"|clip={clip_pos[0]},{clip_pos[1]}"
            
            if size:
                param_str += f"|size={size[0]},{size[1]}"
            
            if click:
                param_str += f"|click={click}"
            
            if chara_id:
                param_str += f"|chara={chara_id}"
            
            if draw_type:
                param_str += f"|type={draw_type}"
            
            # 创建特殊的图片叠加标记
            stack_mark = f"[IMG_STACK:{processed_images[0]}|{param_str}]"
            
            # 添加到动态加载器
            if click:
                self.loader.add_image_mark(stack_mark, click)
            else:
                self.loader.add_image_mark(stack_mark)
            
            # 刷新显示
            self._draw_display()
            pygame.display.flip()
            
        except Exception as e:
            self.PRINT(f"显示图片叠加失败: {e}", colors=(255, 200, 200))
    def _load_all_chara_images(self):
        """加载所有角色的立绘数据 - 支持新的目录结构 ./img/角色id/xx绘/角色id.csv"""
        if not hasattr(self, 'init') or not hasattr(self.init, 'chara_ids'):
            self.PRINT("角色ID列表未初始化，无法加载角色立绘",colors= (255, 200, 200))
            return
        
        total_chara_images = 0
        
        for chara_id in self.init.chara_ids:
            # 构建角色目录路径
            chara_dir = f"./img/{chara_id}/"
            
            if not os.path.exists(chara_dir):
                self.PRINT(f"角色目录不存在: {chara_dir}", colors=(255, 200, 200))
                continue
            
            # 初始化该角色的立绘字典
            self.chara_images[chara_id] = {}
            
            # 扫描角色目录下的所有子目录
            for item in os.listdir(chara_dir):
                item_path = os.path.join(chara_dir, item)
                
                # 只处理目录，并且目录名以"绘"结尾（假设立绘目录都以此结尾）
                if os.path.isdir(item_path) and item.endswith('绘'):
                    draw_type = item  # 例如："立绘", "表情绘", "服装绘"等
                    csv_path = os.path.join(item_path, f"{chara_id}.csv")
                    
                    if os.path.exists(csv_path):
                        try:
                            draw_image_list = []
                            
                            with open(csv_path, 'r', encoding='utf-8-sig') as f:
                                for line in f:
                                    line = line.strip()
                                    if line and not line.startswith(';'):
                                        parts = [p.strip() for p in line.split(',')]
                                        if len(parts) >= 2:
                                            name = parts[0]
                                            filename = parts[1]
                                            
                                            # 使用角色ID和立绘类型作为前缀，避免命名冲突
                                            prefixed_name = f"{chara_id}_{draw_type}_{name}"
                                            
                                            if len(parts) >= 6:
                                                try:
                                                    x, y, width, height = int(parts[2]), int(parts[3]), int(parts[4]), int(parts[5])
                                                    self.image_data[prefixed_name] = {
                                                        'filename': filename,
                                                        'base_dir': item_path,  # 使用立绘目录作为基础目录
                                                        'x': x,
                                                        'y': y,
                                                        'width': width,
                                                        'height': height,
                                                        'chara_id': chara_id,
                                                        'draw_type': draw_type,  # 新增：立绘类型
                                                        'original_name': name  # 保留原始名称
                                                    }
                                                except ValueError:
                                                    self.image_data[prefixed_name] = {
                                                        'filename': filename,
                                                        'base_dir': item_path,
                                                        'x': 0,
                                                        'y': 0,
                                                        'width': 270,
                                                        'height': 270,
                                                        'chara_id': chara_id,
                                                        'draw_type': draw_type,
                                                        'original_name': name
                                                    }
                                            else:
                                                self.image_data[prefixed_name] = {
                                                    'filename': filename,
                                                    'base_dir': item_path,
                                                    'x': 0,
                                                    'y': 0,
                                                    'width': 270,
                                                    'height': 270,
                                                    'chara_id': chara_id,
                                                    'draw_type': draw_type,
                                                    'original_name': name
                                                }
                                            
                                            draw_image_list.append(prefixed_name)
                                            total_chara_images += 1
                            
                            # 将立绘类型下的图片列表存储到字典中
                            self.chara_images[chara_id][draw_type] = draw_image_list
                            
                            chara_name = self.init.charaters_key.get(chara_id, {}).get('名前', f'角色{chara_id}')
                            self.PRINT(f"已加载角色立绘: {chara_name}({chara_id}) - {draw_type} - {len(draw_image_list)}张", colors=(200, 220, 255))
                            
                        except Exception as e:
                            self.PRINT(f"加载角色{chara_id}的{draw_type}立绘失败: {e}",colors= (255, 200, 200))
                    else:
                        self.PRINT(f"立绘数据文件不存在: {csv_path}",colors= (255, 200, 200))
        
        self.PRINT(f"角色立绘加载完成，共{total_chara_images}张图片", colors=(200, 255, 200))
        
        # 显示所有角色ID和对应的图片数量
        self.PRINT_DIVIDER("-", 40, (150, 150, 150))
        self.PRINT("角色立绘统计:", colors=(200, 200, 255))
        for chara_id, draw_types in self.chara_images.items():
            chara_name = self.init.charaters_key.get(chara_id, {}).get('名前', f'角色{chara_id}')
            total_for_chara = sum(len(images) for images in draw_types.values())
            self.PRINT(f"  {chara_name}({chara_id}): {total_for_chara}张立绘",colors= (200, 200, 200))
            for draw_type, images in draw_types.items():
                self.PRINT(f"    {draw_type}: {len(images)}张",colors= (150, 150, 150))
        self.PRINT_DIVIDER("-", 40, (150, 150, 150))
            # 在加载完成后，将图片信息注册到loader
        for img_name, img_info in self.image_data.items():
            full_path = os.path.join(img_info['base_dir'], img_info['filename'])
            self.loader.register_image_info(img_name, {
                'path': full_path,
                'original_width': img_info['width'],
                'original_height': img_info['height'],
                'chara_id': img_info.get('chara_id'),
                'draw_type': img_info.get('draw_type')
            })
    def _load_image_data(self):
        """加载所有角色的图片数据"""
        image_data = {}
        chara_images = {}
        
        # 初始化时还没有角色ID列表，这个方法会在init_all之后调用
        return image_data, chara_images
    # main.py - 修复 PRINT 方法
    def _handle_mouse_click(self, pos):
        """处理鼠标点击事件"""
        # 委托给动态加载器处理
        click_value = self.loader.handle_mouse_click(pos)
        
        if click_value:
            # 模拟输入
            self.input_text = click_value
            
            # 显示用户输入
            self.loader.add_text(f"> {click_value}", (255, 255, 200))
            self.loader.add_text("")  # 空行
            
            # 清空点击区域（避免重复点击）
            # self.loader.clear_clickable_regions()
            
            # 返回输入值
            return click_value
        
        return None

    def PRINT(self, *args, colors=None, click=None):
        """
        输出文本到控制台 - 支持可变参数和ClickableString
        
        所有参数在同一行显示，支持+连接
        """
        # 在输出新内容前清空旧的点击区域
        #self.loader.clear_clickable_regions()这是一个bug所以我取消了
        
        # 处理颜色参数
        default_color = colors or (255, 255, 255)
        
        # 如果没有参数，处理空输出
        if not args:
            self.loader.add_text("")
            self._draw_display()
            pygame.display.flip()
            return
        
        # 处理所有参数
        inline_fragments = []
        
        for arg in args:
            if isinstance(arg, ClickableString):
                # ClickableString可能包含多个部分
                for part in arg.get_parts():
                    fragment = InlineFragment(
                        part['text'],
                        part['color'],
                        part['click_value']
                    )
                    inline_fragments.append(fragment)
            elif isinstance(arg, str):
                # 普通字符串
                fragment = InlineFragment(arg, default_color, None)
                inline_fragments.append(fragment)
            else:
                # 其他类型转换为字符串
                fragment = InlineFragment(str(arg), default_color, None)
                inline_fragments.append(fragment)
        
        # 如果有全局click参数，应用到所有没有点击值的片段
        if click is not None:
            for fragment in inline_fragments:
                if fragment.click_value is None:
                    fragment.click_value = click
        
        # 添加到动态加载器
        self.loader.add_inline_fragments(inline_fragments)
        
        # 刷新显示
        self._draw_display()
        pygame.display.flip()
    def PRINT_MENU(self, items, colors=(200, 200, 255)):
        """输出菜单到控制台"""
        self.loader.add_menu(items, colors)
        self._draw_display()
        pygame.display.flip()
    
    def PRINT_DIVIDER(self, char="─", length=40, colors=(150, 150, 150)):
        """输出分割线"""
        self.loader.add_divider(char, length, colors)
        self._draw_display()
        pygame.display.flip()
    
    # main.py - 修复 INPUT 方法中的空行处理

    def INPUT(self):
            """获取用户输入 - 支持功能键和鼠标点击"""
            self.input_text = ""
            waiting_for_input = True
            
            while waiting_for_input and self.running:
                for event in pygame.event.get():
                    if event.type == pygame.QUIT:
                        self.quit()
                        return None
                    
                    # 先处理动态加载器事件（滚动等）
                    if self.loader.handle_event(event):
                        self._draw_display()
                        pygame.display.flip()
                        continue
                    
                    # 处理鼠标点击（修改为使用动态加载器的方法）
                    elif event.type == pygame.MOUSEBUTTONDOWN:
                        if event.button == 1:  # 左键点击
                            clicked_input = self._handle_mouse_click(event.pos)
                            if clicked_input:
                                return clicked_input
                    
                    elif event.type == pygame.KEYUP:
                        # 功能键处理
                        if event.key == pygame.K_RETURN:
                            user_input = self.input_text
                            
                            if user_input is not None:
                                # 保存到输入历史
                                self.input_history.append(user_input)
                                self.input_history_index = -1
                                
                                # 显示用户输入（不同颜色）
                            self.loader.add_text(f"> {user_input}", (255, 255, 200))
                            
                            # 总是添加一个空行，即使输入为空
                            self.loader.add_text("")  # 空行
                            
                            # 重置输入文本并返回
                            self.input_text = ""
                            waiting_for_input = False
                            return user_input
                        
                        elif event.key == pygame.K_BACKSPACE:
                            self.input_text = self.input_text[:-1]
                        
                        elif event.key == pygame.K_UP:
                            # 向上浏览输入历史
                            if self.input_history:
                                if self.input_history_index < len(self.input_history) - 1:
                                    self.input_history_index += 1
                                    self.input_text = self.input_history[-(self.input_history_index + 1)]
                        
                        elif event.key == pygame.K_DOWN:
                            # 向下浏览输入历史
                            if self.input_history_index > 0:
                                self.input_history_index -= 1
                                self.input_text = self.input_history[-(self.input_history_index + 1)]
                            elif self.input_history_index == 0:
                                self.input_history_index = -1
                                self.input_text = ""
                        
                        else:
                            # 只接受可打印字符
                            if event.unicode.isprintable():
                                self.input_text += event.unicode
                
                # 绘制界面
                self._draw_display()
                
                # 光标闪烁效果
                self.cursor_timer += 1
                if self.cursor_timer > 30:  # 每半秒切换一次
                    self.cursor_visible = not self.cursor_visible
                    self.cursor_timer = 0
                
                pygame.display.flip()
                pygame.time.Clock().tick(60)
            
            return None
    def _init_background_music(self):
        """初始化背景音乐 - 从global_key['musicbox']获取音乐列表"""
        try:
            # 检查是否有init属性
            if not hasattr(self, 'init') or not self.init:
                self.PRINT("初始化数据未加载，无法初始化音乐", colors=(255, 200, 200))
                return
            
            # 从全局变量获取音乐列表
            if hasattr(self.init, 'global_key') and 'musicbox' in self.init.global_key:
                self.music_list = self.init.global_key['musicbox']
                self.PRINT(f"已加载音乐列表，共{len(self.music_list)}首音乐")
                
                # 如果有音乐，播放第一首
                if self.music_list:
                    first_music_name = list(self.music_list.keys())[0]
                    first_music_path = self.music_list[first_music_name]
                    
                    # 检查音乐文件是否存在
                    if os.path.exists(first_music_path):
                        self.music_box = MusicBox(first_music_path)
                        self.current_music_name = first_music_name
                        # 播放背景音乐（无限循环）
                        self.music_box.play(loops=-1)
                        self.PRINT(f"背景音乐已加载: {first_music_name}")
                    else:
                        self.PRINT(f"背景音乐文件不存在: {first_music_path}", colors=(255, 200, 200))
                        self.PRINT("请检查音乐文件路径", colors=(255, 200, 200))
                else:
                    self.PRINT("音乐列表为空，无法播放背景音乐", colors=(255, 200, 200))
            else:
                self.PRINT("全局变量中没有找到musicbox键", colors=(255, 200, 200))
        except Exception as e:
            self.PRINT(f"初始化音乐失败: {e}", colors=(255, 200, 200))
    
    def _draw_display(self):
        """绘制整个界面"""
        # 清屏
        self.screen.fill((0, 0, 0))
        
        # 绘制动态加载器的内容
        self.loader.draw(self.screen)
        
        # 绘制输入文本和光标（始终在左下角）
        input_y = self.screen_height - self.input_area_height + 10
        input_surface = self.font.render("> " + self.input_text, True, (255, 255, 255))
        self.screen.blit(input_surface, (10, input_y))
        
        # 绘制光标
        if self.cursor_visible:
            cursor_x = 10 + self.font.size("> " + self.input_text)[0]
            pygame.draw.line(
                self.screen,
                (255, 255, 255),
                (cursor_x, input_y),
                (cursor_x, input_y + 20),
                2
            )
        
        # 绘制滚动提示
        scroll_info = self.loader.get_scroll_info()
        if scroll_info["total_items"] > scroll_info["visible_items"]:
            # 显示滚动位置信息
            scroll_text = f"行: {scroll_info['total_items'] - scroll_info['scroll_offset'] - scroll_info['visible_items'] + 1}-{scroll_info['total_items'] - scroll_info['scroll_offset']} / {scroll_info['total_items']}"
            info_surface = self.font.render(scroll_text, True, (150, 150, 150))
            info_x = self.screen_width - info_surface.get_width() - 20
            self.screen.blit(info_surface, (info_x, self.screen_height - 60))
            
            # 显示滚动提示
            if not scroll_info["at_bottom"]:
                hint_surface = self.font.render("↑ 滚动查看历史", True, (100, 150, 255))
                self.screen.blit(hint_surface, (self.screen_width - hint_surface.get_width() - 20, 10))
    
    def clear_screen(self):
        """清屏"""
        self.loader.clear_history()
        self.loader.clear_clickable_regions()  # 使用加载器的方法
        self.PRINT("控制台已清空", (200, 255, 200))
    
    def show_scroll_info(self):
        """显示滚动信息"""
        scroll_info = self.loader.get_scroll_info()
        self.PRINT_DIVIDER("=", 40)
        self.PRINT("滚动信息:", (200, 200, 255))
        self.PRINT(f"总行数: {scroll_info['total_items']}", (200, 200, 200))
        self.PRINT(f"可见行数: {scroll_info['visible_items']}", (200, 200, 200))
        self.PRINT(f"滚动偏移: {scroll_info['scroll_offset']}", (200, 200, 200))
        self.PRINT(f"是否在顶部: {'是' if scroll_info['at_top'] else '否'}", (200, 200, 200))
        self.PRINT(f"是否在底部: {'是' if scroll_info['at_bottom'] else '否'}", (200, 200, 200))
        self.PRINT_DIVIDER("=", 40)
    
    
    def init_all(self):
        """初始化所有组件，包括数据和音乐"""
        try:
            from init import initall
            init = initall("./csv/")
            self.init = init  # 这里设置self.init属性
            
            # 使用动态加载器输出
            self.loader.add_divider("=", 60, (100, 200, 100))
            self.loader.add_text("少女祈祷中...", (200, 255, 200))
            
            for i in init.charaters_key:
                chara_name = init.charaters_key[i].get('名前', '未知角色')
                self.loader.add_text(f"已加载角色：{chara_name}", (200, 220, 255))
            
            time.sleep(1)
            self.loader.add_text("角色全部载入~", (100, 255, 100))
            
            # 初始化图片数据字典
            self.image_data, self.chara_images = self._load_image_data()
            
            # 加载所有角色的立绘数据
            self._load_all_chara_images()
            
            for i in init.global_key:
                self.loader.add_text(f"已加载全局设置：{i}", (200, 200, 255))
            
            time.sleep(1)
            self.loader.add_text("全部载入~", (100, 255, 100))
            self.loader.add_divider("=", 60, (100, 200, 100))
            
            # 初始化背景音乐
            self._init_background_music()
            
            # 滚动到底部
            self.loader.scroll_to_bottom()
            
            return init
        except Exception as e:
            self.PRINT(f"初始化失败: {e}", colors=(255, 200, 200))
            self.PRINT("按任意键继续...")
            self.INPUT()
            return None
    def quit(self):
        """退出程序"""
        # 停止音乐
        if self.music_box:
            self.music_box.stop()
        
        # 记录退出日志
        self.loader.add_divider("=", 60, (255, 100, 100))
        self.loader.add_text("游戏结束，感谢游玩！", (255, 200, 100))
        self.loader.add_text(f"会话日志已保存到: {self.loader.log_file}", (200, 200, 200))
        
        # 短暂显示退出信息
        self._draw_display()
        pygame.display.flip()
        pygame.time.delay(1000)
        
        self.running = False
        pygame.quit()
        sys.exit()