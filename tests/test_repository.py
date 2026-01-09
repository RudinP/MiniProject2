import pytest
from datetime import datetime, timedelta
from models import TodoItem, TodoStatus
from repositories import TodoRepository
from services import TodoService
from utils import TodoSerializer, TodoNotFoundError, InvalidTodoError


class TestTodoItem:
    """TodoItem 모델 테스트"""

    def test_create_todo_item(self):
        """TODO 항목 생성 테스트"""
        target_date = datetime.now() + timedelta(days=7)
        todo = TodoItem(
            content="테스트 항목",
            target_date=target_date,
            status=TodoStatus.SCHEDULED
        )
        
        assert todo.content == "테스트 항목"
        assert todo.target_date == target_date
        assert todo.status == TodoStatus.SCHEDULED
        assert todo.id is not None
        assert todo.created_at is not None
        assert todo.updated_at is not None

    def test_todo_item_with_default_status(self):
        """기본 상태(SCHEDULED)로 TODO 항목 생성"""
        target_date = datetime.now() + timedelta(days=7)
        todo = TodoItem(content="항목", target_date=target_date)
        
        assert todo.status == TodoStatus.SCHEDULED

    def test_todo_item_content_validation_empty(self):
        """빈 내용으로 TODO 생성 시 실패"""
        target_date = datetime.now() + timedelta(days=7)
        
        with pytest.raises(ValueError):
            TodoItem(content="", target_date=target_date)

    def test_todo_item_content_validation_whitespace(self):
        """공백만 있는 내용으로 TODO 생성 시 실패"""
        target_date = datetime.now() + timedelta(days=7)
        
        with pytest.raises(ValueError):
            TodoItem(content="   ", target_date=target_date)

    def test_todo_item_content_trim(self):
        """TODO 내용 양옆 공백 제거"""
        target_date = datetime.now() + timedelta(days=7)
        todo = TodoItem(content="  테스트  ", target_date=target_date)
        
        assert todo.content == "테스트"

    def test_todo_item_dict_serialization(self):
        """TODO를 딕셔너리로 변환"""
        target_date = datetime.now() + timedelta(days=7)
        todo = TodoItem(
            content="테스트",
            target_date=target_date,
            status=TodoStatus.IN_PROGRESS
        )
        
        todo_dict = todo.dict()
        
        assert todo_dict["content"] == "테스트"
        assert todo_dict["status"] == "진행중"
        assert "created_at" in todo_dict
        assert "updated_at" in todo_dict
        assert "target_date" in todo_dict


class TestTodoRepository:
    """TodoRepository 클래스 테스트"""

    @pytest.fixture
    def repo(self):
        """각 테스트마다 새로운 저장소 인스턴스 생성"""
        return TodoRepository()

    @pytest.fixture
    def sample_todo_date(self):
        """샘플 목표 날짜"""
        return datetime.now() + timedelta(days=7)

    # CREATE 테스트
    def test_create_todo(self, repo, sample_todo_date):
        """TODO 항목 생성"""
        todo = repo.create("새로운 항목", sample_todo_date)
        
        assert todo is not None
        assert todo.content == "새로운 항목"
        assert todo.target_date == sample_todo_date
        assert todo.status == TodoStatus.SCHEDULED

    def test_create_todo_with_custom_status(self, repo, sample_todo_date):
        """커스텀 상태로 TODO 항목 생성"""
        todo = repo.create("진행중 항목", sample_todo_date, TodoStatus.IN_PROGRESS)
        
        assert todo.status == TodoStatus.IN_PROGRESS

    def test_create_multiple_todos(self, repo, sample_todo_date):
        """여러 TODO 항목 생성"""
        todo1 = repo.create("항목 1", sample_todo_date)
        todo2 = repo.create("항목 2", sample_todo_date + timedelta(days=1))
        todo3 = repo.create("항목 3", sample_todo_date + timedelta(days=2))
        
        assert repo.count() == 3
        assert todo1.id != todo2.id != todo3.id

    # READ 테스트
    def test_get_todo_by_id(self, repo, sample_todo_date):
        """ID로 TODO 조회"""
        created_todo = repo.create("테스트 항목", sample_todo_date)
        
        fetched_todo = repo.get_by_id(created_todo.id)
        
        assert fetched_todo is not None
        assert fetched_todo.id == created_todo.id
        assert fetched_todo.content == "테스트 항목"

    def test_get_todo_by_id_not_found(self, repo):
        """존재하지 않는 ID로 조회"""
        result = repo.get_by_id("non-existent-id")
        
        assert result is None

    def test_get_all_todos(self, repo, sample_todo_date):
        """모든 TODO 조회"""
        repo.create("항목 1", sample_todo_date)
        repo.create("항목 2", sample_todo_date + timedelta(days=1))
        repo.create("항목 3", sample_todo_date + timedelta(days=2))
        
        all_todos = repo.get_all()
        
        assert len(all_todos) == 3

    def test_get_all_todos_empty(self, repo):
        """빈 저장소에서 모든 TODO 조회"""
        all_todos = repo.get_all()
        
        assert len(all_todos) == 0

    def test_get_todos_by_status(self, repo, sample_todo_date):
        """상태별로 TODO 조회"""
        repo.create("항목 1", sample_todo_date, TodoStatus.SCHEDULED)
        repo.create("항목 2", sample_todo_date, TodoStatus.IN_PROGRESS)
        repo.create("항목 3", sample_todo_date, TodoStatus.IN_PROGRESS)
        repo.create("항목 4", sample_todo_date, TodoStatus.COMPLETED)
        
        scheduled = repo.get_by_status(TodoStatus.SCHEDULED)
        in_progress = repo.get_by_status(TodoStatus.IN_PROGRESS)
        completed = repo.get_by_status(TodoStatus.COMPLETED)
        
        assert len(scheduled) == 1
        assert len(in_progress) == 2
        assert len(completed) == 1

    # UPDATE 테스트
    def test_update_todo_content(self, repo, sample_todo_date):
        """TODO 내용 수정"""
        todo = repo.create("원본 내용", sample_todo_date)
        original_id = todo.id
        
        updated_todo = repo.update(todo.id, content="수정된 내용")
        
        assert updated_todo is not None
        assert updated_todo.id == original_id
        assert updated_todo.content == "수정된 내용"

    def test_update_todo_status(self, repo, sample_todo_date):
        """TODO 상태 수정"""
        todo = repo.create("항목", sample_todo_date, TodoStatus.SCHEDULED)
        
        updated_todo = repo.update(todo.id, status=TodoStatus.IN_PROGRESS)
        
        assert updated_todo.status == TodoStatus.IN_PROGRESS

    def test_update_todo_target_date(self, repo, sample_todo_date):
        """TODO 목표 날짜 수정"""
        todo = repo.create("항목", sample_todo_date)
        new_date = sample_todo_date + timedelta(days=10)
        
        updated_todo = repo.update(todo.id, target_date=new_date)
        
        assert updated_todo.target_date == new_date

    def test_update_todo_all_fields(self, repo, sample_todo_date):
        """TODO 모든 필드 수정"""
        todo = repo.create("원본", sample_todo_date, TodoStatus.SCHEDULED)
        new_date = sample_todo_date + timedelta(days=5)
        
        updated_todo = repo.update(
            todo.id,
            content="수정됨",
            target_date=new_date,
            status=TodoStatus.COMPLETED
        )
        
        assert updated_todo.content == "수정됨"
        assert updated_todo.target_date == new_date
        assert updated_todo.status == TodoStatus.COMPLETED

    def test_update_todo_updates_timestamp(self, repo, sample_todo_date):
        """TODO 수정 시 updated_at 필드 갱신"""
        todo = repo.create("항목", sample_todo_date)
        original_updated_at = todo.updated_at
        
        # 약간의 시간 경과
        import time
        time.sleep(0.1)
        
        updated_todo = repo.update(todo.id, content="수정됨")
        
        assert updated_todo.updated_at > original_updated_at

    def test_update_non_existent_todo(self, repo):
        """존재하지 않는 TODO 수정"""
        result = repo.update("non-existent-id", content="새 내용")
        
        assert result is None

    # DELETE 테스트
    def test_delete_todo(self, repo, sample_todo_date):
        """TODO 항목 삭제"""
        todo = repo.create("삭제할 항목", sample_todo_date)
        todo_id = todo.id
        
        assert repo.get_by_id(todo_id) is not None
        
        result = repo.delete(todo_id)
        
        assert result is True
        assert repo.get_by_id(todo_id) is None

    def test_delete_non_existent_todo(self, repo):
        """존재하지 않는 TODO 삭제"""
        result = repo.delete("non-existent-id")
        
        assert result is False

    def test_clear_all_todos(self, repo, sample_todo_date):
        """모든 TODO 삭제"""
        repo.create("항목 1", sample_todo_date)
        repo.create("항목 2", sample_todo_date)
        repo.create("항목 3", sample_todo_date)
        
        assert repo.count() == 3
        
        repo.clear_all()
        
        assert repo.count() == 0
        assert len(repo.get_all()) == 0

    # COUNT 테스트
    def test_count_todos(self, repo, sample_todo_date):
        """TODO 개수 반환"""
        assert repo.count() == 0
        
        repo.create("항목 1", sample_todo_date)
        assert repo.count() == 1
        
        repo.create("항목 2", sample_todo_date)
        assert repo.count() == 2
        
        repo.delete(repo.get_all()[0].id)
        assert repo.count() == 1

    # 통합 테스트
    def test_crud_workflow(self, repo, sample_todo_date):
        """CRUD 전체 워크플로우"""
        # CREATE
        todo = repo.create("프로젝트 완료", sample_todo_date, TodoStatus.SCHEDULED)
        todo_id = todo.id
        
        # READ
        fetched = repo.get_by_id(todo_id)
        assert fetched.content == "프로젝트 완료"
        assert fetched.status == TodoStatus.SCHEDULED
        
        # UPDATE
        updated = repo.update(todo_id, status=TodoStatus.IN_PROGRESS)
        assert updated.status == TodoStatus.IN_PROGRESS
        
        # Verify update
        refetch = repo.get_by_id(todo_id)
        assert refetch.status == TodoStatus.IN_PROGRESS
        
        # DELETE
        deleted = repo.delete(todo_id)
        assert deleted is True
        
        # Verify deletion
        final = repo.get_by_id(todo_id)
        assert final is None


class TestTodoService:
    """TodoService 클래스 테스트"""

    @pytest.fixture
    def service(self):
        """각 테스트마다 새로운 서비스 인스턴스 생성"""
        repository = TodoRepository()
        return TodoService(repository)

    @pytest.fixture
    def sample_todo_date(self):
        """샘플 목표 날짜"""
        return datetime.now() + timedelta(days=7)

    # CREATE 테스트
    def test_create_todo(self, service, sample_todo_date):
        """TODO 생성"""
        todo = service.create_todo("새로운 항목", sample_todo_date)
        
        assert todo is not None
        assert todo.content == "새로운 항목"
        assert todo.status == TodoStatus.SCHEDULED

    def test_create_todo_with_status(self, service, sample_todo_date):
        """커스텀 상태로 TODO 생성"""
        todo = service.create_todo(
            "진행중 항목",
            sample_todo_date,
            TodoStatus.IN_PROGRESS
        )
        
        assert todo.status == TodoStatus.IN_PROGRESS

    def test_create_todo_invalid(self, service, sample_todo_date):
        """유효하지 않은 TODO 생성"""
        with pytest.raises(InvalidTodoError):
            service.create_todo("", sample_todo_date)

    # READ 테스트
    def test_get_all_todos(self, service, sample_todo_date):
        """모든 TODO 조회"""
        service.create_todo("항목 1", sample_todo_date)
        service.create_todo("항목 2", sample_todo_date)
        
        todos = service.get_all_todos()
        
        assert len(todos) == 2

    def test_get_todo_by_id(self, service, sample_todo_date):
        """ID로 TODO 조회"""
        created = service.create_todo("테스트", sample_todo_date)
        
        fetched = service.get_todo_by_id(created.id)
        
        assert fetched.id == created.id

    def test_get_todo_by_id_not_found(self, service):
        """존재하지 않는 TODO 조회"""
        with pytest.raises(TodoNotFoundError):
            service.get_todo_by_id("non-existent-id")

    def test_get_todos_by_status(self, service, sample_todo_date):
        """상태별 TODO 조회"""
        service.create_todo("예정 1", sample_todo_date, TodoStatus.SCHEDULED)
        service.create_todo("예정 2", sample_todo_date, TodoStatus.SCHEDULED)
        service.create_todo("진행중", sample_todo_date, TodoStatus.IN_PROGRESS)
        
        scheduled = service.get_todos_by_status(TodoStatus.SCHEDULED)
        in_progress = service.get_todos_by_status(TodoStatus.IN_PROGRESS)
        
        assert len(scheduled) == 2
        assert len(in_progress) == 1

    # UPDATE 테스트
    def test_update_todo(self, service, sample_todo_date):
        """TODO 수정"""
        todo = service.create_todo("원본", sample_todo_date)
        
        updated = service.update_todo(todo.id, content="수정됨")
        
        assert updated.content == "수정됨"

    def test_update_todo_not_found(self, service):
        """존재하지 않는 TODO 수정"""
        with pytest.raises(TodoNotFoundError):
            service.update_todo("non-existent-id", content="새 내용")

    def test_update_todo_invalid(self, service, sample_todo_date):
        """유효하지 않은 수정"""
        todo = service.create_todo("항목", sample_todo_date)
        
        # Pydantic의 field_validator가 작동하도록 None 대신 공백 문자열 사용
        try:
            updated = service.update_todo(todo.id, content="  ")
            # 공백이 자동으로 제거되는 경우 테스트
            assert updated.content == "항목"  # 공백이 제거되므로 업데이트되지 않음
        except InvalidTodoError:
            # 예외가 발생하는 경우도 유효한 동작
            pass

    # DELETE 테스트
    def test_delete_todo(self, service, sample_todo_date):
        """TODO 삭제"""
        todo = service.create_todo("삭제할 항목", sample_todo_date)
        
        result = service.delete_todo(todo.id)
        
        assert result is True
        with pytest.raises(TodoNotFoundError):
            service.get_todo_by_id(todo.id)

    def test_delete_todo_not_found(self, service):
        """존재하지 않는 TODO 삭제"""
        with pytest.raises(TodoNotFoundError):
            service.delete_todo("non-existent-id")

    # STATISTICS 테스트
    def test_get_statistics(self, service, sample_todo_date):
        """통계 조회"""
        service.create_todo("1", sample_todo_date, TodoStatus.SCHEDULED)
        service.create_todo("2", sample_todo_date, TodoStatus.SCHEDULED)
        service.create_todo("3", sample_todo_date, TodoStatus.IN_PROGRESS)
        service.create_todo("4", sample_todo_date, TodoStatus.COMPLETED)
        
        stats = service.get_statistics()
        
        assert stats['total'] == 4
        assert stats['scheduled'] == 2
        assert stats['in_progress'] == 1
        assert stats['completed'] == 1

    # MANAGEMENT 테스트
    def test_reorder_todos(self, service, sample_todo_date):
        """TODO 순서 변경"""
        todo1 = service.create_todo("1", sample_todo_date)
        todo2 = service.create_todo("2", sample_todo_date)
        todo3 = service.create_todo("3", sample_todo_date)
        
        service.reorder_todos([todo3.id, todo1.id, todo2.id])
        
        todos = service.get_all_todos()
        assert todos[0].id == todo3.id
        assert todos[1].id == todo1.id
        assert todos[2].id == todo2.id

    def test_sort_by_date(self, service, sample_todo_date):
        """날짜순 정렬"""
        service.create_todo("1", sample_todo_date + timedelta(days=3))
        service.create_todo("2", sample_todo_date + timedelta(days=1))
        service.create_todo("3", sample_todo_date + timedelta(days=2))
        
        sorted_todos = service.sort_by_date()
        
        assert sorted_todos[0].target_date < sorted_todos[1].target_date
        assert sorted_todos[1].target_date < sorted_todos[2].target_date

    def test_get_todo_count(self, service, sample_todo_date):
        """TODO 개수 조회"""
        assert service.get_todo_count() == 0
        
        service.create_todo("1", sample_todo_date)
        assert service.get_todo_count() == 1
        
        service.create_todo("2", sample_todo_date)
        assert service.get_todo_count() == 2

    def test_clear_all_todos(self, service, sample_todo_date):
        """모든 TODO 삭제"""
        service.create_todo("1", sample_todo_date)
        service.create_todo("2", sample_todo_date)
        
        assert service.get_todo_count() == 2
        
        service.clear_all_todos()
        
        assert service.get_todo_count() == 0


class TestTodoSerializer:
    """TodoSerializer 클래스 테스트"""

    @pytest.fixture
    def sample_todo(self):
        """샘플 TODO"""
        return TodoItem(
            content="테스트 항목",
            target_date=datetime.now() + timedelta(days=7),
            status=TodoStatus.IN_PROGRESS
        )

    def test_to_dict(self, sample_todo):
        """TodoItem을 딕셔너리로 변환"""
        result = TodoSerializer.to_dict(sample_todo)
        
        assert isinstance(result, dict)
        assert result['content'] == "테스트 항목"
        assert result['status'] == "진행중"
        assert 'id' in result
        assert 'created_at' in result
        assert 'updated_at' in result

    def test_to_response(self, sample_todo):
        """TodoItem을 TodoResponse로 변환"""
        response = TodoSerializer.to_response(sample_todo)
        
        assert response.content == "테스트 항목"
        assert response.status == "진행중"
        assert response.id == sample_todo.id

    def test_to_list(self):
        """TodoItem 리스트를 딕셔너리 리스트로 변환"""
        todos = [
            TodoItem(
                content="항목 1",
                target_date=datetime.now() + timedelta(days=1),
                status=TodoStatus.SCHEDULED
            ),
            TodoItem(
                content="항목 2",
                target_date=datetime.now() + timedelta(days=2),
                status=TodoStatus.IN_PROGRESS
            ),
        ]
        
        result = TodoSerializer.to_list(todos)
        
        assert len(result) == 2
        assert result[0]['content'] == "항목 1"
        assert result[1]['content'] == "항목 2"
