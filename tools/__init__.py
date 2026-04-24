"""
工具模块
=======

提供各种功能性工具，包括：
- Shell 命令执行
- 文件读写
- GitHub API 集成
- 网页内容抓取
- 待办事项管理
"""

from .shell import bash
from .fileio import read_file, write_file
from .github import search_github_repos, get_github_repo_info
from .web import fetch_page, extract_text_from_html
from .todo import (
    todo_add,
    todo_change_status,
    todo_delete,
    todo_list,
    TodoManager,
    todo_manager,
)

__all__ = [
    'bash',
    'read_file',
    'write_file',
    'search_github_repos',
    'get_github_repo_info',
    'fetch_page',
    'extract_text_from_html',
    'todo_add',
    'todo_change_status',
    'todo_delete',
    'todo_list',
    'TodoManager',
    'todo_manager',
]
