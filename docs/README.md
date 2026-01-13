# 📖 完整使用和开发文档

## 快速开始

### 1. 安装依赖

```bash
pip install -r requirements.txt
```

### 2. 运行程序

```bash
python main.py  # Linux/Mac
启动.bat        # Windows
```

### 3. 放置模板图像

将 PNG 文件放入 `templates/png/` 目录

---

## 使用指南

### 功能特性

#### 🎬 点击记录与回放

- **开始记录** - 点击"▶️ 开始记录"按钮开始记录鼠标点击
- **停止记录** - 点击"⏹️ 停止记录"按钮结束
- **播放回放** - 点击"🎬 播放点击"按钮按设定循环次数回放

#### 🖼️ 图像识别与点击

- **开始识别** - 点击"🔍 开始识别"开始查找并点击模板图像
- **停止识别** - 点击"⏹️ 停止识别"或按 ESC 键停止

### 配置参数

在配置窗口中可调整以下参数：

| 参数 | 范围 | 说明 |
|-----|------|------|
| **点击速度** | >= 0 | 每次点击的间隔时间（秒） |
| **相似度阈值** | 0-1 | 图像匹配的严格程度（越高越严格） |
| **等待时间** | >= 0 | 寻找模板的最大等待时间（秒） |
| **循环次数** | >= 1 | 重复执行的次数 |
| **立即点击** | ON/OFF | 找到图像后是否立即点击 |

### 快捷键

| 快捷键 | 功能 |
|-------|------|
| **ESC** | 全局停止所有运行 |

---

## 项目结构

```
click/
├── src/
│   ├── core/              # 核心功能（点击记录、图像识别）
│   ├── ui/                # 用户界面
│   ├── config/            # 配置管理
│   └── utils/             # 工具函数
├── templates/
│   └── png/               # 图像模板存储
├── data/
│   └── logs/              # 日志文件存储
├── tests/                 # 测试代码
├── docs/                  # 文档
├── main.py                # 程序入口
├── requirements.txt       # 依赖列表
├── README.md              # 项目说明
└── 启动.bat              # Windows启动脚本
```

---

## API 参考

### 核心模块 (src.core)

#### ClickRecorder - 点击记录器

```python
from src.core import ClickRecorder

recorder = ClickRecorder(config)
recorder.start()                    # 开始记录
recorder.stop()                     # 停止记录
recorder.play_clicks()              # 播放
recorder.set_loop_times(5)          # 设置循环次数
recorder.set_interval(0.1)          # 设置间隔
clicks = recorder.clicks            # 获取记录列表
```

#### ImageClicker - 图像识别器

```python
from src.core import ImageClicker

clicker = ImageClicker(config)
clicker.start()                          # 开始识别
clicker.stop()                           # 停止识别
clicker.set_threshold(0.85)              # 设置相似度阈值
clicker.set_wait_time(5)                 # 设置等待时间
clicker.set_loop_times(10)               # 设置循环次数
clicker.set_progress_callback(callback)  # 设置进度回调
```

### UI 模块 (src.ui)

#### ConfigUI - 配置界面

```python
from src.ui import ConfigUI
import tkinter as tk

root = tk.Tk()
ConfigUI(root, recorder, clicker, config_path, on_save=callback)
root.mainloop()
```

### 配置管理 (src.config)

#### ConfigManager - 配置管理器

```python
from src.config import ConfigManager

manager = ConfigManager('src/config/config.json')
manager.get('threshold')                    # 获取配置
manager.set('threshold', 0.9)               # 设置配置
manager.save()                              # 保存配置
```

### 工具函数 (src.utils)

#### setup_global_logging - 日志配置

```python
from src.utils import setup_global_logging
import logging

setup_global_logging(config)
logger = logging.getLogger('my_module')
logger.info('日志信息')
```

---

## 配置文件说明

位置：`src/config/config.json`

```json
{
    "base_dir": ".",
    "png_dir": "templates/png",
    "click_interval": 1.0,
    "loop_times": 1,
    "threshold": 0.8,
    "wait_time": 5.0,
    "immediate_click": false,
    "log_level": "INFO",
    "log_file": "data/logs/app.log"
}
```

| 配置项 | 说明 |
|-------|------|
| `png_dir` | 图像模板目录 |
| `click_interval` | 点击间隔（秒） |
| `loop_times` | 循环次数 |
| `threshold` | 相似度阈值（0-1） |
| `wait_time` | 等待时间（秒） |
| `immediate_click` | 是否立即点击 |
| `log_level` | 日志级别 |
| `log_file` | 日志文件路径 |

---

## 常见问题

### ❓ 找不到图像怎么办？

- 检查 `templates/png/` 目录是否存在
- 确认 PNG 文件格式正确
- 调整"相似度阈值"，降低阈值使匹配更宽松
- 查看 `data/logs/app.log` 获取详细信息

### ❓ 点击位置不准确？

- 确保模板图像清晰且代表性强
- 调整"点击速度"，给屏幕刷新时间
- 检查分辨率是否改变

### ❓ 程序无法启动？

```bash
python --version              # 检查 Python 版本（需要 3.7+）
pip install -r requirements.txt --upgrade  # 重新安装依赖
```

### ❓ 能否实时修改配置？

可以，在配置窗口修改并保存后会立即应用。

---

## 代码示例

### 示例 1: 点击记录和回放

```python
from src.core import ClickRecorder
import json
import time

# 加载配置
with open('src/config/config.json') as f:
    config = json.load(f)

# 创建并使用记录器
recorder = ClickRecorder(config)
recorder.start()
time.sleep(5)  # 记录5秒内的点击
recorder.stop()

print(f"已记录 {len(recorder.clicks)} 个点击")
recorder.play_clicks()  # 回放
```

### 示例 2: 图像识别和点击

```python
from src.core import ImageClicker
from src.utils import setup_global_logging
import json

# 加载配置和设置日志
with open('src/config/config.json') as f:
    config = json.load(f)
setup_global_logging(config)

# 创建图像点击器
clicker = ImageClicker(config)
print(f"已加载 {len(clicker.templates)} 个模板")

# 设置进度回调
def on_progress(progress):
    print(f"进度: {progress:.1f}%")

clicker.set_progress_callback(on_progress)
clicker.start()  # 开始识别和点击
```

### 示例 3: 配置管理

```python
from src.config import ConfigManager

manager = ConfigManager('src/config/config.json')

# 修改配置
manager.set('threshold', 0.9)
manager.set('wait_time', 10)
manager.save()

# 读取配置
print(f"相似度阈值: {manager.get('threshold')}")
```

---

## 扩展开发

### 添加自定义点击器

```python
from src.core import ClickerBase

class CustomClicker(ClickerBase):
    def __init__(self, config):
        super().__init__(config)
    
    def start(self):
        """自定义实现"""
        pass
    
    def stop(self):
        """自定义实现"""
        pass
```

### 添加单元测试

在 `tests/` 目录下创建测试文件：

```python
# tests/test_custom.py
import unittest
from src.core import ImageClicker

class TestImageClicker(unittest.TestCase):
    def test_threshold(self):
        config = {'threshold': 0.8}
        clicker = ImageClicker(config)
        self.assertEqual(clicker.threshold, 0.8)
```

---

## 安全提示

⚠️ **重要**：

- 自动点击会真实控制鼠标，请在测试环境运行
- 在虚拟机或专门的测试屏幕上测试
- 备份重要数据，防止误操作
- 使用 ESC 键随时停止执行

---

## 线程和性能

- ClickRecorder 和 ImageClicker 支持在独立线程中运行
- 使用 `threading.Event` 进行线程间停止信号通信
- UI 更新使用 `root.after()` 确保线程安全
- 图像识别是 CPU 密集型，大图像模板会降低性能

---

## 日志文件

日志文件位置：`data/logs/app.log`

可用于调试和问题诊断。设置 `log_level` 为 `DEBUG` 获取详细信息。

---

## 导入速查表

```python
# 核心功能
from src.core import ClickerBase, ClickRecorder, ImageClicker

# UI 界面
from src.ui import ConfigUI

# 配置管理
from src.config import ConfigManager

# 工具函数
from src.utils import setup_global_logging
```

---

**最后更新**: 2026年1月13日  
**版本**: 1.0.0
