# Ollama Agent

A powerful AI agent built with Ollama that can use tools to interact with your filesystem and execute commands, while staying within a secure sandbox environment.

## ✨ Features

- **Tool Calling**: Supports multiple tools including `bash`, `read_file`, and `write_file`
- **Multi-turn Tool Usage**: Model can call multiple tools in sequence to complete complex tasks
- **Security Sandbox**: Restricted to working directory only, preventing access to system files
- **System Prompt Guidance**: Agent follows a structured workflow instead of just returning code
- **Real-time Execution**: Tools execute immediately with visible output

## 🛠️ Tools Available

- **`bash`**: Execute shell commands (restricted to working directory)
- **`read_file`**: Read file content (only within working directory)
- **`write_file`**: Write content to files (only within working directory)

## 📋 Requirements

- Python 3.9+
- Ollama (with a model that supports tool calling, e.g., `qwen3.5:9b`)
- Ollama Python SDK

## 🚀 Installation

1. **Clone the repository**
   ```bash
   git clone https://github.com/rabbitdeng/ollama-agent.git
   cd ollama-agent
   ```

2. **Install dependencies**
   ```bash
   pip install ollama
   ```

3. **Ensure Ollama is running**
   ```bash
   # Start Ollama service if not already running
   ollama serve
   ```

4. **Pull a model that supports tool calling**
   ```bash
   ollama pull qwen3.5:9b
   ```

## 🎯 Usage

1. **Run the agent**
   ```bash
   python agent.py
   ```

2. **Interact with the agent**
   ```
   user: Create a file called test.py with a hello world function
   assistant: I'll help you create a test.py file with a hello world function.
   [执行工具: write_file {"file_path": "test.py", "content": "def hello():\n    print('Hello, world!')\n\nif __name__ == '__main__':\n    hello()"}]
   [工具输出]: 
   assistant: I've created the test.py file with a hello world function.
   ```

## 🔒 Security Features

- **Path Sandbox**: All file operations are restricted to the working directory
- **Command Isolation**: `bash` commands run in the working directory context
- **Safe Path Handling**: Prevents directory traversal attacks

## 📁 Project Structure

```
ollama-agent/
├── agent.py          # Main agent code
├── hello.py          # Example file
├── kalman_filter.py  # Example Kalman filter implementation
└── .gitignore        # Git ignore file
```

## 🤖 Agent Workflow

1. **User Input**: You provide a task or question
2. **Tool Selection**: Agent decides which tools to use
3. **Execution**: Tools execute with visible output
4. **Result Analysis**: Agent processes tool results
5. **Final Response**: Agent provides a summary of the work done

## 🌐 Model Compatibility

This agent works best with models that support tool calling, such as:
- `qwen3.5:9b`
- `llama3.1`
- `qwen2.5`

## 📝 Examples

### Example 1: Create and run a script
```
user: Create a Python script that prints Fibonacci numbers up to 100
assistant: I'll create a Python script to generate Fibonacci numbers.
[执行工具: write_file {"file_path": "fibonacci.py", "content": "def fibonacci(n):\n    a, b = 0, 1\n    result = []\n    while a < n:\n        result.append(a)\n        a, b = b, a + b\n    return result\n\nprint(fibonacci(100))"}]
[工具输出]: 
assistant: Now let's run the script to see the output.
[执行工具: bash {"command": "python fibonacci.py"}]
[工具输出]: [0, 1, 1, 2, 3, 5, 8, 13, 21, 34, 55, 89]
assistant: The Fibonacci script has been created and executed successfully.
```

### Example 2: Read and modify a file
```
user: Read the content of hello.py and add a comment
assistant: I'll read the current content of hello.py first.
[执行工具: read_file {"file_path": "hello.py"}]
[工具输出]: print('Hello, world!')
assistant: Now I'll add a comment to the file.
[执行工具: write_file {"file_path": "hello.py", "content": "# Hello world example\nprint('Hello, world!')"}]
[工具输出]: 
assistant: I've added a comment to hello.py.
```

## 🤝 Contributing

Feel free to fork the repository and submit pull requests. Contributions are welcome!

## 📄 License

This project is open source and available under the [MIT License](LICENSE).

---

**Happy coding with your Ollama agent!** 🎉