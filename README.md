# Hermes Toolkit

> 为 Hermes AI 助手打造的桌面可视化控制台

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)
[![Python: 3.10+](https://img.shields.io/badge/Python-3.10+-blue.svg)](https://www.python.org/)

##  功能概览

- 📁 **Skills 管理** — 可视化浏览、创建、编辑、导入导出你的所有 Skills
- 🧠 **Memory 管理** — 查看和管理 Hermes 的持久记忆
- 💬 **会话历史** — 搜索、收藏、继续历史对话
- ⏰ **定时任务** — 可视化管理 Cron 任务，支持启用/暂停/日志查看
- 🤖 **智能体配置** — 管理多个 AI 模型接入、API 密钥、场景预设
- 🔌 **系统状态** — MCP 服务状态、平台连接监控、快捷命令
- ⚙️ **设置中心** — 主题切换、多语言支持、路径配置

##  界面预览

```
┌──────────────────────────────────────────────────────────┐
│  🔧 Hermes Toolkit              [🌐 语言] [⚙️ 设置] [?]  │
├────────────┬─────────────────────────────────────────────┤
│            │                                              │
│  📁 Skills │         主内容区                             │
│  🧠 记忆   │                                             │
│  💬 会话   │   (根据左侧选择动态加载对应模块)              │
│  ⏰ 定时   │                                             │
│  🤖 智能体 │                                             │
│  🔌 系统   │                                             │
│            │                                             │
├────────────┴─────────────────────────────────────────────┤
│  状态栏: 已连接 Telegram │ Skills: 32 │ 🟢 Hermes 运行中 │
└──────────────────────────────────────────────────────────┘
```

##  支持语言

- 🇨🇳 简体中文 (zh_CN)
- 🇺🇸 English (en_US)
- 🇯🇵 日本語 (ja_JP)
- 🇹🇼 繁體中文 (zh_TW)

##  快速开始

###  前置要求

- Python 3.10 或更高版本
- Hermes AI 助手（本地已安装并运行）

###  安装

```bash
# 克隆仓库
git clone https://github.com/yourusername/hermes-toolkit.git
cd hermes-toolkit

# 安装依赖
pip install -r requirements.txt

# 运行
python src/main.py
```

###  使用 Homebrew 安装（macOS）

```bash
brew tap yourusername/tap
brew install hermes-toolkit
```

##  项目结构

```
hermes-toolkit/
├── SPEC.md              # 完整功能规格说明书
├── README.md            # 本文件
├── CHANGELOG.md         # 版本变更记录
├── LICENSE              # MIT 许可证
├── docs/                # 详细文档
│   ├── user-guide.md
│   ├── developer-guide.md
│   └── i18n-guide.md
├── locales/             # 多语言资源
│   ├── zh_CN.json
│   ├── en_US.json
│   ├── ja_JP.json
│   └── zh_TW.json
├── assets/              # 静态资源
└── src/                 # 源代码
    ├── main.py          # 程序入口
    ├── i18n/            # 多语言引擎
    ├── ui/              # 界面模块
    ├── core/            # 核心功能
    └── utils/           # 工具函数
```

##  文档

- [用户手册](docs/user-guide.md) — 详细使用说明
- [开发者指南](docs/developer-guide.md) — 如何扩展和贡献
- [多语言指南](docs/i18n-guide.md) — 如何添加新语言
- [规格说明书](SPEC.md) — 完整功能规格

##  许可证

本项目采用 [MIT License](LICENSE) 开源。

##  贡献

欢迎提交 Issue 和 Pull Request！

##  版本历史

详见 [CHANGELOG.md](CHANGELOG.md)
