# 多语言指南

> 了解如何为 Hermes Toolkit 添加新的语言支持或更新翻译。

---

## 目录

1. [工作原理](#工作原理)
2. [语言文件结构](#语言文件结构)
3. [添加新语言](#添加新语言)
4. [更新现有翻译](#更新现有翻译)
5. [代码中使用翻译](#代码中使用翻译)
6. [翻译规范](#翻译规范)
7. [常见问题](#常见问题)

---

## 工作原理

Hermes Toolkit 使用自研的 JSON-based 国际化系统，具有以下特点：

- **运行时切换**：语言切换即时生效，无需重启应用
- **层级嵌套**：使用点号（`.`）访问嵌套的翻译键
- **自动回退**：找不到翻译时自动回退到默认语言
- **零依赖**：纯 Python 实现，无第三方 i18n 库依赖

### 核心组件

```
src/i18n/
├── __init__.py
└── manager.py          # I18nManager 类
```

**I18nManager** 是核心类，负责：
- 从 `locales/` 目录加载 JSON 翻译文件
- 根据当前语言查找翻译
- 支持运行时切换语言

---

## 语言文件结构

### 文件位置

```
hermes-toolkit/
├── locales/
│   ├── zh_CN.json      # 简体中文
│   ├── en_US.json      # 英语
│   ├── ja_JP.json      # 日语
│   └── zh_TW.json      # 繁体中文
```

### JSON 结构

```json
{
  "app": {
    "name": "Hermes Toolkit",
    "version": "版本"
  },
  "menu": {
    "skills": "Skills 管理",
    "memory": "记忆管理"
  },
  "common": {
    "save": "保存",
    "cancel": "取消"
  }
}
```

### 命名规范

- 文件名：`{语言代码}.json`
- 语言代码格式：`{语言}_{地区}`，如：
  - `zh_CN` — 简体中文（中国）
  - `en_US` — 英语（美国）
  - `ja_JP` — 日语（日本）
  - `zh_TW` — 繁体中文（台湾）

---

## 添加新语言

### 步骤 1：创建语言文件

在 `locales/` 目录创建新语言文件，如 `de_DE.json`（德语）：

```bash
touch locales/de_DE.json
```

### 步骤 2：编写翻译

复制一份现有语言文件作为基础（如 `en_US.json`），然后逐条翻译：

```json
{
  "app": {
    "name": "Hermes Toolkit",
    "version": "Version"
  },
  "menu": {
    "skills": "Skills-Verwaltung",
    "memory": "Speicherverwaltung",
    "conversation": "Konversationen",
    "cron": "Geplante Aufgaben",
    "agents": "Agenten",
    "system": "System",
    "settings": "Einstellungen"
  },
  "common": {
    "save": "Speichern",
    "cancel": "Abbrechen",
    "confirm": "Bestätigen",
    "delete": "Löschen",
    "edit": "Bearbeiten",
    "create": "Erstellen",
    "search": "Suchen",
    "loading": "Wird geladen...",
    "success": "Erfolg",
    "error": "Fehler"
  }
}
```

### 步骤 3：注册新语言

在 `src/i18n/manager.py` 中更新 `SUPPORTED_LANGUAGES` 字典：

```python
SUPPORTED_LANGUAGES = {
    'zh_CN': '简体中文',
    'en_US': 'English',
    'ja_JP': '日本語',
    'zh_TW': '繁體中文',
    'de_DE': 'Deutsch',  # ← 添加新语言
}
```

### 步骤 4：更新代码（如需要）

在 `src/ui/app.py` 的语言切换菜单中添加新语言选项（如果菜单是动态生成的则无需修改）。

### 步骤 5：测试

```bash
python src/main.py
```

在设置中选择新语言，确认界面正确显示。

---

## 更新现有翻译

### 编辑语言文件

直接编辑 `locales/` 目录下的 JSON 文件：

```bash
# 编辑简体中文
vim locales/zh_CN.json
```

### 保持 JSON 格式正确

更新翻译时注意：
- 确保 JSON 语法正确（引号、逗号等）
- 不要删除未翻译的键（保留英文作为占位）
- 使用适当的嵌套层级

### 验证 JSON 格式

```python
import json

with open('locales/zh_CN.json', 'r', encoding='utf-8') as f:
    data = json.load(f)  # 如果格式错误会抛出异常
    print("JSON 格式正确")
```

---

## 代码中使用翻译

### 获取翻译

```python
# 方法 1：通过 I18nManager 实例
from src.i18n import get_i18n

i18n = get_i18n()
label = i18n.t('menu.skills')  # 返回 "Skills 管理"
```

### 使用翻译函数

```python
# 方法 2：使用 _() 简写函数
from src.i18n import _

label = _('menu.skills')  # 返回 "Skills 管理"
```

### 带参数的翻译

```python
# 在 JSON 中定义：
# "skills": { "count": "共 {count} 个 Skills" }

# 代码中使用：
from src.i18n import get_i18n

i18n = get_i18n()
msg = i18n.t('skills.count')  # "共 {count} 个 Skills"

# 字符串格式化
msg_formatted = msg.format(count=32)  # "共 32 个 Skills"
```

### 在 UI 类中使用

```python
class MyView:
    def __init__(self, parent, app, i18n):
        self.parent = parent
        self.app = app
        self.i18n = i18n

    def create_widgets(self):
        # 使用 self.i18n.t() 获取翻译
        label = tk.Label(
            self.parent,
            text=self.i18n.t('menu.skills')
        )
```

### 在主程序中使用

```python
# src/ui/app.py
from src.i18n import get_i18n, _

i18n = get_i18n()

# 设置语言
i18n.set_language('en_US')

# 获取翻译
title = _('app.name')  # "Hermes Toolkit"
```

---

## 翻译规范

### 命名空间分组

使用有意义的分组，保持键名简洁：

```json
{
  "app": { },           // 应用级信息
  "menu": { },          // 菜单和导航
  "skills": { },        // Skills 模块
  "memory": { },        // Memory 模块
  "conversation": { },  // 会话模块
  "cron": { },          // 定时任务模块
  "agents": { },        // 智能体模块
  "system": { },        // 系统状态模块
  "settings": { },      // 设置模块
  "common": { }          // 通用文本（按钮、提示等）
}
```

### 键命名规范

- 使用小写字母和点号
- 使用蛇底式（snake_case）：如 `confirm_delete`
- 语义化命名：如 `no_skills` 而非 `n1`

### 翻译指南

#### 需要翻译的内容

- 所有 UI 文本（按钮、标签、菜单）
- 提示信息（成功、错误、警告）
- 占位符文本
- 日期格式说明

#### 不需要翻译的内容

- 文件名和路径
- 代码标识符
- URL 和链接
- 技术术语（如 HTTP、API、JSON）

#### 翻译原则

1. **准确**：准确传达原意
2. **自然**：使用目标语言的自然表达方式
3. **一致**：相同术语保持一致翻译
4. **简洁**：保持简洁，避免过长
5. **文化适配**：适当本地化（如日期格式）

#### 示例

| 英文 | 中文 | 日文 |
|------|------|------|
| Save | 保存 | 保存 |
| Cancel | 取消 | キャンセル |
| Confirm delete | 确认删除 | 削除の確認 |
| No data | 暂无数据 | データなし |
| Loading... | 加载中... | 読み込み中... |

---

## 常见问题

### Q: 翻译键找不到会怎样？

找不到翻译时，返回键本身（而不是空字符串）。

```python
result = i18n.t('nonexistent.key')  # 返回 "nonexistent.key"
```

### Q: 如何添加新的翻译键？

1. 在所有语言文件的适当位置添加新键
2. 保持所有语言文件的键一致

### Q: 语言切换为什么不生效？

确保在 `app.py` 中调用了刷新 UI 的方法：

```python
def _change_language(self, lang_code):
    if self.i18n.set_language(lang_code):
        self.config.set_setting('settings.language', lang_code)
        self._apply_theme()
        self._show_view(self.current_view or 'skills')
```

### Q: 如何贡献翻译？

1. Fork 项目
2. 在 `locales/` 目录创建或编辑语言文件
3. 提交 Pull Request
4. 在 PR 中说明：
   - 添加了哪些翻译
   - 更新了哪些翻译
   - 翻译的语言

### Q: 如何测试翻译完整性？

```python
import json
from pathlib import Path

def check_translations():
    locales_dir = Path('locales')
    base_lang = 'en_US'

    with open(locales_dir / f'{base_lang}.json') as f:
        base = json.load(f)

    def get_keys(d, prefix=''):
        keys = []
        for k, v in d.items():
            full_key = f'{prefix}.{k}' if prefix else k
            if isinstance(v, dict):
                keys.extend(get_keys(v, full_key))
            else:
                keys.append(full_key)
        return keys

    base_keys = set(get_keys(base))

    for locale_file in locales_dir.glob('*.json'):
        if locale_file.name == f'{base_lang}.json':
            continue

        with open(locale_file) as f:
            lang = json.load(f)
        lang_keys = set(get_keys(lang))

        missing = base_keys - lang_keys
        if missing:
            print(f"{locale_file.name}: 缺少 {len(missing)} 个翻译")
            for key in sorted(missing)[:5]:
                print(f"  - {key}")
```

---

## 参考

- 项目规格说明书：[SPEC.md](../SPEC.md)
- 开发者指南：[developer-guide.md](developer-guide.md)

---

*最后更新：2026-04-09*
