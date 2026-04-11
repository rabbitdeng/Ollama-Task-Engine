# VTuber Coding Agent

一个支持VTuber角色扮演的AI编程助手，使用Ollama构建，可以通过工具与文件系统交互并执行命令，同时保持在安全的沙箱环境中。

## ✨ 核心特性

- **VTuber角色扮演**：支持永雏塔菲（Taffy）等虚拟主播角色
- **工具调用**：支持 `bash`、`read_file` 和 `write_file` 等工具
- **多轮工具使用**：模型可以顺序调用多个工具完成复杂任务
- **安全沙箱**：限制在工作目录内操作，防止访问系统文件
- **角色化交互**：以VTuber的性格和语气与用户互动
- **实时执行**：工具执行结果即时可见

## 🎭 可选角色

### 永雏塔菲（Ace Taffy）

- **身份**：来自1885年的个人势虚拟偶像，侦探发明家
- **特点**：活泼可爱，喜欢在句尾加"喵"作为语气词
- **背景**：乘坐自己发明的时光机来到现代，被电子游戏吸引
- **口头禅**："taffy能嘤嘤嘤也能冷冰冰喵！"、"关注永雏塔菲喵，关注永雏塔菲谢谢喵！"

## 🛠️ 可用工具

- **`bash`**：执行shell命令（限制在工作目录）
- **`read_file`**：读取文件内容（仅在工作目录内）
- **`write_file`**：写入文件内容（仅在工作目录内）

## 📋 环境要求

- Python 3.9+
- Ollama（支持工具调用的模型，如 `gemma4:latest`）
- Ollama Python SDK

## 🚀 安装步骤

1. **克隆仓库**
   ```bash
   git clone https://github.com/rabbitdeng/a-very-simple-coding-agent.git
   cd a-very-simple-coding-agent
   ```

2. **安装依赖**
   ```bash
   pip install ollama
   ```

3. **确保Ollama运行**
   ```bash
   # 如果Ollama服务未运行，启动它
   ollama serve
   ```

4. **拉取支持工具调用的模型**
   ```bash
   ollama pull gemma4:latest
   ```

## 🎯 使用方法

1. **运行agent**
   ```bash
   python agent.py
   ```

2. **选择角色**
   ```
   ==================================================
   欢迎使用代码助手！
   ==================================================
   是否使用永雏塔菲角色扮演？(y/n): y

   已切换到永雏塔菲模式！喵~
   ```

3. **与VTuber助手互动**
   ```
   user: 帮我创建一个hello.py文件
   assistant: 好的，雏草姬！我来帮你创建hello.py文件喵~ 让我使用write_file工具来完成这个任务~
   [执行工具: write_file {"file_path": "hello.py", "content": "print('Hello, world!')"}]
   [工具输出]: 
   assistant: 文件创建成功啦！现在我们有了一个简单的hello.py文件喵~ 你还需要我做什么吗？
   ```

## 🔒 安全特性

- **路径沙箱**：所有文件操作限制在工作目录内
- **命令隔离**：`bash` 命令在工作目录上下文中运行
- **安全路径处理**：防止目录遍历攻击

## 📁 项目结构

```
a-very-simple-coding-agent/
├── agent.py               # 主agent代码
├── taffy_system_prompt.txt  # 永雏塔菲角色设定
├── taffy_corpus.csv       # 永雏塔菲语料库
├── hello.py               # 示例文件
├── kalman_filter.py       # 示例卡尔曼滤波器实现
└── .gitignore             # Git忽略文件
```

## 🤖 Agent工作流程

1. **角色选择**：用户选择是否使用VTuber角色扮演
2. **用户输入**：提供任务或问题
3. **工具选择**：Agent根据角色性格决定使用哪些工具
4. **执行**：工具执行并显示输出
5. **结果分析**：Agent以角色语气处理工具结果
6. **最终响应**：Agent以角色身份提供工作总结

## 🌐 模型兼容性

此agent最适合支持工具调用的模型，如：
- `gemma4:latest`
- `qwen3.5:9b`
- `llama3.1`
- `qwen2.5`

## 📝 角色扮演示例

### 示例1：创建并运行脚本
```
user: 创建一个Python脚本，打印斐波那契数列到100
assistant: 好的，雏草姬！我来帮你创建一个斐波那契数列的脚本喵~ 让我使用write_file工具来完成这个任务~
[执行工具: write_file {"file_path": "fibonacci.py", "content": "def fibonacci(n):\n    a, b = 0, 1\n    result = []\n    while a < n:\n        result.append(a)\n        a, b = b, a + b\n    return result\n\nprint(fibonacci(100))"}]
[工具输出]: 
assistant: 现在让我们运行这个脚本来看看输出喵~ 我使用bash工具来执行它~
[执行工具: bash {"command": "python fibonacci.py"}]
[工具输出]: [0, 1, 1, 2, 3, 5, 8, 13, 21, 34, 55, 89]
assistant: 斐波那契脚本已经成功创建并执行啦！输出了0到89的斐波那契数列喵~ 你还需要我做什么吗？
```

### 示例2：读取并修改文件
```
user: 读取hello.py的内容并添加注释
assistant: 好的，雏草姬！我先读取hello.py的当前内容喵~
[执行工具: read_file {"file_path": "hello.py"}]
[工具输出]: print('Hello, world!')
assistant: 现在我来给这个文件添加注释喵~
[执行工具: write_file {"file_path": "hello.py", "content": "# Hello world example\nprint('Hello, world!')"}]
[工具输出]: 
assistant: 我已经给hello.py添加了注释啦！现在文件看起来更清晰了喵~ 你还需要我帮你做什么吗？
```

## 🎨 角色设定

永雏塔菲的完整角色设定包含：
- 个人信息（年龄、身高、体重等）
- 形象特点（粉发、呆毛、M形刘海等）
- 性格和行为准则（活泼可爱、乐观开朗等）
- 发明（时光机等）
- 活动平台（B站、YouTube等）
- 经典梗和口头禅

这些设定都存储在 `taffy_system_prompt.txt` 文件中，可以根据需要修改。

## 🤝 贡献

欢迎fork仓库并提交pull requests。我们非常欢迎你的贡献！

## 📄 许可证

本项目是开源的，基于 [MIT License](LICENSE) 发布。

---

**与你的VTuber编程助手一起愉快编码！** 🎉