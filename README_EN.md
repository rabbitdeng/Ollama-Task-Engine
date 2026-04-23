# Ollama Task Engine

**Your All-in-One Local Code Sandbox & Intelligent Agent Engine**

No API leaks, no closed-source wrappers.
This is a 100% local computing power (based on Ollama) geek-level Coding Agent. It not only understands your needs, but also directly controls your physical hard drive, executes Shell commands, crawls the latest web pages, and calls GitHub APIs for in-depth research through a complete Tool Calling mechanism.

Give it a goal, and it will build the world for you in a secure local sandbox.

&lt;br /&gt;

## 💡 Design Philosophy

- **Local First**: Your code is your core asset. All reasoning and file operations are completed locally, cutting off dependence on external commercial APIs.
- **Agentic, not Scripted**: Empower the large model with a state machine (TodoList) and environment awareness (Bash/file read/write), allowing it to plan paths autonomously instead of rigidly executing preset processes.
- **Context is King**: Extremely restrained memory management strategy. Through dynamic compression, Token threshold control, and log isolation, it ensures absolute clarity of long logical chains even on small-scale local models like 9B/14B.

## ✨ Features

### ✅ Implemented Features

#### 📁 File Management

- **Read File** - Safely read local file content
- **Write File** - Create or overwrite files, auto-create parent directories
- **Path Safety** - Prevent directory traversal attacks, limited to working directory

#### 🖥️ Shell Command Execution

- Execute any Shell command
- Display execution status (success/failure) and full output
- Timeout protection (5 minutes)
- Friendly error messages

#### 🔍 GitHub Integration

- **Project Search** - Search popular projects by keyword and programming language via GitHub API
- **Repository Details** - Get complete information and README content of specified repositories
- Display Stars, Forks, programming language, last updated time, etc.
- Auto-formatted results display

#### 🌐 Web Content Scraping

- Automatically extract plain text from web pages
- Remove scripts, styles, navigation, footers and other irrelevant elements
- Auto truncation for long content (3000 characters)
- Support custom User-Agent

#### ✅ Todo Management

- Three statuses: Pending ⬜, In Progress 🔄, Done ✅
- Maximum 5 tasks supported
- Limited to 1 task in progress at a time
- Auto-display current task list with each interaction
- Support task status switching and deletion

#### 💾 Smart Context Management

- **Lightweight Compression** - Replace old tool call results with placeholders (keep last 3 full results)
- **Auto Summary** - Auto-compress conversation when token exceeds threshold (8000)
- **Conversation Persistence** - Complete conversation history saved to `transcripts/` directory (JSONL format)
- **History Limit** - Keep up to 16 most recent messages
- **System Prompt Retention** - Always keep first system prompt and initial user request

#### 🛡️ Security & Error Handling

- **Path Safety Check** - All file operations verified via `realpath`
- **Request Timeout Protection** - Retry API calls on timeout (up to 3 times)
- **Network Error Handling** - Friendly prompts for connection failures, timeouts, etc.
- **Service Health Check** - Automatically detect if Ollama service is available on startup
- **Graceful Exit** - Support `Ctrl+C`, `Ctrl+D` and `exit` commands to exit

***

### 🚀 Planned Features

#### 🤖 Multi-Agent Architecture

- **Sub-Agent System** - Support creation of dedicated sub-agents for specific tasks
  - **Code Review Agent** - Specialized in analyzing code quality and potential issues
  - **Test Generation Agent** - Automatically generate unit test code
  - **Documentation Agent** - Auto-generate project documentation and comments
  - **Refactoring Agent** - Analyze and suggest code refactoring improvements
- **Multi-Agent Collaboration** - Conversation and collaboration between multiple agents
- **Task Allocation** - Main Agent intelligently assigns tasks to appropriate sub-agents
- **Result Aggregation** - Integrate outputs from multiple sub-agents

#### 🧠 Advanced Intelligence Features

- **Enhanced Code Understanding** - AST analysis support for deep code structure comprehension
- **Dependency Analysis** - Automatically analyze project dependencies and call graphs
- **Intelligent Completion** - Context-based smart code completion suggestions
- **Auto Bug Detection** - Analyze potential bugs and security vulnerabilities in code
- **Code Style Learning** - Learn project code style patterns to maintain consistent output

#### 📦 Tool Extensions

- **Database Operations** - Support MySQL, PostgreSQL, SQLite query and modification
- **Deep Git Integration** - Git diff, commit history, blame, checkout, and more operations
- **Docker Support** - Command execution inside containers, image build and run
- **Regex Tools** - Regular expression testing, matching, and replacement tools
- **File Diff Tool** - Support diff comparison for file changes
- **Batch Rename** - File batch renaming and moving operations

#### 👥 Collaboration & Multi-Session

- **Multi-Session Management** - Support multiple independent sessions simultaneously
- **Session Persistence** - Save and load conversation history, support resumption after interruption
- **Session Export** - Export conversation records to Markdown, PDF, and other formats
- **Session Search** - Search keywords and context within historical conversations
- **Branch Conversations** - Support branching from a point to try different solutions

#### 🎨 User Experience Enhancements

- **Web UI Interface** - Provide web interface for easy remote usage and visualization
- **Streaming Output** - LLM response streaming output to reduce perceived waiting time
- **Live Preview** - File modification diff preview, confirm before applying changes
- **Shortcut Support** - Command-line mode with keyboard shortcuts (Ctrl+R history, Tab completion)
- **Color Output** - Terminal colored output for improved readability
- **Progress Display** - Progress bar for long-running operations

#### ⚙️ Configuration & Extension

- **Config File Support** - TOML/YAML configuration files with custom parameters
- **Model Auto Selection** - Automatically select appropriate model size based on task complexity
- **Tool Hot Reload** - Support dynamic loading of custom tool plugins
- **Prompt Templates** - Built-in multiple prompt templates for different styles
- **Multi-Model Support** - Configure and switch between multiple models (local + cloud)

#### 🔧 Development & Debugging

- **Debug Mode** - Detailed log output for easy diagnostics
- **Performance Monitoring** - Token consumption and response time statistics
- **Tool Call Visualization** - Visual display of tool calling process
- **Unit Tests** - Comprehensive unit test coverage for core functions

## 🚀 Quick Start

### Requirements

- Python 3.8+
- Ollama service
- At least 8GB RAM (16GB recommended)

### Installation Steps

1. **Install Ollama**

```bash
# macOS
brew install ollama

# Linux
curl -fsSL https://ollama.com/install.sh | sh

# Windows
# Visit https://ollama.ai/ to download installer
```

2. **Pull Model**

```bash
ollama pull qwen3.5:9b
```

3. **Install Python Dependencies**

```bash
pip install -r requirements.txt
```

4. **Run Agent**

```bash
python agent.py
```

## 📖 Usage

### Basic Commands

- Enter questions or task descriptions for direct interaction
- Type `exit`, `quit`, or `q` to exit the program
- Press `Ctrl+C` or `Ctrl+D` to exit

### Available Tools

| Tool                     | Function           | Parameters                                                |
| ---------------------- | ---------------- | ------------------------------------------------------- |
| `todo_add`             | Add new task       | text: Task description                                        |
| `todo_change_status`   | Change task status | item\_id: Task ID, status: pending/in\_progress/done         |
| `todo_delete`          | Delete task        | item\_id: Task ID                                        |
| `todo_list`            | View task list     | No parameters                                               |
| `search_github_repos`  | Search GitHub projects | keyword: Search term, language: Programming language (optional)          |
| `get_github_repo_info` | Get repository details | repo\_url: Repository URL                                  |
| `bash`                 | Execute Shell command | command: Command string                                    |
| `read_file`            | Read file          | file\_path: File path                                      |
| `write_file`           | Write to file      | file\_path: File path, content: Content                     |
| `fetch_page`           | Fetch web content  | url: Web page URL                                        |

### Common Examples

**Search GitHub AI Projects**

```
user: Help me search for popular Python AI projects on GitHub
```

**List Current Directory**

```
user: List files in current directory
```

**Read a File**

```
user: Read the content of agent.py file
```

**Add a Todo**

```
user: Add task: Improve error handling in the code
```

## 🔧 Configuration

### Environment Variables

- `OLLAMA_HOST` - Ollama service address (default: http://localhost:11434)

### Configurable Parameters

The following parameters can be adjusted in `agent.py`:

| Parameter                  | Default Value    | Description                               |
| ----------------------- | -------------- | --------------------------------------- |
| `DEFAULT_MODEL`         | qwen3.5:9b     | Model name to use                        |
| `MAX_ITERATIONS`        | 20             | Maximum thinking iterations               |
| `MAX_HISTORY`           | 16             | Number of conversation history to keep    |
| `TOKEN_THRESHOLD`       | 8000           | Token threshold to trigger auto-compression |
| `KEEP_RECENT_TOOLS`     | 3              | Number of tool calls with full results kept |

## 📊 Project Structure

```
codeagent/
├── agent.py              # Main program file
├── README.md            # Chinese documentation
├── README_EN.md         # English documentation
├── requirements.txt     # Python dependencies
└── transcripts/         # Conversation history directory (auto-created)
    └── transcript_*.jsonl
```

## 🛡️ Security Features

1. **Path Safety** - All file operations undergo security checks to prevent directory traversal
2. **Command Timeout** - Shell commands have 5-minute timeout protection
3. **Network Timeout** - API call timeout protection
4. **Content Truncation** - Auto truncation for large files and web content

## 🤝 Contributing

Contributions, issues, and feature requests are welcome!

1. Fork the Project
2. Create your Feature Branch (`git checkout -b feature/AmazingFeature`)
3. Commit your Changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the Branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

## 📝 Development Milestones

### v0.1 ✅ Completed

- [x] Basic file operations (read/write)
- [x] Shell command execution
- [x] GitHub project search
- [x] Repository details retrieval
- [x] Web content scraping
- [x] Todo management (3 statuses)
- [x] Basic context management
- [x] Lightweight tool result compression
- [x] Conversation persistence storage

### v0.2 📋 In Progress

- [ ] Web UI interface (initial version)
- [ ] Session history save and load
- [ ] Streaming output support
- [ ] File diff preview

### v0.3 🚀 Planned

- [ ] Sub-Agent basic architecture
- [ ] Code review dedicated Agent
- [ ] Deep Git integration
- [ ] Configuration file support

### v1.0 🎯 Future Goals

- [ ] Multi-agent collaboration framework
- [ ] Complete plugin system
- [ ] Multi-model intelligent routing
- [ ] Performance optimization and monitoring

## 📄 License

This project is licensed under the MIT License - See the [LICENSE](LICENSE) file for details.

## 📞 Contact

- Project Homepage: [GitHub](https://github.com/rabbitdeng/Ollama-Task-Engine)
- Issues: [Issues Page](https://github.com/rabbitdeng/Ollama-Task-Engine/issues)
- Feature Requests: [Discussions](https://github.com/rabbitdeng/Ollama-Task-Engine/discussions)

## ⚠️ Notes

- This is a locally running tool. Please exercise caution when executing Shell commands
- All file operations are limited to the current working directory and its subdirectories
- Recommended for use in Git repositories to allow file change rollbacks
- Reading large files may consume many tokens, please use with caution
