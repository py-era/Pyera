@echo off
chcp 65001 >nul
setlocal

:: =================配置区域=================
:: 虚拟环境文件夹名称
set VENV_DIR=venv
:: 依赖文件名称
set REQ_FILE=requirements.txt
:: =========================================

echo [INFO] 正在检查 Python 环境...
python --version >nul 2>&1
if %errorlevel% neq 0 (
    echo [ERROR] 未检测到 Python，请确保已安装 Python 并将其添加到系统环境变量 PATH 中。
    pause
    exit /b 1
)

:: 1. 检查虚拟环境是否存在
if exist %VENV_DIR% (
    echo [INFO] 检测到虚拟环境 "%VENV_DIR%" 已存在，跳过创建步骤。
) else (
    echo [INFO] 正在创建虚拟环境 "%VENV_DIR%"...
    python -m venv %VENV_DIR%
    if %errorlevel% neq 0 (
        echo [ERROR] 虚拟环境创建失败！
        pause
        exit /b 1
    )
    echo [SUCCESS] 虚拟环境创建成功。
)

:: 2. 激活虚拟环境
echo [INFO] 正在激活虚拟环境...
call %VENV_DIR%\Scripts\activate.bat

:: 3. 检查 pip 更新
echo [INFO] 正在检查并更新 pip...
python -m pip install --upgrade pip

:: 4. 安装依赖
if exist %REQ_FILE% (
    echo [INFO] 正在安装依赖库 (来自 %REQ_FILE%)...
    pip install -r %REQ_FILE%
    if %errorlevel% neq 0 (
        echo [ERROR] 依赖安装过程中出错，请检查错误信息。
        pause
        exit /b 1
    )
    echo [SUCCESS] 所有依赖已安装完毕。
) else (
    echo [WARNING] 未找到 "%REQ_FILE%" 文件，跳过依赖安装。
)
python .\main.py


pause