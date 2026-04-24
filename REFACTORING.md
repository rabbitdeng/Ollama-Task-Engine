# 代码重构说明

## 概述

本次重构将原来的单文件 `agent.py` 拆分为模块化的项目结构，遵循软件工程最佳实践，实现了低耦合高内聚的架构设计。

## 重构前后对比

### 重构前（单文件结构）
```
codeagent/
└── agent.py (约 1000 行，包含所有功能)
```

### 重构后（模块化结构）
```
codeagent/
├── __init__.py          # 包初始化
├── agent.py             # 主程序入口 (170 行)
├── config.py            # 配置常量模块
├── REFACTORING.md       # 本文档
├── utils/               # 工具包
│   ├── __init__.py
│   └── path.py          # 路径安全功能
├── tools/               # 功能工具包
│   ├── __init__.py
│   ├── shell.py         # Shell 命令执行
│   ├── fileio.py        # 文件读写操作
│   ├── github.py        # GitHub API 集成
│   ├── web.py           # 网页内容抓取
│   └── todo.py          # 待办事项管理
└── core/                # 核心功能包
    ├── __init__.py
    ├── context.py       # 上下文管理（token 估算、对话压缩）
    └── llm.py           # LLM 客户端（Ollama API 调用）
```

## 模块职责划分

### 1. config.py - 配置模块
**职责**: 集中管理所有配置常量和环境变量
**内容**:
- `BASE_DIR`: 工作目录路径
- `DEFAULT_MODEL`: 默认 Ollama 模型
- `OLLAMA_HOST`: Ollama 服务地址
- `TOKEN_THRESHOLD`: 触发自动压缩的 token 阈值
- `MAX_ITERATIONS`: 最大思考迭代次数
- `MAX_HISTORY`: 最大对话历史保留条数
- `TRANSCRIPT_DIR`: 对话历史存储目录

### 2. utils/path.py - 路径安全工具
**职责**: 提供安全的路径处理功能，防止目录遍历攻击
**核心函数**:
- `safe_path(path)`: 验证并规范化路径，确保其位于工作目录内

### 3. tools/shell.py - Shell 命令执行模块
**职责**: 封装 Shell 命令执行功能，提供统一的错误处理
**核心函数**:
- `bash(command)`: 执行 Shell 命令，带超时保护和状态输出

### 4. tools/fileio.py - 文件操作模块
**职责**: 封装文件读写操作，集成路径安全检查
**核心函数**:
- `read_file(file_path)`: 安全读取文件内容
- `write_file(file_path, content)`: 安全写入文件内容（自动创建父目录）

### 5. tools/github.py - GitHub API 模块
**职责**: 封装 GitHub 仓库搜索和信息获取功能
**核心函数**:
- `search_github_repos(keyword, language)`: 搜索 GitHub 开源项目
- `get_github_repo_info(repo_url)`: 获取仓库详细信息（含 README）

### 6. tools/web.py - 网页内容抓取模块
**职责**: 封装网页内容获取和 HTML 纯文本提取
**核心函数**:
- `fetch_page(url)`: 获取网页内容并自动提取纯文本
- `extract_text_from_html(html_content)`: 从 HTML 中提取可读文本

### 7. tools/todo.py - 待办事项管理模块
**职责**: 提供完整的待办事项管理功能（状态管理、约束检查）
**核心类**:
- `TodoManager`: 待办事项管理器，支持三种状态管理

**核心函数**:
- `todo_add(text)`: 添加新任务
- `todo_change_status(item_id, status)`: 更改任务状态
- `todo_delete(item_id)`: 删除任务
- `todo_list()`: 查看当前待办列表

### 8. core/context.py - 上下文管理模块
**职责**: 管理对话上下文，实现 token 控制和对话压缩
**核心函数**:
- `estimate_tokens(messages)`: 粗略估算消息的 token 数量
- `auto_compact(messages)`: token 超过阈值时自动压缩对话
- `micro_compact(messages)`: LLM 调用前的轻量级工具结果压缩

### 9. core/llm.py - LLM 客户端模块
**职责**: 封装与 Ollama 服务的通信逻辑
**核心函数**:
- `chat_with_retry(messages, max_retries)`: 调用 Ollama Chat API，带自动重试
- `select_roleplay()`: 初始化系统提示词
- `check_ollama_available()`: 检查 Ollama 服务是否可用
- `get_tools_schema()`: 获取工具 Schema 定义
- `get_available_functions()`: 获取可用函数字典映射

### 10. agent.py - 主程序入口
**职责**: 协调各模块，实现主交互循环
**核心函数**:
- `agentloop()`: Agent 主交互循环
- `main()`: 程序入口，检查服务可用性并启动循环

## 模块间依赖关系

```
agent.py (主入口)
├── config.py (配置)
├── tools/
│   ├── todo.py (待办管理)
│   ├── shell.py (Shell命令)
│   ├── fileio.py (文件操作)
│   ├── github.py (GitHub API)
│   └── web.py (网页抓取)
└── core/
    ├── context.py (上下文管理)
    └── llm.py (LLM 客户端)

utils/path.py
└── 被 tools/fileio.py 依赖 (路径安全检查)

tools/* (所有工具模块)
└── 被 core/llm.py 依赖 (工具 Schema 和函数映射)

core/* (核心模块)
└── 被 agent.py 依赖 (主循环调用)
```

## 重构原则

### 1. 单一职责原则 (Single Responsibility Principle)
每个模块只负责一个特定的功能领域：
- 配置只在 `config.py`
- 路径安全只在 `utils/path.py`
- Shell 命令只在 `tools/shell.py`
- 等等

### 2. 低耦合 (Low Coupling)
- 模块间通过明确的接口通信
- 减少直接依赖
- 功能变更只影响相关模块

### 3. 高内聚 (High Cohesion)
- 相关功能放在同一模块
- 每个模块的函数都是为了完成该模块的核心职责

### 4. 可测试性 (Testability)
- 每个模块可以独立测试
- 依赖注入友好
- 便于单元测试和集成测试

### 5. 可维护性 (Maintainability)
- 代码结构清晰
- 便于定位问题
- 便于添加新功能

## 接口文档规范

### 函数文档标准
每个公共函数都包含以下文档：
1. **功能描述**: 简要说明函数做什么
2. **Args**: 参数列表，包含参数名、类型、描述
3. **Returns**: 返回值描述
4. **Example** (可选): 使用示例
5. **Raises** (可选): 可能抛出的异常
6. **Note** (可选): 额外说明

### 类型注解
所有函数都使用 Python 类型注解：
- 参数类型
- 返回值类型
- 便于静态类型检查

## 新增特性

### 1. 模块化导入
```python
from tools import todo_add, bash, read_file
from core import chat_with_retry
```

### 2. 清晰的导入路径
每个模块有明确的职责和导入路径，避免循环依赖。

### 3. 便于扩展
添加新工具只需在 `tools/` 目录下创建新模块，并更新 `tools/__init__.py` 和 `core/llm.py`。

## 向后兼容性

- 原有功能全部保留
- 接口保持一致
- 配置常量保持相同名称

## 后续优化建议

### 1. 添加单元测试
为每个模块创建对应的测试文件：
- `tests/test_utils_path.py`
- `tests/test_tools_shell.py`
- `tests/test_tools_fileio.py`
- ...

### 2. 添加日志系统
使用 `logging` 模块替代 `print`，支持不同日志级别和输出目标。

### 3. 配置文件支持
支持从 `toml` 或 `yaml` 配置文件读取配置，而不仅限于硬编码常量。

### 4. 插件系统
支持动态加载自定义工具插件。

### 5. 类型检查
集成 `mypy` 进行静态类型检查。

## 总结

本次重构成功地将 1000 行的单文件代码拆分为清晰的模块化架构，带来以下好处：

1. ✅ **代码可读性**: 每个模块职责明确，易于理解
2. ✅ **可维护性**: 问题定位快速，修改影响范围可控
3. ✅ **可扩展性**: 添加新功能只需创建对应模块，不影响现有代码
4. ✅ **可测试性**: 每个模块可以独立测试
5. ✅ **协作友好**: 多人开发时冲突概率降低
6. ✅ **文档完善**: 每个函数都有完整的文档和类型注解
