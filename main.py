import pygame
import sys
import time
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
        
        # 文本缓冲区
        self.output_lines = []
        self.max_lines = (self.screen_height - 40) // self.line_height  # 底部留出输入空间
        
        # 输入相关
        self.input_text = ""
        self.cursor_visible = True
        self.cursor_timer = 0
        self.running = True
        self.init=self.init_all()
    def init_all(self):
        init = self.initall("./csv/")
        self.PRINT("少女祈祷中...")
        for i in init.charaters_key:
            self.PRINT(f"已加载角色：{init.charaters_key[i].get('名前')}")
        time.sleep(1)
        self.PRINT("角色全部载入~")
        for i in init.global_key:
            self.PRINT(f"已加载全局设置：{i}")
        time.sleep(1)
        self.PRINT("全部载入~")
        return init
    def PRINT(self, text=None,colors=(255,255,255)):
        """输出文本到控制台 - 无输入时输出空行"""
        # 如果没有传入文本或文本为空，输出空行
        color_tuple = colors if isinstance(colors, tuple) and len(colors) >= 3 else (255, 255, 255)
        if text is None or text == "":
            self.output_lines.append(("",color_tuple))
            # 限制缓冲区大小
            if len(self.output_lines) > self.max_lines:
                self.output_lines = self.output_lines[-self.max_lines:]
            # 刷新显示
            self._draw_display()
            pygame.display.flip()
            return
        
        # 处理制表符
        text = text.replace('\t', '    ')  # 将制表符转换为4个空格
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
            
            # 如果超出屏幕宽度
            if text_width > self.screen_width - 20:
                if current_line:
                    lines.append(current_line)
                current_line = char
            else:
                current_line = test_line
        
        # 添加最后一行
        if current_line:
            lines.append(current_line)
        
        # 将新行添加到输出缓冲区
        for line in lines:
            self.output_lines.append((line,color_tuple))
        
        # 限制缓冲区大小
        if len(self.output_lines) > self.max_lines:
            self.output_lines = self.output_lines[-self.max_lines:]
        
        # 刷新显示
        self._draw_display()
        pygame.display.flip()
    
    def INPUT(self):
        """获取用户输入"""
        self.input_text = ""
        waiting_for_input = True
        
        while waiting_for_input and self.running:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    self.quit()
                    return None
                
                elif event.type == pygame.KEYUP:
                    if event.key == pygame.K_RETURN:
                        user_input = self.input_text
                        self.input_text = ""
                        waiting_for_input = False
                        return user_input
                    
                    elif event.key == pygame.K_BACKSPACE:
                        self.input_text = self.input_text[:-1]
                    
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
    
    def _draw_display(self):
        """绘制整个界面"""
        # 清屏
        self.screen.fill((0, 0, 0))
        
        # 绘制输出文本
        for i, (line,color) in enumerate(self.output_lines):
            text_surface = self.font.render(line, True,color)
            y_pos = 10 + i * self.line_height
            self.screen.blit(text_surface, (10, y_pos))
        
        # 绘制输入文本和光标（始终在左下角）
        input_y = self.screen_height - 30
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
    def quit(self):
        """退出程序"""
        self.running = False
        pygame.quit()
        sys.exit()

# 使用示例
class thethings:
    #在这里输入你的事件
    def __init__(self):
        self.console=SimpleERAConsole()
        self.input=""
        self.charater_pwds={}
        self.main()
        #初始化角色位置
    def text(self):
        self.console.PRINT('[1]测试文本')
        if self.input=='1':
            self.console.PRINT("GREEN",(0,255,0))
            self.console.PRINT("BLUE",(0,0,255))
            self.console.PRINT("RED",(255,0,0))
    def getpwd(self,id='0'):
        self.console.PRINT('[0]查询位置')
        mypwd=self.charater_pwds[id]
        if self.input=='0':
            self.console.PRINT(f"{self.console.init.charaters_key[id].get('名前')}当前位置....")
            self.console.PRINT(f"[{self.console.init.global_key['map'][mypwd['大地图']]}]"+f"[{self.console.init.global_key['map'][mypwd['小地图']]}]")
    def map(self):
        #注意，如果您需要在口上中设定角色的移动，请直接修改map.json，map会自动更新角色当前位置
        import json
        with open('./json/map/map.json', 'r', encoding='utf-8') as f:
            map_data = json.load(f)
            #现在我们有一个map的字典了
        for i in self.console.init.chara_ids:
            self.charater_pwds[i]={
                '大地图':'10000',
                '小地图':'10000'
            }
        for big_map,small_maps in map_data.items():
            for small_map,charater_list in small_maps.items():
                for charater_id in charater_list:
                    if charater_id in self.charater_pwds:
                        self.charater_pwds[charater_id]={
                            '大地图':big_map,
                            '小地图':small_map
                        }
    def main(self):
        running = True
        while running:
        # 获取用户输入
            self.input = self.console.INPUT()
        # 处理用户输入
            if self.input.lower() == "quit":
                running = False
            elif self.input:
                #==============================================
                #===================在这里输入你的事件===========
                self.map()
                self.getpwd(id='1')
                self.text()
                self.console.PRINT("")#默认没有任何事件处理
        
        # 处理退出事件
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False
    
        pygame.quit()
        sys.exit()
if __name__ == "__main__":
    start=thethings()
    """     console = SimpleERAConsole()
    
    # 测试PRINT功能
    console.PRINT("\t\t\t\t\t\t\t\t欢迎来到Pera!")
    console.PRINT("\t\t\t\t\t\t\t\tpower by PYgame")
    console.PRINT("请输入您的命令:")
    
    # 主循环
    running = True
    while running:
        # 获取用户输入
        user_input = console.INPUT()
        if user_input =='350234':
            console.PRINT("真是一对苦命鸳鸯啊")
        # 处理用户输入
        if user_input.lower() == "quit":
            running = False
        elif user_input:
            console.PRINT(f"您输入了: {user_input}")
        
        # 处理退出事件
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
    
    pygame.quit()
    sys.exit() """