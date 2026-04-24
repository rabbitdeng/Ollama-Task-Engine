"""
路径安全模块
===========

提供安全的路径处理功能，防止目录遍历攻击。

本模块提供：
- safe_path: 验证并规范化路径，确保其位于工作目录内
"""

import os
from config import BASE_DIR


def safe_path(path: str) -> str:
    """
    安全路径处理 - 防止目录遍历攻击
    
    通过以下方式确保路径安全：
    1. 替换 Windows 反斜杠为正斜杠
    2. 转换为绝对路径
    3. 解析符号链接得到真实路径
    4. 验证路径是否位于工作目录内
    
    Args:
        path: 要处理的路径字符串（可以是相对或绝对路径）
        
    Returns:
        验证后的绝对真实路径
        
    Raises:
        PermissionError: 如果路径指向工作目录之外
        
    Example:
        >>> safe_path("file.txt")
        "/path/to/workdir/file.txt"
        
        >>> safe_path("../secret.txt")
        PermissionError: Access denied: ../secret.txt is pointing outside the working directory
    """
    path = path.replace("\\", "/")
    abs_path = os.path.abspath(path)
    real_path = os.path.realpath(abs_path)
    
    if not real_path.startswith(BASE_DIR):
        raise PermissionError(f"Access denied: {path} is pointing outside the working directory")

    return real_path


__all__ = ['safe_path']
