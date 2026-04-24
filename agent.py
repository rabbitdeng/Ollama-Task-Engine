#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Code Agent - 基于 Ollama 的代码助手工具
==========================================

这是主程序入口文件。

功能特性：
- 代码文件管理（读取、写入、修改）
- Shell 命令执行
- GitHub 项目搜索
- 网页内容抓取
- 待办事项管理（Todo List）
- 上下文自动压缩
- 对话历史持久化

项目结构：
- config.py: 配置常量
- utils/: 工具函数（路径安全等）
- tools/: 功能模块（文件、Shell、GitHub、Web、待办）
- core/: 核心模块（上下文管理、LLM 客户端）

Authors: Code Agent Team
Date: 2025
"""

import sys
from typing import List, Dict, Any
from config import (
    MAX_ITERATIONS,
    MAX_HISTORY,
    DEFAULT_MODEL,
)
from tools import todo_list
from core import (
    chat_with_retry,
    select_roleplay,
    check_ollama_available,
    auto_compact,
    micro_compact,
    get_available_functions,
)


def agentloop() -> None:
    """
    Agent 主交互循环
    
    负责：
    - 接受用户输入
    - 显示待办列表
    - 调用 LLM 处理
    - 执行工具调用
    - 管理对话历史
    
    工作流程：
    1. 用户输入
    2. 自动压缩对话（如果需要）
    3. 显示当前待办列表
    4. 迭代思考（最多 MAX_ITERATIONS 次）
       - 调用 LLM
       - 处理工具调用
       - 或结束思考
    5. 循环回到 1
    """
    messages: List[Dict[str, Any]] = select_roleplay()
    
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
                
            available_functions = get_available_functions()
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


def main() -> None:
    """
    程序主入口
    
    负责：
    - 检查 Ollama 服务可用性
    - 启动主交互循环
    """
    if not check_ollama_available():
        print(f"[错误] 无法连接到 Ollama 服务: {DEFAULT_MODEL}")
        print("[提示] 请确保 Ollama 已安装并正在运行：")
        print("       1. 安装: https://ollama.ai/")
        print("       2. 启动: ollama serve")
        print(f"       3. 拉取模型: ollama pull {DEFAULT_MODEL}")
        sys.exit(1)
    
    agentloop()


if __name__ == "__main__":
    main()
