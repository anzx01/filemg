#!/bin/bash

echo "=========================================="
echo "Excel合并工具 - 打包脚本"
echo "=========================================="

echo "正在检查Python环境..."
python3 --version
if [ $? -ne 0 ]; then
    echo "错误: 未找到Python3环境"
    exit 1
fi

echo "正在检查PyInstaller..."
pip3 show pyinstaller > /dev/null 2>&1
if [ $? -ne 0 ]; then
    echo "正在安装PyInstaller..."
    pip3 install pyinstaller
    if [ $? -ne 0 ]; then
        echo "错误: PyInstaller安装失败"
        exit 1
    fi
fi

echo "正在清理旧的构建文件..."
rm -rf build dist

echo "正在打包程序..."
pyinstaller build_exe.spec

if [ $? -ne 0 ]; then
    echo "错误: 打包失败"
    exit 1
fi

echo "打包完成！"
echo "可执行文件位置: dist/Excel合并工具"
echo "运行命令: ./dist/Excel合并工具"

