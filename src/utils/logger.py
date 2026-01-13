import logging
import sys
import os
from logging.handlers import RotatingFileHandler

def setup_global_logging(config):
    """设置全局日志配置"""
    log_file = config.get('log_file', 'app.log')
    log_level = getattr(logging, config.get('log_level', 'INFO').upper())
    # 日志大小限制：默认 1MB，单位字节
    max_log_size = config.get('max_log_size', 1 * 1024 * 1024)
    # 备份日志文件数：默认保留 5 个备份
    backup_count = config.get('backup_count', 5)
    
    # 确保日志目录存在
    log_dir = os.path.dirname(log_file)
    if log_dir and not os.path.exists(log_dir):
        os.makedirs(log_dir, exist_ok=True)
    
    # 使用 RotatingFileHandler 实现日志轮转
    rotating_handler = RotatingFileHandler(
        log_file,
        maxBytes=max_log_size,
        backupCount=backup_count,
        encoding='utf-8'
    )
    rotating_handler.setFormatter(
        logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    )
    
    logging.basicConfig(
        level=log_level,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        handlers=[
            rotating_handler,
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
