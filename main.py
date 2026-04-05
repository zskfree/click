import os
import sys
import tkinter as tk
from tkinter import ttk, messagebox
import threading
import logging
from pynput import keyboard

# 添加src目录到路径中
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from src.core import ClickRecorder, ImageClicker
from src.ui import ConfigUI, Theme
from src.config import ConfigManager
from src.utils import setup_global_logging

class UITextHandler(logging.Handler):
    """自定义日志处理器，将日志显示在UI文本框中"""
    def __init__(self, text_widget):
        super().__init__()
        self.text_widget = text_widget
        self.setFormatter(logging.Formatter('%(asctime)s - %(levelname)s - %(message)s'))
    
    def emit(self, record):
        msg = self.format(record)
        self.text_widget.after(0, lambda: self._append_text(msg))
    
    def _append_text(self, msg):
        self.text_widget.insert(tk.END, msg + '\n')
        self.text_widget.see(tk.END)
        # 限制日志行数
        if int(self.text_widget.index('end-1c').split('.')[0]) > 100:
            self.text_widget.delete('1.0', '2.0')


class MainApp:
    def __init__(self, root):
        self.root = root
        self.root.title("按键精灵")
        # 先初始化日志记录器，防止 load_config 中使用 self.logger 时未定义
        self.logger = logging.getLogger('main_app')

        # 基础路径和配置管理
        self.base_dir = os.path.dirname(os.path.abspath(__file__))
        self.config_path = os.path.join(self.base_dir, 'src', 'config', 'config.json')
        self.config_manager = ConfigManager(self.config_path)

        # 加载配置文件
        self.config = self.load_config()

        # 获取图片目录
        self.png_dir = os.path.join(self.base_dir, self.config['png_dir'])

        # 初始化点击记录器和图片点击器
        self.recorder = ClickRecorder(self.config)
        self.clicker = ImageClicker(self.config)
        
        # 设置进度回调
        self.clicker.set_progress_callback(self.update_progress)

        self.is_clicking = True  # 添加停止标志
        self.loop_times = tk.IntVar(value=self.config['loop_times'])  # 从config获取默认值
        self.status_var = tk.StringVar(value="就绪")
        self.progress_var = tk.DoubleVar(value=0.0)
        
        # 全局停止事件
        self.global_stop_event = threading.Event()
        
        self.create_widgets()
        self.image_click_thread = None  # 添加线程引用
        self.thread_lock = threading.Lock()  # 添加线程锁
        self.thread_running = False  # 添加线程运行状态标志
        
        # 启动键盘监听器
        self.keyboard_listener = None
        self.start_keyboard_listener()

    def load_config(self):
        return self.config_manager.as_dict()

    def create_widgets(self):
        # 设置窗口样式
        self.root.configure(bg=Theme.BG_MAIN)
        self.root.geometry("800x810")
        self.root.resizable(True, True)
        
        # 创建样式
        style = ttk.Style()
        Theme.apply_ttk_styles(style)
        
        # 标题
        title_frame = ttk.Frame(self.root)
        title_frame.grid(row=0, column=0, columnspan=2, padx=20, pady=10, sticky="ew")
        title_label = ttk.Label(title_frame, text="🔥 智能点击精灵", font=Theme.FONT_TITLE, foreground=Theme.ACCENT)
        title_label.pack()
        
        # 左侧控制面板
        left_frame = ttk.LabelFrame(self.root, text="🎮 控制面板")
        left_frame.grid(row=1, column=0, padx=15, pady=10, sticky="nsew")
        
        # 点击记录控制
        record_frame = ttk.LabelFrame(left_frame, text="📝 点击记录")
        record_frame.pack(fill=tk.X, padx=8, pady=8)
        
        ttk.Button(record_frame, text="▶️ 开始记录", command=self.start_recording).pack(fill=tk.X, padx=5, pady=4)
        ttk.Button(record_frame, text="⏹️ 停止记录", command=self.stop_recording).pack(fill=tk.X, padx=5, pady=4)
        ttk.Button(record_frame, text="🎬 播放点击", command=self.play_clicks).pack(fill=tk.X, padx=5, pady=4)
        
        # 图片识别控制
        image_frame = ttk.LabelFrame(left_frame, text="🖼️ 图片识别")
        image_frame.pack(fill=tk.X, padx=8, pady=8)
        
        ttk.Button(image_frame, text="🔍 开始识别", command=self.start_image_click).pack(fill=tk.X, padx=5, pady=4)
        ttk.Button(image_frame, text="⏹️ 停止识别", command=self.stop_image_click).pack(fill=tk.X, padx=5, pady=4)
        
        # 全局控制
        global_frame = ttk.LabelFrame(left_frame, text="⚡ 全局控制")
        global_frame.pack(fill=tk.X, padx=8, pady=8)
        
        ttk.Button(global_frame, text="🚨 全局停止 (ESC)", command=self.global_stop).pack(fill=tk.X, padx=5, pady=4)
        ttk.Button(global_frame, text="⚙️ 配置参数", command=self.open_config).pack(fill=tk.X, padx=5, pady=4)
        
        # 右侧设置面板
        right_frame = ttk.LabelFrame(self.root, text="🔧 设置面板")
        right_frame.grid(row=1, column=1, padx=15, pady=10, sticky="nsew")
        
        # 循环次数设置
        loop_frame = ttk.Frame(right_frame)
        loop_frame.pack(fill=tk.X, padx=5, pady=10)
        ttk.Label(loop_frame, text="🔄 循环次数:").pack(side=tk.LEFT, padx=5)
        ttk.Entry(loop_frame, textvariable=self.loop_times, width=8).pack(side=tk.LEFT, padx=5)
        ttk.Button(loop_frame, text="✅ 更新", command=self.update_loop_times).pack(side=tk.LEFT, padx=5)
        
        # 状态显示框架
        status_frame = ttk.LabelFrame(right_frame, text="📊 运行状态")
        status_frame.pack(fill=tk.X, padx=5, pady=15)
        
        # 状态标签
        status_container = ttk.Frame(status_frame)
        status_container.pack(fill=tk.X, padx=5, pady=8)
        ttk.Label(status_container, text="状态:").pack(side=tk.LEFT, padx=5)
        status_label = ttk.Label(status_container, textvariable=self.status_var, foreground=Theme.SUCCESS, font=Theme.FONT_HEADER)
        status_label.pack(side=tk.LEFT, padx=5)
        
        # 进度条
        progress_container = ttk.Frame(status_frame)
        progress_container.pack(fill=tk.X, padx=5, pady=8)
        ttk.Label(progress_container, text="进度:").pack(side=tk.LEFT, padx=5)
        self.progress_bar = ttk.Progressbar(
            progress_container, 
            variable=self.progress_var, 
            maximum=100, 
            length=200,
            mode='determinate'
        )
        self.progress_bar.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=5)
        # 进度百分比标签
        self.progress_label = ttk.Label(progress_container, text="0%", width=5, anchor='e')
        self.progress_label.pack(side=tk.LEFT, padx=5)
        
        # 日志显示区域
        log_frame = ttk.LabelFrame(self.root, text="📋 运行日志")
        log_frame.grid(row=2, column=0, columnspan=2, padx=15, pady=10, sticky="nsew")
        
        # 创建文本框用于显示日志
        self.log_text = tk.Text(log_frame, height=8, wrap=tk.WORD, font=Theme.FONT_CODE, 
                                bg=Theme.BG_PANEL, fg=Theme.FG_PRIMARY, relief='flat', padx=10, pady=10)
        scrollbar = ttk.Scrollbar(log_frame, orient=tk.VERTICAL, command=self.log_text.yview)
        self.log_text.configure(yscrollcommand=scrollbar.set)
        
        self.log_text.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=2, pady=2)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y, padx=2, pady=2)
        
        # 设置网格权重
        self.root.grid_rowconfigure(1, weight=1)
        self.root.grid_rowconfigure(2, weight=1)
        self.root.grid_columnconfigure(0, weight=1)
        self.root.grid_columnconfigure(1, weight=1)
        
        # 设置日志处理器
        self.setup_ui_logging()

    def start_keyboard_listener(self):
        """启动键盘监听器，带错误处理"""
        try:
            if self.keyboard_listener:
                self.keyboard_listener.stop()
            self.keyboard_listener = keyboard.Listener(on_press=self.on_key_press)
            self.keyboard_listener.start()
            self.logger.info("键盘监听器已启动")
        except Exception as e:
            self.logger.error(f"启动键盘监听器失败: {e}")
            self.keyboard_listener = None

    def setup_ui_logging(self):
        """设置UI日志处理器"""
        ui_handler = UITextHandler(self.log_text)
        ui_handler.setLevel(logging.INFO)
        
        # 获取相关日志器并添加处理器
        for logger_name in ['main_app', 'src.core.click_recorder', 'src.core.image_clicker']:
            logging.getLogger(logger_name).addHandler(ui_handler)

    def update_loop_times(self):
        """更新循环次数，带错误处理"""
        try:
            times = self.loop_times.get()
            if times < 1:
                messagebox.showerror("错误", "循环次数必须大于等于1")
                return
            
            # 更新配置对象
            self.config['loop_times'] = times
            
            # 更新 recorder 和 clicker
            self.recorder.set_loop_times(times)
            self.clicker.set_loop_times(times)
            
            self.logger.info(f"更新循环次数为: {times}")
            
            # 显示成功提示
            messagebox.showinfo("成功", f"循环次数已更新为: {times}")
        except ValueError as e:
            messagebox.showerror("错误", f"请输入有效的数字: {str(e)}")
            self.logger.error(f"更新循环次数失败: {e}")

    def on_key_press(self, key):
        """键盘按键监听器"""
        try:
            if key == keyboard.Key.esc:
                self.logger.info("检测到ESC键按下")
                self.global_stop()
        except Exception as e:
            self.logger.error(f"键盘监听器错误: {e}")

    def global_stop(self):
        """全局停止所有运行中的操作"""
        self.logger.info("触发全局停止")
        self.global_stop_event.set()
        
        # 停止所有可能的操作
        self.stop_recording()
        self.recorder.stop_playing()  # 停止播放点击
        self.stop_image_click()
        
        # 等待线程完成
        if self.image_click_thread and self.image_click_thread.is_alive():
            self.image_click_thread.join(timeout=2.0)
            if self.image_click_thread.is_alive():
                self.logger.warning("图片点击线程未能及时停止")
        
        self.status_var.set("已全局停止")
        self.progress_var.set(0.0)
        
        # 重置停止事件，允许后续操作
        self.global_stop_event.clear()
        self.logger.info("全局停止完成，已重置状态")

    def start_recording(self):
        """开始记录点击，带状态检查"""
        try:
            if self.recorder.recording:
                messagebox.showwarning("警告", "已经在记录中")
                return
            
            self.recorder.start()
            self.status_var.set("正在记录点击...")
            self.logger.info("开始记录点击")
        except Exception as e:
            self.logger.error(f"开始记录失败: {e}")
            self.status_var.set("就绪")
            messagebox.showerror("错误", f"开始记录失败: {str(e)}")

    def stop_recording(self):
        """停止记录点击，带状态检查"""
        try:
            if not self.recorder.recording:
                return
            
            self.recorder.stop()
            self.status_var.set("就绪")
            
            # 显示记录的点击数量
            click_count = len(self.recorder.clicks)
            self.logger.info(f"停止记录点击，共记录 {click_count} 个点击")
            
            if click_count > 0:
                messagebox.showinfo("记录完成", f"已记录 {click_count} 个点击位置")
        except Exception as e:
            self.logger.error(f"停止记录失败: {e}")
            self.status_var.set("就绪")

    def play_clicks(self):
        """播放点击，在线程中运行以避免阻塞UI"""
        try:
            # 修改播放逻辑，使用循环次数
            self.recorder.set_loop_times(self.loop_times.get())
            self.status_var.set("正在播放点击...")
            
            # 在新线程中播放以避免阻塞UI
            def _play():
                try:
                    self.recorder.play_clicks(self.global_stop_event)
                    self.status_var.set("就绪")
                    self.logger.info("播放点击完成")
                except Exception as e:
                    self.logger.error(f"播放点击时出错: {e}")
                    self.status_var.set("播放出错")
            
            play_thread = threading.Thread(target=_play, daemon=True)
            play_thread.start()
            self.logger.info("开始播放点击")
        except Exception as e:
            self.logger.error(f"启动播放点击失败: {e}")
            self.status_var.set("就绪")

    def start_image_click(self):
        """开始图片识别点击，带状态检查和错误处理"""
        if self.thread_running:
            messagebox.showwarning("警告", "图片识别任务已在运行中")
            self.logger.info("图片识别任务已在运行中")
            return

        # 检查图片目录
        if not os.path.exists(self.png_dir):
            messagebox.showerror("错误", f"图片目录不存在: {self.png_dir}")
            self.logger.error(f"图片目录不存在: {self.png_dir}")
            return
        
        # 检查是否有图片文件
        png_files = [f for f in os.listdir(self.png_dir) if f.endswith('.png')]
        if not png_files:
            messagebox.showerror("错误", f"图片目录中没有PNG文件: {self.png_dir}")
            self.logger.error(f"图片目录中没有PNG文件: {self.png_dir}")
            return

        self.thread_running = True
        self.is_clicking = True
        self.clicker.set_loop_times(self.loop_times.get())
        self.status_var.set("正在进行图片识别点击...")
        self.progress_var.set(0.0)
        
        try:
            self.image_click_thread = threading.Thread(target=self.run_image_click)
            self.image_click_thread.daemon = True
            self.image_click_thread.start()
            self.logger.info(f"开始图片识别点击，设定循环次数：{self.loop_times.get()}，图片数量：{len(png_files)}")
        except Exception as e:
            self.thread_running = False
            self.is_clicking = False
            self.status_var.set("就绪")
            self.logger.error(f"启动图片识别线程失败: {str(e)}")
            messagebox.showerror("错误", f"启动图片识别失败: {str(e)}")

    def stop_image_click(self):
        with self.thread_lock:
            if not self.thread_running:
                return
                
            self.logger.info("正在停止图片识别点击...")
            self.is_clicking = False
            self.clicker.stop()
            self.thread_running = False
            
            # 等待线程完成，最多等待3秒
            if self.image_click_thread and self.image_click_thread.is_alive():
                self.image_click_thread.join(timeout=3.0)
                if self.image_click_thread.is_alive():
                    self.logger.warning("图片点击线程未能及时停止，可能需要强制终止")
                else:
                    self.logger.info("图片点击线程已成功停止")
            
            self.status_var.set("就绪")
            self.progress_var.set(0.0)
            self.logger.info("停止图片识别点击完成")

    def run_image_click(self):
        try:
            self.clicker.start(self.global_stop_event)
        except Exception as e:
            self.logger.error(f"图片识别过程出错: {str(e)}")
        finally:
            self.is_clicking = False
            self.thread_running = False
            self.status_var.set("就绪")
            self.progress_var.set(100.0)
    
    def update_progress(self, progress):
        """更新进度条（线程安全）"""
        try:
            # 确保进度值在0-100之间
            progress = max(0.0, min(100.0, progress))
            self.root.after(0, lambda p=progress: self._set_progress(p))
        except Exception as e:
            self.logger.error(f"更新进度失败: {e}")
    
    def _set_progress(self, progress):
        """设置进度条的值（在主线程中调用）"""
        try:
            self.progress_var.set(progress)
            self.progress_label.config(text=f"{progress:.0f}%")
            self.progress_bar.update()
            # 只在显著变化时记录日志，避免日志过多
            if progress == 0 or progress == 100 or int(progress) % 10 == 0:
                self.logger.info(f"进度更新: {progress:.1f}%")
        except Exception as e:
            self.logger.error(f"设置进度失败: {e}")

    def open_config(self):
        """打开配置界面，带错误处理"""
        try:
            config_window = tk.Toplevel(self.root)
            
            # 定义回调函数，用于保存后更新主程序配置
            def _on_config_saved(new_config):
                try:
                    # 更新主程序配置对象
                    self.config.update(new_config)
                    
                    # 更新可能依赖的属性
                    self.png_dir = os.path.join(self.base_dir, self.config.get('png_dir', 'templates/png'))
                    
                    # 更新循环次数显示
                    self.loop_times.set(self.config.get('loop_times', 1))
                    
                    # 应用到 recorder/clicker（已在 ConfigUI.save_config 中完成，这里是确保）
                    self.recorder.set_interval(self.config.get('click_interval', 0.1))
                    self.recorder.set_loop_times(self.config.get('loop_times', 1))
                    self.clicker.set_threshold(self.config.get('threshold', 0.8))
                    self.clicker.set_wait_time(self.config.get('wait_time', 5.0))
                    self.clicker.set_immediate_click(self.config.get('immediate_click', False))
                    self.clicker.set_loop_times(self.config.get('loop_times', 1))
                    
                    # 重新加载模板（如果图片目录改变）
                    self.clicker.folder_path = self.png_dir
                    self.clicker.templates = self.clicker.load_templates()

                    # 重新配置日志（应用新的日志文件/级别设置）
                    try:
                        setup_global_logging(self.config)
                        self.logger.info("日志配置已更新")
                    except Exception as log_err:
                        self.logger.exception(f"更新日志配置时出错: {log_err}")
                    
                    self.logger.info(f"已应用新配置: {self.config}")
                except Exception as e:
                    self.logger.exception(f"应用新配置时出错: {e}")
                    messagebox.showerror("错误", f"应用配置时出错: {str(e)}")

            ConfigUI(config_window, self.recorder, self.clicker, self.config_path, on_save=_on_config_saved)
            self.logger.info("打开配置界面")
        except Exception as e:
            self.logger.error(f"打开配置界面失败: {e}")
            messagebox.showerror("错误", f"打开配置界面失败: {str(e)}")

# 在文件顶部添加以下代码，用于控制PyInstaller打包后的日志文件位置
def get_log_path():
    if getattr(sys, 'frozen', False):
        # 如果是打包后的exe
        return os.path.join(os.path.dirname(sys.executable), 'app.log')
    else:
        # 如果是开发环境
        return os.path.join(os.path.dirname(os.path.abspath(__file__)), 'data', 'logs', 'app.log')

if __name__ == "__main__":
    # 加载配置
    base_dir = os.path.dirname(os.path.abspath(__file__))
    config_path = os.path.join(base_dir, 'src', 'config', 'config.json')
    config = ConfigManager(config_path).as_dict()
    
    # 设置日志
    setup_global_logging(config)
    
    root = tk.Tk()
    app = MainApp(root)
    
    def on_closing():
        """程序关闭时的清理函数"""
        app.logger.info("程序正在关闭，进行清理...")
        
        # 停止所有运行中的操作
        app.global_stop()
        
        # 停止键盘监听器
        if app.keyboard_listener:
            try:
                app.keyboard_listener.stop()
                app.logger.info("键盘监听器已停止")
            except Exception as e:
                app.logger.error(f"停止键盘监听器时出错: {e}")
        
        # 等待所有线程完成
        if app.image_click_thread and app.image_click_thread.is_alive():
            app.image_click_thread.join(timeout=5.0)
            if app.image_click_thread.is_alive():
                app.logger.warning("程序退出时线程仍未停止")
        
        app.logger.info("程序清理完成")
        root.destroy()
    
    # 设置窗口关闭事件
    root.protocol("WM_DELETE_WINDOW", on_closing)
    
    try:
        root.mainloop()
    except KeyboardInterrupt:
        app.logger.info("收到键盘中断信号")
        on_closing()
    except Exception as e:
        app.logger.error(f"程序运行时出错: {e}")
        on_closing()
