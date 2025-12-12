# main.py 修改部分
import pygame
import sys
import time
import json
import os
from dynamic_loader import DynamicLoader, ContentType,InlineFragment  # 导入动态加载器
from clickable import ClickableString
from ERAconsole import SimpleERAConsole
from Eventmanger import EventManager
#这是一个快捷调用的东西，为了让PRINT变得强强
def cs(text="", color=None, click=None):
    """创建ClickableString的快捷函数"""
    return ClickableString(text, color, click)
# 在 main.py 的 thethings 类中添加新功能
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
        self.console.PRINT("加载完成，回车以继续...")
        running = True
        while running:
            self.input = self.console.INPUT()
            gradient_text = (cs("红").set_color((255, 0, 0)) +cs("橙").set_color((255, 127, 0)) +cs("黄").set_color((255, 255, 0)) +cs("绿").set_color((0, 255, 0)) +cs("青").set_color((0, 255, 255)) +cs("蓝").set_color((0, 0, 255)) +cs("紫").set_color((127, 0, 255)))
            self.console.PRINT(gradient_text.click("gradient"))
            img_list = [
                {"img": "別顔_服_笑顔_0", "draw_type": "玩家立绘",'chara_id':'0'},
                {"img": "別顔_汗_0", "draw_type": "玩家立绘",'chara_id':'0'},
                {'img': "1_EN绘_別顔_服_通常_1","offset":(180,0)}
            ]
            self.console.PRINTIMG("",img_list=img_list)#在输出图片时请在需要输出的图片名前加上角色id_，你可以直接输出在csv中的图片名
            self.console.PRINT(cs("嗯？你来啦？欢迎来到Pera的世界！这里演示的是图片调用，很抱歉直接使用了eratw🐍版里的你小姐的立绘）").set_color((215, 200, 203)))
            self.console.PRINT(cs("[0]start").click("0"),"          ",cs("点击查看凌冬色图").click("no way!!!"),"          ",cs("点击更改字体").click("fontreset"),"        ",cs("[666]和你小姐对话").click("666"))
            if self.input and self.input.lower() == "quit":
                running = False
            elif self.input:
                #在这里添加事件
                if self.input=='0':
                    self.event_manager.trigger_event('start',self)
                if self.input=='debug':
                    self.event_manager.trigger_event('showme',self)
                if self.input=="666":
                    self.event_manager.trigger_event("isay",self)
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