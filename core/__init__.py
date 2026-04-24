"""
核心模块
=======

提供 Agent 核心功能：
- 上下文管理（token 估算、对话压缩）
- LLM 客户端
"""

from .context import estimate_tokens, auto_compact, micro_compact
from .llm import (
    chat_with_retry,
    select_roleplay,
    check_ollama_available,
    get_available_functions,
    get_tools_schema,
)

__all__ = [
    'estimate_tokens',
    'auto_compact',
    'micro_compact',
    'chat_with_retry',
    'select_roleplay',
    'check_ollama_available',
    'get_available_functions',
    'get_tools_schema',
]
