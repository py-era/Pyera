# dynamic_loader.py - 更新版
import pygame
import os
import json
import time
from typing import List, Tuple, Dict, Optional
from enum import Enum
# 在dynamic_loader.py中修改InlineFragment类
class InlineFragment:
    """行内片段 - 增强版，支持图片标记"""
    def __init__(self, text, color=(255, 255, 255), click_value=None, 
                 is_image_mark=False, img_info=None, clip_pos=None, size=None):
        self.text = str(text)
        self.color = color
        self.click_value = click_value
        self.is_image_mark = is_image_mark  # 是否是图片标记
        self.img_info = img_info  # 图片信息（如果是图片标记）
        self.clip_pos = clip_pos  # 裁剪位置
        self.size = size  # 调整大小
        self.width = 0  # 将在绘制时计算（图片需要特殊处理）
        self.height = 0  # 图片高度
    
    def calculate_width(self, font):
        """计算片段宽度"""
        if self.is_image_mark and self.img_info:
            # 如果是图片标记，宽度为图片宽度（或默认占位符宽度）
            if self.size:
                self.width = self.size[0]
            else:
                self.width = self.img_info.get('original_width', 270)
        else:
            # 普通文本
            self.width = font.size(self.text)[0]
        
        return self.width
    
    def render_image(self):
        """渲染图片（如果是图片标记）"""
        if not self.is_image_mark or not self.img_info:
            return None
        
        try:
            img_path = os.path.join(self.img_info.get('base_dir', './'), 
                                   self.img_info.get('filename', ''))
            
            if not os.path.exists(img_path):
                return None
            
            image = pygame.image.load(img_path).convert_alpha()
            
            # 裁剪
            clip_x, clip_y = self.clip_pos if self.clip_pos else (0, 0)
            clip_width = self.img_info.get('width', 270)
            clip_height = self.img_info.get('height', 270)
            
            # 确保裁剪区域有效
            img_width, img_height = image.get_size()
            if clip_x + clip_width > img_width:
                clip_width = img_width - clip_x
            if clip_y + clip_height > img_height:
                clip_height = img_height - clip_y
            
            if clip_width > 0 and clip_height > 0:
                clip_rect = pygame.Rect(clip_x, clip_y, clip_width, clip_height)
                clipped_image = image.subsurface(clip_rect)
            else:
                return None
            
            # 调整大小
            if self.size:
                target_width, target_height = self.size
                clipped_image = pygame.transform.scale(clipped_image, (target_width, target_height))
            
            return clipped_image
            
        except Exception as e:
            print(f"渲染行内图片失败: {e}")
            return None
class ContentType(Enum):
    TEXT = "text"
    IMAGE = "image"
    IMAGE_MARK = "image_mark"  # 图片标记类型
    IMAGE_STACK = "image_stack"  # 新增：图片叠加类型
    DIVIDER = "divider"
    MENU = "menu"

class ConsoleContent:
    """控制台内容项 - 支持行内片段"""
    def __init__(self, content_type: ContentType, data, color=(255, 255, 255), height=30, 
                 metadata=None, fragments=None):
        self.type = content_type
        self.data = data  # 主文本内容（用于向后兼容）
        self.color = color
        self.height = height
        self.metadata = metadata or {}
        self.timestamp = time.time()
        
        # 行内片段（用于支持同一行内的多个部分）
        self.fragments = fragments or []
        if not self.fragments and self.data:
            # 如果没有片段但有数据，创建一个默认片段
            self.fragments = [InlineFragment(self.data, color)]
    def add_fragment(self, fragment: InlineFragment):
        """添加行内片段"""
        self.fragments.append(fragment)
    
    def get_full_text(self):
        """获取完整文本"""
        if self.fragments:
            return ''.join(f.text for f in self.fragments)
        return self.data
    
    def __repr__(self):
        return f"ConsoleContent(type={self.type}, text={self.get_full_text()[:50]})"

class DynamicLoader:
    """动态加载器 - 支持滚动和日志记录"""
    
    def __init__(self, screen_width: int, screen_height: int, font, 
                 input_area_height: int = 40, log_file: str = "log.txt"):
        """
        初始化动态加载器
        
        Args:
            screen_width: 屏幕宽度
            screen_height: 屏幕高度
            font: PyGame字体对象
            input_area_height: 输入区域高度
            log_file: 日志文件路径
        """
        self.screen_width = screen_width
        self.screen_height = screen_height
        self.font = font
        self.input_area_height = input_area_height
        # 图片信息注册表
        self.image_registry = {}  # url -> 图片信息
        self.image_surface_cache = {}  # 缓存已渲染的图片Surface
        self.placeholder_color = (100, 100, 150)  # 图片加载前的占位符颜色
        # 内容管理
        self.history: List[ConsoleContent] = []  # 完整的历史记录
        self.max_history_length = 10000  # 最大历史记录数
        self.current_display: List[ConsoleContent] = []  # 当前显示的内容
        self.max_visible_items = 10000  # 最大可见项目数
        
        # 滚动控制
        self.scroll_offset = 0  # 滚动偏移（项目数）
        self.line_height = 30  # 每行高度
        self.content_area_height = screen_height - input_area_height - 20  # 内容区域高度
        
        # 滚动条
        self.scrollbar_width = 10
        self.scrollbar_visible = False
        self.scrollbar_color = (100, 100, 100)
        self.scrollbar_active_color = (150, 150, 150)
        
        # 日志文件
        self.log_file = log_file
        self._init_log_file()
        
        # 缓存
        self.text_surface_cache = {}  # 文本surface缓存
        self.image_cache = {}  # 图片缓存
        self.clickable_regions = []  # 存储所有可点击区域
        self.clickable_region_counter = 0  # 可点击区域计数器
        self.active_clickable_regions = []  # 当前显示的可点击区域
    def parse_image_stack_mark(self, text):
        """解析图片叠加标记字符串"""
        if not text.startswith("[IMG_STACK:") or not text.endswith("]"):
            return None, {}
        
        content = text[11:-1]  # 移除 [IMG_STACK: 和 ]
        parts = content.split("|")
        
        if not parts:
            return None, {}
        
        main_img_url = parts[0]
        params = {}
        
        for param in parts[1:]:
            if "=" in param:
                key, value = param.split("=", 1)
                params[key] = value
        
        return main_img_url, params
    def _parse_image_mark(self, text):
        """解析图片标记字符串"""
        if not text.startswith("[IMG:") or not text.endswith("]"):
            return None, {}
        
        content = text[5:-1]  # 移除 [IMG: 和 ]
        parts = content.split("|")
        
        if not parts:
            return None, {}
        
        img_url = parts[0]
        params = {}
        
        for param in parts[1:]:
            if "=" in param:
                key, value = param.split("=", 1)
                params[key] = value
        
        return img_url, params
    def register_image_info(self, url, img_info):
        """注册图片信息"""
        if not hasattr(self, 'image_registry'):
            self.image_registry = {}
        
        self.image_registry[url] = img_info
    def get_registered_image_info(self, url):
        """获取已注册的图片信息"""
        if hasattr(self, 'image_registry') and url in self.image_registry:
            return self.image_registry[url]
        return None
    def add_image_mark(self, img_mark, click_value=None):
        """
        添加图片标记到历史记录 - 增强版，支持图片叠加
        
        Args:
            img_mark: 图片标记字符串，格式 [IMG:图片ID|参数] 或 [IMG_STACK:图片1|参数]
            click_value: 点击时输入的文本
        """
        # 检查是否是图片叠加标记
        if img_mark.startswith("[IMG_STACK:"):
            return self._add_image_stack_mark(img_mark, click_value)
        
        # 原有的单张图片处理逻辑
        img_url, params = self._parse_image_mark(img_mark)
        if not img_url:
            return self.add_text(img_mark)
        
        img_info = self.get_registered_image_info(img_url)
        
        if not img_info:
            item = ConsoleContent(
                ContentType.TEXT,
                f"[图片未找到: {img_url}]",
                color=(255, 100, 100),
                height=self.line_height
            )
            self.history.append(item)
            self._update_current_display()
            return item
        
        # 解析参数
        clip_pos = None
        size = None
        
        if 'clip' in params:
            clip_x, clip_y = map(int, params['clip'].split(','))
            clip_pos = (clip_x, clip_y)
        
        if 'size' in params:
            width, height = map(int, params['size'].split(','))
            size = (width, height)
        
        # 创建图片内容项
        item = ConsoleContent(
            ContentType.IMAGE_MARK,
            img_mark,
            height=size[1] + 10 if size else img_info.get('original_height', 270) + 10,
            metadata={
                'img_url': img_url,
                'img_info': img_info,
                'clip_pos': clip_pos,
                'size': size,
                'click_value': click_value,
                'cached_surface': None,
                'needs_rendering': True
            }
        )
        
        if click_value:
            item.metadata['clickable'] = True
            item.metadata['region_id'] = self.clickable_region_counter
            
            self.clickable_regions.append({
                'id': self.clickable_region_counter,
                'content_item': item,
                'click_value': click_value,
                'text': f"[图片] {img_url}",
                'type': 'image'
            })
            
            self.clickable_region_counter += 1
        
        self.history.append(item)
        self._write_to_log(f"[IMAGE] {img_url}")
        self._update_current_display()
        
        if self.scroll_offset <= 5:
            self.scroll_to_bottom()
        
        return item

    def _add_image_stack_mark(self, img_mark, click_value=None):
        """
        添加图片叠加标记
        """
        # 格式: [IMG_STACK:主图片|img_list=图片1,图片2,...|clip=x,y|size=w,h|click=值]
        main_img_url, params = self.parse_image_stack_mark(img_mark)
        
        if not main_img_url or 'img_list' not in params:
            return self.add_text(img_mark)
        
        # 解析图片列表
        img_list_str = params['img_list']
        img_list = img_list_str.split(',')
        
        if not img_list:
            return self.add_text("[空图片列表]")
        
        # 获取所有图片的信息
        img_infos = {}
        for img_url in img_list:
            img_info = self.get_registered_image_info(img_url)
            if img_info:
                img_infos[img_url] = img_info
        
        # 解析其他参数
        clip_pos = None
        size = None
        chara_id = params.get('chara')
        draw_type = params.get('type')
        
        if 'clip' in params:
            clip_x, clip_y = map(int, params['clip'].split(','))
            clip_pos = (clip_x, clip_y)
        
        if 'size' in params:
            width, height = map(int, params['size'].split(','))
            size = (width, height)
        
        # 计算高度
        if size:
            height = size[1] + 10
        else:
            # 使用第一个图片的高度
            first_img_url = img_list[0]
            first_info = img_infos.get(first_img_url, {})
            height = first_info.get('original_height', 270) + 10
        
        # 创建图片叠加内容项
        item = ConsoleContent(
            ContentType.IMAGE_STACK,
            img_mark,
            height=height,
            metadata={
                'img_list': img_list,
                'img_infos': img_infos,
                'clip_pos': clip_pos,
                'size': size,
                'click_value': click_value,
                'chara_id': chara_id,
                'draw_type': draw_type,
                'cached_surface': None,
                'needs_rendering': True
            }
        )
        
        if click_value:
            item.metadata['clickable'] = True
            item.metadata['region_id'] = self.clickable_region_counter
            
            self.clickable_regions.append({
                'id': self.clickable_region_counter,
                'content_item': item,
                'click_value': click_value,
                'text': f"[图片叠加] {len(img_list)}张",
                'type': 'image_stack'
            })
            
            self.clickable_region_counter += 1
        
        self.history.append(item)
        self._write_to_log(f"[IMAGE_STACK] {len(img_list)}张图片")
        self._update_current_display()
        
        if self.scroll_offset <= 5:
            self.scroll_to_bottom()
        
        return item
    
    def set_font(self, font):
        self.font = font

    
    def handle_mouse_click(self, mouse_pos: Tuple[int, int]) -> Optional[str]:
        """
        处理鼠标点击事件
        
        Args:
            mouse_pos: 鼠标位置 (x, y)
            
        Returns:
            点击的文本值，如果没有点击可点击区域则返回None
        """
        # 更新活动点击区域
        self._update_active_clickable_regions()
        
        # 检查是否点击了任何活动区域
        for region in self.active_clickable_regions:
            if region['rect'].collidepoint(mouse_pos):
                return region['click_value']
        
        return None
    
    def _update_active_clickable_regions(self):
        """更新当前显示的可点击区域"""
        self.active_clickable_regions = []
        current_y = 10
        
        # 遍历当前显示的内容项
        for item in self.current_display:
            # 检查普通文本点击区域
            if 'clickable' in item.metadata and item.metadata['clickable']:
                # 根据项目类型计算区域
                region_rect = None
                
                if item.type == ContentType.TEXT:
                    # 文本区域
                    text_width = self.font.size(item.data)[0] if item.data else 0
                    region_rect = pygame.Rect(10, current_y, text_width, item.height)
                
                elif item.type == ContentType.IMAGE:
                    # 图片区域
                    if item.data in self.image_cache:
                        image = self.image_cache[item.data]
                        img_x = 10  # 图片从左侧开始
                        region_rect = pygame.Rect(img_x, current_y, image.get_width(), item.height)
                
                if region_rect:
                    # 查找对应的点击区域记录
                    for region in self.clickable_regions:
                        if region.get('content_item') == item and region.get('type') in ['text', 'image']:
                            region['rect'] = region_rect
                            self.active_clickable_regions.append({
                                'id': region['id'],
                                'rect': region_rect,
                                'click_value': region['click_value'],
                                'text': region['text'],
                                'type': region['type']
                            })
            
            # 检查行内片段点击区域
            elif item.fragments:
                current_x = 10
                
                for i, fragment in enumerate(item.fragments):
                    # 计算片段宽度
                    fragment.calculate_width(self.font)
                    
                    # 检查是否需要换行
                    available_width = self.screen_width - current_x - 20
                    if fragment.width > available_width and current_x > 10:
                        current_x = 10
                        current_y += item.height
                    
                    # 如果是可点击片段
                    if fragment.click_value:
                        region_rect = pygame.Rect(current_x, current_y, fragment.width, item.height)
                        
                        # 查找对应的点击区域记录
                        for region in self.clickable_regions:
                            if (region.get('content_item') == item and 
                                region.get('fragment_index') == i and 
                                region.get('type') == 'inline_fragment'):
                                region['rect'] = region_rect
                                self.active_clickable_regions.append({
                                    'id': region['id'],
                                    'rect': region_rect,
                                    'click_value': region['click_value'],
                                    'text': region['text'],
                                    'type': region['type']
                                })
                    
                    current_x += fragment.width
                
                # 一行绘制完毕，换行
                if item.fragments:
                    current_y += item.height
            else:
                # 更新Y位置
                current_y += item.height
    def clear_clickable_regions(self):
        """清空所有可点击区域"""
        self.clickable_regions = []
        self.active_clickable_regions = []
        self.clickable_region_counter = 0
        
        # 清空历史记录中所有内容的点击元数据

    def _init_log_file(self):
        """初始化日志文件"""
        try:
            # 创建日志文件目录（如果不存在）
            log_dir = os.path.dirname(self.log_file)
            if log_dir and not os.path.exists(log_dir):
                os.makedirs(log_dir)
                
            # 写入初始信息
            with open(self.log_file, 'a', encoding='utf-8') as f:
                f.write(f"\n{'='*60}\n")
                f.write(f"会话开始时间: {time.strftime('%Y-%m-%d %H:%M:%S')}\n")
                f.write(f"{'='*60}\n\n")
        except Exception as e:
            print(f"初始化日志文件失败: {e}")

    def add_text(self, text: str, color: Tuple[int, int, int] = (255, 255, 255)) -> List[ConsoleContent]:
        """
        添加文本到历史记录
        
        Args:
            text: 要添加的文本
            color: 文本颜色
            
        Returns:
            添加的内容项列表
        """
        added_items = []
        
        # 处理空文本
        if text is None or text == "":
            item = ConsoleContent(ContentType.TEXT, "", color, self.line_height)
            self.history.append(item)
            self._write_to_log("")
            added_items.append(item)
            self._update_current_display()
            
            # 自动滚动到底部（如果已经在底部附近）
            if self.scroll_offset <= 5:
                self.scroll_to_bottom()
            
            return added_items
        
        # 处理制表符
        text = text.replace('\t', '    ')
        
        # 分割文本为多行
        lines = []
        current_line = ""
        
        for char in text:
            # 处理换行符
            if char == '\n':
                if current_line:
                    lines.append(current_line)
                    current_line = ""
                lines.append("")  # 空行
                continue
            
            # 测试添加当前字符后的宽度
            test_line = current_line + char
            text_width = self.font.size(test_line)[0]
            
            # 如果超出屏幕宽度（减去滚动条和边距）
            max_width = self.screen_width - 40 - (self.scrollbar_width if self.scrollbar_visible else 0)
            if text_width > max_width:
                if current_line:
                    lines.append(current_line)
                current_line = char
            else:
                current_line = test_line
        
        # 添加最后一行
        if current_line:
            lines.append(current_line)
        
        # 将新行添加到历史记录
        for line in lines:
            item = ConsoleContent(ContentType.TEXT, line, color, self.line_height)
            self.history.append(item)
            self._write_to_log(line)
            added_items.append(item)
        
        # 限制历史记录长度
        if len(self.history) > self.max_history_length:
            self.history = self.history[-self.max_history_length:]
        
        # 更新当前显示
        self._update_current_display()
        
        # 自动滚动到底部（如果已经在底部附近）
        if self.scroll_offset <= 5:
            self.scroll_to_bottom()
        
        return added_items
    
    
    
    def add_divider(self, char: str = "─", length: int = 40, color: Tuple[int, int, int] = (150, 150, 150)):
        """
        添加分割线
        
        Args:
            char: 分割线字符
            length: 分割线长度
            color: 颜色
        """
        divider_text = char * length
        item = ConsoleContent(ContentType.DIVIDER, divider_text, color, self.line_height)
        self.history.append(item)
        self._write_to_log(divider_text)
        self._update_current_display()
        return item
    
    def add_menu(self, items: List[str], color: Tuple[int, int, int] = (200, 200, 255)):
        """
        添加菜单
        
        Args:
            items: 菜单项列表
            color: 颜色
        """
        added_items = []
        for item in items:
            content_item = ConsoleContent(ContentType.MENU, item, color, self.line_height)
            self.history.append(content_item)
            self._write_to_log(item)
            added_items.append(content_item)
        
        self._update_current_display()
        return added_items
    
    def _write_to_log(self, text: str):
        """写入日志文件"""
        try:
            with open(self.log_file, 'a', encoding='utf-8') as f:
                timestamp = time.strftime("[%H:%M:%S] ")
                f.write(timestamp + text + "\n")
        except Exception as e:
            print(f"写入日志失败: {e}")
    
    def _update_current_display(self):
        """更新当前显示的内容（根据滚动偏移）"""
        # 清空当前显示
        self.current_display = []
        
        # 如果历史记录为空，直接返回
        if not self.history:
            return
        
        # 计算起始索引
        # scroll_offset 表示跳过的最新项目数
        start_index = max(0, len(self.history) - 1 - self.scroll_offset)
        
        # 从起始索引开始向前（向历史方向）显示
        available_height = self.content_area_height
        current_height = 0
        
        for i in range(start_index, -1, -1):
            item = self.history[i]
            if current_height + item.height <= available_height:
                self.current_display.insert(0, item)  # 保持顺序
                current_height += item.height
            else:
                break
        
        # 如果显示区域还有空间，尝试向后（向最新方向）显示
        # 这样可以确保显示区域总是填满
        if current_height < available_height and start_index < len(self.history) - 1:
            for i in range(start_index + 1, len(self.history)):
                item = self.history[i]
                if current_height + item.height <= available_height:
                    self.current_display.append(item)  # 添加到末尾
                    current_height += item.height
                else:
                    break
        
        # 更新滚动条可见性
        total_height = sum(item.height for item in self.history)
        self.scrollbar_visible = total_height > self.content_area_height
    
    def scroll_up(self, amount: int = 1):
        """向上滚动（查看更旧的内容）"""
        # 最大滚动偏移是历史记录总数减1
        max_scroll = max(0, len(self.history) - 1)
        self.scroll_offset = min(max_scroll, self.scroll_offset + amount)
        self._update_current_display()
    
    def scroll_down(self, amount: int = 1):
        """向下滚动（查看更新的内容）"""
        self.scroll_offset = max(0, self.scroll_offset - amount)
        self._update_current_display()
    
    def scroll_to_bottom(self):
        """滚动到底部 - 显示最新的内容"""
        self.scroll_offset = 0
        self._update_current_display()
        
    def scroll_to_top(self):
        """滚动到顶部 - 显示最旧的内容"""
        # 设置滚动偏移为最大值
        self.scroll_offset = max(0, len(self.history) - 1)
        self._update_current_display()
    def clear_history(self):
        """清空历史记录"""
        self.history = []
        self.current_display = []
        self.scroll_offset = 0
        self.image_cache = {}
        
        # 在日志中记录清空操作
        self._write_to_log("[系统] 历史记录已清空")
    
    
    # dynamic_loader.py - 添加 _render_and_draw_image_stack 方法
    def _render_and_draw_image_stack(self, screen, item, x, y):
        """渲染并绘制图片叠加"""
        metadata = item.metadata
        
        # 检查是否有缓存的图片
        if metadata.get('cached_surface') and not metadata.get('needs_rendering'):
            surface = metadata['cached_surface']
            screen.blit(surface, (x, y))
            return surface
        
        # 需要渲染图片叠加
        img_list = metadata.get('img_list', [])
        img_infos = metadata.get('img_infos', {})
        
        if not img_list:
            # 绘制错误指示
            self._draw_image_error(screen, x, y, item.height - 10)
            return None
        
        try:
            # 创建透明Surface
            if metadata.get('size'):
                target_width, target_height = metadata['size']
                final_surface = pygame.Surface((target_width, target_height), pygame.SRCALPHA)
            else:
                # 使用第一个图片的尺寸
                if img_list and img_list[0] in img_infos:
                    first_info = img_infos[img_list[0]]
                    final_surface = pygame.Surface(
                        (first_info.get('original_width', 270), 
                        first_info.get('original_height', 270)), 
                        pygame.SRCALPHA
                    )
                else:
                    final_surface = pygame.Surface((270, 270), pygame.SRCALPHA)
            
            # 依次叠加每个图片
            for img_url in img_list:
                if img_url not in img_infos:
                    continue
                
                img_info = img_infos[img_url]
                img_path = img_info.get('path', '')
                
                if not os.path.exists(img_path):
                    continue
                
                try:
                    image = pygame.image.load(img_path).convert_alpha()
                    
                    # 裁剪
                    clip_pos = metadata.get('clip_pos') or (0, 0)
                    clip_x, clip_y = clip_pos
                    clip_width = img_info.get('original_width', 270)
                    clip_height = img_info.get('original_height', 270)
                    
                    # 确保裁剪区域有效
                    img_width, img_height = image.get_size()
                    if clip_x + clip_width > img_width:
                        clip_width = img_width - clip_x
                    if clip_y + clip_height > img_height:
                        clip_height = img_height - clip_y
                    
                    if clip_width > 0 and clip_height > 0:
                        clip_rect = pygame.Rect(clip_x, clip_y, clip_width, clip_height)
                        clipped_image = image.subsurface(clip_rect)
                    else:
                        continue
                    
                    # 调整大小
                    size = metadata.get('size')
                    if size:
                        target_width, target_height = size
                        clipped_image = pygame.transform.scale(
                            clipped_image, (target_width, target_height)
                        )
                    
                    # 叠加到最终Surface上
                    final_surface.blit(clipped_image, (0, 0))
                    
                except Exception as e:
                    print(f"加载叠加图片 {img_url} 失败: {e}")
                    continue
            
            # 缓存结果
            metadata['cached_surface'] = final_surface
            metadata['needs_rendering'] = False
            
            # 绘制
            screen.blit(final_surface, (x, y))
            
            # 更新点击区域（如果有点击功能）
            if metadata.get('clickable'):
                for region in self.clickable_regions:
                    if region.get('content_item') == item:
                        region['rect'] = pygame.Rect(x, y, 
                                                final_surface.get_width(), 
                                                final_surface.get_height())
            
            return final_surface
            
        except Exception as e:
            print(f"渲染图片叠加失败: {e}")
            self._draw_image_error(screen, x, y, item.height - 10)
            return None
    # dynamic_loader.py - 修改 draw 方法
    def draw(self, screen: pygame.Surface):
        """绘制内容到屏幕 - 增强版，支持图片标记和图片叠加渲染"""
        current_y = 10
        
        # 绘制可见内容
        for item in self.current_display:
            if current_y + item.height > self.content_area_height + 10:
                break
                
            if item.type == ContentType.TEXT:
                current_x = 10
                
                # 如果有行内片段，逐个绘制
                if item.fragments:
                    # 需要先计算这行的基线位置（考虑图片高度）
                    max_height_in_line = item.height - 10  # 减去边距
                    
                    for fragment in item.fragments:
                        # 计算片段宽度
                        fragment.calculate_width(self.font)
                        
                        # 检查是否需要换行
                        available_width = self.screen_width - current_x - 20
                        if fragment.width > available_width and current_x > 10:
                            current_x = 10
                            current_y += item.height
                            # 重新计算基线
                            max_height_in_line = item.height - 10
                        
                        # 如果是图片标记
                        if fragment.is_image_mark:
                            # 渲染图片
                            image = fragment.render_image()
                            if image:
                                # 计算图片位置（垂直居中于行高）
                                img_y = current_y + (max_height_in_line - image.get_height()) // 2
                                screen.blit(image, (current_x, img_y))
                                
                                # 如果有点击功能，添加点击区域
                                if fragment.click_value:
                                    # 创建点击区域
                                    region_id = self.clickable_region_counter
                                    self.clickable_region_counter += 1
                                    
                                    region_rect = pygame.Rect(current_x, img_y, 
                                                            image.get_width(), 
                                                            image.get_height())
                                    
                                    self.active_clickable_regions.append({
                                        'id': region_id,
                                        'rect': region_rect,
                                        'click_value': fragment.click_value,
                                        'type': 'image'
                                    })
                            else:
                                # 图片加载失败，绘制占位符
                                placeholder_rect = pygame.Rect(current_x, current_y, 
                                                            fragment.width, 
                                                            max_height_in_line)
                                pygame.draw.rect(screen, self.placeholder_color, placeholder_rect)
                                pygame.draw.rect(screen, (150, 150, 150), placeholder_rect, 1)
                                
                                # 绘制加载失败文本
                                error_text = self.font.render("X", True, (255, 100, 100))
                                screen.blit(error_text, (current_x + 5, current_y + 5))
                            
                            current_x += fragment.width
                        
                        else:
                            # 普通文本
                            text_surface = self.font.render(fragment.text, True, fragment.color)
                            
                            # 计算文本基线位置（与图片垂直居中）
                            text_y = current_y + (max_height_in_line - text_surface.get_height()) // 2
                            screen.blit(text_surface, (current_x, text_y))
                            
                            # 如果有点击功能，添加点击区域
                            if fragment.click_value:
                                region_id = self.clickable_region_counter
                                self.clickable_region_counter += 1
                                
                                region_rect = pygame.Rect(current_x, text_y, 
                                                        text_surface.get_width(), 
                                                        text_surface.get_height())
                                
                                self.active_clickable_regions.append({
                                    'id': region_id,
                                    'rect': region_rect,
                                    'click_value': fragment.click_value,
                                    'type': 'text'
                                })
                            
                            current_x += fragment.width
                    
                    # 一行绘制完毕，换行
                    current_y += item.height
                
                else:
                    # 普通文本（没有片段）
                    text_surface = self.font.render(item.data, True, item.color)
                    screen.blit(text_surface, (10, current_y))
                    current_y += item.height
            
            elif item.type == ContentType.IMAGE_STACK:  # 新增：处理图片叠加
                # 渲染图片叠加
                self._render_and_draw_image_stack(screen, item, 10, current_y)
                current_y += item.height
            
            elif item.type == ContentType.IMAGE_MARK:
                # 渲染图片标记
                self._render_and_draw_image_mark(screen, item, 10, current_y)
                current_y += item.height
            
            elif item.type == ContentType.IMAGE:
                # 处理旧的图片类型（向后兼容）
                if item.data in self.image_cache:
                    image = self.image_cache[item.data]
                    screen.blit(image, (10, current_y))
                
                current_y += item.height
                    
            elif item.type == ContentType.DIVIDER:
                # 绘制分割线
                text_surface = self.font.render(item.data, True, item.color)
                text_width = text_surface.get_width()
                x_pos = (self.screen_width - text_width) // 2
                screen.blit(text_surface, (x_pos, current_y))
                current_y += item.height
                
            elif item.type == ContentType.MENU:
                # 绘制菜单项
                text_surface = self.font.render(item.data, True, item.color)
                screen.blit(text_surface, (20, current_y))
                current_y += item.height
        
        # 绘制滚动条（如果需要）
        if self.scrollbar_visible and len(self.history) > 0:
            self._draw_scrollbar(screen)
    def _render_and_draw_image_mark(self, screen, item, x, y):
        """渲染并绘制图片标记"""
        metadata = item.metadata
        
        # 检查是否有缓存的图片
        if metadata.get('cached_surface') and not metadata.get('needs_rendering'):
            surface = metadata['cached_surface']
            screen.blit(surface, (x, y))
            return surface
        
        # 需要渲染图片
        img_url = metadata.get('img_url')
        img_info = metadata.get('img_info')
        
        if not img_url or not img_info:
            # 绘制错误指示
            self._draw_image_error(screen, x, y, item.height - 10)
            return None
        
        try:
            # 加载图片
            if not os.path.exists(img_info['path']):
                # 尝试其他路径
                alt_path = os.path.join("./", os.path.basename(img_info['path']))
                if not os.path.exists(alt_path):
                    self._draw_image_error(screen, x, y, item.height - 10)
                    return None
                img_info['path'] = alt_path
            
            image = pygame.image.load(img_info['path']).convert_alpha()
            
            # 裁剪
            clip_pos = metadata.get('clip_pos') or (0, 0)
            clip_x, clip_y = clip_pos
            clip_width = img_info['original_width']
            clip_height = img_info['original_height']
            
            # 确保裁剪区域有效
            img_width, img_height = image.get_size()
            if clip_x + clip_width > img_width:
                clip_width = img_width - clip_x
            if clip_y + clip_height > img_height:
                clip_height = img_height - clip_y
            
            if clip_width > 0 and clip_height > 0:
                clip_rect = pygame.Rect(clip_x, clip_y, clip_width, clip_height)
                clipped_image = image.subsurface(clip_rect)
            else:
                self._draw_image_error(screen, x, y, item.height - 10)
                return None
            
            # 调整大小
            size = metadata.get('size')
            if size:
                target_width, target_height = size
                clipped_image = pygame.transform.scale(clipped_image, (target_width, target_height))
            
            # 缓存结果
            metadata['cached_surface'] = clipped_image
            metadata['needs_rendering'] = False
            
            # 绘制
            screen.blit(clipped_image, (x, y))
            
            # 更新点击区域（如果有点击功能）
            if metadata.get('clickable'):
                for region in self.clickable_regions:
                    if region.get('content_item') == item:
                        region['rect'] = pygame.Rect(x, y, clipped_image.get_width(), clipped_image.get_height())
            
            return clipped_image
            
        except Exception as e:
            print(f"渲染图片标记失败 {img_url}: {e}")
            self._draw_image_error(screen, x, y, item.height - 10)
            return None

    def _draw_image_error(self, screen, x, y, height):
        """绘制图片错误指示"""
        placeholder_rect = pygame.Rect(x, y, 270, height)
        pygame.draw.rect(screen, (100, 100, 150), placeholder_rect)
        pygame.draw.rect(screen, (150, 150, 150), placeholder_rect, 1)
        
        error_text = self.font.render("?", True, (255, 200, 100))
        text_x = x + (270 - error_text.get_width()) // 2
        text_y = y + (height - error_text.get_height()) // 2
        screen.blit(error_text, (text_x, text_y))
    def _draw_scrollbar(self, screen: pygame.Surface):
        """绘制滚动条"""
        total_height = sum(item.height for item in self.history)
        visible_ratio = self.content_area_height / total_height
        
        # 滚动条轨道
        scrollbar_x = self.screen_width - self.scrollbar_width - 5
        pygame.draw.rect(
            screen, 
            self.scrollbar_color, 
            (scrollbar_x, 10, self.scrollbar_width, self.content_area_height),
            border_radius=3
        )
        
        # 滚动条滑块
        if visible_ratio < 1.0:
            scrollbar_height = max(20, self.content_area_height * visible_ratio)
            scrollbar_y = 10 + (self.scroll_offset / len(self.history)) * (self.content_area_height - scrollbar_height)
            
            pygame.draw.rect(
                screen,
                self.scrollbar_active_color,
                (scrollbar_x, scrollbar_y, self.scrollbar_width, scrollbar_height),
                border_radius=3
            )
    
    def handle_event(self, event: pygame.event.Event):
        """
        处理PyGame事件
        
        Args:
            event: PyGame事件
        """
        if event.type == pygame.MOUSEWHEEL:
            # 处理鼠标滚轮
            if event.y > 0:  # 向上滚动
                self.scroll_up(3)
            elif event.y < 0:  # 向下滚动
                self.scroll_down(3)
            return True
        
        elif event.type == pygame.KEYDOWN:
            # 处理键盘滚动
            if event.key == pygame.K_UP:
                self.scroll_up(1)
                return True
            elif event.key == pygame.K_DOWN:
                self.scroll_down(1)
                return True
            elif event.key == pygame.K_PAGEUP:
                self.scroll_up(10)
                return True
            elif event.key == pygame.K_PAGEDOWN:
                self.scroll_down(10)
                return True
            elif event.key == pygame.K_HOME:
                self.scroll_to_top()
                return True
            elif event.key == pygame.K_END:
                self.scroll_to_bottom()
                return True
        
        return False
    
    
    def get_scroll_info(self) -> Dict:
        """获取滚动信息"""
        total_items = len(self.history)
        visible_items = len(self.current_display)
        
        # 计算是否在顶部
        at_top = False
        if total_items > 0:
            total_height = sum(item.height for item in self.history)
            at_top = total_height > self.content_area_height and self.scroll_offset >= total_items - visible_items
        
        return {
            "total_items": total_items,
            "visible_items": visible_items,
            "scroll_offset": self.scroll_offset,
            "at_top": at_top,
            "at_bottom": self.scroll_offset == 0
        }