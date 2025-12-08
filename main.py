# main.py 修改部分
import pygame
import sys
import time
import json
import os
from dynamic_loader import DynamicLoader, ContentType,InlineFragment  # 导入动态加载器
from clickable import ClickableString
#这是一个快捷调用的东西，为了让PRINT变得强强
def cs(text="", color=None, click=None):
    """创建ClickableString的快捷函数"""
    return ClickableString(text, color, click)
class EventManager:
    def __init__(self, console_instance):
        self.console = console_instance
        self.events = {}  # 存储事件函数
        self.eventid={}#存事件的对应id，目前还没什么用
        self.load_events()
    def load_events(self):
        """动态加载事件文件"""
        import importlib
        import os
        events_dir = "./events"  # 事件文件目录
        if not os.path.exists(events_dir):
            os.makedirs(events_dir)
        
        # 扫描事件文件
        for file in os.listdir(events_dir):
            if file.endswith(".py"):
                module_name = f"events.{file[:-3]}"
                try:
                    module = importlib.import_module(module_name)
                    
                    # 查找事件函数（以 event_ 开头的函数）
                    for attr_name in dir(module):
                        if attr_name.startswith("event_"):
                            event_func = getattr(module, attr_name)
                            event_key = attr_name[6:]  # 去掉 "event_"
                            event_id=getattr(event_func,'event_trigger',event_key)#因为要把对应id读取进键值对应表所以这里直接读取他的触发按键
                            self.events[event_key] = event_func
                            self.eventid[event_id]=event_key
                            self.console.PRINT(f"已加载事件: {event_key}")
                except Exception as e:
                    self.console.PRINT(f"加载事件失败 {file}: {e}", (255, 200, 200))
    
    def trigger_event(self, event_name, things_instance):
        """触发指定事件"""
        if event_name in self.events:
            # 传递 thethings 实例给事件函数
            self.events[event_name](things_instance)
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
            
            self.PRINT(f"字体已更改为: {os.path.basename(font_path)} (大小: {font_size})", (200, 255, 200))
            
            # 刷新显示
            self._draw_display()
            pygame.display.flip()
            
        except FileNotFoundError:
            self.PRINT(f"字体文件未找到: {font_path}", (255, 200, 200))
        except Exception as e:
            self.PRINT(f"更改字体失败: {e}", (255, 200, 200))

    def PRINTIMG(self, url, clip_pos=None, size=None, click=None, chara_id=None, draw_type=None):
        """
        显示图片到控制台 - 支持新的目录结构
        
        Args:
            url: 图片名，可以是完整图片名（如"13_立绘_別立ち_服_睡衣_笑顔_13"）或原始图片名
            clip_pos: 裁剪位置 (x, y)，可选
            size: 调整大小 (width, height)，可选
            click: 点击回调函数，可选
            chara_id: 角色ID，可选
            draw_type: 立绘类型（如"立绘", "表情绘"等），可选
        """
        try:
            # 如果指定了角色ID，尝试查找图片
            if chara_id and chara_id in self.chara_images:
                # 如果有立绘类型，优先在指定类型中查找
                if draw_type and draw_type in self.chara_images[chara_id]:
                    # 尝试查找带角色ID和立绘类型前缀的图片名
                    prefixed_url = f"{chara_id}_{draw_type}_{url}"
                    if prefixed_url in self.image_data:
                        url = prefixed_url
                    else:
                        # 如果没有找到带前缀的，尝试在指定立绘类型的图片列表中查找
                        for img_name in self.chara_images[chara_id][draw_type]:
                            if self.image_data[img_name].get('original_name') == url:
                                url = img_name
                                break
                else:
                    # 如果没有指定立绘类型，遍历所有立绘类型查找
                    found = False
                    for draw_type_key, img_list in self.chara_images[chara_id].items():
                        # 尝试查找带角色ID和立绘类型前缀的图片名
                        prefixed_url = f"{chara_id}_{draw_type_key}_{url}"
                        if prefixed_url in self.image_data:
                            url = prefixed_url
                            found = True
                            break
                        else:
                            # 如果没有找到带前缀的，尝试在当前立绘类型的图片列表中查找
                            for img_name in img_list:
                                if self.image_data[img_name].get('original_name') == url:
                                    url = img_name
                                    found = True
                                    break
                            if found:
                                break
            
            # 检查图片数据是否存在
            if url not in self.image_data:
                self.PRINT(f"图片 {url} 不存在于数据中", (255, 200, 200))
                
                # 尝试查找原始名称匹配的图片
                found = False
                for img_name, img_info in self.image_data.items():
                    if img_info.get('original_name') == url:
                        url = img_name
                        found = True
                        break
                
                if not found:
                    return
            
            img_info = self.image_data[url]
            
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
            self.loader.register_image_info(url, {
                'path': os.path.join(img_info['base_dir'], img_info['filename']),
                'original_width': img_info['width'],
                'original_height': img_info['height'],
                'chara_id': img_info.get('chara_id'),
                'draw_type': img_info.get('draw_type')
            })
            
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
    def _load_all_chara_images(self):
        """加载所有角色的立绘数据 - 支持新的目录结构 ./img/角色id/xx绘/角色id.csv"""
        if not hasattr(self, 'init') or not hasattr(self.init, 'chara_ids'):
            self.PRINT("角色ID列表未初始化，无法加载角色立绘", (255, 200, 200))
            return
        
        total_chara_images = 0
        
        for chara_id in self.init.chara_ids:
            # 构建角色目录路径
            chara_dir = f"./img/{chara_id}/"
            
            if not os.path.exists(chara_dir):
                self.PRINT(f"角色目录不存在: {chara_dir}", (255, 200, 200))
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
                            self.PRINT(f"已加载角色立绘: {chara_name}({chara_id}) - {draw_type} - {len(draw_image_list)}张", (200, 220, 255))
                            
                        except Exception as e:
                            self.PRINT(f"加载角色{chara_id}的{draw_type}立绘失败: {e}", (255, 200, 200))
                    else:
                        self.PRINT(f"立绘数据文件不存在: {csv_path}", (255, 200, 200))
        
        self.PRINT(f"角色立绘加载完成，共{total_chara_images}张图片", (200, 255, 200))
        
        # 显示所有角色ID和对应的图片数量
        self.PRINT_DIVIDER("-", 40, (150, 150, 150))
        self.PRINT("角色立绘统计:", (200, 200, 255))
        for chara_id, draw_types in self.chara_images.items():
            chara_name = self.init.charaters_key.get(chara_id, {}).get('名前', f'角色{chara_id}')
            total_for_chara = sum(len(images) for images in draw_types.values())
            self.PRINT(f"  {chara_name}({chara_id}): {total_for_chara}张立绘", (200, 200, 200))
            for draw_type, images in draw_types.items():
                self.PRINT(f"    {draw_type}: {len(images)}张", (150, 150, 150))
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
    def _print_clickable_parts(self, parts):
        """输出可点击部分"""
        # 使用动态加载器的方法
        if any(part.get('click_value') for part in parts):
            # 如果有可点击部分，使用专门的方法
            formatted_parts = []
            for part in parts:
                formatted_parts.append({
                    'text': part['text'],
                    'color': part['color'],
                    'click_value': part.get('click_value')
                })
            self.loader.add_clickable_parts(formatted_parts)
        else:
            # 没有可点击部分，合并为普通文本
            combined_text = ''.join(part['text'] for part in parts)
            color = parts[0]['color'] if parts else (255, 255, 255)
            self.loader.add_text(combined_text, color)
        
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
                            user_input = self.input_text.strip()
                            
                            if user_input:
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
# 在 main.py 的 thethings 类中添加新功能
class MusicBox:
    def __init__(self, url=None):
        """
        初始化音乐盒
        :param url: 音乐文件路径，可以是绝对路径或相对路径
        """
        # 初始化pygame mixer模块
        pygame.mixer.init(frequency=44100, size=-16, channels=2, buffer=4096)
        
        self.url = url
        self.is_playing = False
        self.is_paused = False
        
        if url and os.path.exists(url):
            self.load_music(url)
    
    def load_music(self, url):
        """
        加载音乐文件
        :param url: 音乐文件路径
        :return: 成功加载返回True，否则返回False
        """
        try:
            if os.path.exists(url):
                pygame.mixer.music.load(url)
                self.url = url
                print(f"已加载音乐: {url}")
                return True
            else:
                print(f"错误: 文件不存在 - {url}")
                return False
        except pygame.error as e:
            print(f"加载音乐失败: {e}")
            return False
    
    def play(self, loops=0, start=0.0, fade_in=0):
        """
        播放音乐
        :param loops: 循环次数，0表示播放一次，-1表示无限循环
        :param start: 开始播放的位置（秒）
        :param fade_in: 淡入时间（毫秒）
        """
        if self.url and os.path.exists(self.url):
            if fade_in > 0:
                pygame.mixer.music.play(loops, start, fade_ms=fade_in)
            else:
                pygame.mixer.music.play(loops, start)
            self.is_playing = True
            self.is_paused = False
            print(f"开始播放: {self.url}")
        else:
            print("错误: 未加载有效的音乐文件")
    
    def stop(self):
        """停止音乐播放"""
        pygame.mixer.music.stop()
        self.is_playing = False
        self.is_paused = False
        print("音乐已停止")
    
    def pause(self):
        """暂停音乐播放"""
        if self.is_playing and not self.is_paused:
            pygame.mixer.music.pause()
            self.is_paused = True
            print("音乐已暂停")
    
    def unpause(self):
        """取消暂停，继续播放"""
        if self.is_playing and self.is_paused:
            pygame.mixer.music.unpause()
            self.is_paused = False
            print("继续播放音乐")
    
    def countion(self):
        """
        继续播放音乐（为保持与题目要求的兼容性）
        注意：方法名是countion而不是continue，因为continue是Python关键字
        """
        self.unpause()
    
    def newurl(self, url):
        """
        更换音乐文件并加载
        :param url: 新的音乐文件路径
        :return: 成功更换返回True，否则返回False
        """
        # 停止当前播放的音乐
        if self.is_playing:
            self.stop()
        
        # 加载新音乐
        return self.load_music(url)
    
    def is_loaded(self):
        """检查是否已加载音乐"""
        return self.url is not None and os.path.exists(self.url)
    
    def get_volume(self):
        """获取当前音量（0.0到1.0）"""
        return pygame.mixer.music.get_volume()
    
    def set_volume(self, volume):
        """
        设置音量
        :param volume: 音量值，范围0.0到1.0
        """
        pygame.mixer.music.set_volume(max(0.0, min(1.0, volume)))
        print(f"音量已设置为: {volume:.2f}")
    
    def get_position(self):
        """获取当前播放位置（秒）"""
        return pygame.mixer.music.get_pos() / 1000.0
    
    def fadeout(self, duration):
        """
        淡出停止音乐
        :param duration: 淡出时间（毫秒）
        """
        pygame.mixer.music.fadeout(duration)
        self.is_playing = False
        self.is_paused = False
        print(f"音乐将在{duration}毫秒内淡出")
    
    def get_status(self):
        """获取音乐播放状态"""
        if not self.is_loaded():
            return "未加载音乐"
        elif self.is_paused:
            return "已暂停"
        elif self.is_playing:
            return "播放中"
        else:
            return "已停止"
class thethings:
    def __init__(self):
        self.console = SimpleERAConsole()
        # 在创建console后立即初始化所有组件
        self.console.init_all()
        self.input = ""
        self.event_manager = EventManager(self.console)
        self.charater_pwds = {}
        self.cs = ClickableString
        self.main()
    def main(self):
        # 首先初始化地图数据
        self.event_manager.trigger_event('map',self)
        running = True
        while running:
            self.input = self.console.INPUT()
            gradient_text = (cs("红").set_color((255, 0, 0)) +cs("橙").set_color((255, 127, 0)) +cs("黄").set_color((255, 255, 0)) +cs("绿").set_color((0, 255, 0)) +cs("青").set_color((0, 255, 255)) +cs("蓝").set_color((0, 0, 255)) +cs("紫").set_color((127, 0, 255)))
            self.console.PRINT(gradient_text.click("gradient"))
            self.console.PRINTIMG("0_玩家立绘_顔絵_服_通常_0",clip_pos=(0,0),size=(200, 200))#在输出图片时请在需要输出的图片名前加上角色id_，你可以直接输出在csv中的图片名
            self.console.PRINT(cs("嗯？你来啦？欢迎来到Pera的世界！这里演示的是图片调用，很抱歉直接使用了eratw🐍版里的你小姐的立绘）").set_color((215, 200, 203)))
            self.console.PRINT(cs("[0]start").click("0"),"          ",cs("点击查看凌冬色图").click("no way!!!"),"          ",cs("点击更改字体").click("fontreset"))
            self.event_manager.trigger_event('fontreset',self)
            self.event_manager.trigger_event("top",self)
            if self.input and self.input.lower() == "quit":
                running = False
            elif self.input:
                #在这里添加事件
                if self.input=='debug':
                    self.event_manager.trigger_event('showme',self)
                self.event_manager.trigger_event('start',self)
                self.console.PRINT("")
            # 处理退出事件
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False
        
        pygame.quit()
        sys.exit()
if __name__ == "__main__":
    start = thethings()
"""    
这是为框架测试中用的一个，现在不需要了 
    def _add_test_content(self):
        添加测试内容以演示滚动功能
        colors = [
            (255, 255, 255),  # 白色
            (255, 200, 200),  # 淡红色
            (200, 255, 200),  # 淡绿色
            (200, 200, 255),  # 淡蓝色
            (255, 255, 200),  # 淡黄色
            (255, 200, 255),  # 淡紫色
        ]
        
        # 添加分割线
        self.loader.add_divider("=", 60, (100, 150, 255))
        self.loader.add_text("欢迎来到 ERA Console 动态加载器测试", (100, 200, 255))
        self.loader.add_text("使用鼠标滚轮或方向键滚动查看历史", (150, 150, 255))
        self.loader.add_divider("-", 50, (100, 100, 150))
        
        # 添加大量测试文本
        # 添加菜单示例
        self.loader.add_divider("=", 60, (150, 100, 255))
        self.loader.add_text("菜单示例:", (200, 150, 255))
        self.loader.add_menu([
            "[1] 开始游戏",
            "[2] 加载存档",
            "[3] 设置选项",
            "[4] 退出游戏"
        ])
        
        # 添加更多测试内容
        self.loader.add_divider("=", 60, (255, 150, 100))
        self.loader.add_text("滚动到底部以查看最新消息", (255, 200, 100))
        
        # 自动滚动到底部
        self.loader.scroll_to_bottom()
"""