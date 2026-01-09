from typing import List, Optional
from datetime import datetime
from .todo import TodoItem, TodoStatus


class TodoRepository:
    """TODO 항목을 메모리에 저장하고 관리하는 저장소"""

    def __init__(self):
        """저장소 초기화"""
        self._todos: dict[str, TodoItem] = {}

    def create(self, content: str, target_date: datetime, status: TodoStatus = TodoStatus.SCHEDULED) -> TodoItem:
        """새로운 TODO 항목 생성"""
        todo = TodoItem(
            content=content,
            target_date=target_date,
            status=status
        )
        self._todos[todo.id] = todo
        return todo

    def get_by_id(self, todo_id: str) -> Optional[TodoItem]:
        """ID로 TODO 항목 조회"""
        return self._todos.get(todo_id)

    def get_all(self) -> List[TodoItem]:
        """모든 TODO 항목 조회"""
        return list(self._todos.values())

    def get_by_status(self, status: TodoStatus) -> List[TodoItem]:
        """상태별로 TODO 항목 조회"""
        return [todo for todo in self._todos.values() if todo.status == status]

    def update(self, todo_id: str, content: Optional[str] = None, 
               target_date: Optional[datetime] = None, 
               status: Optional[TodoStatus] = None) -> Optional[TodoItem]:
        """TODO 항목 수정"""
        todo = self._todos.get(todo_id)
        if not todo:
            return None

        if content is not None:
            todo.content = content
        if target_date is not None:
            todo.target_date = target_date
        if status is not None:
            todo.status = status

        todo.updated_at = datetime.now()
        return todo

    def delete(self, todo_id: str) -> bool:
        """TODO 항목 삭제"""
        if todo_id in self._todos:
            del self._todos[todo_id]
            return True
        return False

    def clear_all(self) -> None:
        """모든 TODO 항목 삭제"""
        self._todos.clear()

    def count(self) -> int:
        """TODO 항목 개수 반환"""
        return len(self._todos)
