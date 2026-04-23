# Code Agent - 代码助手

基于 Ollama 的本地代码助手工具，支持代码文件管理、Shell 命令执行、GitHub 项目搜索、网页内容抓取和待办事项管理。

## ✨ 功能特性

### 📁 文件管理
- **读取文件** - 安全读取本地文件内容
- **写入文件** - 创建或覆盖文件，自动创建父目录
- **路径安全** - 防止目录遍历攻击，仅限工作目录内操作

### 🖥️ Shell 命令执行
- 执行任意 Shell 命令
- 显示执行状态和完整输出
- 支持超时保护（5 分钟）

### 🔍 GitHub 集成
- **项目搜索** - 通过 GitHub API 按关键词和编程语言搜索热门项目
- **仓库详情** - 获取指定仓库的完整信息和 README 内容
- 显示 Stars、Forks、编程语言等信息

### 🌐 网页内容抓取
- 自动提取网页纯文本内容
- 移除脚本、样式、导航等无关元素
- 内容过长自动截断

### ✅ 待办事项管理
- 三种状态：待完成 ⬜、进行中 🔄、已完成 ✅
- 最多支持 5 个任务
- 限制同时只有 1 个进行中的任务
- 每次交互自动显示当前任务列表

### 💾 智能上下文管理
- **轻量级压缩** - 旧的工具调用结果替换为占位符
- **自动摘要** - token 超过阈值时自动压缩对话
- **对话持久化** - 完整对话历史保存到 `transcripts/` 目录
- **历史限制** - 最多保留最近 16 条消息

## 🚀 快速开始

### 环境要求
- Python 3.8+
- Ollama 服务
- 至少 8GB 内存（推荐 16GB）

### 安装步骤

1. **安装 Ollama**
```bash
# macOS
brew install ollama

# Linux
curl -fsSL https://ollama.com/install.sh | sh

# Windows
# 访问 https://ollama.ai/ 下载安装
```

2. **拉取模型**
```bash
ollama pull qwen3.5:9b
```

3. **安装 Python 依赖**
```bash
pip install requests beautifulsoup4
```

4. **运行 Agent**
```bash
python agent.py
```

## 📖 使用说明

### 基本命令
- 输入问题或任务描述直接交互
- 输入 `exit`、`quit` 或 `q` 退出程序
- 按 `Ctrl+C` 或 `Ctrl+D` 也可以退出

### 可用工具

| 工具 | 功能 | 参数 |
|------|------|------|
| `todo_add` | 添加新任务 | text: 任务描述 |
| `todo_change_status` | 更改任务状态 | item_id: 任务ID, status: pending/in_progress/done |
| `todo_delete` | 删除任务 | item_id: 任务ID |
| `todo_list` | 查看任务列表 | 无参数 |
| `search_github_repos` | 搜索 GitHub 项目 | keyword: 关键词, language: 编程语言(可选) |
| `get_github_repo_info` | 获取仓库详情 | repo_url: 仓库URL |
| `bash` | 执行 Shell 命令 | command: 命令字符串 |
| `read_file` | 读取文件 | file_path: 文件路径 |
| `write_file` | 写入文件 | file_path: 文件路径, content: 内容 |
| `fetch_page` | 获取网页内容 | url: 网页URL |

### 常用示例

**搜索 GitHub AI 项目**
```
user: 帮我搜索一下 GitHub 上热门的 Python AI 项目
```

**查看当前目录**
```
user: 列出当前目录的文件
```

**读取文件**
```
user: 读取 agent.py 文件的内容
```

**添加待办**
```
user: 添加任务：优化代码的错误处理
```

## 🔧 配置说明

### 环境变量
- `OLLAMA_HOST` - Ollama 服务地址（默认: http://localhost:11434）

### 可配置参数
在 `agent.py` 中可以调整以下参数：

| 参数 | 默认值 | 说明 |
|------|--------|------|
| `DEFAULT_MODEL` | qwen3.5:9b | 使用的模型名称 |
| `MAX_ITERATIONS` | 20 | 最大思考迭代次数 |
| `MAX_HISTORY` | 16 | 保留对话历史数量 |
| `TOKEN_THRESHOLD` | 8000 | 触发自动压缩的 token 阈值 |
| `KEEP_RECENT_TOOLS` | 3 | 保留完整结果的工具调用数量 |

## 📊 项目结构

```
codeagent/
├── agent.py              # 主程序文件
├── README.md            # 中文文档
├── README_EN.md         # 英文文档
├── requirements.txt     # Python 依赖
└── transcripts/         # 对话历史目录（自动创建）
    └── transcript_*.jsonl
```

## 🛡️ 安全特性

1. **路径安全** - 所有文件操作经过安全检查，防止目录遍历
2. **命令超时** - Shell 命令 5 分钟超时保护
3. **网络超时** - API 调用超时保护
4. **内容截断** - 大文件和网页内容自动截断

## 🤝 贡献指南

欢迎提交 Issue 和 Pull Request！

1. Fork 本项目
2. 创建特性分支 (`git checkout -b feature/AmazingFeature`)
3. 提交更改 (`git commit -m 'Add some AmazingFeature'`)
4. 推送到分支 (`git push origin feature/AmazingFeature`)
5. 打开 Pull Request

## 📝 开发计划

- [ ] 支持多模型切换
- [ ] 添加文件差异对比
- [ ] 支持流式输出
- [ ] 添加更多工具（数据库、Git 操作等）
- [ ] 支持多会话管理
- [ ] 对话历史搜索和导出

## 📄 许可证

本项目采用 MIT 许可证 - 详见 [LICENSE](LICENSE) 文件。

## 📞 联系方式

- 项目主页: [GitHub](https://github.com/yourusername/codeagent)
- 问题反馈: [Issues](https://github.com/yourusername/codeagent/issues)

## ⚠️ 注意事项

- 这是一个本地运行的工具，请谨慎执行 Shell 命令
- 所有文件操作仅限于当前工作目录及其子目录
- 建议在 Git 仓库中使用，以便可以回滚文件更改
- 大文件读取可能会消耗较多 token，请谨慎使用
