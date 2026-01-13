# 日志清理机制说明

## 概述
本项目实现了**日志轮转（Log Rotation）**机制，自动防止日志文件无限增长。

## 工作原理

采用 Python 内置的 `RotatingFileHandler`：

```python
RotatingFileHandler(
    log_file,
    maxBytes=max_log_size,      # 单个日志文件最大大小（字节）
    backupCount=backup_count,   # 保留的备份文件数
    encoding='utf-8'
)
```

**轮转流程：**
1. 当日志文件大小达到 `maxBytes` 时，自动触发轮转
2. 将当前日志文件重命名为备份（如 `app.log.1`, `app.log.2`...）
3. 创建新的日志文件继续记录
4. 当备份数超过 `backupCount` 时，自动删除最旧的备份

## 配置参数

在 `config.json` 中配置：

```json
{
    "log_file": "data/logs/app.log",
    "max_log_size": 1048576,      // 1MB，以字节为单位
    "backup_count": 5              // 保留5个备份
}
```

### 参数说明

| 参数 | 单位 | 默认值 | 说明 |
|------|------|--------|------|
| `log_file` | - | `data/logs/app.log` | 日志文件路径 |
| `max_log_size` | 字节 | 10485760 (10MB) | 单个日志文件的最大大小 |
| `backup_count` | - | 5 | 保留的备份日志文件数 |

## 图形界面配置

在 GUI "⚙️ 配置参数" 中的**"📝 日志配置"**部分：

- **💾 日志大小限制(MB)** - 输入数值时使用 MB 单位（自动转换为字节）
- **📦 备份日志数量** - 保留的备份文件数量

## 实现细节

### 文件修改

1. **[src/utils/logger.py](../src/utils/logger.py)**
   - 导入 `RotatingFileHandler`
   - 在 `setup_global_logging()` 中使用轮转处理器
   - 自动创建日志目录

2. **[src/config/config.json](../src/config/config.json)**
   - 添加 `max_log_size` 和 `backup_count` 参数

3. **[src/config/config_manager.py](../src/config/config_manager.py)**
   - 在默认配置中添加新参数

4. **[src/ui/config_ui.py](../src/ui/config_ui.py)**
   - 添加两个输入字段供用户配置
   - MB ↔ 字节的自动转换

## 文件命名规则

轮转后的备份文件命名：

```
app.log          # 当前活跃日志文件
app.log.1        # 最近的备份
app.log.2        # 次新备份
app.log.3        # ...
app.log.4
app.log.5        # 最旧备份（超过此数量会被删除）
```

## 常见问题

**Q: 如何禁用日志轮转？**
- 将 `max_log_size` 设置为极大的值（如 1TB）

**Q: 日志文件什么时候被删除？**
- 当备份文件数量超过 `backup_count` 时，最旧的备份会在下次轮转时自动删除

**Q: 能否恢复已删除的备份？**
- 无法恢复，请合理设置 `backup_count` 来保留足够的历史日志

**Q: 配置修改后何时生效？**
- 在 GUI 中修改并保存后，需要**重启应用**才能生效

## 磁盘空间估算

假设日志文件大小 = 10MB，备份数 = 5：
```
总占用空间 = 10MB × (1 + 5) = 60MB
```

根据实际业务量调整参数：
- 日志少 → 可增加 `max_log_size` 和 `backup_count`
- 磁盘紧张 → 减小参数值

---
**最后更新**：2026-01-13
