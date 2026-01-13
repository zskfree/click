"""
UI 主题配置模块
定义全局颜色、字体和样式常量
"""

class Theme:
    # 配色方案 (Modern Minimalist + Tech Innovation)
    BG_MAIN = "#F5F7FA"        # 主背景（浅灰）
    BG_PANEL = "#FFFFFF"      # 面板/卡片背景（白）
    BG_BUTTON = "#E2E8F0"     # 默认按钮背景
    
    FG_PRIMARY = "#1F2937"    # 主要文本（深灰/近黑）
    FG_SECONDARY = "#6B7280"  # 次要文本（中灰）
    
    ACCENT = "#2B6CB0"        # 强调色（Tech 蓝）
    SUCCESS = "#16A34A"       # 成功色
    WARNING = "#F59E0B"       # 警告色
    ERROR = "#DC2626"         # 错误色
    
    BORDER = "#E2E8F0"        # 边框颜色
    
    # 字体方案
    FONT_HEADER = ("Segoe UI Semibold", 12)
    FONT_TITLE = ("Segoe UI Semibold", 16)
    FONT_BODY = ("Segoe UI", 10)
    FONT_SMALL = ("Segoe UI", 9)
    FONT_CODE = ("Consolas", 9)

    @classmethod
    def apply_ttk_styles(cls, style):
        """应用全局 TTK 样式配置"""
        # 基础 Frame
        style.configure('TFrame', background=cls.BG_MAIN)
        
        # LabelFrame
        style.configure('TLabelFrame', 
                        background=cls.BG_MAIN, 
                        borderwidth=1, 
                        relief='solid')
        style.configure('TLabelFrame.Label', 
                        background=cls.BG_MAIN, 
                        foreground=cls.ACCENT, 
                        font=cls.FONT_HEADER)
        
        # Label
        style.configure('TLabel', 
                        background=cls.BG_MAIN, 
                        foreground=cls.FG_PRIMARY, 
                        font=cls.FONT_BODY)
        
        # Button
        style.configure('TButton', 
                        font=cls.FONT_BODY, 
                        padding=6)
        
        # Entry
        style.configure('TEntry', 
                        font=cls.FONT_BODY)
        
        # Progressbar
        style.configure('TProgressbar', 
                        thickness=15, 
                        troughcolor=cls.BG_PANEL, 
                        background=cls.ACCENT)
        
        # Combobox
        style.configure('TCombobox', 
                        font=cls.FONT_BODY)
