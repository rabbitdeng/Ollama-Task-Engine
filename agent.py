from ollama import chat
from ollama import ChatResponse
import subprocess
import os

BASE_DIR = os.path.abspath(os.getcwd())

def safe_path(path: str) -> str:
    """安全路径处理，限制只能在当前目录下访问
    
    Args:
        path: 路径字符串
    
    Returns:
        安全的绝对路径
    
    Raises:
        PermissionError: 如果尝试访问当前目录之外的路径
    """
    path = path.replace("\\", "/")
    abs_path = os.path.abspath(path)
    
    if not abs_path.startswith(BASE_DIR):
        raise PermissionError(f"Access denied: {path} is outside the working directory")

    return abs_path
    
def bash(command: str) -> str:
    """执行bash命令
    
    Args:
        command: 要执行的bash命令
    """
    result = subprocess.run(command, shell=True, capture_output=True, text=True, cwd=BASE_DIR)
    return result.stdout + result.stderr

def read_file(file_path: str) -> str:
    """读取文件内容
    
    Args:
        file_path: 文件路径（相对当前目录）
    
    Returns:
        文件内容字符串
    """
    safe_file_path = safe_path(file_path)
    with open(safe_file_path, 'r', encoding='utf-8') as file:
        return file.read()

def write_file(file_path: str, content: str) -> None:
    """写入文件内容
    
    Args:
        file_path: 文件路径（相对当前目录）
        content: 要写入的内容字符串
    """
    safe_file_path = safe_path(file_path)
    with open(safe_file_path, 'w', encoding='utf-8') as file:
        file.write(content)
available_functions = {
    'bash': bash,
    'read_file': read_file,
    'write_file': write_file,
}

tools = [bash, read_file, write_file]
messages: list[dict] = [
    {
        "role": "system",
        "content": """你是一个能干的代码助手，可以使用工具来帮助用户完成编程任务。

工作规则：
1. 不要直接在回复中写出完整代码，应该使用工具来读取和修改文件
2. 先理解任务 → 查看现有文件 → 分析问题 → 逐步修改 → 验证结果
3. 在每次工具调用之间，简要说明你正在做什么
4. 所有文件操作都必须通过工具完成，不能直接描述文件内容在回复中

可用工具：
- bash: 执行shell命令，适合查看目录、运行测试等
- read_file: 读取文件内容
- write_file: 写入文件内容（覆盖写入）

开始工作吧！""",
    },
]

def agentloop():
    while True:
        user_input = input("user: ")
        messages.append({"role": "user", "content": user_input})
        
        while True:
            resp: ChatResponse = chat(
                model="qwen3.5:9b",
                messages=messages,
                tools=tools,
            )
            
            if resp.message.content:
                print(f"\nassistant: {resp.message.content}\n")
            
            messages.append(resp.message)
            
            if not resp.message.tool_calls:
                break
                
            for tool_call in resp.message.tool_calls:
                if tool_call.function.name in available_functions:
                    func = available_functions[tool_call.function.name]
                    print(f"[执行工具: {tool_call.function.name} {tool_call.function.arguments}]")
                    output = func(**tool_call.function.arguments)
                    print(f"[工具输出]: {output}")
                    messages.append({
                        "role": "tool",
                        "tool_name": tool_call.function.name,
                        "content": output,
                    })

agentloop()