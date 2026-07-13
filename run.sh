#!/bin/bash

# MathNotebook 启动脚本

cd "$(dirname "$0")"

# 检查依赖
if ! python3 -c "import PySide6" 2>/dev/null; then
    echo "正在安装依赖..."
    pip3 install PySide6 --quiet
fi

# 启动应用
echo "🚀 启动 MathNotebook..."
python3 app.py
