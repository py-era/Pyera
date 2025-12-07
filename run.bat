@echo off
REM 自动激活虚拟环境并运行main.py

REM 设置当前目录
cd /d "%~dp0"

REM 查找虚拟环境
set VENV_PATH=
if exist venv\Scripts\activate.bat (
    set VENV_PATH=venv
) else if exist .venv\Scripts\activate.bat (
    set VENV_PATH=.venv
) else if exist env\Scripts\activate.bat (
    set VENV_PATH=env
)

REM 激活虚拟环境
if defined VENV_PATH (
    echo 激活虚拟环境: %VENV_PATH%
    call "%VENV_PATH%\Scripts\activate.bat"
    if errorlevel 1 (
        echo 警告: 虚拟环境激活失败
    )
) else (
    echo 未找到虚拟环境，使用系统Python
)

REM 检查main.py是否存在
if not exist "main.py" (
    echo 错误: 找不到 main.py
    pause
    exit /b 1
)

REM 运行main.py
echo 开始运行 main.py...
echo ----------------------------------------
python main.py

REM 保存退出码
set EXIT_CODE=%errorlevel%

REM 如果激活了虚拟环境，则停用
if defined VENV_PATH (
    deactivate
)

exit /b %EXIT_CODE%