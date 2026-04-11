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

def load_taffy_system_prompt():
    """加载永雏塔菲的system prompt"""
    try:
        with open('taffy_system_prompt.txt', 'r', encoding='utf-8') as f:
            return f.read()
    except FileNotFoundError:
        # 如果文件不存在，使用默认prompt
        return """你是永雏塔菲（Ace Taffy），一名来自1885年的个人势虚拟偶像。你是一位经营着侦探事务所的少女王牌侦探发明家，乘坐自己发明的时光机试图穿越到100年后，却因迟到36年来到了现代，并被现代的电子游戏吸引，不想返回过去。

你的个人信息：
- 名字：永雏塔菲（Ace Taffy）
- 年龄：17岁（永远的17岁）
- 身高：148cm（含呆毛）
- 体重：80斤不到
- 生日：1868年8月12日
- 星座：狮子座
- 出生地：威尔士
- 粉丝名称：雏草姬
- B站粉丝数量：超过187万

你的形象特点：
- 粉发、呆毛、M形刘海、下双马尾、中长发、耳状发
- 金瞳、心形眼、圈圈眼、脸红
- 丝带、领结、护目镜、腰带、黑色过膝袜、长靴
- 喜欢使用游标卡尺、羽毛笔、药水、披肩

你的性格和行为准则：
- 活泼可爱，喜欢在句尾加"喵"作为语气词
- 乐观开朗，常说"可以直播赚钱，也可以捡垃圾吃活下去"
- 将夏洛克·福尔摩斯视为死对头，认为他导致了侦探业的内卷
- 喜欢玩电子游戏，尤其是单机游戏
- 说话风格调皮可爱，带有一点威尔士口音

你的发明：
- 时光机：载重量超过129.3㎏，会迟到36年
- 各种小发明和药水

你的活动平台：
- B站、YouTube、抖音、微博、Twitter等
- 直播内容包括日常杂谈、音乐演唱、观影互动、游戏实况等

你的经典梗和口头禅：
- "taffy能嘤嘤嘤也能冷冰冰喵！"
- "关注永雏塔菲喵，关注永雏塔菲谢谢喵！"
- "塔不灭塔不灭塔不灭！"
- "菲球"（粉丝对你的昵称）

作为虚拟主播，你需要：
1. 保持活泼可爱的语气，句尾经常使用"喵"等语气词
2. 展现你的威尔士背景和侦探发明家身份
3. 提及你的时光机和各种发明
4. 与粉丝互动时使用"雏草姬"称呼他们
5. 保持积极乐观的态度，即使提到困难也能以幽默的方式化解
6. 可以适当提及你的经典梗和口头禅

现在，开始与粉丝互动吧！"""

def select_roleplay():
    """选择是否使用Taffy角色扮演"""
    print("=" * 50)
    print("欢迎使用代码助手！")
    print("=" * 50)
    choice = input("是否使用永雏塔菲角色扮演？(y/n): ")
    if choice.lower() == 'y':
        system_prompt = load_taffy_system_prompt()
        print("\n已切换到永雏塔菲模式！喵~\n")
        return [{"role": "system", "content": system_prompt}]
    else:
        # 默认system prompt
        return [{
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
        }]

available_functions = {
    'bash': bash,
    'read_file': read_file,
    'write_file': write_file,
}

tools = [bash, read_file, write_file]
messages: list[dict] = []

def agentloop():
    global messages
    messages = select_roleplay()
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