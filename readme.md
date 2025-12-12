
# 🐱 Pera Framework 开发指南 (Demo版)

**注意：** 本项目目前正在施工中！

## 📖 简介

大家好，这里是 **凌冬**。众所周知，使用原版 ERB 开发 Era 游戏时，我们经常会遇到各种问题（看代码像天书、变量裸奔等）。为了让想开发 Era 游戏但在 ERB 面前却步的朋友们有更多选择，我开发了 **Pera** 框架。

### 什么是 Pera？

Pera 是一个基于 **Python** 和 **Pygame** 构建的前端框架，旨在让 Era 系游戏的开发变得更加方便。

### 为什么选择 Pera？

* **CSV 搬运友好**：虽然不能直接转码 ERB，但可以直接搬迁 CSV 文件。  
* **自动导入**：框架初始化时会自动导入 ./csv 下的所有 .csv 文件，并自动分类为 **角色数据** 和 **全局变量**。
* **python语法简单**，入门轻松

## 🛠️ 快速开始

### 环境需求

* 使用pip安装requirements中的库

  * ```Shell
    pip install -r ./requirements.txt
    ```

* 使用 **Python 3.13.x**。  

### 启动方式

```shell
python main.py
```

---

## 小白请看这里！！

* 什么是self？什么是this？什么是thething啊？为什么事件之间的PRINT前面有时候都不一样啊?console又是什么啊？
  * 什么是**self**，self用于框架的默认主循环，您可以吧他看作一个指名，也就是我自己，也就是默认主循环他自己的意思
  * 为什么有时候是this？有时候是thethings？因为您在写事件的时候，必须要给事件提供一个默认值

      ```Python
    def event_text(默认参数):
      默认参数.console.PRINT()
      ```

  * **这个默认值会在事件加载器处理时自动被代入为主循环中的self，所以不用担心别的！大胆的去用您喜欢的名字吧！**
  * 什么是**console**,console是主循环调用框架的一个功能啦~也就是在默认主循环的开始时，我们**初始化**（初始化是指创建了console这个承载框架各种功能的一个盒子）了console作为框架功能的一个调用，也就是说我们可以通过console来和我们的框架进行对话！
  * 那么根据对**console**的理解，我们可以知道任何一个接口（也叫api，大家可以理解成框架给你的一个个的按钮）的调用都需要从主循环的**console**盒子里面去拿呀？所以，这个时候我们再来看前面看不懂的语句
    * **self.console.PRINT()**,self是指是在哪里调用的呢？是我们的默认主循环是不是呀？console的意思呢？是不是从**console**这个盒子里面去拿接口呀？所以这条命令的意思就是，在主循环中，才console里去拿PRINT()这个接口
    * **this.console.PRINT()**,this是不是指的这个事件的默认参数为this呀？那么我们已经知道在事件加载器中无论默认值是什么最后都会被映射成主循环中的self，所以其实这句话的意思就是self.console.PRINT()
  * **几乎所有的接口逻辑都可以这么理解哦！**
  * 当然，INPUT接口是和例外哦，**注意啦！**（敲黑板）
    * INPUT接口的调用一般是给他赋值和等待输入，我们分类讨论哦
      * 首先，是赋值的情况，我们可以把需要赋值的INPUT这样理解，主循环拉取的INPUT是他的事情，和我们任何一个事件中的INPUT都没有关系，每一个事件中只能用他自己的INPUT啦！就好像...**专一的对象**一样！每个事件都要有一个自己的对象吧！所以说，要检测输入的事件，就请单独为其赋值吧！

        ```Python
        def event_text(默认值):
          input=默认值.console.INPUT()#在这里会进行一次输入读取，所以如果有什么要说的PRINT要提前写在输入赋值的前面
          if input=='114514':
            默认值.console.PRINT("好臭！")
        ```

      * 接下来是不赋值的情况，默认调用一次INPUT就会等待用户输入，如果什么都不做也是可以的哦\

        ```Python
        def event_text(默认值):
          默认值.console.PRINT("摁回车继续")
          默认值.console.INPUT()
        ```

    * 所以，因为**INPUT很专一**，所以如果进入到别的事件的话，您的上一层事件（所谓上一层事件就是你从哪里触发这个事件的哪里就是这个事件的上一层事件）的INPUT赋值无论您输入什么是都不会发生改变的哦！
      (ps:如果您真的要更改上一层事件可以通过默认值.上一层事件赋值的输入='xxx'来强行赋值哦)

## API快速查找

* **PRINT接口**
  * **关于参数**
    * **colors**,您需要输入一个RGB数组，输出将变成数组的颜色
    * **click**,您需要指定一个字符串，点击时会模拟用户输入该字符串
    * **多参数**您可以通过导入多个字符串来实现多参数调用
  * 关于快捷函数cs()
    * **.set_color()**同colors，但是因为其本身是一个函数，所以需要set_color((0,0,0))这样子
    * **.click()**和PRINT的click参数一样
  * **普通输出**：  

     ```python
     self.console.PRINT("helloworld!")  
     self.console.PRINT("helloworld!", colors=(0,0,255)) # 蓝色文本  
     self.console.PRINT("helloworld!", click="你好！Pera") # 点击后模拟输入  
     self.console.PRINT("hello", "world") # 多参数
     ```

  * **高级输出 (使用 cs)**：在事件中使用时，cs 前需要加 this 或 thethings 引用。  

       ```Python  
       # 链式调用：设置颜色 -> 设置点击事件  ,会输出在同一行哦
       self.console.PRINT(  
           cs("helloworld").set_color((0,0,255)).click("你好！Pera"),  
           "          ",  
           cs("helloworld").set_color((0,0,255)).click("你好！Pera")  
       )
       ```

* **INPUT接口**
  * **接口调用**:调用接口可以直接在代码中使用console.INPUT()进行调用，这个调用会使程序进行一次用户输入等待
  * **赋值**:一般我们通过对INPUT接口赋值来获取用户输入，如input=thethings.console.INPUT()
* **PRINTIMG接口**
  * **关于参数**
    * 必须要有的参数是图片的索引，也就是角色id_xx绘_对应csv下第一列的拼接
    * **clip_pos**，输入一个数组传递xy，来裁剪图片，默认是不裁剪,(0,0)
    * **size**，输入一个数组传递xy，来指定一个图片的大小，默认是(270,270)
    * **click**，同PRINT的click
    * **chara_id**，按照指定角色id查询，使用后必须参数可以不加角色id
    * **draw_type**，按照xx绘进行查询，使用后必须参数可以不加xx绘
    * **img_list**，导入一个列表，会将列表中的索引从前往后依次打印在一个地方，用于添加气泡等，如果引用img_list，那么第一个参数导入可以为空
      * 在img_list中你可以通过传入一个列表中包含多个字典来实现为每一个图片设置他的专属属性！
      * **现在Pera的PRINTIMG会在图片当前行创建一个高度为最高图片高度宽度为屏幕宽度的透明底，尽情创作吧~**
  * **接口调用**
    * **使用全名调用**：  

         ```Python  
         PRINTIMG("0_玩家立绘_顔絵_服_通常_0")  
         # 调用 ./0/玩家立绘/0.csv 中第一列值为 "顔絵_服_通常_0" 对应的图片
         ```

    * **指定参数调用**：  

         ```Python  
         PRINTIMG("顔絵_服_通常_0", chara_id="0", draw_type="玩家立绘")
         ```

    * **列表调用**:

        ```Python
            img_list = ["別顔_服_笑顔_0","別顔_汗_0",]
            self.console.PRINTIMG("",img_list=img_list,chara_id='0',draw_type='玩家立绘')
        ```

    * **列表高级调用**
      * **高级列表调用追加属性**
        * **"img"**,图片的id，和前面的方法是通用的
        * **"draw_type"**,同上面的，什么立绘，可以写在名称里面
        * **"chara_id"**,角色主键，可以写在名称里面
        * **"offset"**,该图片的x，y偏移值，默认输出在整个底板的左上角，输入元组，第一个值是x轴，越大越往右，第二个是y轴，越大越往下
        * **逻辑解释**,如果没有任何配置只配置了img属性的话，会按照一下流程去找图片大小和裁剪位置PRINTIMG属性->csv中给的属性->默认属性
  
        ```Python
            img_list = [
                {"img": "別顔_服_笑顔_0", "draw_type": "玩家立绘",'chara_id':'0'},
                {"img": "別顔_汗_0", "draw_type": "玩家立绘",'chara_id':'0'},
                {'img': "1_EN绘_別顔_服_通常_1","offset":(180,0)}
            ]
            self.console.PRINTIMG("",img_list=img_list)#会在同一行中输出
        ```

      * 也可以不加字典哦！
* **event_manager接口**
  * **理解事件管理器**事件管理器就像一个盒子，他首先会把你写的event放进这个盒子，然后你通过这个盒子去拿你写的event，而在盒子中你的事件命名是按着你的文件名来的
  * **使用**
    * 盒子本身是可以搬到哪里都是可以的，不过为了避免莫名其妙的逻辑错误，所以我建议您在还不熟练的时候只调用main中提供的盒子，可以使用event\_manager.trigger\_event('text', this)调用名称为text的事件
* **关于角色数据**
  * **charaters_key**
    * 这里面你可以通过**self.console.inti.charaters_key[角色id]**去提取这个角色的所有数据哦~
      * 目前已经添加的数据
        * 角色csv文件下的所有属性
        * **draw_type**点击start后添加，若不进行立绘检查则默认初始绘，您可以通过修改默认事件**对象选择.py**中的12行把初始绘替换成其他来更改角色的默认立绘类型
        * **选择对象**点击start后追加，返回您的角色当前选择对象的id
* **关于图片数据**
  * **image_data**
    * 里面包含了图片全名**角色id_立绘类型_源csv文件下的第一列**和该图片数据的键值对
    * 目前已经添加的键值对
      * 'filename'：源图片地址
      * 'base_dir'：图片所在目录
      * 'x'：裁剪区域x
      * 'y'：裁剪区域y
      * 'width'：宽度
      * 'height'：高度
      * 'chara_id'：所属角色id
      * 'draw_type'：所属立绘类型
      * 'original_name'：源csv第一列的数据
  * **chara_images**
    * 对image_data可用的快速查询所用的字典
    * 结构
      * 角色id子字典-立绘类型子字典-立绘下所有图片全名列表

## 💻 核心功能指南

### 1. 编写你的第一个事件

在 Pera 中，事件函数通常以 `event_` 开头。

```Python
# 开始你的第一个 Pera 事件！  
def event_helloworld(things):  
    # 从 things 中调用控制台并打印  
    # 获取 0 号角色的 "名前"  
    name = things.console.init.charaters_key["0"].get("名前")  
    things.console.PRINT("你好Pera！", f"{name}")
```

* 该事件被调用时，终端会打印出：你好！Pera 你

### 2. 数据结构与调用

#### 无论如何都要了解的知识

* **id即主键**:Pera为您提供了方便快捷的**主键式**数据调用，您可以通过角色id为主键去调用到和这个角色相关的所有数据
* **永远不会更改源文件**:在Pera中，会优先将所有csv数据加入内存，所有更改在内存中进行，更改字典内容**并不会**更改源文件数据
* **动态读取数据**:为了不破坏原有逻辑，如果您真的需要一个可以更改的数据，请将其作为json文件加入到框架根目录的json文件下并自己写读写逻辑,可以参考map.py
  
#### 🧑 角色数据 (`charaters_key`)

这是一个存储全体角色键值对和数据的字典。

* **结构示例**：  
  
  ```json  
  {  
      "0": {  
          "名前": "你",  
          // ...  
      },  
      // ...  
  }
  ```

* **数据来源**：./csv/characters/0/0.csv

* **ID 列表**：`chara_ids` (例如 `["0", "1", ...]`)

#### 🌐 全局变量 (`global_key`)

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

* **ID 列表**： `globalid`

---

## 🎮 事件系统详解

### 首先是无论是口上开发者还是游戏开发者都必须了解的事件逻辑

* **事件与主循环之间对于主框架的接口调用是独立的** :就是说你在事件中**不能**直接使用主循环中的输入去读取，比如你的事件触发是1，那么在事件触发的那一刻主循环的input值就被固定为1了，所以如果你想要在事件中也调用用户输入，就需要用一个单独的变量去调用框架的INPUT()接口,如：
  
  ```Python
  input=thethings.console.INPUT()
  if input=="2":
    thethings.console.PRINT("请输入文本")
  ```

  这是一个常规调用

  ```Python
    if thethings.input()=="2":
      thethings.console.PRINT("请输入文本")
  ```

  这是一个错误调用并且是一个**非常危险**的行为，因为这时候无论用户输入什么都无法触发输出"请输入文本"
* **关于“按任意键继续”这个功能的实现**无论是在什么地方，调用框架的**INPUT接口**就会进行一次等待用户输入，例如
  
  ```Python
    thethings.console.PRINT("按任意键继续....")
    thethings.console.INPUT()
  ```

  这个事件会等待用户输入任意值之后结束
* **主事件OR事件？**
  * 在Pera中，可以把**主事件**当作一个**单独的main**，一般来说**主事件**的作用是创建一个循环并包含其他的**多个事件**(参考start事件)，一般来说在Pera中开发游戏，一个**主事件**是游戏必不可缺的开始，主事件的定义是很广的，一般来说任何事件中包含了主循环和其他事件，就可以视为是一个主事件，而一个普通的事件一般是调取一次就弃用的，比如说一个治疗事件，他的功能是将角色的字典中你的精力设定为100就退出事件，一般这种事件被称为*普通事件*，我们可以把整个游戏流程看做为一个入口，场景，功能的搭积木，入口是一个主事件，场景一般也是主事件，功能则是事件
* **作为开发者我需要了解什么？**
  * 您要了解框架的基础接口调用**PRINT()**,**PRINTIMG()**,**INPUT()**,**PRINT_DIVIDER()**,**init 对象**,**chara_images字典**,**music_box**
  * 了解python的**基础语法**（循环，判断，列表and字典的数据调用，字符串操作，函数定义）
  * 了解**事件的调用**
  * **cs()**,快捷函数使用,可以高级输出(想要五颜六色？想要单独每个字点击有不同效果？)
  * **需要用户输入时，调用thethings.console.INPUT()并存储返回值。**
  * **多看看默认事件**
  * **框架结构**虽然您不需要了解框架是怎么工作的，但是作为一个用Pera的开发者，您需要了解框架是怎么工作的
  * **事件结构**您明确**事件结构**，确立**游戏事件链**，什么是主事件，哪个主事件下应该包含哪些事件，我在此强烈建议您在开发前用文档写好对应的事件链触发

### 事件加载机制

* **自动加载**：事件加载器**只会**加载以 event\_ 开头的函数。  
* **辅助函数**：不以 event\_ 开头的函数（如 def helloworld(things):）不会被加载到事件池中，适合作为内部辅助函数.

### 事件元数据 (Metadata)

你需要在事件函数末尾定义元数据，以便框架识别和调用(其实也可以不写)：

```Python
event_helloworld.event_id = "helloworld"      # 加载后的唯一标识  
event_helloworld.event_name = "你好！Pera"    # 事件显示名称  
event_helloworld.event_trigger = "8"          # 触发条件等
```

### 触发与通讯

* 在主循环中触发：  
  self.event\_manager.trigger\_event('helloworld', self)  
* 在事件内部触发其他事件（事件间通讯）：  
  this.event\_manager.trigger\_event('text', this)这里的 this 指代当前事件导入的上下文对象。

---

## 🎨 图像与立绘系统 (Img)

### 目录结构

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

### 图片数据存储

* **chara_images字典**
  * 首先这是一个嵌套字典，您可以通过`console.chara_images['0']['初始绘']`去调用角色id为0的角色初始绘中的所有图片数据
* **image_data**
  * 如果知道某一个图片的id，可以通过这个字典调用，console.image_data.get(“图片ID”),图片id会根据以下逻辑自动拼接：角色id_xx绘_那个文件夹下csv文件中的第一列

### 调用立绘 (PRINTIMG)

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

### 裁剪与尺寸

* **默认行为**：自动读取 CSV 中的裁剪值和大小。若未指定，默认不裁剪（即(0,0)），大小设为 (270, 270)。  
* **手动指定**：  
  * clip\_pos：传入数组指定裁剪区域。  
  * size：传入数组指定图片显示大小。

## 🎵音乐控制

### 🎶 音乐盒 (Musicbox)

* **用法示例**：参考 ./events/music\_control.py。  
* **导入音乐**：  
  1. 将音频文件放入 Musicbox 文件夹。  
  2. 在全局变量 musicbox.csv 中添加键值对：音乐游戏中显示的名称, 音乐路径。

## 🖥️ 文本输出与字体

### 字体控制

* 使用 `set_font` 接口更改字体。  
* **注意**：更改只会影响后续的输出。  
* 参考代码：./events/fontreset.py

### PRINT 输出详解

Pera 提供了普通输出和高级交互输出（cs/ColorString）。

1. **普通输出**：  

   ```python
   self.console.PRINT("helloworld!")  
   self.console.PRINT("helloworld!", colors=(0,0,255)) # 蓝色文本  
   self.console.PRINT("helloworld!", click="你好！Pera") # 点击后模拟输入  
   self.console.PRINT("hello", "world") # 多参数
   ```

2. **高级输出 (使用 cs)**：在事件中使用时，cs 前需要加 this 或 thethings 引用。  

   ```Python  
   # 链式调用：设置颜色 -> 设置点击事件  ,会输出在同一行哦
   self.console.PRINT(  
       cs("helloworld").set_color((0,0,255)).click("你好！Pera"),  
       "          ",  
       cs("helloworld").set_color((0,0,255)).click("你好！Pera")  
   )
   ```

## 关于INPUT

* **INPUT的接口调用是一个非常重要的内容，您必须要了解这些才能开始Pera的框架使用**

* **什么是INPUT调用？怎么调用？**
  * **INPUT调用**一般指的是input=thethins.console.INPUT()，也就是为一个变量赋值为用户输入，这会执行一次用户输入调用，并将其赋值给input，**注意！！！不要去调用main中的input，因为他在你进入事件的那一刻就已经和你这个事件没有关系了！**
  * **INPUT直接调用**一般指的是不为INPUT赋值而是直接调用INPUT接口，这时将会停留在当前界面并等待用户输入

## 开发指南

### 事件结构？游戏事件链到底是什么啊。。。

* 一般来说，您必须要有一个主事件去包括您需要开发的其他事件，除了测试，任何的其他事件都应当被放置在一个类似于start的主事件下，在主事件下再调用别的主事件或者事件，这就是游戏事件链

* **事件结构**:一般来说，您的**主事件**应当有一个**while循环**和一个**INPUT调用**，并包含**其他事件**，应当包含**事件的退出**，**事件处理**和处理**游戏退出**事件，具体内容可以参考**start.py**，**事件**的结构中一般要包含一个**INPUT调用**，和**事件功能**等

---
