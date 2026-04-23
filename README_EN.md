# Code Agent

A local code assistant tool based on Ollama, supporting code file management, Shell command execution, GitHub project search, web content scraping, and todo management.

## ✨ Features

### 📁 File Management
- **Read File** - Safely read local file content
- **Write File** - Create or overwrite files, auto-create parent directories
- **Path Security** - Prevent directory traversal attacks, limited to working directory

### 🖥️ Shell Command Execution
- Execute any Shell command
- Display execution status and full output
- Timeout protection (5 minutes)

### 🔍 GitHub Integration
- **Project Search** - Search popular projects by keyword and programming language via GitHub API
- **Repository Details** - Get complete information and README content of specified repositories
- Display Stars, Forks, programming language, etc.

### 🌐 Web Content Scraping
- Automatically extract plain text from web pages
- Remove scripts, styles, navigation and other irrelevant elements
- Auto truncation for long content

### ✅ Todo Management
- Three statuses: Pending ⬜, In Progress 🔄, Done ✅
- Maximum 5 tasks supported
- Limited to 1 task in progress at a time
- Auto-display current task list with each interaction

### 💾 Smart Context Management
- **Lightweight Compression** - Replace old tool call results with placeholders
- **Auto Summary** - Auto-compress conversation when token exceeds threshold
- **Conversation Persistence** - Complete conversation history saved to `transcripts/` directory
- **History Limit** - Keep up to 16 most recent messages

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
pip install requests beautifulsoup4
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

| Tool | Function | Parameters |
|------|----------|------------|
| `todo_add` | Add new task | text: Task description |
| `todo_change_status` | Change task status | item_id: Task ID, status: pending/in_progress/done |
| `todo_delete` | Delete task | item_id: Task ID |
| `todo_list` | View task list | No parameters |
| `search_github_repos` | Search GitHub projects | keyword: Search term, language: Programming language (optional) |
| `get_github_repo_info` | Get repository details | repo_url: Repository URL |
| `bash` | Execute Shell command | command: Command string |
| `read_file` | Read file | file_path: File path |
| `write_file` | Write to file | file_path: File path, content: Content |
| `fetch_page` | Fetch web content | url: Web page URL |

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

| Parameter | Default | Description |
|-----------|---------|-------------|
| `DEFAULT_MODEL` | qwen3.5:9b | Model name to use |
| `MAX_ITERATIONS` | 20 | Maximum thinking iterations |
| `MAX_HISTORY` | 16 | Number of conversation history to keep |
| `TOKEN_THRESHOLD` | 8000 | Token threshold to trigger auto-compression |
| `KEEP_RECENT_TOOLS` | 3 | Number of tool calls with full results kept |

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

## 📝 Roadmap

- [ ] Support multi-model switching
- [ ] Add file diff comparison
- [ ] Support streaming output
- [ ] Add more tools (database, Git operations, etc.)
- [ ] Support multi-session management
- [ ] Conversation history search and export

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 📞 Contact

- Project Homepage: [GitHub](https://github.com/yourusername/codeagent)
- Issues: [Issues Page](https://github.com/yourusername/codeagent/issues)

## ⚠️ Notes

- This is a locally running tool. Please exercise caution when executing Shell commands
- All file operations are limited to the current working directory and its subdirectories
- Recommended for use in Git repositories to allow file change rollbacks
- Reading large files may consume many tokens, please use with caution
