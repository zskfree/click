import json
import os
import logging

class ConfigManager:
    DEFAULT_CONFIG = {
        "base_dir": ".",
        "png_dir": "templates/png",
        "click_interval": 0.1,
        "loop_times": 1,
        "threshold": 0.8,
        "wait_time": 5.0,
        "immediate_click": False,
        "log_level": "INFO",
        "log_file": "data/logs/app.log",
        "max_log_size": 1048576,
        "backup_count": 5
    }

    def __init__(self, config_path='config.json'):
        self.config_path = config_path
        self.logger = logging.getLogger('config_manager')
        self._config = self._load_config()

    def _load_config(self):
        try:
            if os.path.exists(self.config_path):
                with open(self.config_path, 'r', encoding='utf-8') as f:
                    loaded = json.load(f)
                    merged = self.default_config()
                    merged.update(loaded)
                    return merged
            else:
                return self.default_config()
        except (FileNotFoundError, json.JSONDecodeError) as e:
            self.logger.warning(f"加载配置文件失败，使用默认配置: {e}")
            return self.default_config()

    @classmethod
    def default_config(cls):
        return dict(cls.DEFAULT_CONFIG)

    def as_dict(self):
        return dict(self._config)

    def get(self, key, default=None):
        return self._config.get(key, default)

    def set(self, key, value):
        self._config[key] = value

    def save(self):
        try:
            with open(self.config_path, 'w', encoding='utf-8') as f:
                json.dump(self._config, f, indent=4)
            self.logger.info("配置已保存")
        except Exception as e:
            self.logger.error(f"保存配置失败: {e}")

    def update_from_dict(self, updates):
        self._config.update(updates)
        self.save()
