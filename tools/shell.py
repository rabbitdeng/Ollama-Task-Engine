"""
Shell 命令执行模块
=================

提供安全的 Shell 命令执行功能，带有超时保护。

本模块提供：
- bash: 执行 Shell 命令并返回格式化结果
"""

import subprocess
from typing import Final
from config import BASE_DIR

COMMAND_TIMEOUT: Final[int] = 300  # 5 分钟超时


def bash(command: str) -> str:
    """
    执行 Shell 命令
    
    Args:
        command: 要执行的 shell 命令字符串
        
    Returns:
        包含执行状态和输出的格式化字符串
        
    Example:
        >>> bash("ls -la")
        "[SUCCESS]
        --- STDOUT & STDERR ---
        total 100
        drwxr-xr-x  5 user  group   160 Dec 20 10:00 .
        ..."
        
    Note:
        - 命令在工作目录内执行
        - 超时时间为 5 分钟
        - 返回结果包含状态和合并的标准输出/错误
    """
    try:
        result = subprocess.run(
            command,
            shell=True,
            capture_output=True,
            text=True,
            cwd=BASE_DIR,
            timeout=COMMAND_TIMEOUT,
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


__all__ = ['bash']
