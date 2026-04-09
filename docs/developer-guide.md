# 开发者指南

> 了解 Hermes Toolkit 的架构，方便扩展和贡献代码。

---

## 目录

1. [项目架构](#项目架构)
2. [目录结构](#目录结构)
3. [核心模块](#核心模块)
4. [UI 模块](#ui模块)
5. [多语言](#多语言)
6. [添加新功能](#添加新功能)
7. [代码规范](#代码规范)
8. [测试](#测试)
9. [提交代码](#提交代码)

---

## 项目架构

Hermes Toolkit 采用 **分层架构**：

```
┌─────────────────────────────────────┐
│         UI Layer (TkInter)          │  ← 用户界面
├─────────────────────────────────────┤
│       Business Logic Layer           │  ← 业务逻辑
│   (Skills, Memory, Cron, Agents)    │
├─────────────────────────────────────┤
│         Core Layer                   │  ← 核心功能
│   (Config, Hermes IPC, Utils)        │
├─────────────────────────────────────┤
│         i18n Layer                   │  ← 国际化
└─────────────────────────────────────┘
```

**技术栈：**
- **GUI**: TkInter（Python 内置，零依赖）
- **数据存储**: JSON / YAML 文件
- **加密**: cryptography (Fernet)
- **国际化**: 自定义 JSON-based i18n

---

## 目录结构

```
hermes-toolkit/
├── src/
│   ├── main.py              # 程序入口
│   │
│   ├── i18n/               # 国际化
│   │   ├── __init__.py
│   │   └── manager.py       # I18nManager 类
│   │
│   ├── ui/                  # 界面层
│   │   ├── __init__.py
│   │   ├── app.py           # 主窗口（HermesApp）
│   │   ├── sidebar.py        # 侧边栏
│   │   ├── skills.py         # Skills 管理页面
│   │   ├── memory.py        # Memory 管理页面
│   │   ├── conversation.py  # 会话历史页面
│   │   ├── cron.py          # 定时任务页面
│   │   ├── agents.py        # 智能体配置页面
│   │   ├── system.py        # 系统状态页面
│   │   └── settings.py      # 设置页面
│   │
│   ├── core/                 # 核心业务层
│   │   ├── __init__.py
│   │   ├── config.py         # 配置管理（ConfigManager）
│   │   ├── skills.py         # Skills 文件操作（SkillsManager）
│   │   ├── memory.py        # Memory 持久化（MemoryManager）
│   │   ├── cron.py          # Cron 任务管理（CronManager）
│   │   └── hermes.py        # Hermes IPC（HermesClient）
│   │
│   └── utils/               # 工具函数
│       ├── __init__.py
│       ├── logger.py         # 日志工具
│       └── helpers.py        # 辅助函数
│
├── locales/                  # 语言资源文件
│   ├── zh_CN.json
│   ├── en_US.json
│   ├── ja_JP.json
│   └── zh_TW.json
│
└── docs/                     # 文档
```

---

## 核心模块

### ConfigManager

配置管理，负责加载和保存应用配置。

```python
from src.core import ConfigManager

config = ConfigManager()

# 获取设置
settings = config.get_settings()

# 获取单个设置
language = config.get_setting('settings.language', 'zh_CN')

# 保存设置
config.save_settings({'theme': 'dark'})

# API 密钥加密
encrypted = config.encrypt_secret('my-api-key')
decrypted = config.decrypt_secret(encrypted)
```

### SkillsManager

Skills 文件管理，负责 Skills 的增删改查。

```python
from src.core import SkillsManager

manager = SkillsManager(skills_dir='~/.hermes/skills')

# 列出所有 Skills
skills = manager.list_skills()

# 按分类列出
skills = manager.list_skills(category='mlops')

# 搜索 Skills
results = manager.search_skills('docker')

# 创建 Skill
manager.create_skill(
    name='my-skill',
    title='My Skill',
    category='general',
    content='# My Skill\n\nDescription...',
    description='A test skill',
    tags=['test'],
)

# 更新 Skill
skill = manager.get_skill('my-skill', 'general')
skill.content = 'New content'
manager.update_skill(skill)

# 删除 Skill
manager.delete_skill('my-skill', 'general')
```

### MemoryManager

记忆管理，负责 Memory 条目的持久化。

```python
from src.core import MemoryManager

manager = MemoryManager(memory_file='~/.hermes/memory.json')

# 列出所有记忆
entries = manager.list_entries()

# 按类型筛选
user_entries = manager.list_entries(target='user')

# 添加记忆
entry = manager.add_entry('User prefers dark theme', target='user')

# 更新记忆
manager.update_entry(entry.id, 'Updated content')

# 删除记忆
manager.delete_entry(entry.id)

# 搜索记忆
results = manager.search('dark theme')
```

### CronManager

定时任务管理。

```python
from src.core import CronManager

manager = CronManager(
    cron_file='~/.hermes/crontab.json',
    logs_dir='~/.hermes/cron_logs'
)

# 列出任务
jobs = manager.list_jobs()

# 创建任务
job = manager.create_job(
    name='Daily Report',
    prompt='Generate a daily report',
    schedule='0 9 * * *',
    deliver='telegram',
)

# 暂停/启用
manager.pause_job(job.job_id)
manager.resume_job(job.job_id)

# 删除任务
manager.delete_job(job.job_id)

# 查看执行日志
logs = manager.get_job_logs(job.job_id)
```

### HermesClient

与 Hermes Agent 通信。

```python
from src.core import HermesClient

client = HermesClient()

# 检查运行状态
if client.is_running():
    print('Hermes is running')

# 获取状态详情
status = client.get_status()
print(f"Version: {status.version}")
print(f"Platforms: {status.connected_platforms}")

# 重载配置
client.reload_config()

# 重启
client.restart()

# 执行 Skill
result = client.execute_skill('my-skill', {'param': 'value'})
```

---

## UI 模块

每个 UI 模块都是一个独立的类，遵循相同的模式：

```python
class MyModule:
    def __init__(self, parent, app, i18n, some_manager):
        self.parent = parent      # 父容器
        self.app = app           # 应用实例
        self.i18n = i18n         # 国际化管理器
        self.manager = some_manager

        self._create_widgets()   # 创建组件
        self._load_data()        # 加载数据

    def _create_widgets(self):
        """创建所有 UI 组件"""
        colors = self.app.colors  # 获取当前主题颜色
        # ... 创建 UI ...

    def _load_data(self):
        """从 manager 加载数据并更新 UI"""
        # ...
```

### 在 app.py 中注册新页面

```python
# 在 src/ui/app.py 中

def _show_view(self, view_id):
    if view_id == 'my_module':
        from . import my_module
        my_module.MyModuleView(self.content_inner, self, self.i18n, self.my_manager)
```

---

## 多语言

### 添加新翻译

1. 在 `locales/` 目录创建新的语言文件，如 `de_DE.json`
2. 参考现有语言文件的结构
3. 在 `src/i18n/manager.py` 的 `SUPPORTED_LANGUAGES` 字典中添加新语言

### 使用翻译

```python
from src.i18n import get_i18n

i18n = get_i18n()

# 获取翻译
title = i18n.t('skills.title')

# 翻译函数
from src.i18n.manager import _
label = _('common.save')

# 带参数翻译
msg = _('skills.count', count=32)
```

### 翻译 JSON 结构

```json
{
  "section": {
    "key": "翻译文本",
    "key_with_param": "参数: {count}"
  }
}
```

---

## 添加新功能

### 步骤 1：定义数据模型

在 `src/core/` 中添加新的 manager 类：

```python
# src/core/mymodule.py
class MyData:
    def __init__(self, **kwargs):
        self.field1 = kwargs.get('field1', '')
        # ...

    def to_dict(self):
        return {...}

    @classmethod
    def from_dict(cls, data):
        return cls(**data)
```

### 步骤 2：创建 Manager

```python
# src/core/mymodule.py
class MyModuleManager:
    def __init__(self, data_file):
        self._data_file = Path(data_file)
        self._load()

    def _load(self):
        # 从文件加载

    def _save(self):
        # 保存到文件

    def list(self):
        return self._data

    def create(self, data):
        # 创建新条目
        pass
```

### 步骤 3：创建 UI

在 `src/ui/` 中添加新的视图文件：

```python
# src/ui/mymodule.py
class MyModuleView:
    def __init__(self, parent, app, i18n, manager):
        self.parent = parent
        self.app = app
        self.i18n = i18n
        self.manager = manager

        self._create_widgets()
        self._load_data()
```

### 步骤 4：注册视图

在 `app.py` 的 `_show_view` 方法中添加：

```python
elif view_id == 'my_module':
    from . import mymodule
    mymodule.MyModuleView(self.content_inner, self, self.i18n, self.my_manager)
```

在 `sidebar_items` 中添加导航项：

```python
self.sidebar_items = [
    # ... existing items ...
    ('my_module', '🔧', _('my_module.title')),
]
```

### 步骤 5：添加翻译

在 `locales/zh_CN.json` 等文件中添加翻译：

```json
{
  "my_module": {
    "title": "我的模块",
    "new": "新建",
    "edit": "编辑"
  }
}
```

---

## 代码规范

### Python 代码风格

- 遵循 [PEP 8](https://pep8.org/)
- 使用 4 空格缩进
- 类名使用 PascalCase
- 函数和变量使用 snake_case
- 私有方法和属性以 `_` 开头

### 文档字符串

```python
def my_function(arg1: str, arg2: int) -> bool:
    """
    函数简短描述。

    Args:
        arg1: 参数1的说明
        arg2: 参数2的说明

    Returns:
        返回值说明

    Raises:
        ValueError: 什么时候抛出
    """
    pass
```

### 导入顺序

1. 标准库
2. 第三方库
3. 本项目模块
4. 使用绝对导入

```python
import os
import sys
from pathlib import Path

import yaml
from cryptography.fernet import Fernet

from src.core import ConfigManager
```

---

## 测试

### 运行测试

```bash
# 后续版本将添加测试框架
pytest tests/
```

### 添加测试

```python
# tests/test_skills.py
import pytest
from src.core import SkillsManager

def test_list_skills():
    manager = SkillsManager()
    skills = manager.list_skills()
    assert isinstance(skills, list)
```

---

## 提交代码

### Git 工作流

1. 创建功能分支
   ```bash
   git checkout -b feature/my-new-feature
   ```

2. 提交代码
   ```bash
   git add .
   git commit -m "feat: add my new feature"
   ```

3. 推送分支
   ```bash
   git push origin feature/my-new-feature
   ```

4. 创建 Pull Request

### Commit 消息规范

参考 [Conventional Commits](https://www.conventionalcommits.org/)：

- `feat:` 新功能
- `fix:` 修复 bug
- `docs:` 文档更新
- `style:` 代码格式（不影响功能）
- `refactor:` 重构
- `perf:` 性能优化
- `test:` 测试相关
- `chore:` 构建/工具相关

### Pull Request 模板

```markdown
## 描述
<!-- 简要描述这个 PR 做了什么 -->

## 类型
- [ ] 新功能 (feat)
- [ ] 修复 bug (fix)
- [ ] 文档更新 (docs)
- [ ] 其他 (chore)

## 截图（如果涉及 UI）
<!-- 添加 UI 相关的截图 -->

## 检查清单
- [ ] 代码通过现有测试
- [ ] 添加了必要的测试
- [ ] 文档已更新（如适用）
- [ ] 翻译文件已更新（如涉及 UI 文本）
```

---

*最后更新：2026-04-09*
