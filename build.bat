@echo off
echo ==========================================
echo Excel合并工具 - 打包脚本
echo ==========================================

echo 正在检查Python环境...
python --version
if errorlevel 1 (
    echo 错误: 未找到Python环境
    pause
    exit /b 1
)

echo 正在检查PyInstaller...
pip show pyinstaller
if errorlevel 1 (
    echo 正在安装PyInstaller...
    pip install pyinstaller
    if errorlevel 1 (
        echo 错误: PyInstaller安装失败
        pause
        exit /b 1
    )
)

echo 正在清理旧的构建文件...
if exist "build" rmdir /s /q "build"
if exist "dist" rmdir /s /q "dist"

echo 正在打包程序...
pyinstaller build_exe.spec

if errorlevel 1 (
    echo 错误: 打包失败
    pause
    exit /b 1
)

echo 打包完成！
echo 可执行文件位置: dist\Excel合并工具.exe
echo 按任意键退出...
pause

