"""TodoItem 직렬화 클래스"""
from datetime import datetime
from .todo import TodoItem
from .dtos import TodoResponse


class TodoSerializer:
    """TodoItem을 다양한 형식으로 변환하는 직렬화 클래스"""

    @staticmethod
    def to_response(todo: TodoItem) -> TodoResponse:
        """TodoItem을 TodoResponse로 변환"""
        return TodoResponse(
            id=todo.id,
            content=todo.content,
            target_date=todo.target_date.isoformat(),
            status=todo.status,
            created_at=todo.created_at.isoformat(),
            updated_at=todo.updated_at.isoformat()
        )

    @staticmethod
    def to_dict(todo: TodoItem) -> dict:
        """TodoItem을 딕셔너리로 변환 (Flask JSON 응답용)"""
        return {
            'id': todo.id,
            'content': todo.content,
            'target_date': todo.target_date.isoformat(),
            'status': todo.status,
            'created_at': todo.created_at.isoformat(),
            'updated_at': todo.updated_at.isoformat()
        }

    @staticmethod
    def to_list(todos: list[TodoItem]) -> list[dict]:
        """TodoItem 리스트를 딕셔너리 리스트로 변환"""
        return [TodoSerializer.to_dict(todo) for todo in todos]
