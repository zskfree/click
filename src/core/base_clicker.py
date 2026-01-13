from abc import ABC, abstractmethod
import logging

class ClickerBase(ABC):
    def __init__(self, config):
        self.config = config
        self.loop_times = config.get('loop_times', 1)
        self.logger = logging.getLogger(self.__class__.__name__)

    @abstractmethod
    def start(self):
        pass

    @abstractmethod
    def stop(self):
        pass

    def set_loop_times(self, times):
        self.loop_times = max(1, times)
        self.logger.info(f"设置循环次数为: {self.loop_times}")

    def get_config_value(self, key, default=None):
        return self.config.get(key, default)
