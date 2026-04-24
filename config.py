"""
配置模块
========

管理应用程序的所有配置常量和环境变量。

本模块提供：
- 基础路径配置
- 模型和 API 配置
- 上下文管理阈值
- 对话历史存储
"""

import os
from pathlib import Path
from typing import Final

# ==================== 基础路径配置 ====================
"""工作目录 - 所有文件操作都限制在此目录内"""
BASE_DIR: Final[str] = os.path.abspath(os.getcwd())

# ==================== 模型配置 ====================
"""默认使用的 Ollama 模型名称"""
DEFAULT_MODEL: Final[str] = "qwen3.5:9b"

"""Ollama 服务地址，可通过环境变量 OLLAMA_HOST 覆盖"""
OLLAMA_HOST: Final[str] = os.environ.get("OLLAMA_HOST", "http://localhost:11434")

# ==================== 工具结果保留配置 ====================
"""保留最近多少个工具调用的完整结果（不压缩）"""
KEEP_RECENT_TOOLS: Final[int] = 3

# ==================== Token 阈值配置 ====================
"""触发自动对话压缩的 Token 阈值（粗略估计）"""
TOKEN_THRESHOLD: Final[int] = 8000

# ==================== 迭代限制配置 ====================
"""单次思考最大迭代次数，防止无限循环"""
MAX_ITERATIONS: Final[int] = 20

# ==================== 历史记录配置 ====================
"""保留在内存中的最大对话历史条数"""
MAX_HISTORY: Final[int] = 16

# ==================== 对话持久化配置 ====================
"""对话历史 JSONL 文件存储目录"""
TRANSCRIPT_DIR: Final[Path] = Path(BASE_DIR) / "transcripts"
TRANSCRIPT_DIR.mkdir(exist_ok=True)

# ==================== 工具导出 ====================
__all__ = [
    'BASE_DIR',
    'DEFAULT_MODEL',
    'OLLAMA_HOST',
    'KEEP_RECENT_TOOLS',
    'TOKEN_THRESHOLD',
    'MAX_ITERATIONS',
    'MAX_HISTORY',
    'TRANSCRIPT_DIR',
]
