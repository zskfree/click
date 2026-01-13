import tkinter as tk
from tkinter import ttk, messagebox
import logging
import json
import os

class ConfigUI:
    def __init__(self, root, recorder, clicker, config_path='config.json', on_save=None):
        self.root = root
        self.root.title("按键精灵配置")

        # 先初始化 logger
        self.logger = logging.getLogger('config_ui')

        self.recorder = recorder
        self.clicker = clicker
        self.config_path = config_path
        self.on_save = on_save

        # 加载当前配置
        self.config = self.load_config()

        # 初始化参数变量
        self.click_speed = tk.DoubleVar(value=self.config.get('click_interval', 0.1))
        self.similarity = tk.DoubleVar(value=self.config.get('threshold', 0.8))
        self.wait_time = tk.DoubleVar(value=self.config.get('wait_time', 5))
        self.immediate_click = tk.BooleanVar(value=self.config.get('immediate_click', False))
        self.loop_times = tk.IntVar(value=self.config.get('loop_times', 1))
        self.png_dir = tk.StringVar(value=self.config.get('png_dir', 'png'))
        self.log_level = tk.StringVar(value=self.config.get('log_level', 'INFO'))
        self.log_file = tk.StringVar(value=self.config.get('log_file', 'app.log'))
        self.base_dir = tk.StringVar(value=self.config.get('base_dir', '.'))

        self.create_widgets()

    def load_config(self):
        """加载配置文件，带错误处理"""
        try:
            if os.path.exists(self.config_path):
                with open(self.config_path, 'r', encoding='utf-8') as f:
                    config = json.load(f)
                    self.logger.info(f"成功加载配置文件: {self.config_path}")
                    return config
            else:
                self.logger.warning(f"配置文件不存在: {self.config_path}，使用默认配置")
                return self._get_default_config()
        except json.JSONDecodeError as e:
            self.logger.error(f"配置文件格式错误: {e}，使用默认配置")
            return self._get_default_config()
        except Exception as e:
            self.logger.error(f"加载配置文件失败: {e}，使用默认配置")
            return self._get_default_config()
    
    def _get_default_config(self):
        """返回默认配置"""
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

    def create_widgets(self):
        # 设置窗口样式
        self.root.configure(bg='#f0f0f0')
        self.root.geometry("550x680")  # 适当调整尺寸
        self.root.resizable(True, True)  # 允许调整大小
        self.root.title("⚙️ 配置参数 - 智能点击精灵")
        
        # 创建样式
        style = ttk.Style()
        style.configure('Config.TFrame', background='#f0f0f0')
        style.configure('Config.TLabel', background='#f0f0f0', font=('Microsoft YaHei', 10))
        style.configure('Config.TButton', font=('Microsoft YaHei', 10), padding=8)
        
        # 主框架
        main_frame = ttk.Frame(self.root, style='Config.TFrame')
        main_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=20)
        
        # 标题
        title_label = ttk.Label(main_frame, text="🔧 参数配置", font=('Microsoft YaHei', 14, 'bold'), foreground='#2E86C1')
        title_label.pack(pady=(0, 15))
        
        # 创建Canvas和滚动条框架
        canvas_frame = ttk.Frame(main_frame)
        canvas_frame.pack(fill=tk.BOTH, expand=True)
        
        # 创建Canvas
        canvas = tk.Canvas(canvas_frame, bg='#f0f0f0', highlightthickness=0)
        scrollbar = ttk.Scrollbar(canvas_frame, orient="vertical", command=canvas.yview)
        scrollable_frame = ttk.Frame(canvas, style='Config.TFrame')
        
        scrollable_frame.bind(
            "<Configure>",
            lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
        )
        
        canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)
        
        # 布局Canvas和滚动条
        canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        # 配置项框架（在可滚动框架内）
        config_frame = ttk.LabelFrame(scrollable_frame, text="⚙️ 运行参数")
        config_frame.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        # 点击速度
        speed_frame = ttk.Frame(config_frame)
        speed_frame.pack(fill=tk.X, padx=10, pady=5)
        ttk.Label(speed_frame, text="⚡ 点击速度(秒):", style='Config.TLabel', width=20).pack(side=tk.LEFT)
        ttk.Entry(speed_frame, textvariable=self.click_speed, width=20).pack(side=tk.RIGHT, padx=5)
        
        # 相似度阈值
        threshold_frame = ttk.Frame(config_frame)
        threshold_frame.pack(fill=tk.X, padx=10, pady=5)
        ttk.Label(threshold_frame, text="🎯 相似度阈值(0-1):", style='Config.TLabel', width=20).pack(side=tk.LEFT)
        ttk.Entry(threshold_frame, textvariable=self.similarity, width=20).pack(side=tk.RIGHT, padx=5)
        
        # 等待时间
        wait_frame = ttk.Frame(config_frame)
        wait_frame.pack(fill=tk.X, padx=10, pady=5)
        ttk.Label(wait_frame, text="⏱️ 等待时间(秒):", style='Config.TLabel', width=20).pack(side=tk.LEFT)
        ttk.Entry(wait_frame, textvariable=self.wait_time, width=20).pack(side=tk.RIGHT, padx=5)
        
        # 循环次数
        loop_frame = ttk.Frame(config_frame)
        loop_frame.pack(fill=tk.X, padx=10, pady=5)
        ttk.Label(loop_frame, text="🔄 循环次数:", style='Config.TLabel', width=20).pack(side=tk.LEFT)
        ttk.Entry(loop_frame, textvariable=self.loop_times, width=20).pack(side=tk.RIGHT, padx=5)
        
        # 立即点击
        immediate_frame = ttk.Frame(config_frame)
        immediate_frame.pack(fill=tk.X, padx=10, pady=5)
        ttk.Label(immediate_frame, text="⚡ 立即点击:", style='Config.TLabel', width=20).pack(side=tk.LEFT)
        ttk.Checkbutton(immediate_frame, variable=self.immediate_click).pack(side=tk.RIGHT, padx=5)
        
        # 分隔线
        ttk.Separator(scrollable_frame, orient='horizontal').pack(fill=tk.X, padx=5, pady=10)
        
        # 路径配置框架
        path_frame = ttk.LabelFrame(scrollable_frame, text="📁 路径配置")
        path_frame.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        # 图片目录配置
        png_dir_frame = ttk.Frame(path_frame)
        png_dir_frame.pack(fill=tk.X, padx=10, pady=5)
        ttk.Label(png_dir_frame, text="📁 图片目录:", style='Config.TLabel', width=20).pack(side=tk.LEFT)
        ttk.Entry(png_dir_frame, textvariable=self.png_dir, width=20).pack(side=tk.RIGHT, padx=5)
        
        # 基础目录配置
        base_dir_frame = ttk.Frame(path_frame)
        base_dir_frame.pack(fill=tk.X, padx=10, pady=5)
        ttk.Label(base_dir_frame, text="🏠 基础目录:", style='Config.TLabel', width=20).pack(side=tk.LEFT)
        ttk.Entry(base_dir_frame, textvariable=self.base_dir, width=20).pack(side=tk.RIGHT, padx=5)
        
        # 分隔线
        ttk.Separator(scrollable_frame, orient='horizontal').pack(fill=tk.X, padx=5, pady=10)
        
        # 日志配置框架
        log_frame = ttk.LabelFrame(scrollable_frame, text="📝 日志配置")
        log_frame.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        # 日志级别配置
        log_level_frame = ttk.Frame(log_frame)
        log_level_frame.pack(fill=tk.X, padx=10, pady=5)
        ttk.Label(log_level_frame, text="📋 日志级别:", style='Config.TLabel', width=20).pack(side=tk.LEFT)
        log_combo = ttk.Combobox(log_level_frame, textvariable=self.log_level, 
                                  values=['DEBUG', 'INFO', 'WARNING', 'ERROR'], 
                                  state='readonly', width=17)
        log_combo.pack(side=tk.RIGHT, padx=5)
        
        # 日志文件配置
        log_file_frame = ttk.Frame(log_frame)
        log_file_frame.pack(fill=tk.X, padx=10, pady=5)
        ttk.Label(log_file_frame, text="📄 日志文件:", style='Config.TLabel', width=20).pack(side=tk.LEFT)
        ttk.Entry(log_file_frame, textvariable=self.log_file, width=20).pack(side=tk.RIGHT, padx=5)
        
        # 按钮框架
        button_frame = ttk.Frame(main_frame)
        button_frame.pack(fill=tk.X, pady=(20, 0))
        
        ttk.Button(button_frame, text="💾 保存配置", command=self.save_config, style='Config.TButton').pack(side=tk.LEFT, padx=10)
        ttk.Button(button_frame, text="❌ 取消", command=self.root.destroy, style='Config.TButton').pack(side=tk.RIGHT, padx=10)

    def save_config(self):
        """保存配置参数，带错误处理和用户反馈"""
        try:
            # 验证输入
            click_interval = self.click_speed.get()
            threshold = self.similarity.get()
            wait_time = self.wait_time.get()
            loop_times = self.loop_times.get()
            
            # 验证参数范围
            if click_interval < 0:
                self._show_error("点击速度必须大于等于0")
                return
            if not (0 <= threshold <= 1):
                self._show_error("相似度阈值必须在0到1之间")
                return
            if wait_time < 0:
                self._show_error("等待时间必须大于等于0")
                return
            if loop_times < 1:
                self._show_error("循环次数必须大于等于1")
                return
            
            # 更新配置
            self.config['click_interval'] = click_interval
            self.config['threshold'] = threshold
            self.config['wait_time'] = wait_time
            self.config['immediate_click'] = self.immediate_click.get()
            self.config['loop_times'] = loop_times
            self.config['png_dir'] = self.png_dir.get().strip()
            self.config['log_level'] = self.log_level.get()
            self.config['log_file'] = self.log_file.get().strip()
            self.config['base_dir'] = self.base_dir.get().strip()
            
            # 验证必填字段
            png_dir_path = self.config['png_dir']
            if not png_dir_path:
                self._show_error("图片目录不能为空")
                return
            
            log_file_path = self.config['log_file']
            if not log_file_path:
                self._show_error("日志文件名不能为空")
                return
            
            base_dir_path = self.config['base_dir']
            if not base_dir_path:
                self._show_error("基础目录不能为空")
                return

            # 保存到文件
            with open(self.config_path, 'w', encoding='utf-8') as f:
                json.dump(self.config, f, indent=4, ensure_ascii=False)

            # 更新 recorder 和 clicker 的配置
            self.recorder.set_interval(click_interval)
            self.recorder.set_loop_times(loop_times)
            self.clicker.set_threshold(threshold)
            self.clicker.set_wait_time(wait_time)
            self.clicker.set_immediate_click(self.immediate_click.get())
            self.clicker.set_loop_times(loop_times)
            
            self.logger.info(f"配置已保存: {self.config}")

            # 调用回调以便主应用更新其配置
            if callable(self.on_save):
                try:
                    self.on_save(self.config)
                except Exception as e:
                    self.logger.exception("调用 on_save 回调时出错")
                    self._show_error(f"应用配置时出错: {str(e)}")
                    return
            
            # 显示成功消息
            self._show_success("配置保存成功！")
            
            # 延迟关闭窗口，让用户看到成功提示
            self.root.after(1000, self.root.destroy)
            
        except ValueError as e:
            self.logger.error(f"配置值错误: {e}")
            self._show_error(f"配置值错误: {str(e)}")
        except Exception as e:
            self.logger.error(f"保存配置失败: {e}")
            self._show_error(f"保存配置失败: {str(e)}")
    
    def _show_success(self, message):
        """显示成功消息"""
        messagebox.showinfo("成功", message)
    
    def _show_error(self, message):
        """显示错误消息"""
        messagebox.showerror("错误", message)
