# Hermes Toolkit — 完整规格说明书

> Hermes 桌面管理工具，为 AI 助手提供可视化控制台。

---

## 1. 项目概述

**项目名称:** Hermes Toolkit
**项目类型:** 桌面应用程序（Python + TkInter）
**核心功能:** 为 Hermes AI 助手提供 Skills 管理、Memory 管理、对话历史、定时任务、智能体配置、系统状态等功能的可视化界面。
**目标用户:** 使用 Hermes AI 助手的高级用户和开发者。

---

## 2. 技术规格

### 2.1 技术栈

| 层级 | 技术选型 |
|------|---------|
| GUI 框架 | Python 3.10+ / TkInter（内置库，零依赖） |
| 数据存储 | JSON / YAML 配置文件 |
| 多语言 | JSON-based i18n（支持运行时切换） |
| 图标资源 | 内置 PhotoImage 或外部 PNG/ICO |
| 日志 | Python logging 模块 |
| IPC | Hermes Agent 原生接口（REST/CLI） |

### 2.2 目录结构

```
hermes-toolkit/
├── SPEC.md
├── README.md
├── CHANGELOG.md
├── LICENSE
├── docs/                      # 文档
│   ├── user-guide.md
│   ├── developer-guide.md
│   └── i18n-guide.md
├── locales/                   # 多语言资源
│   ├── zh_CN.json
│   ├── en_US.json
│   ├── ja_JP.json
│   └── zh_TW.json
├── assets/                    # 静态资源
│   └── icons/
├── src/
│   ├── main.py               # 程序入口
│   ├── ui/
│   │   ├── __init__.py
│   │   ├── app.py            # 主窗口
│   │   ├── sidebar.py        # 侧边栏
│   │   ├── skills.py         # Skills 管理
│   │   ├── memory.py         # Memory 管理
│   │   ├── conversation.py   # 会话历史
│   │   ├── cron.py           # 定时任务
│   │   ├── agents.py         # 智能体配置
│   │   ├── system.py         # 系统状态
│   │   └── settings.py       # 设置页面
│   ├── i18n/
│   │   ├── __init__.py
│   │   ├── manager.py        # 多语言管理器
│   │   └── locales/
│   │       ├── zh_CN.json
│   │       ├── en_US.json
│   │       ├── ja_JP.json
│   │       └── zh_TW.json
│   ├── core/
│   │   ├── __init__.py
│   │   ├── config.py         # 配置读写
│   │   ├── skills.py         # Skills 底层操作
│   │   ├── memory.py         # Memory 底层操作
│   │   ├── cron.py           # Cron 任务操作
│   │   └── hermes.py        # Hermes Agent IPC
│   └── utils/
│       ├── __init__.py
│       ├── logger.py
│       └── helpers.py
└── tests/
    ├── test_skills.py
    ├── test_memory.py
    └── test_i18n.py
```

---

## 3. 功能模块详细规格

### 3.1 Skills 管理

#### 功能列表
- **技能浏览** — 左侧树形列表，按分类分组显示所有 Skills
- **搜索过滤** — 实时按名称/内容关键词过滤
- **内容预览** — 右侧 Markdown 渲染预览
- **创建技能** — 提供标准化模板（SKILL.md 格式）
- **编辑技能** — 内置 Markdown 编辑器，语法高亮
- **删除技能** — 二次确认后删除
- **标签管理** — 给技能打标签/分类
- **导入/导出** — .md 文件批量导入，单个技能导出

#### 数据模型（Skill）
```yaml
name: skill-name          # 唯一标识（文件名）
title: "技能显示名称"
category: "category-name"
description: "简短描述"
tags: [tag1, tag2]
content: |                # SKILL.md 完整内容
  # Skill Name
  ...
author: "作者名"
version: "1.0.0"
created_at: "ISO8601"
updated_at: "ISO8601"
```

#### 存储路径
- Skills 根目录: `~/.hermes/skills/`
- 每个 Skill: `~/.hermes/skills/<category>/<name>.md`

---

### 3.2 Memory 管理

#### 功能列表
- **查看记忆** — 以卡片形式展示当前 Memory 条目
- **添加记忆** — 手动新增用户信息条目
- **编辑记忆** — 修改现有记忆内容
- **删除记忆** — 移除过期/错误记忆
- **记忆分类** — 按 target（user/memory）分类查看

#### 数据模型（Memory Entry）
```json
{
  "id": "uuid",
  "target": "user|memory",
  "content": "记忆内容",
  "created_at": "ISO8601",
  "updated_at": "ISO8601"
}
```

#### 存储路径
- Memory 文件: `~/.hermes/memory.json`

---

### 3.3 对话 & 会话

#### 功能列表
- **历史记录** — 按时间倒序展示所有对话记录
- **搜索历史** — 按关键词搜索历史消息
- **收藏对话** — 标记重要对话方便回溯
- **继续对话** — 选中历史会话后新建 Tab 继续
- **会话详情** — 展开查看完整对话内容

#### 数据模型（Session）
```json
{
  "id": "uuid",
  "title": "会话标题（自动生成或用户命名）",
  "messages": [
    {
      "role": "user|assistant|system",
      "content": "消息内容",
      "timestamp": "ISO8601"
    }
  ],
  "created_at": "ISO8601",
  "updated_at": "ISO8601",
  "favorite": false
}
```

#### 存储路径
- 会话记录: `~/.hermes/sessions/`

---

### 3.4 定时任务（Cron）

#### 功能列表
- **任务列表** — 展示所有定时任务及状态
- **创建任务** — 表单填写任务名称、触发时间、目标、prompt
- **编辑任务** — 修改现有任务参数
- **删除任务** — 移除任务（带确认）
- **启用/暂停** — 一键切换任务状态
- **执行日志** — 展示每次运行的输入输出和结果

#### 数据模型（Cron Job）
```json
{
  "job_id": "uuid",
  "name": "任务名称",
  "schedule": "cron表达式 或 自然语言如 'every 2h'",
  "prompt": "任务执行的 prompt",
  "deliver": "origin|local|telegram|...",
  "skills": ["skill-name"],
  "status": "active|paused",
  "model": {
    "provider": "openrouter",
    "model": "anthropic/claude-sonnet-4"
  },
  "created_at": "ISO8601",
  "last_run": "ISO8601",
  "next_run": "ISO8601"
}
```

#### 存储路径
- Cron 配置: `~/.hermes/crontab.json`

---

### 3.5 智能体 & API 配置

#### 功能列表
- **智能体列表** — 展示所有已配置的 AI 智能体
- **添加智能体** — 表单填写名称、类型、API Endpoint、模型
- **编辑配置** — 修改智能体参数
- **删除智能体** — 移除智能体（带确认）
- **默认切换** — 设为当前默认智能体
- **API 密钥管理** — 添加/编辑/删除各平台 API Key（加密）
- **Endpoint 配置** — 自定义 API 接入地址
- **模型选择** — 为不同任务预设使用模型
- **用量统计** — API 调用次数/消耗量
- **请求限流** — QPS/每日上限配置
- **场景预设** — 保存多套配置方案
- **System Prompt** — 定制系统提示词
- **工具权限** — 开启/关闭特定工具能力

#### 数据模型（Agent）
```yaml
agents:
  - id: "agent-uuid"
    name: "Claude"
    provider: "anthropic"
    endpoint: "https://api.anthropic.com"
    api_key: "encrypted:xxx"
    models:
      - "claude-sonnet-4-20250514"
      - "claude-opus-4-5"
    default_model: "claude-sonnet-4-20250514"
    system_prompt: "You are a helpful assistant."
    tool_permissions:
      execute_code: true
      browser: true
      file_write: false
    is_default: true
    status: "active"

api_config:
  openai:
    api_key: "encrypted:xxx"
    endpoint: "https://api.openai.com/v1"
    organization: ""
  anthropic:
    api_key: "encrypted:xxx"
    endpoint: "https://api.anthropic.com"
  openrouter:
    api_key: "encrypted:xxx"
    endpoint: "https://openrouter.ai/api/v1"

presets:
  - name: "工作模式"
    is_active: true
    agent_id: "agent-uuid"
    model: "claude-sonnet-4-20250514"
    system_prompt: "..."

rate_limits:
  openai:
    qps: 10
    daily_limit: 10000
  anthropic:
    qps: 5
    daily_limit: 5000
```

#### 存储路径
- 智能体配置: `~/.hermes/config/agents.yaml`
- API 密钥: `~/.hermes/config/secrets.yaml`（0600 权限）

---

### 3.6 工具 & 系统状态

#### 功能列表
- **MCP 服务** — 查看已连接的 MCP 服务状态、可用工具列表
- **平台连接** — Telegram 等已连接平台的状态
- **快捷命令** — 一键触发：重启 Hermes、重新加载配置、同步数据等
- **系统信息** — 显示 Hermes 版本、运行时间、系统资源
- **健康检查** — 一键诊断连接状态

---

### 3.7 设置

#### 功能列表
- **外观主题** — 深色/浅色模式切换
- **语言切换** — 简体中文 / English / 日本語 / 繁體中文
- **通知偏好** — 任务完成/失败通知开关
- **路径配置** — 修改 Skills/Memory/Sessions 目录路径
- **日志级别** — DEBUG / INFO / WARNING / ERROR
- **数据备份** — 一键备份所有配置和数据
- **关于** — 版本信息、许可证、帮助链接

---

## 4. 多语言（i18n）规格

### 4.1 支持语言

| 语言代码 | 语言名称 | 状态 |
|---------|---------|------|
| zh_CN | 简体中文 | ✅ 默认 |
| en_US | English | ✅ |
| ja_JP | 日本語 | ✅ |
| zh_TW | 繁體中文 | ✅ |

### 4.2 i18n 实现

- 基于 JSON 文件存储翻译资源
- 支持运行时动态切换语言，无需重启
- 所有 UI 文本均通过翻译 key 引用
- 翻译文件按语言代码命名: `locales/<lang>.json`

### 4.3 翻译 JSON 结构

```json
{
  "app": {
    "name": "Hermes Toolkit",
    "version": "版本"
  },
  "menu": {
    "skills": "Skills 管理",
    "memory": "记忆管理",
    "conversation": "会话历史",
    "cron": "定时任务",
    "agents": "智能体配置",
    "system": "系统状态",
    "settings": "设置"
  },
  "skills": {
    "title": "Skills 管理",
    "search_placeholder": "搜索 Skills...",
    "new": "新建 Skill",
    "edit": "编辑",
    "delete": "删除",
    "import": "导入",
    "export": "导出",
    "confirm_delete": "确定要删除这个 Skill 吗？",
    "category": "分类",
    "tags": "标签",
    "description": "描述"
  },
  "common": {
    "save": "保存",
    "cancel": "取消",
    "confirm": "确认",
    "delete": "删除",
    "edit": "编辑",
    "create": "创建",
    "search": "搜索",
    "loading": "加载中...",
    "success": "操作成功",
    "error": "操作失败",
    "no_data": "暂无数据",
    "actions": "操作"
  }
}
```

---

## 5. 用户界面规格

### 5.1 主窗口布局

```
┌──────────────────────────────────────────────────────────┐
│  🔧 Hermes Toolkit              [🌐 语言] [⚙️ 设置] [?]   │
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

### 5.2 窗口规格

- **默认尺寸:** 1200 × 800 像素
- **最小尺寸:** 900 × 600 像素
- **窗口标题:** "Hermes Toolkit"
- **图标:** 使用内置默认图标

---

## 6. 数据安全规格

- API 密钥加密存储（Fernet 对称加密）
- 敏感配置文件权限: `0600`
- 支持数据导出时脱敏处理
- 备份文件支持加密压缩

---

## 7. 验收标准

### 7.1 功能验收

- [ ] Skills 增删改查、导入导出全部正常
- [ ] Memory 查看、添加、编辑、删除全部正常
- [ ] 会话历史搜索、收藏、继续对话全部正常
- [ ] Cron 任务创建、启用/暂停、执行日志全部正常
- [ ] 智能体添加、编辑、删除、默认切换全部正常
- [ ] API 配置保存、加密、加载全部正常
- [ ] 语言切换实时生效，无需重启
- [ ] 主题切换（深色/浅色）实时生效
- [ ] 所有模块数据持久化正确

### 7.2 视觉验收

- [ ] 侧边栏导航高亮当前选中项
- [ ] 所有按钮有 Hover/Active 状态反馈
- [ ] 表格列表支持排序和分页
- [ ] 表单验证错误信息友好提示
- [ ] 加载状态有 Loading 动画或提示
- [ ] 深色/浅色主题配色协调

### 7.3 文档验收

- [ ] README.md 包含完整安装和使用说明
- [ ] SPEC.md 包含所有功能详细规格
- [ ] docs/user-guide.md 用户操作手册
- [ ] docs/developer-guide.md 开发者指南
- [ ] docs/i18n-guide.md 多语言贡献指南
- [ ] CHANGELOG.md 记录版本变更

---

## 8. 版本规划

| 版本 | 主要内容 | 状态 |
|------|---------|------|
| v0.1.0 | 基础框架 + Skills 管理 + i18n | 🔨 开发中 |
| v0.2.0 | Memory 管理 + 会话历史 | 📋 计划中 |
| v0.3.0 | Cron 定时任务管理 | 📋 计划中 |
| v0.4.0 | 智能体 & API 配置 | 📋 计划中 |
| v0.5.0 | 系统状态 + 完整集成 | 📋 计划中 |
| v1.0.0 | 首个正式版本发布 | 📋 计划中 |

---

*文档版本: v0.1.0-draft*
*最后更新: 2026-04-09*
