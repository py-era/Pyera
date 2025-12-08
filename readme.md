
# ---

**🐱 Pera Framework 开发指南 (Demo版)**
**注意：** 本项目目前正在施工中！

## **📖 简介**

大家好，这里是 **凌冬**。众所周知，使用原版 ERB 开发 Era 游戏时，我们经常会遇到各种问题（看代码像天书、变量裸奔等）。为了让想开发 Era 游戏但在 ERB 面前却步的朋友们有更多选择，我开发了 **Pera** 框架。

### **什么是 Pera？**

Pera 是一个基于 **Python** 和 **Pygame** 构建的前端框架，旨在让 Era 系游戏的开发变得更加方便。

### **为什么选择 Pera？**

* **CSV 搬运友好**：虽然不能直接转码 ERB，但可以直接搬迁 CSV 文件。  
* **自动导入**：框架初始化时会自动导入 ./csv 下的所有 .csv 文件，并自动分类为 **角色数据** 和 **全局变量**。

## ---

**🛠️ 快速开始**

### **环境需求**

* 已配置虚拟环境（你可以直接使用）。  
* 如果出现莫名其妙的问题
* 使用 **Python 3.x**。  
* 必须安装 **Pygame** 库。 

### **启动方式**

1. 点击 run.bat。  
2. 或者在 VSCode 终端输入：  
   Bash  
   python main.py



## ---

**💻 核心功能指南**

### **1\. 编写你的第一个事件**

在 Pera 中，事件函数通常以 event\_ 开头。

```Python

# 开始你的第一个 Pera 事件！  
def event_helloworld(things):  
    # 从 things 中调用控制台并打印  
    # 获取 0 号角色的 "名前"  
    name = things.console.init.charaters_key["0"].get("名前")  
    things.console.PRINT("你好Pera！", f"{name}")
```
* 该事件被调用时，终端会打印出：你好！Pera 你 

### **2\. 数据结构与调用**

#### **🧑 角色数据 (charaters\_key)**

这是一个存储全体角色键值对和数据的字典。

* **结构示例**：  
  ```json  
  {  
      "0": {  
          "名前": "你",  
          ...  
      },  
      ...  
  }
  ```
* **数据来源**：./csv/characters/0/0.csv 

* **ID 列表**：chara\_ids (例如 \["0", "1", ...\]) 

#### **🌐 全局变量 (global\_key)**

用于存储游戏内的物品或其他全局数据。

* **调用示例**：  
  ```Python  
  def event_helloworld(things):  
      # 获取 Item 中 ID 为 1 的物品  
      item_name = things.console.init.global_key["Item"].get("1")  
      things.console.PRINT(f"{item_name} 会输出放在 ./csv/global/Item.csv 中物品id为1的物品")
  ```
* **结构示例**：  
  ```Python  
  #字典结构展示
  {  
      "Item": {  
          "0": { ... },  
          "1": { ... },  
          ...  
      },  
      ...  
  }
  ```


* **ID 列表**：globalid 

## ---

**🎮 事件系统详解**

### **事件加载机制**

* **自动加载**：事件加载器**只会**加载以 event\_ 开头的函数。  
* **辅助函数**：不以 event\_ 开头的函数（如 def helloworld(things):）不会被加载到事件池中，适合作为内部辅助函数。 

### **事件元数据 (Metadata)**

你需要在事件函数末尾定义元数据，以便框架识别和调用(其实也可以不写)：

```Python

event_helloworld.event_id = "helloworld"      # 加载后的唯一标识  
event_helloworld.event_name = "你好！Pera"    # 事件显示名称  
event_helloworld.event_trigger = "8"          # 触发条件等
```
### **触发与通讯**

* 在主框架中触发：  
  self.event\_manager.trigger\_event('helloworld', self)  
* 在事件内部触发其他事件（事件间通讯）：  
  this.event\_manager.trigger\_event('text', this)这里的 this 指代当前事件导入的上下文对象。 

## ---

**🎨 图像与立绘系统 (Img)**

### **目录结构**

图片通常存放在 ./img 目录下，按角色 ID 分类：

```Plaintext

./img/  
 ├── 角色id/  
 │    ├── xx绘/  
 │    │    ├── 角色id.csv   \<-- 建立立绘与源文件的关系  
 │    │    ├── xxx.webp  
 │    │    ├── xxx.jpg  
 │    │    └── ...
```

### **调用立绘 (PRINTIMG)**

接口提供了灵活的调用方式：

1. **使用全名调用**：  
   ```Python  
   PRINTIMG("0_玩家立绘_顔絵_服_通常_0")  
   # 调用 ./0/玩家立绘/0.csv 中第一列值为 "顔絵_服_通常_0" 对应的图片
   ```
2. **指定参数调用**：  
   ```Python  
   PRINTIMG("顔絵_服_通常_0", chara_id="0", draw_type="玩家立绘")
   ```
### **裁剪与尺寸**

* **默认行为**：自动读取 CSV 中的裁剪值和大小。若未指定，默认不裁剪，大小设为 (270, 270)。  
* **手动指定**：  
  * clip\_pos：传入数组指定裁剪区域。  
  * size：传入数组指定图片显示大小。 

## ---

**🎵 音乐与地图**

### **🗺️ 地图系统**

* **配置文件**：./json/map.json。  
* **更新地图**：如果更改了 json 文件，需要调用 map 事件来更新位置。 

### **🎶 音乐盒 (Musicbox)**

* **用法示例**：参考 ./events/music\_control.py。  
* **导入音乐**：  
  1. 将音频文件放入 Musicbox 文件夹。  
  2. 在全局变量 musicbox.csv 中添加键值对：音乐游戏中显示的名称, 音乐路径。 

## ---

**🖥️ 文本输出与字体**

### **字体控制**

* 使用 `set_font` 接口更改字体。  
* **注意**：更改只会影响后续的输出。  
* 参考代码：./events/fontreset.py 

### **PRINT 输出详解**

Pera 提供了普通输出和高级交互输出（cs/ColorString）。

1. **普通输出**：  
   ```python
   self.console.PRINT("helloworld\!")  
   self.console.PRINT("helloworld\!", colors=(0,0,255)) \# 蓝色文本  
   self.console.PRINT("helloworld\!", click="你好！Pera") \# 点击后模拟输入  
   self.console.PRINT("hello", "world") \# 多参数
   ```

2. **高级输出 (使用 cs)**：在事件中使用时，cs 前需要加 this 或 thethings 引用。  
   Python  
   \# 链式调用：设置颜色 \-\> 设置点击事件  ,会输出在同一行哦
   self.console.PRINT(  
       cs("helloworld").set\_color((0,0,255)).click("你好！Pera"),  
       "          ",  
       cs("helloworld").set\_color((0,0,255)).click("你好！Pera")  
   )


---
