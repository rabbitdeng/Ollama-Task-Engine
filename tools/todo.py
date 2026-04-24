"""
待办事项管理模块
===============

提供三状态待办事项管理功能，支持任务的增删改查和状态切换。

本模块提供：
- TodoManager: 待办事项管理器类
- todo_add: 添加新任务
- todo_change_status: 更改任务状态
- todo_delete: 删除任务
- todo_list: 查看当前待办列表
"""

from typing import List, Dict, Any, Final


class TodoManager:
    """
    待办事项管理器 - 支持三种状态管理
    
    状态说明：
    - pending:    待完成 ⬜
    - in_progress: 进行中 🔄
    - done:       已完成 ✅
    
    限制：
    - 最多 5 个任务
    - 最多 1 个进行中的任务
    
    Example:
        >>> tm = TodoManager()
        >>> tm.add("完成代码重构")
        >>> tm.change_status(1, "in_progress")
        >>> print(tm.render())
        [待办列表]
          🔄 [#1] 完成代码重构 (in_progress)
    """
    
    MAX_TASKS: Final[int] = 5
    ALLOWED_STATUSES: Final[List[str]] = ["pending", "in_progress", "done"]
    
    def __init__(self):
        """初始化空的待办列表"""
        self.items: List[Dict[str, Any]] = []
    
    def update(self, items: List[Dict[str, Any]]) -> str:
        """
        更新整个待办列表 - 验证状态约束
        
        Args:
            items: 任务列表，每个任务包含 id, text, status
            
        Returns:
            渲染后的待办列表字符串
        """
        validated: List[Dict[str, Any]] = []
        in_progress_count = 0
        
        if len(items) > self.MAX_TASKS:
            raise ValueError(f"待办列表最多只能有 {self.MAX_TASKS} 个任务")
        
        for item in items:
            status = item.get("status", "pending")
            if status == "in_progress":
                in_progress_count += 1
            validated.append({
                "id": item["id"],
                "text": item["text"],
                "status": status,
            })
        
        if in_progress_count > 1:
            raise ValueError("Only one task can be in_progress")
        
        self.items = validated
        return self.render()
    
    def add(self, text: str) -> str:
        """
        添加新任务
        
        Args:
            text: 任务描述文字
            
        Returns:
            渲染后的待办列表字符串
            
        Raises:
            ValueError: 如果任务数量超限或当前有进行中的任务
        """
        if len(self.items) >= self.MAX_TASKS:
            raise ValueError(f"待办列表已满，最多只能有 {self.MAX_TASKS} 个任务")
        
        has_in_progress = any(item["status"] == "in_progress" for item in self.items)
        if has_in_progress:
            raise ValueError("当前有进行中的任务，请先完成或暂停当前任务再添加新任务")
        
        new_id = max([item["id"] for item in self.items], default=0) + 1
        self.items.append({
            "id": new_id,
            "text": text,
            "status": "pending",
        })
        return self.render()
    
    def change_status(self, item_id: int, status: str) -> str:
        """
        更改任务状态
        
        Args:
            item_id: 任务 ID 编号
            status: 新状态 (pending | in_progress | done)
            
        Returns:
            渲染后的待办列表字符串
            
        Raises:
            ValueError: 如果状态无效，或尝试同时创建多个进行中任务，
                       或任务 ID 不存在
        """
        if status not in self.ALLOWED_STATUSES:
            raise ValueError(f"Invalid status. Use: {', '.join(self.ALLOWED_STATUSES)}")
        
        if status == "in_progress":
            has_in_progress = any(
                item["status"] == "in_progress" and item["id"] != item_id
                for item in self.items
            )
            if has_in_progress:
                raise ValueError("Only one task can be in_progress")
        
        for item in self.items:
            if item["id"] == item_id:
                item["status"] = status
                return self.render()
        
        raise ValueError(f"Task {item_id} not found")
    
    def delete(self, item_id: int) -> str:
        """
        删除任务
        
        Args:
            item_id: 任务 ID 编号
            
        Returns:
            渲染后的待办列表字符串
        """
        self.items = [item for item in self.items if item["id"] != item_id]
        return self.render()
    
    def render(self) -> str:
        """
        渲染待办列表为可读的字符串格式
        
        Returns:
            格式化的待办列表字符串，包含统计信息
        """
        if not self.items:
            return "[待办列表为空]"
        
        status_emoji = {
            "pending": "⬜",
            "in_progress": "🔄",
            "done": "✅",
        }
        
        lines = ["[待办列表]"]
        for item in self.items:
            emoji = status_emoji.get(item["status"], "⬜")
            lines.append(f"  {emoji} [#{item['id']}] {item['text']} ({item['status']})")
        
        pending = sum(1 for i in self.items if i["status"] == "pending")
        in_progress = sum(1 for i in self.items if i["status"] == "in_progress")
        done = sum(1 for i in self.items if i["status"] == "done")
        
        lines.append(f"\n统计: 待完成 {pending} | 进行中 {in_progress} | 已完成 {done}")
        return "\n".join(lines)


todo_manager = TodoManager()


def todo_add(text: str) -> str:
    """
    添加新任务到待办列表
    
    Args:
        text: 任务描述
        
    Returns:
        更新后的待办列表字符串或错误信息
    """
    try:
        return todo_manager.add(text)
    except Exception as e:
        return f"添加失败: {str(e)}"


def todo_change_status(item_id: int, status: str) -> str:
    """
    更改任务状态
    
    Args:
        item_id: 任务 ID 编号
        status: 新状态 (pending | in_progress | done)
        
    Returns:
        更新后的待办列表字符串或错误信息
    """
    try:
        return todo_manager.change_status(item_id, status)
    except Exception as e:
        return f"状态更新失败: {str(e)}"


def todo_delete(item_id: int) -> str:
    """
    删除任务
    
    Args:
        item_id: 任务 ID 编号
        
    Returns:
        更新后的待办列表字符串或错误信息
    """
    try:
        return todo_manager.delete(item_id)
    except Exception as e:
        return f"删除失败: {str(e)}"


def todo_list() -> str:
    """
    查看当前待办列表
    
    Returns:
        格式化的待办列表字符串
    """
    return todo_manager.render()


__all__ = [
    'TodoManager',
    'todo_manager',
    'todo_add',
    'todo_change_status',
    'todo_delete',
    'todo_list',
]
