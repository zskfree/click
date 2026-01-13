"""
核心功能模块
包含点击记录、图像匹配等核心自动化功能
"""
from .base_clicker import ClickerBase
from .click_recorder import ClickRecorder
from .image_clicker import ImageClicker

__all__ = ['ClickerBase', 'ClickRecorder', 'ImageClicker']
