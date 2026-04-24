"""
上下文管理模块
=============

提供对话上下文管理和压缩功能，防止 token 溢出。

本模块提供：
- estimate_tokens: 估算消息的 token 数量
- auto_compact: 当 token 超过阈值时自动压缩对话
- micro_compact: LLM 调用前的轻量级工具结果压缩
"""

import json
import time
import requests
from typing import List, Dict, Any
from config import (
    TOKEN_THRESHOLD,
    KEEP_RECENT_TOOLS,
    TRANSCRIPT_DIR,
    OLLAMA_HOST,
    DEFAULT_MODEL,
)


def estimate_tokens(messages: List[Dict[str, Any]]) -> int:
    """
    粗略估算消息的 token 数量
    
    简单算法：每个字符约等于 0.25 token
    
    Args:
        messages: 消息列表
        
    Returns:
        估算的 token 数量
        
    Example:
        >>> messages = [{"role": "user", "content": "Hello"}]
        >>> estimate_tokens(messages)
        1
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
    
    压缩策略：
    1. 保存完整对话到磁盘
    2. 调用 LLM 生成对话摘要
    3. 返回压缩后的消息列表（保留系统提示 + 摘要 + 最近用户消息）
    
    Args:
        messages: 原始消息列表
        
    Returns:
        压缩后的消息列表（或原列表如果未超限）
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
            "content": f"[对话已自动压缩，完整记录已保存]\n\n对话摘要：\n{summary}",
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
    
    把旧的 tool result 变成占位符，只保留最近 KEEP_RECENT_TOOLS 个完整结果。
    这样可以减少 token 消耗但保持上下文连贯性。
    
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


__all__ = ['estimate_tokens', 'auto_compact', 'micro_compact']
