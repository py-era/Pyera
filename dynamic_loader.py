# dynamic_loader.py - 更新版
import pygame
import os
import json
import time
from typing import List, Tuple, Dict, Optional
from enum import Enum
class InlineFragment:
    """行内片段"""
    def __init__(self, text, color=(255, 255, 255), click_value=None):
        self.text = str(text)
        self.color = color
        self.click_value = click_value
        self.width = 0  # 将在绘制时计算
    
    def calculate_width(self, font):
        """计算片段宽度"""
        self.width = font.size(self.text)[0]
        return self.width
class ContentType(Enum):
    TEXT = "text"
    IMAGE = "image"
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
        
        # 内容管理
        self.history: List[ConsoleContent] = []  # 完整的历史记录
        self.max_history_length = 10000  # 最大历史记录数
        self.current_display: List[ConsoleContent] = []  # 当前显示的内容
        self.max_visible_items = 30  # 最大可见项目数
        
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
    def add_inline_fragments(self, fragments: List[InlineFragment]) -> ConsoleContent:
        """
        添加行内片段到历史记录（所有片段在同一行）
        
        Args:
            fragments: 行内片段列表
            
        Returns:
            添加的内容项
        """
        # 创建内容项
        item = ConsoleContent(
            ContentType.TEXT,
            "",  # 主文本为空，使用片段
            height=self.line_height,
            fragments=fragments,
            metadata={'has_inline_fragments': True}
        )
        
        self.history.append(item)
        
        # 写入日志
        full_text = item.get_full_text()
        self._write_to_log(full_text)
        
        # 为每个可点击片段创建区域记录
        for i, fragment in enumerate(fragments):
            if fragment.click_value:
                self.clickable_regions.append({
                    'id': self.clickable_region_counter,
                    'fragment_index': i,
                    'content_item': item,
                    'click_value': fragment.click_value,
                    'text': fragment.text,
                    'type': 'inline_fragment'
                })
                self.clickable_region_counter += 1
        
        # 更新显示
        self._update_current_display()
        
        # 自动滚动到底部
        if self.scroll_offset <= 5:
            self.scroll_to_bottom()
        
        return item
    def add_clickable_parts(self, parts: List[Dict]) -> List[ConsoleContent]:
        """
        添加多个可点击部分到历史记录
        
        Args:
            parts: 部分列表，每个元素是包含以下键的字典：
                - 'text': 文本内容
                - 'color': 文本颜色（可选）
                - 'click_value': 点击时输入的文本（可选）
                
        Returns:
            添加的内容项列表
        """
        added_items = []
        combined_text = ""
        
        for part in parts:
            text = part.get('text', '')
            color = part.get('color', (255, 255, 255))
            click_value = part.get('click_value')
            
            combined_text += text
            
            # 创建内容项
            metadata = {'is_part': True, 'part_index': len(added_items)}
            
            if click_value is not None:
                metadata.update({
                    'clickable': True,
                    'click_value': click_value,
                    'region_id': self.clickable_region_counter
                })
                
                # 记录点击区域
                self.clickable_regions.append({
                    'id': self.clickable_region_counter,
                    'text': text,
                    'click_value': click_value,
                    'type': 'text'
                })
                
                self.clickable_region_counter += 1
            
            item = ConsoleContent(
                ContentType.TEXT, 
                text, 
                color=color,
                height=self.line_height,
                metadata=metadata
            )
            
            self.history.append(item)
            added_items.append(item)
        
        # 写入日志
        self._write_to_log(combined_text)
        
        # 更新显示
        self._update_current_display()
        
        # 自动滚动到底部
        if self.scroll_offset <= 5:
            self.scroll_to_bottom()
        
        return added_items
    def add_clickable_text(self, text: str, color: Tuple[int, int, int] = (255, 255, 255), 
                          click_value: str = None) -> List[ConsoleContent]:
        """
        添加可点击文本到历史记录
        
        Args:
            text: 文本内容
            color: 文本颜色
            click_value: 点击时输入的文本
            
        Returns:
            添加的内容项列表
        """
        added_items = self.add_text(text, color)
        
        # 将点击信息添加到最后一个内容项的元数据中
        if click_value is not None and added_items:
            for item in added_items:
                if item.data:  # 只对有实际内容的项添加点击
                    item.metadata['clickable'] = True
                    item.metadata['click_value'] = click_value
                    item.metadata['region_id'] = self.clickable_region_counter
                    
                    # 记录点击区域
                    self.clickable_regions.append({
                        'id': self.clickable_region_counter,
                        'content_item': item,
                        'click_value': click_value,
                        'text': text,
                        'type': 'text'
                    })
                    
                    self.clickable_region_counter += 1
        
        return added_items
    
    def add_clickable_image(self, surface: pygame.Surface, identifier: str = None,
                           click_value: str = None) -> Optional[ConsoleContent]:
        """
        添加可点击图片到历史记录
        
        Args:
            surface: 图片Surface
            identifier: 图片标识符
            click_value: 点击时输入的文本
            
        Returns:
            添加的内容项或None
        """
        item = self.add_image_surface(surface, identifier)
        
        if item is not None and click_value is not None:
            item.metadata['clickable'] = True
            item.metadata['click_value'] = click_value
            item.metadata['region_id'] = self.clickable_region_counter
            
            # 记录点击区域
            self.clickable_regions.append({
                'id': self.clickable_region_counter,
                'content_item': item,
                'click_value': click_value,
                'text': f"[图片] {identifier}",
                'type': 'image'
            })
            
            self.clickable_region_counter += 1
        
        return item
    
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
        for item in self.history:
            if 'clickable' in item.metadata:
                item.metadata['clickable'] = False
                item.metadata.pop('click_value', None)
                item.metadata.pop('region_id', None)
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
    
    def add_image_surface(self, surface: pygame.Surface, identifier: str = None) -> Optional[ConsoleContent]:
        """
        添加图片Surface到历史记录
        
        Args:
            surface: PyGame Surface对象
            identifier: 可选的标识符
            
        Returns:
            添加的内容项或None
        """
        try:
            if identifier is None:
                identifier = f"image_{len(self.history)}_{time.time()}"
            
            # 缓存图片
            self.image_cache[identifier] = surface
            
            # 计算图片高度
            img_height = surface.get_height() + 10  # 图片高度 + 边距
            
            # 创建内容项
            item = ConsoleContent(
                ContentType.IMAGE, 
                identifier, 
                height=img_height,
                metadata={
                    "surface": surface, 
                    "width": surface.get_width(), 
                    "height": surface.get_height()
                }
            )
            
            self.history.append(item)
            self._write_to_log(f"[图片: {identifier}]")
            self._update_current_display()
            
            # 自动滚动到底部（如果已经在底部附近）
            if self.scroll_offset <= 5:
                self.scroll_to_bottom()
                
            return item
        except Exception as e:
            error_msg = f"添加图片失败: {e}"
            self.add_text(error_msg, (255, 100, 100))
            return None
    
    def add_image(self, image_path: str, max_height: int = 200) -> Optional[ConsoleContent]:
        """
        添加图片到历史记录
        
        Args:
            image_path: 图片路径
            max_height: 图片最大高度
            
        Returns:
            添加的内容项或None
        """
        try:
            if os.path.exists(image_path):
                # 加载图片
                image = pygame.image.load(image_path).convert_alpha()
                
                # 调整大小
                img_width, img_height = image.get_size()
                if img_height > max_height:
                    scale_factor = max_height / img_height
                    new_width = int(img_width * scale_factor)
                    new_height = max_height
                    image = pygame.transform.smoothscale(image, (new_width, new_height))
                
                # 缓存图片
                self.image_cache[image_path] = image
                
                # 创建内容项
                item = ConsoleContent(
                    ContentType.IMAGE, 
                    image_path, 
                    height=new_height + 10,  # 图片高度 + 边距
                    metadata={"surface": image, "width": new_width, "height": new_height}
                )
                
                self.history.append(item)
                self._write_to_log(f"[图片: {os.path.basename(image_path)}]")
                self._update_current_display()
                
                # 自动滚动到底部（如果已经在底部附近）
                if self.scroll_offset <= 5:
                    self.scroll_to_bottom()
                    
                return item
            else:
                error_msg = f"图片文件不存在: {image_path}"
                self.add_text(error_msg, (255, 100, 100))
                return None
        except Exception as e:
            error_msg = f"加载图片失败: {e}"
            self.add_text(error_msg, (255, 100, 100))
            return None
    
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
        # 计算最大可显示的项目数
        available_height = self.content_area_height
        current_height = 0
        display_items = []
        
        # 从后往前遍历历史记录，直到填满显示区域
        for i in range(len(self.history) - 1 - self.scroll_offset, -1, -1):
            item = self.history[i]
            if current_height + item.height <= available_height:
                display_items.insert(0, item)
                current_height += item.height
            else:
                break
        
        self.current_display = display_items
        
        # 更新滚动条可见性
        total_height = sum(item.height for item in self.history)
        self.scrollbar_visible = total_height > self.content_area_height
    
    def scroll_up(self, amount: int = 1):
        """向上滚动"""
        # 计算最大滚动偏移
        max_scroll = 0
        current_height = 0
        for i in range(len(self.history) - 1, -1, -1):
            current_height += self.history[i].height
            if current_height > self.content_area_height:
                max_scroll = len(self.history) - i
                break
        
        self.scroll_offset = min(max_scroll, self.scroll_offset + amount)
        self._update_current_display()
    
    def scroll_down(self, amount: int = 1):
        """向下滚动"""
        self.scroll_offset = max(0, self.scroll_offset - amount)
        self._update_current_display()
    
    def scroll_to_bottom(self):
        """滚动到底部"""
        self.scroll_offset = 0
        self._update_current_display()
    
    def scroll_to_top(self):
        """滚动到顶部"""
        # 计算最大滚动偏移
        max_scroll = 0
        current_height = 0
        for i in range(len(self.history) - 1, -1, -1):
            current_height += self.history[i].height
            if current_height > self.content_area_height:
                max_scroll = len(self.history) - i
                break
        
        self.scroll_offset = max_scroll
        self._update_current_display()
    
    def clear_history(self):
        """清空历史记录"""
        self.history = []
        self.current_display = []
        self.scroll_offset = 0
        self.image_cache = {}
        
        # 在日志中记录清空操作
        self._write_to_log("[系统] 历史记录已清空")
    
    def get_history_items(self) -> List[ConsoleContent]:
        """获取历史记录中的所有项目"""
        return self.history
    
    def get_display_area_info(self) -> Dict:
        """获取显示区域信息"""
        return {
            'visible_items': len(self.current_display),
            'scroll_offset': self.scroll_offset,
            'total_items': len(self.history),
            'content_area_height': self.content_area_height,
            'line_height': self.line_height,
            'at_bottom': self.scroll_offset == 0,
            'at_top': False  # 需要在后续计算
        }
    
    def draw(self, screen: pygame.Surface):
        """绘制内容到屏幕"""
        current_y = 10
        
        # 绘制可见内容
        for item in self.current_display:
            if current_y + item.height > self.content_area_height + 10:
                break
                
            if item.type == ContentType.TEXT:
                current_x = 10
                
                # 如果有行内片段，逐个绘制
                if item.fragments:
                    for fragment in item.fragments:
                        # 计算片段宽度
                        fragment.calculate_width(self.font)
                        
                        # 检查是否需要换行（当前行剩余宽度不够）
                        available_width = self.screen_width - current_x - 20
                        if fragment.width > available_width and current_x > 10:
                            current_x = 10
                            current_y += item.height
                        
                        # 绘制文本
                        text_surface = self.font.render(fragment.text, True, fragment.color)
                        screen.blit(text_surface, (current_x, current_y))
                        
                        current_x += fragment.width
                    
                    # 一行绘制完毕，换行
                    current_y += item.height
                else:
                    # 普通文本
                    text_surface = self.font.render(item.data, True, item.color)
                    screen.blit(text_surface, (10, current_y))
                    current_y += item.height
                    
            elif item.type == ContentType.IMAGE:
                # 绘制图片
                if item.data in self.image_cache:
                    image = self.image_cache[item.data]
                    img_x = 10  # 图片从左侧开始
                    screen.blit(image, (img_x, current_y))
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
    
    def get_history_count(self) -> int:
        """获取历史记录数量"""
        return len(self.history)
    
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