"""
按键精灵 - 智能点击自动化工具
主要功能：
- 鼠标点击记录与回放
- 图像识别与自动点击
"""
__version__ = "1.0.0"
__author__ = "Your Name"

from .core import ClickerBase, ClickRecorder, ImageClicker
from .config import ConfigManager
from .utils import setup_global_logging

__all__ = [
    'ClickerBase',
    'ClickRecorder', 
    'ImageClicker',
    'ConfigManager',
    'setup_global_logging'
]
