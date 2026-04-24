"""
文件操作模块
===========

提供安全的文件读写功能，带有路径安全检查。

本模块提供：
- read_file: 读取文件内容
- write_file: 写入文件内容（支持自动创建父目录）
"""

import os
from utils.path import safe_path


def read_file(file_path: str) -> str:
    """
    读取文件内容
    
    Args:
        file_path: 文件路径（相对于工作目录）
        
    Returns:
        文件内容字符串，或错误信息
        
    Example:
        >>> read_file("agent.py")
        "#!/usr/bin/env python3
        ..."
        
    Note:
        - 路径会经过安全检查，防止目录遍历
        - 文件必须使用 UTF-8 编码
        - 找不到文件或权限不足时会返回友好的错误信息
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
        
    Example:
        >>> write_file("test.txt", "Hello, World!")
        "[SUCCESS] File written successfully: test.txt (13 bytes)"
        
    Note:
        - 路径会经过安全检查，防止目录遍历
        - 父目录会自动创建（如果不存在）
        - 文件如果存在将被覆盖
        - 文件使用 UTF-8 编码
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


__all__ = ['read_file', 'write_file']
