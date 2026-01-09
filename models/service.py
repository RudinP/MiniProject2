"""TODO 비즈니스 로직 계층"""
from typing import List, Optional
from datetime import datetime
from .todo import TodoItem, TodoStatus
from .repository import TodoRepository
from .exceptions import TodoNotFoundError, InvalidTodoError


class TodoService:
    """TODO 관련 비즈니스 로직을 담당하는 서비스 클래스"""

    def __init__(self, repository: TodoRepository):
        """
        서비스 초기화
        
        Args:
            repository: TodoRepository 인스턴스 (의존성 주입)
        """
        self._repository = repository

    def create_todo(self, content: str, target_date: datetime, 
                    status: TodoStatus = TodoStatus.SCHEDULED) -> TodoItem:
        """
        새로운 TODO 생성
        
        Args:
            content: TODO 내용
            target_date: 목표 날짜
            status: 상태 (기본값: SCHEDULED)
            
        Returns:
            생성된 TodoItem
            
        Raises:
            InvalidTodoError: 유효하지 않은 입력
        """
        try:
            return self._repository.create(content, target_date, status)
        except ValueError as e:
            raise InvalidTodoError(f"TODO 생성 실패: {str(e)}")

    def get_all_todos(self) -> List[TodoItem]:
        """
        모든 TODO 조회
        
        Returns:
            TodoItem 리스트
        """
        return self._repository.get_all()

    def get_todo_by_id(self, todo_id: str) -> TodoItem:
        """
        특정 TODO 조회
        
        Args:
            todo_id: TODO ID
            
        Returns:
            TodoItem
            
        Raises:
            TodoNotFoundError: TODO를 찾을 수 없음
        """
        todo = self._repository.get_by_id(todo_id)
        if not todo:
            raise TodoNotFoundError(f"ID '{todo_id}'인 TODO를 찾을 수 없습니다")
        return todo

    def get_todos_by_status(self, status: TodoStatus) -> List[TodoItem]:
        """
        상태별 TODO 조회
        
        Args:
            status: TODO 상태
            
        Returns:
            해당 상태의 TodoItem 리스트
        """
        return self._repository.get_by_status(status)

    def update_todo(self, todo_id: str, content: Optional[str] = None,
                    target_date: Optional[datetime] = None,
                    status: Optional[TodoStatus] = None) -> TodoItem:
        """
        TODO 수정
        
        Args:
            todo_id: TODO ID
            content: 새로운 내용 (선택사항)
            target_date: 새로운 목표 날짜 (선택사항)
            status: 새로운 상태 (선택사항)
            
        Returns:
            수정된 TodoItem
            
        Raises:
            TodoNotFoundError: TODO를 찾을 수 없음
            InvalidTodoError: 유효하지 않은 입력
        """
        try:
            todo = self._repository.update(todo_id, content, target_date, status)
            if not todo:
                raise TodoNotFoundError(f"ID '{todo_id}'인 TODO를 찾을 수 없습니다")
            return todo
        except ValueError as e:
            raise InvalidTodoError(f"TODO 수정 실패: {str(e)}")

    def delete_todo(self, todo_id: str) -> bool:
        """
        TODO 삭제
        
        Args:
            todo_id: TODO ID
            
        Returns:
            성공 여부
            
        Raises:
            TodoNotFoundError: TODO를 찾을 수 없음
        """
        if not self._repository.delete(todo_id):
            raise TodoNotFoundError(f"ID '{todo_id}'인 TODO를 찾을 수 없습니다")
        return True

    def get_statistics(self) -> dict:
        """
        TODO 통계 조회
        
        Returns:
            통계 정보 딕셔너리
        """
        all_todos = self.get_all_todos()
        
        return {
            'total': len(all_todos),
            'scheduled': len(self.get_todos_by_status(TodoStatus.SCHEDULED)),
            'in_progress': len(self.get_todos_by_status(TodoStatus.IN_PROGRESS)),
            'completed': len(self.get_todos_by_status(TodoStatus.COMPLETED))
        }

    def reorder_todos(self, order: List[str]) -> None:
        """
        TODO 순서 변경
        
        Args:
            order: 새로운 순서 (ID 리스트)
        """
        self._repository.set_order(order)

    def sort_by_date(self) -> List[TodoItem]:
        """
        TODO를 날짜순으로 정렬
        
        Returns:
            정렬된 TodoItem 리스트
        """
        self._repository.sort_by_date()
        return self._repository.get_all()

    def clear_all_todos(self) -> None:
        """모든 TODO 삭제"""
        self._repository.clear_all()

    def get_todo_count(self) -> int:
        """
        TODO 개수 조회
        
        Returns:
            TODO 개수
        """
        return self._repository.count()
