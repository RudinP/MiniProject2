from typing import List, Optional
from datetime import datetime
from .todo import TodoItem, TodoStatus


class TodoRepository:
    """TODO 항목을 메모리에 저장하고 관리하는 저장소"""

    def __init__(self):
        """저장소 초기화"""
        self._todos: dict[str, TodoItem] = {}
        self._order: List[str] = []  # TODO ID의 순서를 유지

    def create(self, content: str, target_date: datetime, status: TodoStatus = TodoStatus.SCHEDULED) -> TodoItem:
        """새로운 TODO 항목 생성"""
        todo = TodoItem(
            content=content,
            target_date=target_date,
            status=status
        )
        self._todos[todo.id] = todo
        self._order.append(todo.id)  # 순서 목록에 추가
        return todo

    def get_by_id(self, todo_id: str) -> Optional[TodoItem]:
        """ID로 TODO 항목 조회"""
        return self._todos.get(todo_id)

    def get_all(self) -> List[TodoItem]:
        """모든 TODO 항목 조회 (저장된 순서 유지)"""
        # _order 리스트 기준으로 정렬하여 반환
        return [self._todos[todo_id] for todo_id in self._order if todo_id in self._todos]

    def get_by_status(self, status: TodoStatus) -> List[TodoItem]:
        """상태별로 TODO 항목 조회 (저장된 순서 유지)"""
        return [self._todos[todo_id] for todo_id in self._order if todo_id in self._todos and self._todos[todo_id].status == status]

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
            if todo_id in self._order:
                self._order.remove(todo_id)  # 순서 목록에서도 제거
            return True
        return False

    def clear_all(self) -> None:
        """모든 TODO 항목 삭제"""
        self._todos.clear()
        self._order.clear()  # 순서 목록도 초기화
    
    def set_order(self, order: List[str]) -> None:
        """TODO 순서 설정"""
        self._order = [todo_id for todo_id in order if todo_id in self._todos]
    
    def get_order(self) -> List[str]:
        """TODO 순서 조회"""
        return self._order.copy()
    
    def sort_by_date(self) -> None:
        """날짜순으로 정렬"""
        self._order.sort(key=lambda todo_id: self._todos[todo_id].target_date if todo_id in self._todos else datetime.max)

    def count(self) -> int:
        """TODO 항목 개수 반환"""
        return len(self._todos)
