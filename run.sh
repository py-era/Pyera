#!/bin/bash

# 定义虚拟环境文件夹名称
VENV_DIR="venv"

# 1. 检查虚拟环境是否存在，不存在则创建
if [ ! -d "$VENV_DIR" ]; then
    echo "正在创建虚拟环境..."
    python -m venv $VENV_DIR
fi

# 2. 激活虚拟环境
echo "激活虚拟环境..."
source $VENV_DIR/bin/activate

# 3. 安装/更新依赖
if [ -f "requirements.txt" ]; then
    echo "正在安装依赖..."
    pip install -r requirements.txt
else
    echo "警告：未找到 requirements.txt"
fi

# 4. 运行主程序
echo "启动 main.py..."
python main.py

# 5. 退出时取消激活 (可选)
deactivate