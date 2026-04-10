# 一个非常简单的编程助手

一个基于Ollama的简单AI编程助手，可以使用工具与文件系统交互并执行命令，同时保持在安全的沙箱环境中。

## ✨ 特性

- **工具调用**：支持多个工具，包括 `bash`、`read_file` 和 `write_file`
- **多轮工具使用**：模型可以按顺序调用多个工具来完成复杂任务
- **安全沙箱**：限制在工作目录内，防止访问系统文件
- **系统提示指导**：助手遵循结构化工作流程，而不是直接返回代码
- **实时执行**：工具立即执行并显示输出

## 🛠️ 可用工具

- **`bash`**：执行shell命令（限制在工作目录）
- **`read_file`**：读取文件内容（仅在工作目录内）
- **`write_file`**：写入文件内容（仅在工作目录内）

## 📋 要求

- Python 3.9+
- Ollama（使用支持工具调用的模型，例如 `qwen3.5:9b`）
- Ollama Python SDK

## 🚀 安装

1. **克隆仓库**
   ```bash
   git clone https://github.com/rabbitdeng/a-very-simple-coding-agent.git
   cd a-very-simple-coding-agent
   ```

2. **安装依赖**
   ```bash
   pip install ollama
   ```

3. **确保Ollama正在运行**
   ```bash
   # 如果Ollama服务未运行，请启动它
   ollama serve
   ```

4. **拉取支持工具调用的模型**
   ```bash
   ollama pull qwen3.5:9b
   ```

## 🎯 使用

1. **运行助手**
   ```bash
   python agent.py
   ```

2. **与助手交互**
   ```
   user: 创建一个名为test.py的文件，包含一个hello world函数
   assistant: 我来帮你创建一个包含hello world函数的test.py文件。
   [执行工具: write_file {"file_path": "test.py", "content": "def hello():\n    print('Hello, world!')\n\nif __name__ == '__main__':\n    hello()"}]
   [工具输出]: 
   assistant: 我已经创建了包含hello world函数的test.py文件。
   ```

## 🔒 安全特性

- **路径沙箱**：所有文件操作都限制在工作目录内
- **命令隔离**：`bash`命令在工作目录上下文中运行
- **安全路径处理**：防止目录遍历攻击

## 📁 项目结构

```
a-very-simple-coding-agent/
├── agent.py          # 主助手代码
├── hello.py          # 示例文件
├── kalman_filter.py  # 卡尔曼滤波器示例实现
└── .gitignore        # Git忽略文件
```

## 🤖 助手工作流程

1. **用户输入**：你提供任务或问题
2. **工具选择**：助手决定使用哪些工具
3. **执行**：工具执行并显示输出
4. **结果分析**：助手处理工具结果
5. **最终响应**：助手提供完成工作的总结

## 🌐 模型兼容性

此助手最适合支持工具调用的模型，例如：
- `qwen3.5:9b`
- `llama3.1`
- `qwen2.5`

## 📝 示例

### 示例1：创建并运行脚本
```
user: 创建一个打印斐波那契数列到100的Python脚本
assistant: 我将创建一个生成斐波那契数列的Python脚本。
[执行工具: write_file {"file_path": "fibonacci.py", "content": "def fibonacci(n):\n    a, b = 0, 1\n    result = []\n    while a < n:\n        result.append(a)\n        a, b = b, a + b\n    return result\n\nprint(fibonacci(100))"}]
[工具输出]: 
assistant: 现在让我们运行脚本来查看输出。
[执行工具: bash {"command": "python fibonacci.py"}]
[工具输出]: [0, 1, 1, 2, 3, 5, 8, 13, 21, 34, 55, 89]
assistant: 斐波那契脚本已成功创建并执行。
```

### 示例2：读取并修改文件
```
user: 读取hello.py的内容并添加注释
assistant: 我先读取hello.py的当前内容。
[执行工具: read_file {"file_path": "hello.py"}]
[工具输出]: print('Hello, world!')
assistant: 现在我将向文件添加注释。
[执行工具: write_file {"file_path": "hello.py", "content": "# Hello world示例\nprint('Hello, world!')"}]
[工具输出]: 
assistant: 我已经向hello.py添加了注释。
```

## 🤝 贡献

欢迎fork仓库并提交pull请求。我们欢迎各种贡献！

## 📄 许可证

此项目是开源的，可在 [MIT License](LICENSE) 下使用。

---

**祝您使用编程助手愉快！** 🎉