import cv2
import numpy as np
import pyautogui
import time
from pynput.mouse import Button, Controller
import os
import logging
from .base_clicker import ClickerBase

class ImageClicker(ClickerBase):
    def __init__(self, config):
        super().__init__(config)
        self.folder_path = self.get_config_value('png_dir', 'png')
        self.threshold = self.get_config_value('threshold', 0.8)
        self.wait_time = self.get_config_value('wait_time', 5)
        self.immediate_click = self.get_config_value('immediate_click', False)
        self.mouse = Controller()
        self.templates = self.load_templates()
        self.is_running = True
        self.current_loop = 0
        self.progress_callback = None  # 用于报告进度的回调函数

    def start(self, stop_event=None):
        self.is_running = True
        self.current_loop = 0
        interval = self.get_config_value('click_interval', 0.1)
        self.find_and_click(interval, stop_event)

    def stop(self):
        self.is_running = False
        self.logger.info("停止图片识别点击")

    def load_templates(self):
        # 加载模板图片
        templates = []
        try:
            if not os.path.exists(self.folder_path):
                self.logger.error(f"图片文件夹不存在: {self.folder_path}")
                return templates
                
            for filename in sorted(os.listdir(self.folder_path)):
                if filename.endswith(".png"):
                    template_path = os.path.join(self.folder_path, filename)
                    template = cv2.imread(template_path, 0)
                    if template is None:
                        self.logger.warning(f"无法读取图片: {template_path}")
                        continue
                    templates.append((filename, template))
        except Exception as e:
            self.logger.error(f"加载模板图片时出错: {e}")
        return templates

    def find_and_click(self, interval, stop_event=None):
        """查找并点击图片，带进度报告"""
        total_templates = len(self.templates)
        if total_templates == 0:
            self.logger.warning("没有加载任何模板图片")
            if self.progress_callback:
                self.progress_callback(100.0)
            return False
            
        while self.is_running and self.current_loop < self.loop_times:
            if stop_event and stop_event.is_set():
                self.logger.info("图片识别点击被全局停止")
                break
                
            self.logger.info(f"开始第 {self.current_loop + 1}/{self.loop_times} 次循环")
            
            for idx, (filename, template) in enumerate(self.templates):
                if not self.is_running or (stop_event and stop_event.is_set()):
                    return False
                
                progress = self._calculate_progress(idx, total_templates)
                if self.progress_callback:
                    self.progress_callback(progress)
                
                if self._find_and_click_template(filename, template, interval, stop_event):
                    self.logger.info(f"成功点击图片 [{idx+1}/{total_templates}]: {filename} (进度: {progress:.1f}%)")
                else:
                    self.logger.debug(f"未找到图片 [{idx+1}/{total_templates}]: {filename}")
                
            self.current_loop += 1
            if self.current_loop < self.loop_times:
                self.logger.info(f"完成第 {self.current_loop}/{self.loop_times} 次循环")
                time.sleep(0.5)
        
        # 完成时报告100%
        if self.progress_callback:
            self.progress_callback(100.0)
        
        self.is_running = False
        self.logger.info("图片识别点击任务完成")
        return True
    
    def _calculate_progress(self, current_idx, total_templates):
        """计算当前的进度百分比"""
        loop_progress = self.current_loop / self.loop_times
        template_progress = (current_idx + 1) / total_templates / self.loop_times
        return (loop_progress + template_progress) * 100

    def _find_and_click_template(self, filename, template, interval, stop_event=None):
        start_time = time.time()
        while time.time() - start_time < self.wait_time:
            if not self.is_running or (stop_event and stop_event.is_set()):
                return False
                
            max_val, max_loc = self._match_template_on_screen(template)
            
            if max_val >= self.threshold:
                self._click_at_location(max_loc, template)
                if not self.immediate_click:
                    time.sleep(interval)
                return True
            time.sleep(0.1)
        return False
    
    def _match_template_on_screen(self, template):
        """在屏幕截图上进行模板匹配，返回匹配值和位置"""
        screenshot = pyautogui.screenshot()
        screenshot = cv2.cvtColor(np.array(screenshot), cv2.COLOR_RGB2GRAY)
        res = cv2.matchTemplate(screenshot, template, cv2.TM_CCOEFF_NORMED)
        _, max_val, _, max_loc = cv2.minMaxLoc(res)
        return max_val, max_loc
    
    def _click_at_location(self, location, template):
        """在指定位置点击，使用模板的中心"""
        x, y = location
        w, h = template.shape[::-1]
        center_x = x + w // 2
        center_y = y + h // 2
        self.mouse.position = (center_x, center_y)
        self.mouse.click(Button.left, 1)

    def set_threshold(self, threshold):
        # 设置相似度阈值
        self.threshold = threshold
        self.logger.info(f"设置相似度阈值为: {threshold}")

    def set_wait_time(self, wait_time):
        # 设置等待时间
        self.wait_time = wait_time
        self.logger.info(f"设置等待时间为: {wait_time} 秒")

    def set_immediate_click(self, immediate_click):
        # 设置是否立即点击
        self.immediate_click = immediate_click
        self.logger.info(f"设置立即点击为: {immediate_click}")
    
    def set_progress_callback(self, callback):
        """设置进度回调函数"""
        self.progress_callback = callback
