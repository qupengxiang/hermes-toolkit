# Hermes Toolkit

> 🛠️ 为 Hermes AI 助手打造的桌面可视化控制台 — 管理 Skills、Memory、会话、定时任务、智能体配置，一个界面全搞定。

<p align="center">
  <img src="https://img.shields.io/badge/Python-3.10+-blue.svg" alt="Python">
  <img src="https://img.shields.io/badge/License-MIT-yellow.svg" alt="License">
  <img src="https://img.shields.io/github/stars/qupengxiang/hermes-toolkit?style=flat" alt="Stars">
  <img src="https://img.shields.io/github/forks/qupengxiang/hermes-toolkit?style=flat" alt="Forks">
  <img src="https://img.shields.io/github/v/release/qupengxiang/hermes-toolkit" alt="Release">
</p>

<p align="center">
  <a href="https://github.com/qupengxiang/hermes-toolkit/releases">📦 下载安装</a>
  ·
  <a href="https://github.com/qupengxiang/hermes-toolkit/wiki">📖 文档</a>
  ·
  <a href="https://github.com/qupengxiang/hermes-toolkit/issues">🐛 问题反馈</a>
  ·
  <a href="https://github.com/qupengxiang/hermes-toolkit/discussions">💬 讨论</a>
</p>

---

## ✨ 功能亮点

| 模块 | 功能 |
|------|------|
| 📁 **Skills 管理** | 可视化浏览 / 创建 / 编辑 / 导入导出，支持分类标签和关键词搜索 |
| 🧠 **Memory 管理** | 查看、添加、编辑、删除 Hermes 的持久记忆，支持分类筛选 |
| 💬 **会话历史** | 搜索历史对话、收藏重要会话、随时继续之前的对话 |
| ⏰ **定时任务** | 图形化创建和管理 Cron 任务，支持暂停 / 启用 / 执行日志 |
| 🤖 **智能体配置** | 管理多个 AI 模型接入、API 密钥（加密存储）、场景预设一键切换 |
| 🔌 **系统状态** | 实时查看 Hermes 运行状态、MCP 服务、平台连接情况 |
| ⚙️ **设置中心** | 深色 / 浅色主题、4 种语言实时切换、路径自定义 |

---

## 🖥️ 界面预览

```
┌─────────────────────────────────────────────────────────────────┐
│  🔧 Hermes Toolkit                      🌐 中文  ⚙️ 设置   [?]   │
├────────────┬────────────────────────────────────────────────────┤
│            │                                                     │
│  📁 Skills │   ┌─────────────────────────────────────────────┐  │
│  🧠 记忆   │   │  Skills 管理                    [+ 新建]     │  │
│  💬 会话   │   ├─────────────────────────────────────────────┤  │
│  ⏰ 定时   │   │  🔍 搜索 Skills...        [分类 ▾] [全部]   │  │
│  🤖 智能体 │   ├──────────────┬──────────────────────────────┤  │
│  🔌 系统   │   │ 📁 Skills    │  📄 apple-notes              │  │
│  ⚙️ 设置   │   │  ├─ general  │  ─────────────────────────   │  │
│            │   │  ├─ devops   │  title: Apple Notes          │  │
│            │   │  ├─ mlops    │  category: apple              │  │
│            │   │  └─ creative │  tags: [apple, notes, macos] │  │
│            │   │              │                               │  │
│            │   │              │  # Apple Notes                 │  │
│            │   │              │  Manage Apple Notes via...     │  │
│            │   │              │                               │  │
│            │   │              │          [编辑]  [删除]        │  │
│            │   └──────────────┴──────────────────────────────┘  │
├────────────┴────────────────────────────────────────────────────┤
│  🔴 Hermes 未运行    │  📁 0 Skills  │  🐍 v0.1.0               │
└─────────────────────────────────────────────────────────────────┘
```

---

## 🌐 多语言

| 语言 | 代码 | 状态 |
|------|------|------|
| 🇨🇳 简体中文 | `zh_CN` | ✅ 默认 |
| 🇺🇸 English | `en_US` | ✅ |
| 🇯🇵 日本語 | `ja_JP` | ✅ |
| 🇹🇼 繁體中文 | `zh_TW` | ✅ |

> 语言切换即时生效，无需重启。

---

## 🚀 快速开始

### 环境要求

- **Python** 3.10 或更高版本
- **Hermes AI 助手**（本地已安装并运行）

### 安装

```bash
# 克隆项目
git clone https://github.com/qupengxiang/hermes-toolkit.git
cd hermes-toolkit

# 安装依赖
pip install -r requirements.txt

# 启动
python src/main.py
```

### macOS / Linux 一键启动

```bash
# 确保 Python 3.10+ 已安装后
python3 src/main.py
```

---

## 📂 项目结构

```
hermes-toolkit/
├── SPEC.md              # 完整功能规格说明书
├── README.md            # 本文件
├── CHANGELOG.md         # 版本变更记录
├── LICENSE              # MIT 许可证
├── requirements.txt     # Python 依赖
│
├── locales/              # 多语言资源（4种语言）
│   ├── zh_CN.json
│   ├── en_US.json
│   ├── ja_JP.json
│   └── zh_TW.json
│
└── src/                  # 源代码
    ├── main.py           # 程序入口
    ├── i18n/             # 多语言引擎（支持运行时切换）
    ├── ui/                # TkInter 图形界面
    │   ├── app.py         # 主窗口
    │   ├── skills.py      # Skills 管理页面
    │   ├── memory.py      # Memory 管理页面
    │   ├── conversation.py # 会话历史页面
    │   ├── cron.py        # 定时任务页面
    │   ├── agents.py      # 智能体配置页面
    │   ├── system.py      # 系统状态页面
    │   └── settings.py    # 设置页面
    ├── core/              # 核心业务逻辑
    │   ├── config.py      # 配置管理（加密存储）
    │   ├── skills.py      # Skills 文件操作
    │   ├── memory.py      # Memory 持久化
    │   ├── cron.py       # Cron 任务管理
    │   └── hermes.py     # Hermes Agent IPC
    └── utils/             # 工具函数
        ├── logger.py      # 日志
        └── helpers.py     # 辅助函数
```

---

## 📋 文档

- [📖 用户手册](docs/user-guide.md) — 详细功能使用说明
- [👨‍💻 开发者指南](docs/developer-guide.md) — 如何扩展和贡献代码
- [🌐 多语言指南](docs/i18n-guide.md) — 如何添加新语言支持
- [📐 规格说明书](SPEC.md) — 完整功能规格和实现细节

---

## 🤝 贡献

欢迎各种形式的贡献！

- 🐛 提交 [Issue](https://github.com/qupengxiang/hermes-toolkit/issues) 报告 Bug
- 💡 提交 [Feature Request](https://github.com/qupengxiang/hermes-toolkit/issues/new) 建议新功能
- 🔧 提交 [Pull Request](https://github.com/qupengxiang/hermes-toolkit/pulls) 贡献代码
- 🌐 提交新语言翻译（参考 [i18n 指南](docs/i18n-guide.md)）

---

## 📄 许可证

本项目基于 [MIT License](LICENSE) 开源。

---

## 🔄 版本历史

| 版本 | 日期 | 更新内容 |
|------|------|---------|
| v0.1.0 | 2026-04-09 | 首次发布，包含完整 UI 框架和 7 大功能模块 |

详见 [CHANGELOG.md](CHANGELOG.md)

---

<p align="center">
  如果这个项目对你有帮助，欢迎 ⭐ Star！
</p>
