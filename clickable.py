# 这个东西是我用来强化PRINT用的，他可以让PRINT变得？！强强！？
class ClickableString:
    """可点击字符串类，支持链式操作"""
    
    def __init__(self, text="", color=None, click_value=None):
        self.text = str(text)
        self.color = color or (255, 255, 255)
        self.click_value = click_value
        self._parts = []  # 存储所有部分
        self._add_part(text, color, click_value)
    
    def _add_part(self, text, color=None, click_value=None):
        """添加一个部分"""
        self._parts.append({
            'text': str(text),
            'color': color or self.color,
            'click_value': click_value
        })
    
    def __add__(self, other):
        """重载加法运算符，支持字符串连接"""
        result = ClickableString("", self.color)
        
        # 复制当前所有部分
        result._parts = self._parts.copy()
        
        # 添加新部分
        if isinstance(other, ClickableString):
            # 添加ClickableString的所有部分
            result._parts.extend(other._parts)
        elif isinstance(other, str):
            # 添加普通字符串部分
            result._parts.append({
                'text': other,
                'color': self.color,
                'click_value': None
            })
        else:
            # 尝试转换为字符串
            result._parts.append({
                'text': str(other),
                'color': self.color,
                'click_value': None
            })
        
        return result
    
    def __radd__(self, other):
        """右加运算符"""
        result = ClickableString("", self.color)
        
        if isinstance(other, str):
            result._parts.append({
                'text': other,
                'color': self.color,
                'click_value': None
            })
        else:
            result._parts.append({
                'text': str(other),
                'color': self.color,
                'click_value': None
            })
        
        # 添加当前所有部分
        result._parts.extend(self._parts)
        return result
    
    def click(self, value):
        """设置点击值（只影响最后一个部分）"""
        if self._parts:
            self._parts[-1]['click_value'] = value
        return self
    
    def set_color(self, color):
        """设置颜色（只影响最后一个部分）"""
        if self._parts:
            self._parts[-1]['color'] = color
        return self
    
    def get_parts(self):
        """获取所有部分"""
        return self._parts
    
    def __str__(self):
        """转换为字符串（用于显示）"""
        return ''.join(part['text'] for part in self._parts)
    
    def __len__(self):
        """获取总长度"""
        return len(str(self))