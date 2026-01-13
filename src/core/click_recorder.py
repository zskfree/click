import threading
import time
from pynput import mouse
import logging
from .base_clicker import ClickerBase

class ClickRecorder(ClickerBase):
    def __init__(self, config):
        super().__init__(config)
        self.clicks = []
        self.recording = False
        self.listener = None
        self.interval = self.get_config_value('click_interval', 0.1)
        self.is_playing = False  # 添加播放状态标志

    def start(self):
        """开始记录点击"""
        if self.recording:
            self.logger.warning("已经在记录中，请先停止")
            return
        
        self.recording = True
        self.clicks = []
        
        # 停止旧的监听器（如果存在）
        if self.listener and self.listener.is_alive():
            self.listener.stop()
        
        # 创建新的监听器
        self.listener = mouse.Listener(on_click=self.on_click)
        self.listener.start()
        self.logger.info("开始记录点击")

    def stop(self):
        """停止记录点击"""
        if not self.recording:
            self.logger.warning("当前没有在记录")
            return
            
        self.recording = False
        
        # 停止监听器
        if self.listener and self.listener.is_alive():
            self.listener.stop()
            self.listener = None
        
        # 删除最后一个记录的点击（停止按钮的点击）
        if self.clicks:
            self.clicks.pop()
        
        self.logger.info(f"停止记录点击，共记录 {len(self.clicks)} 个点击")

    def on_click(self, x, y, button, pressed):
        # 记录点击位置
        if self.recording and pressed:
            self.clicks.append((x, y))
            self.logger.info(f"记录点击位置: ({x}, {y})")

    def play_clicks(self, stop_event=None):
        """播放记录的点击，支持全局停止"""
        if not self.clicks:
            self.logger.warning("没有记录的点击可以播放")
            return
        
        self.is_playing = True
        self.logger.info(f"开始播放点击，循环次数: {self.loop_times}, 点击数: {len(self.clicks)}")
        
        try:
            controller = mouse.Controller()
            for loop_idx in range(self.loop_times):
                if self._should_stop_playback(stop_event):
                    self.logger.info(f"播放点击被停止（循环 {loop_idx + 1}/{self.loop_times}）")
                    break
                    
                for idx, click in enumerate(self.clicks):
                    if self._should_stop_playback(stop_event):
                        self.logger.info(f"播放点击被停止（点击 {idx + 1}/{len(self.clicks)}）")
                        return
                    
                    controller.position = click
                    controller.click(mouse.Button.left, 1)
                    time.sleep(self.interval)
                
                if self.loop_times > 1 and loop_idx < self.loop_times - 1:
                    self.logger.info(f"完成第 {loop_idx + 1}/{self.loop_times} 次循环")
                    
            self.logger.info("播放点击完成")
        finally:
            self.is_playing = False
    
    def _should_stop_playback(self, stop_event):
        """检查是否应该停止播放"""
        return (stop_event and stop_event.is_set()) or not self.is_playing
    
    def stop_playing(self):
        """停止播放点击"""
        if self.is_playing:
            self.is_playing = False
            self.logger.info("正在停止播放...")

    def set_interval(self, interval):
        """设置点击间隔"""
        self.interval = interval
        self.logger.info(f"设置点击间隔为: {interval} 秒")
