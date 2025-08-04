#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Meta Data Workshop 可执行文件打包脚本
使用PyInstaller将Python项目打包为独立的可执行文件

使用方法:
1. 安装PyInstaller: pip install pyinstaller
2. 运行此脚本: python build_executable.py
"""

import os
import sys
import shutil
import subprocess
from pathlib import Path

# 项目配置
PROJECT_NAME = "MetaDataWorkshop"
MAIN_SCRIPT = "main.py"
ICON_FILE = "assets/icon.ico"  # 可选，如果没有图标文件会跳过
VERSION = "1.0.0"

def check_pyinstaller():
    """检查PyInstaller是否已安装"""
    try:
        import PyInstaller
        print(f"✓ PyInstaller版本: {PyInstaller.__version__}")
        return True
    except ImportError:
        print("❌ PyInstaller未安装，正在安装...")
        try:
            subprocess.check_call([sys.executable, "-m", "pip", "install", "pyinstaller"])
            print("✓ PyInstaller安装成功")
            return True
        except subprocess.CalledProcessError:
            print("❌ PyInstaller安装失败，请手动安装: pip install pyinstaller")
            return False

def create_spec_file():
    """创建PyInstaller spec文件"""
    spec_content = f'''# -*- mode: python ; coding: utf-8 -*-

block_cipher = None

# 分析主脚本
a = Analysis(
    ['{MAIN_SCRIPT}'],
    pathex=[],
    binaries=[],
    datas=[
        ('src', 'src'),
        ('README.md', '.'),
        ('requirements.txt', '.'),
    ],
    hiddenimports=[
        'pandas',
        'openpyxl',
        'xlsxwriter',
        'tkinter',
        'tkinter.ttk',
        'tkinter.filedialog',
        'tkinter.messagebox',
        'tkinter.scrolledtext',
    ],
    hookspath=[],
    hooksconfig={{}},
    runtime_hooks=[],
    excludes=[
        'matplotlib',
        'numpy.random._pickle',
        'PIL',
        'scipy',
        'IPython',
        'notebook',
        'jupyter',
    ],
    win_no_prefer_redirects=False,
    win_private_assemblies=False,
    cipher=block_cipher,
    noarchive=False,
)

# 处理数据文件
pyz = PYZ(a.pure, a.zipped_data, cipher=block_cipher)

# 创建可执行文件
exe = EXE(
    pyz,
    a.scripts,
    a.binaries,
    a.zipfiles,
    a.datas,
    [],
    name='{PROJECT_NAME}',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    upx_exclude=[],
    runtime_tmpdir=None,
    console=False,  # 不显示控制台窗口
    disable_windowed_traceback=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
    version='version_info.txt',
    icon='{ICON_FILE if os.path.exists(ICON_FILE) else None}',
)
'''
    
    with open(f"{PROJECT_NAME}.spec", "w", encoding="utf-8") as f:
        f.write(spec_content)
    
    print(f"✓ 创建spec文件: {PROJECT_NAME}.spec")

def create_version_info():
    """创建版本信息文件"""
    version_parts = VERSION.split('.')
    file_version = f"{version_parts[0]},{version_parts[1]},{version_parts[2]},0"
    
    version_info = f'''# UTF-8
#
# For more details about fixed file info 'ffi' see:
# http://msdn.microsoft.com/en-us/library/ms646997.aspx
VSVersionInfo(
  ffi=FixedFileInfo(
    filevers=({file_version}),
    prodvers=({file_version}),
    mask=0x3f,
    flags=0x0,
    OS=0x40004,
    fileType=0x1,
    subtype=0x0,
    date=(0, 0)
  ),
  kids=[
    StringFileInfo([
      StringTable(
        u'040904B0',
        [StringStruct(u'CompanyName', u'Meta Data Workshop Team'),
        StringStruct(u'FileDescription', u'数据库元数据处理工具'),
        StringStruct(u'FileVersion', u'{VERSION}'),
        StringStruct(u'InternalName', u'{PROJECT_NAME}'),
        StringStruct(u'LegalCopyright', u'Copyright © 2024 Meta Data Workshop Team'),
        StringStruct(u'OriginalFilename', u'{PROJECT_NAME}.exe'),
        StringStruct(u'ProductName', u'Meta Data Workshop'),
        StringStruct(u'ProductVersion', u'{VERSION}')])
      ]),
    VarFileInfo([VarStruct(u'Translation', [1033, 1200])])
  ]
)'''
    
    with open("version_info.txt", "w", encoding="utf-8") as f:
        f.write(version_info)
    
    print("✓ 创建版本信息文件: version_info.txt")

def build_executable():
    """构建可执行文件"""
    print("开始构建可执行文件...")
    
    # 构建命令
    cmd = [
        "pyinstaller",
        "--clean",  # 清理临时文件
        "--noconfirm",  # 不询问覆盖
        f"{PROJECT_NAME}.spec"
    ]
    
    try:
        result = subprocess.run(cmd, check=True, capture_output=True, text=True)
        print("✓ 构建成功！")
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ 构建失败:")
        print(f"错误代码: {e.returncode}")
        print(f"错误输出: {e.stderr}")
        return False

def create_installer_script():
    """创建安装脚本（Windows批处理文件）"""
    installer_content = f'''@echo off
echo ========================================
echo Meta Data Workshop v{VERSION} 安装程序
echo ========================================
echo.

set INSTALL_DIR=%PROGRAMFILES%\\MetaDataWorkshop

echo 正在创建安装目录...
if not exist "%INSTALL_DIR%" mkdir "%INSTALL_DIR%"

echo 正在复制文件...
copy "{PROJECT_NAME}.exe" "%INSTALL_DIR%\\" >nul
copy "README.md" "%INSTALL_DIR%\\" >nul

echo 正在创建桌面快捷方式...
set DESKTOP=%USERPROFILE%\\Desktop
echo [InternetShortcut] > "%DESKTOP%\\Meta Data Workshop.url"
echo URL=file:///%INSTALL_DIR%\\{PROJECT_NAME}.exe >> "%DESKTOP%\\Meta Data Workshop.url"
echo IconFile=%INSTALL_DIR%\\{PROJECT_NAME}.exe >> "%DESKTOP%\\Meta Data Workshop.url"
echo IconIndex=0 >> "%DESKTOP%\\Meta Data Workshop.url"

echo.
echo ========================================
echo 安装完成！
echo 程序已安装到: %INSTALL_DIR%
echo 桌面快捷方式已创建
echo ========================================
pause
'''
    
    with open("install.bat", "w", encoding="gbk") as f:
        f.write(installer_content)
    
    print("✓ 创建安装脚本: install.bat")

def create_linux_script():
    """创建Linux安装脚本"""
    script_content = f'''#!/bin/bash

echo "========================================"
echo "Meta Data Workshop v{VERSION} 安装程序"
echo "========================================"
echo

INSTALL_DIR="/opt/metadataworkshop"
BIN_DIR="/usr/local/bin"

echo "正在创建安装目录..."
sudo mkdir -p "$INSTALL_DIR"

echo "正在复制文件..."
sudo cp "{PROJECT_NAME}" "$INSTALL_DIR/"
sudo cp "README.md" "$INSTALL_DIR/"

echo "正在创建可执行链接..."
sudo ln -sf "$INSTALL_DIR/{PROJECT_NAME}" "$BIN_DIR/metadataworkshop"

echo "正在设置权限..."
sudo chmod +x "$INSTALL_DIR/{PROJECT_NAME}"

echo
echo "========================================"
echo "安装完成！"
echo "程序已安装到: $INSTALL_DIR"
echo "可以通过命令 'metadataworkshop' 启动程序"
echo "========================================"
'''
    
    with open("install.sh", "w", encoding="utf-8") as f:
        f.write(script_content)
    
    # 设置执行权限
    os.chmod("install.sh", 0o755)
    print("✓ 创建Linux安装脚本: install.sh")

def cleanup_build_files():
    """清理构建过程中的临时文件"""
    cleanup_items = [
        "build",
        "__pycache__",
        f"{PROJECT_NAME}.spec",
        "version_info.txt"
    ]
    
    for item in cleanup_items:
        if os.path.exists(item):
            if os.path.isdir(item):
                shutil.rmtree(item)
            else:
                os.remove(item)
            print(f"✓ 清理: {item}")

def create_distribution_package():
    """创建分发包"""
    dist_dir = f"MetaDataWorkshop-v{VERSION}"
    
    # 创建分发目录
    if os.path.exists(dist_dir):
        shutil.rmtree(dist_dir)
    os.makedirs(dist_dir)
    
    # 复制文件到分发目录
    files_to_copy = [
        f"dist/{PROJECT_NAME}.exe",
        "README.md",
        "requirements.txt",
        "install.bat"
    ]
    
    if sys.platform.startswith('linux'):
        files_to_copy.extend([
            f"dist/{PROJECT_NAME}",
            "install.sh"
        ])
    
    for file_path in files_to_copy:
        if os.path.exists(file_path):
            if os.path.isfile(file_path):
                shutil.copy2(file_path, dist_dir)
            print(f"✓ 复制文件: {file_path}")
    
    print(f"✓ 创建分发包: {dist_dir}/")
    
    # 创建压缩包
    try:
        shutil.make_archive(dist_dir, 'zip', dist_dir)
        print(f"✓ 创建压缩包: {dist_dir}.zip")
    except Exception as e:
        print(f"⚠ 创建压缩包失败: {e}")

def main():
    """主函数"""
    print("========================================")
    print(f"Meta Data Workshop v{VERSION} 打包工具")
    print("========================================")
    print()
    
    # 检查环境
    if not os.path.exists(MAIN_SCRIPT):
        print(f"❌ 主脚本文件不存在: {MAIN_SCRIPT}")
        return False
    
    # 检查并安装PyInstaller
    if not check_pyinstaller():
        return False
    
    try:
        # 创建配置文件
        create_version_info()
        create_spec_file()
        
        # 构建可执行文件
        if not build_executable():
            return False
        
        # 创建安装脚本
        if sys.platform.startswith('win'):
            create_installer_script()
        elif sys.platform.startswith('linux'):
            create_linux_script()
        
        # 创建分发包
        create_distribution_package()
        
        # 清理临时文件
        cleanup_build_files()
        
        print()
        print("========================================")
        print("✓ 打包完成！")
        print(f"可执行文件位置: dist/{PROJECT_NAME}.exe")
        print(f"分发包: MetaDataWorkshop-v{VERSION}.zip")
        print("========================================")
        
        return True
        
    except Exception as e:
        print(f"❌ 打包过程中出现错误: {e}")
        return False

if __name__ == "__main__":
    success = main()
    if not success:
        sys.exit(1)