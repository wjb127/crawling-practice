# -*- mode: python ; coding: utf-8 -*-

import sys
import os
from PyInstaller.utils.hooks import collect_data_files, collect_submodules

# 데이터 파일들 수집
datas = []
datas += collect_data_files('selenium')
datas += collect_data_files('webdriver_manager')
datas += collect_data_files('tkinter')

# 숨겨진 imports 수집
hiddenimports = []
hiddenimports += collect_submodules('selenium')
hiddenimports += collect_submodules('webdriver_manager')
hiddenimports += ['tkinter', 'tkinter.ttk', 'tkinter.scrolledtext', 'tkinter.filedialog', 'tkinter.messagebox']
hiddenimports += ['requests', 'bs4', 'lxml', 'openpyxl', 'pandas', 'numpy']
hiddenimports += ['urllib3', 'certifi', 'charset_normalizer', 'idna']
hiddenimports += ['trio', 'trio_websocket', 'websocket', 'wsproto']

a = Analysis(
    ['main.py'],
    pathex=[],
    binaries=[],
    datas=datas,
    hiddenimports=hiddenimports,
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[],
    win_no_prefer_redirects=False,
    win_private_assemblies=False,
    cipher=None,
    noarchive=False,
)

pyz = PYZ(a.pure, a.zipped_data, cipher=None)

exe = EXE(
    pyz,
    a.scripts,
    a.binaries,
    a.zipfiles,
    a.datas,
    [],
    name='웹크롤러',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    upx_exclude=[],
    runtime_tmpdir=None,
    console=False,  # 콘솔 숨김
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
    icon='app_icon.ico',  # 아이콘 파일 (실제 .ico 파일로 교체 필요)
) 