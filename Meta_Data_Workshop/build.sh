#!/bin/bash

echo "========================================"
echo "Meta Data Workshop 构建脚本 (Linux/macOS)"
echo "========================================"
echo

# 检查Python环境
if ! command -v python3 &> /dev/null; then
    echo "错误: 未找到Python3，请确保Python3已安装"
    exit 1
fi

echo "Python版本:"
python3 --version

echo
echo "正在安装依赖包..."
pip3 install -r requirements.txt
if [ $? -ne 0 ]; then
    echo "错误: 依赖包安装失败"
    exit 1
fi

echo
echo "正在安装PyInstaller..."
pip3 install pyinstaller
if [ $? -ne 0 ]; then
    echo "错误: PyInstaller安装失败"
    exit 1
fi

echo
echo "正在构建可执行文件..."
python3 build_executable.py
if [ $? -ne 0 ]; then
    echo "错误: 构建失败"
    exit 1
fi

echo
echo "========================================"
echo "构建完成！可执行文件已生成"
echo "========================================"