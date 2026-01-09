"""예외 처리 클래스"""


class TodoException(Exception):
    """TODO 관련 기본 예외"""
    pass


class TodoNotFoundError(TodoException):
    """TODO를 찾을 수 없을 때 발생"""
    pass


class InvalidTodoError(TodoException):
    """유효하지 않은 TODO 정보일 때 발생"""
    pass


class TodoValidationError(TodoException):
    """TODO 검증 실패 시 발생"""
    pass
