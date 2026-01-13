import logging
import sys
import os

def setup_global_logging(config):
    """设置全局日志配置"""
    log_file = config.get('log_file', 'app.log')
    log_level = getattr(logging, config.get('log_level', 'INFO').upper())
    
    logging.basicConfig(
        level=log_level,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        handlers=[
            logging.FileHandler(log_file, encoding='utf-8'),
            logging.StreamHandler()
        ]
    )

def get_log_path():
    """获取日志文件路径，支持 PyInstaller 打包后的情况"""
    if getattr(sys, 'frozen', False):
        # 如果是打包后的exe
        return os.path.join(os.path.dirname(sys.executable), 'app.log')
    else:
        # 如果是开发环境
        return os.path.join(os.path.dirname(os.path.abspath(__file__)), 'app.log')
