# setup.py
from setuptools import setup

APP = ['speak_selection.py']
PLIST = {
    'CFBundleName': 'read4me',
    'CFBundleDisplayName': 'read4me',
    'CFBundleIdentifier': 'com.fotiecodes.read4me',  # change if needed
    'CFBundleVersion': '1.0.0',
    'CFBundleShortVersionString': '1.0.0',
    'LSUIElement': True,  # menu bar app, no Dock icon
}
OPTIONS = {
    'argv_emulation': False,
    'iconfile': 'assets/read4me.icns',   # optional
    'plist': PLIST,
    'packages': ['rumps', 'pyperclip', 'pynput'],
    'includes': ['rumps', 'pyperclip', 'pynput'],
}

setup(
    app=APP,
    name='read4me',
    options={'py2app': OPTIONS},
    setup_requires=['py2app'],
)