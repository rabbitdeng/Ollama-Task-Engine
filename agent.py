#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Code Agent - 基于 Ollama 的代码助手工具
==========================================

功能特性：
- 代码文件管理（读取、写入、修改）
- Shell 命令执行
- GitHub 项目搜索
- 网页内容抓取
- 待办事项管理（Todo List）
- 上下文自动压缩
- 对话历史持久化

Authors: Code Agent Team
Date: 2025
"""

import subprocess
import os
import time
import requests
import json
import re
import sys
from datetime import datetime
from pathlib import Path
from typing import List, Dict, Any, Optional, Tuple, Union
from bs4 import BeautifulSoup

# ==================== 配置常量 ====================
BASE_DIR = os.path.abspath(os.getcwd())
DEFAULT_MODEL = "qwen3.5:9b"
OLLAMA_HOST = os.environ.get("OLLAMA_HOST", "http://localhost:11434")
KEEP_RECENT_TOOLS = 3
TOKEN_THRESHOLD = 8000
MAX_ITERATIONS = 20
MAX_HISTORY = 16
TRANSCRIPT_DIR = Path(BASE_DIR) / "transcripts"
TRANSCRIPT_DIR.mkdir(exist_ok=True)

# ==================== 工具函数 ====================

def safe_path(path: str) -> str:
    """
    安全路径处理 - 防止目录遍历攻击
    
    Args:
        path: 要处理的路径字符串
        
    Returns:
        验证后的绝对真实路径
        
    Raises:
        PermissionError: 如果路径指向工作目录之外
    """
    path = path.replace("\\", "/")
    abs_path = os.path.abspath(path)
    real_path = os.path.realpath(abs_path)
    
    if not real_path.startswith(BASE_DIR):
        raise PermissionError(f"Access denied: {path} is pointing outside the working directory")

    return real_path


def bash(command: str) -> str:
    """
    执行 Shell 命令
    
    Args:
        command: 要执行的 shell 命令字符串
        
    Returns:
        包含执行状态和输出的格式化字符串
    """
    try:
        result = subprocess.run(
            command,
            shell=True,
            capture_output=True,
            text=True,
            cwd=BASE_DIR,
            timeout=300
        )
        
        status = "SUCCESS" if result.returncode == 0 else f"FAILED (Exit Code: {result.returncode})"
        
        output = f"[{status}]\n"
        output += "--- STDOUT & STDERR ---\n"
        output += (result.stdout + result.stderr).strip() or "（无输出内容）"
        
        return output
        
    except subprocess.TimeoutExpired:
        return "[ERROR] Command execution timeout (5 minutes limit reached)"
    except Exception as e:
        return f"[ERROR] Command execution failed: {str(e)}"


def read_file(file_path: str) -> str:
    """
    读取文件内容
    
    Args:
        file_path: 文件路径（相对于工作目录）
        
    Returns:
        文件内容字符串
    """
    try:
        safe_file_path = safe_path(file_path)
        with open(safe_file_path, 'r', encoding='utf-8') as file:
            return file.read()
    except FileNotFoundError:
        return f"[ERROR] File not found: {file_path}"
    except PermissionError:
        return f"[ERROR] Permission denied when reading: {file_path}"
    except UnicodeDecodeError:
        return f"[ERROR] Unable to decode file (not UTF-8): {file_path}"
    except Exception as e:
        return f"[ERROR] Failed to read file: {str(e)}"


def write_file(file_path: str, content: str) -> str:
    """
    写入文件内容
    
    Args:
        file_path: 文件路径（相对于工作目录）
        content: 要写入的字符串内容
        
    Returns:
        成功或失败消息
    """
    try:
        safe_file_path = safe_path(file_path)
        dir_name = os.path.dirname(safe_file_path)
        os.makedirs(dir_name, exist_ok=True)
        
        with open(safe_file_path, 'w', encoding='utf-8') as file:
            file.write(content)
        
        return f"[SUCCESS] File written successfully: {file_path} ({len(content)} bytes)"
    except PermissionError:
        return f"[ERROR] Permission denied when writing: {file_path}"
    except Exception as e:
        return f"[ERROR] Failed to write file: {str(e)}"


def search_github_repos(keyword: str, language: str = "") -> str:
    """
    直接搜索 GitHub 仓库（使用 GitHub API）
    
    Args:
        keyword: 搜索关键词，如 'AI', 'LLM', 'machine learning', 'deep learning'
        language: 可选，编程语言，如 'Python', 'JavaScript', 'Rust'
        
    Returns:
        格式化的搜索结果字符串
    """
    try:
        query = keyword
        if language:
            query += f" language:{language}"
        
        url = f"https://api.github.com/search/repositories?q={requests.utils.quote(query)}&sort=stars&order=desc&per_page=8"
        headers = {
            'User-Agent': 'Code-Agent/1.0 (+https://github.com)',
            'Accept': 'application/vnd.github.v3+json'
        }
        
        response = requests.get(url, headers=headers, timeout=15)
        response.raise_for_status()
        data = response.json()
        
        if data.get('total_count', 0) == 0:
            return f"[GitHub 搜索结果 - 关键词: {keyword}]\n未找到相关项目"
        
        results = []
        for item in data.get('items', [])[:8]:
            results.append(
                f"项目名: {item['full_name']}\n"
                f"描述: {item.get('description', '无描述') or '无描述'}\n"
                f"Stars: {item['stargazers_count']:,} | Forks: {item.get('forks_count', 0):,}\n"
                f"语言: {item.get('language', '未知') or '未知'}\n"
                f"链接: {item['html_url']}\n"
            )
        
        return f"[GitHub 搜索结果 - 关键词: {keyword}] (共 {data.get('total_count', 0):,} 个结果)\n" + "\n---\n".join(results)
        
    except requests.exceptions.Timeout:
        return "[ERROR] GitHub API request timeout"
    except requests.exceptions.RequestException as e:
        return f"[ERROR] GitHub API request failed: {str(e)}"
    except Exception as e:
        return f"[ERROR] GitHub 搜索失败: {str(e)}"


def extract_text_from_html(html_content: str) -> str:
    """
    从 HTML 内容中提取纯文本
    
    Args:
        html_content: HTML 字符串
        
    Returns:
        纯文本字符串
    """
    try:
        soup = BeautifulSoup(html_content, 'html.parser')
        for script in soup(["script", "style", "nav", "footer", "header"]):
            script.decompose()
        text = soup.get_text(separator='\n', strip=True)
        lines = (line.strip() for line in text.splitlines())
        chunks = (phrase.strip() for line in lines for phrase in line.split("  "))
        text = '\n'.join(chunk for chunk in chunks if chunk)
        return text
    except Exception as e:
        return f"[ERROR] HTML parsing failed: {str(e)}"


def fetch_page(url: str) -> str:
    """
    获取网页内容（自动提取纯文本）
    
    Args:
        url: 要获取的网页 URL
        
    Returns:
        格式化的页面内容字符串
    """
    MAX_CONTENT_LENGTH = 3000
    
    try:
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
            'Accept-Language': 'zh-CN,zh;q=0.9,en;q=0.8',
        }
        response = requests.get(url, headers=headers, timeout=15)
        response.raise_for_status()
        response.encoding = response.apparent_encoding
        
        content = extract_text_from_html(response.text)
        
        if len(content) > MAX_CONTENT_LENGTH:
            truncated = content[:MAX_CONTENT_LENGTH]
            return (
                f"[页面获取成功]\n"
                f"URL: {url}\n"
                f"内容长度: {len(content)} 字符 (已截断至 {MAX_CONTENT_LENGTH} 字符)\n"
                f"---\n{truncated}\n--- 内容已截断 ---"
            )
        else:
            return (
                f"[页面获取成功]\n"
                f"URL: {url}\n"
                f"---\n{content}\n--- 内容结束 ---"
            )
            
    except requests.exceptions.Timeout:
        return f"[ERROR] 页面请求超时: {url}"
    except requests.exceptions.RequestException as e:
        return f"[ERROR] 页面获取失败\nURL: {url}\n错误: {str(e)}"
    except Exception as e:
        return f"[ERROR] 页面获取失败\nURL: {url}\n错误: {str(e)}"


def get_github_repo_info(repo_url: str) -> str:
    """
    获取 GitHub 仓库详细信息（包括项目描述和 README）
    
    Args:
        repo_url: GitHub 仓库 URL，格式如 https://github.com/username/repo
        
    Returns:
        格式化的仓库信息字符串
    """
    MAX_CONTENT_LENGTH = 4000
    
    try:
        match = re.search(r'github\.com/([^/]+)/([^/]+)', repo_url)
        if not match:
            return f"[错误] 不是有效的 GitHub 仓库URL: {repo_url}"
        
        owner, repo = match.groups()
        repo = repo.rstrip('/')
        
        headers = {
            'User-Agent': 'Code-Agent/1.0 (+https://github.com)',
            'Accept': 'application/vnd.github.v3+json'
        }
        
        api_url = f"https://api.github.com/repos/{owner}/{repo}"
        api_response = requests.get(api_url, headers=headers, timeout=10)
        
        repo_info = ""
        if api_response.status_code == 200:
            data = api_response.json()
            repo_info = (
                f"[仓库信息]\n"
                f"名称: {data.get('name', 'N/A')}\n"
                f"描述: {data.get('description', '无描述') or 'N/A'}\n"
                f"Stars: {data.get('stargazers_count', 0):,}\n"
                f"Forks: {data.get('forks_count', 0):,}\n"
                f"语言: {data.get('language', 'N/A') or 'N/A'}\n"
                f"最后更新: {data.get('updated_at', 'N/A')}\n"
                f"项目主页: {data.get('html_url', 'N/A')}\n"
            )
        else:
            repo_info = f"[仓库信息] 获取失败 (HTTP {api_response.status_code})\n"
        
        readme_content = ""
        for branch in ['master', 'main', 'dev']:
            readme_url = f"https://raw.githubusercontent.com/{owner}/{repo}/{branch}/README.md"
            try:
                readme_response = requests.get(readme_url, headers=headers, timeout=10)
                if readme_response.status_code == 200:
                    readme_content = readme_response.text
                    if len(readme_content) > MAX_CONTENT_LENGTH:
                        readme_content = readme_content[:MAX_CONTENT_LENGTH] + "\n--- README已截断 ---"
                    break
            except Exception:
                continue
        
        if not readme_content:
            readme_content = "无法获取 README 文件"
        
        result = repo_info + "\n[README 内容]\n" + readme_content
        return result
        
    except Exception as e:
        return f"[GitHub 仓库获取失败]\nURL: {repo_url}\n错误: {str(e)}"


# ==================== 待办事项管理器 ====================

class TodoManager:
    """
    待办事项管理器 - 支持三种状态管理
    
    状态说明：
    - pending:    待完成 ⬜
    - in_progress: 进行中 🔄
    - done:       已完成 ✅
    
    限制：
    - 最多 5 个任务
    - 最多 1 个进行中的任务
    """
    
    MAX_TASKS = 5
    ALLOWED_STATUSES = ["pending", "in_progress", "done"]
    
    def __init__(self):
        self.items: List[Dict[str, Any]] = []
    
    def update(self, items: List[Dict[str, Any]]) -> str:
        """
        更新整个待办列表 - 验证状态约束
        
        Args:
            items: 任务列表，每个任务包含 id, text, status
            
        Returns:
            渲染后的待办列表字符串
        """
        validated: List[Dict[str, Any]] = []
        in_progress_count = 0
        
        if len(items) > self.MAX_TASKS:
            raise ValueError(f"待办列表最多只能有 {self.MAX_TASKS} 个任务")
        
        for item in items:
            status = item.get("status", "pending")
            if status == "in_progress":
                in_progress_count += 1
            validated.append({
                "id": item["id"],
                "text": item["text"],
                "status": status
            })
        
        if in_progress_count > 1:
            raise ValueError("Only one task can be in_progress")
        
        self.items = validated
        return self.render()
    
    def add(self, text: str) -> str:
        """
        添加新任务
        
        Args:
            text: 任务描述文字
            
        Returns:
            渲染后的待办列表字符串
        """
        if len(self.items) >= self.MAX_TASKS:
            raise ValueError(f"待办列表已满，最多只能有 {self.MAX_TASKS} 个任务")
        
        has_in_progress = any(item["status"] == "in_progress" for item in self.items)
        if has_in_progress:
            raise ValueError("当前有进行中的任务，请先完成或暂停当前任务再添加新任务")
        
        new_id = max([item["id"] for item in self.items], default=0) + 1
        self.items.append({
            "id": new_id,
            "text": text,
            "status": "pending"
        })
        return self.render()
    
    def change_status(self, item_id: int, status: str) -> str:
        """
        更改任务状态
        
        Args:
            item_id: 任务 ID 编号
            status: 新状态 (pending | in_progress | done)
            
        Returns:
            渲染后的待办列表字符串
        """
        if status not in self.ALLOWED_STATUSES:
            raise ValueError(f"Invalid status. Use: {', '.join(self.ALLOWED_STATUSES)}")
        
        if status == "in_progress":
            has_in_progress = any(
                item["status"] == "in_progress" and item["id"] != item_id
                for item in self.items
            )
            if has_in_progress:
                raise ValueError("Only one task can be in_progress")
        
        for item in self.items:
            if item["id"] == item_id:
                item["status"] = status
                return self.render()
        
        raise ValueError(f"Task {item_id} not found")
    
    def delete(self, item_id: int) -> str:
        """
        删除任务
        
        Args:
            item_id: 任务 ID 编号
            
        Returns:
            渲染后的待办列表字符串
        """
        self.items = [item for item in self.items if item["id"] != item_id]
        return self.render()
    
    def render(self) -> str:
        """
        渲染待办列表为可读的字符串格式
        
        Returns:
            格式化的待办列表字符串
        """
        if not self.items:
            return "[待办列表为空]"
        
        status_emoji = {
            "pending": "⬜",
            "in_progress": "🔄",
            "done": "✅"
        }
        
        lines = ["[待办列表]"]
        for item in self.items:
            emoji = status_emoji.get(item["status"], "⬜")
            lines.append(f"  {emoji} [#{item['id']}] {item['text']} ({item['status']})")
        
        pending = sum(1 for i in self.items if i["status"] == "pending")
        in_progress = sum(1 for i in self.items if i["status"] == "in_progress")
        done = sum(1 for i in self.items if i["status"] == "done")
        
        lines.append(f"\n统计: 待完成 {pending} | 进行中 {in_progress} | 已完成 {done}")
        return "\n".join(lines)


# 全局待办管理器实例
todo_manager = TodoManager()


def todo_add(text: str) -> str:
    """添加新任务到待办列表"""
    try:
        return todo_manager.add(text)
    except Exception as e:
        return f"添加失败: {str(e)}"


def todo_change_status(item_id: int, status: str) -> str:
    """更改任务状态"""
    try:
        return todo_manager.change_status(item_id, status)
    except Exception as e:
        return f"状态更新失败: {str(e)}"


def todo_delete(item_id: int) -> str:
    """删除任务"""
    try:
        return todo_manager.delete(item_id)
    except Exception as e:
        return f"删除失败: {str(e)}"


def todo_list() -> str:
    """查看当前待办列表"""
    return todo_manager.render()


# ==================== 上下文管理函数 ====================

def estimate_tokens(messages: List[Dict[str, Any]]) -> int:
    """
    粗略估算消息的 token 数量
    
    Args:
        messages: 消息列表
        
    Returns:
        估算的 token 数量
    """
    total = 0
    for msg in messages:
        content = msg.get("content", "")
        if isinstance(content, str):
            total += len(content) // 4
        else:
            total += len(str(content)) // 4
    return total


def auto_compact(messages: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    """
    当 token 超过阈值时自动压缩对话
    
    1. 保存完整对话到磁盘
    2. 调用 LLM 生成对话摘要
    3. 返回压缩后的消息列表
    
    Args:
        messages: 原始消息列表
        
    Returns:
        压缩后的消息列表（保留 system + 摘要 + 最近用户消息）
    """
    token_count = estimate_tokens(messages)
    if token_count < TOKEN_THRESHOLD:
        return messages
    
    print(f"\n[系统提示: 对话较长 ({token_count} tokens)，正在自动压缩...]")
    
    transcript_path = TRANSCRIPT_DIR / f"transcript_{int(time.time())}.jsonl"
    try:
        with open(transcript_path, "w", encoding="utf-8") as f:
            for msg in messages:
                f.write(json.dumps(msg, default=str, ensure_ascii=False) + "\n")
    except Exception as e:
        print(f"[警告: 无法保存对话记录 - {str(e)}]")
    
    system_msg = messages[0] if messages and messages[0].get("role") == "system" else None
    last_user_msg = None
    for msg in reversed(messages):
        if msg.get("role") == "user":
            last_user_msg = msg
            break
    
    summary_prompt = f"""请总结以下对话内容，保持关键信息和上下文连续性：

要求：
1. 保留关键决策、问题、答案、工具调用结果摘要
2. 用简洁的中文描述，控制在 500 字以内
3. 保持对话逻辑顺序，便于后续继续对话

对话内容：
{json.dumps(messages[1:], default=str, ensure_ascii=False)[:8000]}
"""
    
    try:
        response = requests.post(
            f"{OLLAMA_HOST}/api/chat",
            json={
                "model": DEFAULT_MODEL,
                "messages": [{"role": "user", "content": summary_prompt}],
                "stream": False,
            },
            timeout=120,
        )
        response.raise_for_status()
        result = response.json()
        summary = result.get("message", {}).get("content", "摘要生成失败")
        
        print(f"[对话已保存至: {transcript_path}]")
        
        new_messages = []
        if system_msg:
            new_messages.append(system_msg)
        new_messages.append({
            "role": "user",
            "content": f"[对话已自动压缩，完整记录已保存]\n\n对话摘要：\n{summary}"
        })
        if last_user_msg and last_user_msg.get("content") != summary_prompt:
            new_messages.append(last_user_msg)
        
        return new_messages
        
    except Exception as e:
        print(f"[摘要生成失败: {str(e)}，将保留原对话]")
        return messages


def micro_compact(messages: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    """
    LLM 调用前的轻量级压缩
    
    把旧的 tool result 变成占位符，只保留最近 KEEP_RECENT_TOOLS 个完整结果
    
    Args:
        messages: 消息列表
        
    Returns:
        压缩后的消息列表
    """
    tool_results = []
    for i, msg in enumerate(messages):
        if msg.get("role") == "tool":
            tool_results.append((i, msg.get("tool_name", "unknown")))
    
    if len(tool_results) <= KEEP_RECENT_TOOLS:
        return messages
    
    for i, tool_name in tool_results[:-KEEP_RECENT_TOOLS]:
        if len(messages[i].get("content", "")) > 50:
            messages[i]["content"] = f"[Previous: used {tool_name}]"
    
    return messages


# ==================== 工具 Schema 定义 ====================

tools_schema: List[Dict[str, Any]] = [
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
                "required": ["text"]
            }
        }
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
                    "status": {"type": "string", "description": "pending | in_progress | done"}
                },
                "required": ["item_id", "status"]
            }
        }
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
                "required": ["item_id"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "todo_list",
            "description": "查看当前完整待办列表，包括所有任务的状态和统计信息"
        }
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
                        "description": "搜索关键词，如 'AI', 'LLM', 'machine learning', 'deep learning', 'chatbot'"
                    },
                    "language": {
                        "type": "string",
                        "description": "可选：编程语言过滤，如 Python, JavaScript, Rust"
                    }
                },
                "required": ["keyword"]
            }
        }
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
                        "description": "GitHub 仓库URL，格式如 https://github.com/username/repo"
                    }
                },
                "required": ["repo_url"]
            }
        }
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
                "required": ["command"]
            }
        }
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
                "required": ["file_path"]
            }
        }
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
                    "content": {"type": "string", "description": "内容"}
                },
                "required": ["file_path", "content"]
            }
        }
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
                "required": ["url"]
            }
        }
    },
]

# 可用函数字典映射
available_functions: Dict[str, Any] = {
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

# 全局消息列表
messages: List[Dict[str, Any]] = []


# ==================== LLM 通信函数 ====================

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
    """
    for attempt in range(max_retries):
        try:
            response = requests.post(
                f"{OLLAMA_HOST}/api/chat",
                json={
                    "model": DEFAULT_MODEL,
                    "messages": messages,
                    "tools": tools_schema,
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


# ==================== 主循环 ====================

def agentloop() -> None:
    """
    Agent 主交互循环
    
    负责：
    - 接受用户输入
    - 显示待办列表
    - 调用 LLM 处理
    - 执行工具调用
    - 管理对话历史
    """
    global messages
    messages = select_roleplay()
    
    rounds_since_todo = 0
 
    while True:
        try:
            user_input = input("user: ")
        except EOFError:
            print("\n[检测到 EOF，退出程序]")
            break
        except KeyboardInterrupt:
            print("\n[用户中断，退出程序]")
            break
            
        if user_input.lower() in ['exit', 'quit', 'q']:
            print("[退出程序]")
            break
        
        if not user_input.strip():
            continue
        
        messages.append({"role": "user", "content": user_input})
        
        messages = auto_compact(messages)
        
        print("\n📋 当前待办列表:")
        print(todo_list())
        print()
        
        iterations = 0
        while iterations < MAX_ITERATIONS:
            iterations += 1
            
            rounds_since_todo += 1
            
            if len(messages) > MAX_HISTORY + 2:
                messages = [messages[0], messages[1]] + messages[-MAX_HISTORY:]
            
            try:
                resp = chat_with_retry(micro_compact(messages))
            except Exception as e:
                print(f"\n[错误: {str(e)}]")
                print("[提示: 请确保 Ollama 服务正在运行，并且模型已正确安装]")
                break
            
            message = resp.get("message", {})
            if message.get("content"):
                print(f"\nassistant: {message['content']}\n")
            
            messages.append(message)
            
            tool_calls = message.get("tool_calls", [])
            if not tool_calls:
                break
                
            for tool_call in tool_calls:
                func_name = tool_call["function"]["name"]
                func_args = tool_call["function"]["arguments"]
                
                if func_name in available_functions:
                    func = available_functions[func_name]
                    print(f"[执行工具: {func_name} {func_args}]")
                    
                    try:
                        output = func(**func_args)
                        if len(str(output)) > 2000:
                            output = str(output)[:2000] + "\n...(内容过长已截断)"
                    except Exception as e:
                        output = f"执行出错: {str(e)}"
                        
                    print(f"[工具输出]: {output}")
                    messages.append({
                        "role": "tool",
                        "tool_name": func_name,
                        "content": str(output),
                    })
                    
                    if func_name.startswith('todo_'):
                        rounds_since_todo = 0
        
        if iterations >= MAX_ITERATIONS:
            print("\n[系统提示: 达到最大思考深度，已强制停止]")


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


if __name__ == "__main__":
    if not check_ollama_available():
        print(f"[错误] 无法连接到 Ollama 服务: {OLLAMA_HOST}")
        print("[提示] 请确保 Ollama 已安装并正在运行：")
        print("       1. 安装: https://ollama.ai/")
        print("       2. 启动: ollama serve")
        print(f"       3. 拉取模型: ollama pull {DEFAULT_MODEL}")
        sys.exit(1)
    
    agentloop()
