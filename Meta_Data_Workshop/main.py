#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Meta Data Workshop - 数据库元数据处理工具
主程序入口文件

Author: Meta Data Workshop Team
Version: 1.0
"""

import sys
import os

# 添加src目录到Python路径
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

def main():
    """主程序入口"""
    try:
        from gui.main_window import MainWindow
        
        # 创建并运行主窗口
        app = MainWindow()
        app.run()
        
    except ImportError as e:
        print(f"导入模块失败: {e}")
        print("请确保已安装所需的依赖包")
        sys.exit(1)
    except Exception as e:
        print(f"程序运行出错: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()