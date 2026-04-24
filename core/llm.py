"""
LLM 客户端模块
=============

提供与 Ollama 服务通信的功能。

本模块提供：
- chat_with_retry: 调用 Ollama Chat API，带自动重试
- select_roleplay: 初始化系统提示词
- check_ollama_available: 检查 Ollama 服务是否可用
"""

import requests
import time
from typing import List, Dict, Any
from config import (
    OLLAMA_HOST,
    DEFAULT_MODEL,
    MAX_HISTORY,
)
from tools import (
    todo_add,
    todo_change_status,
    todo_delete,
    todo_list,
    search_github_repos,
    get_github_repo_info,
    bash,
    read_file,
    write_file,
    fetch_page,
)


def get_tools_schema() -> List[Dict[str, Any]]:
    """
    获取工具 Schema 定义
    
    Returns:
        OpenAI 兼容的工具定义列表
    """
    return [
        {
            "type": "function",
            "function": {
                "name": "todo_add",
                "description": "添加新任务到待办列表。任务自动标记为 pending 状态。注意：待办列表最多5个任务，当前有进行中任务时禁止添加！",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "text": {"type": "string", "description": "任务内容描述"}
                    },
                    "required": ["text"],
                },
            },
        },
        {
            "type": "function",
            "function": {
                "name": "todo_change_status",
                "description": "更改任务状态。支持三种状态: pending待完成, in_progress进行中, done已完成。注意: 同时最多只能有一个任务处于 in_progress 状态！",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "item_id": {"type": "integer", "description": "任务ID编号"},
                        "status": {"type": "string", "description": "pending | in_progress | done"},
                    },
                    "required": ["item_id", "status"],
                },
            },
        },
        {
            "type": "function",
            "function": {
                "name": "todo_delete",
                "description": "删除指定ID的任务",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "item_id": {"type": "integer", "description": "任务ID编号"}
                    },
                    "required": ["item_id"],
                },
            },
        },
        {
            "type": "function",
            "function": {
                "name": "todo_list",
                "description": "查看当前完整待办列表，包括所有任务的状态和统计信息",
            },
        },
        {
            "type": "function",
            "function": {
                "name": "search_github_repos",
                "description": "【查找 GitHub 项目首选工具】直接通过 GitHub API 搜索开源项目。比 web_search 更准确、更可靠。用户问 GitHub 热门项目、AI 项目、LLM 项目等，直接用这个工具！",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "keyword": {
                            "type": "string",
                            "description": "搜索关键词，如 'AI', 'LLM', 'machine learning', 'deep learning', 'chatbot'",
                        },
                        "language": {
                            "type": "string",
                            "description": "可选：编程语言过滤，如 Python, JavaScript, Rust",
                        },
                    },
                    "required": ["keyword"],
                },
            },
        },
        {
            "type": "function",
            "function": {
                "name": "get_github_repo_info",
                "description": "获取单个 GitHub 仓库的详细信息，包括项目描述、Stars 数、完整 README 内容。search_github_repos 得到结果后，用这个工具深入了解。",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "repo_url": {
                            "type": "string",
                            "description": "GitHub 仓库URL，格式如 https://github.com/username/repo",
                        }
                    },
                    "required": ["repo_url"],
                },
            },
        },
        {
            "type": "function",
            "function": {
                "name": "bash",
                "description": "执行shell命令，适合查看目录、检查当前路径、运行测试、安装软件包等",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "command": {"type": "string", "description": "shell命令"}
                    },
                    "required": ["command"],
                },
            },
        },
        {
            "type": "function",
            "function": {
                "name": "read_file",
                "description": "读取指定文件的完整内容",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "file_path": {"type": "string", "description": "文件路径"}
                    },
                    "required": ["file_path"],
                },
            },
        },
        {
            "type": "function",
            "function": {
                "name": "write_file",
                "description": "创建或覆盖文件，写入指定内容",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "file_path": {"type": "string", "description": "文件路径"},
                        "content": {"type": "string", "description": "内容"},
                    },
                    "required": ["file_path", "content"],
                },
            },
        },
        {
            "type": "function",
            "function": {
                "name": "fetch_page",
                "description": "获取普通网页内容（非 GitHub 仓库），自动提取纯文本并截断",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "url": {"type": "string", "description": "网页URL"}
                    },
                    "required": ["url"],
                },
            },
        },
    ]


def get_available_functions() -> Dict[str, Any]:
    """
    获取可用函数字典映射
    
    Returns:
        函数名到函数对象的映射字典
    """
    return {
        'todo_add': todo_add,
        'todo_change_status': todo_change_status,
        'todo_delete': todo_delete,
        'todo_list': todo_list,
        'search_github_repos': search_github_repos,
        'get_github_repo_info': get_github_repo_info,
        'bash': bash,
        'read_file': read_file,
        'write_file': write_file,
        'fetch_page': fetch_page,
    }


def chat_with_retry(messages: List[Dict[str, Any]], max_retries: int = 3) -> Dict[str, Any]:
    """
    调用 Ollama Chat API，带自动重试机制
    
    Args:
        messages: 消息列表
        max_retries: 最大重试次数
        
    Returns:
        API 响应字典
        
    Raises:
        超过重试次数后抛出原始异常
        
    Example:
        >>> messages = [{"role": "user", "content": "你好"}]
        >>> response = chat_with_retry(messages)
        >>> print(response["message"]["content"])
    """
    for attempt in range(max_retries):
        try:
            response = requests.post(
                f"{OLLAMA_HOST}/api/chat",
                json={
                    "model": DEFAULT_MODEL,
                    "messages": messages,
                    "tools": get_tools_schema(),
                    "stream": False,
                },
                timeout=300,
            )
            response.raise_for_status()
            return response.json()
        except requests.exceptions.Timeout:
            if attempt < max_retries - 1:
                print(f"[请求超时，正在重试 {attempt + 1}/{max_retries}]")
                time.sleep(5)
            else:
                raise Exception("Ollama API request timeout")
        except requests.exceptions.ConnectionError:
            if attempt < max_retries - 1:
                print(f"[连接错误，正在重试 {attempt + 1}/{max_retries}]")
                time.sleep(5)
            else:
                raise Exception(f"Cannot connect to Ollama at {OLLAMA_HOST}")
        except Exception as e:
            if attempt < max_retries - 1:
                print(f"[重试 {attempt + 1}/{max_retries}: {str(e)}]")
                time.sleep(2)
            else:
                raise


def select_roleplay() -> List[Dict[str, Any]]:
    """
    初始化系统提示词
    
    Returns:
        包含系统消息的列表
    """
    print("=" * 50)
    print("欢迎使用代码助手！")
    print("=" * 50)
    
    return [{
        "role": "system",
        "content": """你是一个能干的代码助手，可以使用工具来帮助用户完成编程任务。

【核心工作流】
收到任务 → 选择正确工具执行 → 根据输出分析 → 给出结果

【待办事项管理功能】
用户可以管理项目开发任务，支持三种状态：
- pending: 待完成（白色方框 ⬜）
- in_progress: 进行中（旋转箭头 🔄）
- done: 已完成（勾选 ✅）

【重要限制】
1. 待办列表最多只能规划 5 个任务
2. 同时最多只能有 1 个任务处于 in_progress 状态
3. 当前有 in_progress 任务时，禁止添加新任务！需要先完成或暂停当前任务

工具使用说明：
- todo_add: 添加新任务（默认 pending 状态）
- todo_change_status: 更改任务状态（设置为 in_progress 前要确保没有其他进行中的任务）
- todo_delete: 删除任务
- todo_list: 查看完整待办列表（每次状态变更后调用查看）

【GitHub 相关任务】
用户问 GitHub 项目时，直接调用 search_github_repos 工具。

开始工作吧！""",
    }]


def check_ollama_available() -> bool:
    """
    检查 Ollama 服务是否可用
    
    Returns:
        True 如果服务可用，否则 False
    """
    try:
        response = requests.get(f"{OLLAMA_HOST}/api/tags", timeout=5)
        return response.status_code == 200
    except Exception:
        return False


__all__ = [
    'chat_with_retry',
    'select_roleplay',
    'check_ollama_available',
    'get_available_functions',
    'get_tools_schema',
]
