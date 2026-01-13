import json
import os
import logging

class ConfigManager:
    def __init__(self, config_path='config.json'):
        self.config_path = config_path
        self.logger = logging.getLogger('config_manager')
        self._config = self._load_config()

    def _load_config(self):
        try:
            if os.path.exists(self.config_path):
                with open(self.config_path, 'r', encoding='utf-8') as f:
                    return json.load(f)
            else:
                return self._get_default_config()
        except (FileNotFoundError, json.JSONDecodeError) as e:
            self.logger.warning(f"加载配置文件失败，使用默认配置: {e}")
            return self._get_default_config()

    def _get_default_config(self):
        return {
            "png_dir": "png",
            "click_interval": 0.1,
            "loop_times": 1,
            "threshold": 0.8,
            "wait_time": 5.0,
            "immediate_click": False,
            "log_level": "INFO",
            "log_file": "app.log"
        }

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
