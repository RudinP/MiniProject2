# TODO 애플리케이션 - OOP 기반 구조

## 프로젝트 개요
이 프로젝트는 OOP(객체지향 프로그래밍) 원칙을 따르는 Flask 기반의 TODO 관리 애플리케이션입니다.

## 아키텍처

### 계층 구조 (Layered Architecture)

```
┌─────────────────────────────────┐
│        Views Layer (views.py)   │  <- Flask 라우트, HTTP 요청/응답 처리
└──────────────┬──────────────────┘
               │
┌──────────────▼──────────────────┐
│      Service Layer (service.py) │  <- 비즈니스 로직
└──────────────┬──────────────────┘
               │
┌──────────────▼──────────────────┐
│   Repository Layer (repository.py) <- 데이터 접근
└──────────────┬──────────────────┘
               │
┌──────────────▼──────────────────┐
│     Model Layer (todo.py)       │  <- 데이터 정의
└─────────────────────────────────┘
```

### 주요 클래스 및 책임

#### 1. **Model Layer** (`models/todo.py`)
- `TodoStatus`: TODO의 상태를 정의하는 열거형
- `TodoItem`: TODO 항목의 데이터 모델 (Pydantic 사용)
  - 데이터 검증: content, target_date 유효성 검사
  - 자동 ID 생성, 타임스탬프 관리

#### 2. **Repository Layer** (`models/repository.py`)
- `TodoRepository`: 데이터 저장 및 조회 담당
  - CRUD 작업: create, get_by_id, get_all, update, delete
  - 상태별 조회: get_by_status
  - 정렬/순서 관리: sort_by_date, set_order
  - **책임**: 데이터 영속성 처리 (메모리 기반)

#### 3. **Service Layer** (`models/service.py`)
- `TodoService`: 비즈니스 로직 구현
  - Repository를 주입받아 데이터 접근 (의존성 주입)
  - 고수준 API 제공: create_todo, get_all_todos 등
  - 예외 처리: TodoNotFoundError, InvalidTodoError 발생
  - **책임**: 비즈니스 규칙 적용, 예외 처리

#### 4. **Serializer** (`models/serializer.py`)
- `TodoSerializer`: TodoItem을 다양한 형식으로 변환
  - to_dict(): 딕셔너리로 변환
  - to_response(): TodoResponse DTO로 변환
  - to_list(): 리스트 변환
  - **책임**: 데이터 직렬화

#### 5. **DTOs** (`models/dtos.py`)
- 요청/응답 데이터 모델 정의
  - `CreateTodoRequest`: TODO 생성 요청
  - `UpdateTodoRequest`: TODO 수정 요청
  - `TodoResponse`: TODO 응답
  - `StatsResponse`: 통계 응답
  - **책임**: API 계약(contract) 정의

#### 6. **Exceptions** (`models/exceptions.py`)
- 커스텀 예외 클래스
  - `TodoException`: 기본 예외
  - `TodoNotFoundError`: TODO 없음
  - `InvalidTodoError`: 유효하지 않은 데이터
  - `TodoValidationError`: 검증 실패
  - **책임**: 예외 처리 표준화

#### 7. **Views Layer** (`views.py`)
- Flask 라우트 정의
- HTTP 요청/응답 처리
- Service 호출 및 응답 변환
- 에러 핸들링
- **책임**: HTTP 인터페이스 구현

#### 8. **Application Factory** (`app_factory.py`)
- `TodoApp`: Flask 애플리케이션 팩토리 클래스
  - 앱 설정 관리
  - 의존성 주입
  - 라우트 등록
  - 초기 데이터 설정
  - **책임**: 애플리케이션 초기화 및 조립

#### 9. **Entry Point** (`app.py`)
- 애플리케이션 진입점
- main() 함수로 앱 실행
- **책임**: 애플리케이션 시작

---

## OOP 원칙 적용

### 1. **단일 책임 원칙 (Single Responsibility Principle)**
- 각 클래스는 하나의 책임만 가짐
  - Repository: 데이터 접근
  - Service: 비즈니스 로직
  - Serializer: 직렬화
  - Views: HTTP 처리

### 2. **개방-폐쇄 원칙 (Open-Closed Principle)**
- 확장에는 열려있고 수정에는 닫혀있음
- 새로운 Repository 구현 추가 가능 (예: 데이터베이스 연동)
- Service는 Repository 인터페이스에만 의존

### 3. **리스코프 치환 원칙 (Liskov Substitution Principle)**
- Repository의 다양한 구현이 가능
- 기존 코드 수정 없이 새로운 Repository 사용 가능

### 4. **인터페이스 분리 원칙 (Interface Segregation Principle)**
- 작은 크기의 인터페이스 설계
- Service는 필요한 메서드만 호출

### 5. **의존성 역전 원칙 (Dependency Inversion Principle)**
- Service는 Repository의 구체적 구현이 아닌 추상화에 의존
- 생성자 주입을 통한 의존성 주입 패턴 사용

---

## 사용 예시

### 애플리케이션 실행
```python
# app.py
from app_factory import TodoApp

todo_app = TodoApp()
todo_app.initialize_sample_data()
todo_app.run(debug=True)
```

### Service 사용
```python
from models import TodoRepository, TodoService, TodoStatus
from datetime import datetime, timedelta

# 의존성 주입
repository = TodoRepository()
service = TodoService(repository)

# TODO 생성
todo = service.create_todo(
    "프로젝트 완료",
    datetime.now() + timedelta(days=7),
    TodoStatus.SCHEDULED
)

# TODO 조회
all_todos = service.get_all_todos()

# TODO 수정
updated = service.update_todo(todo.id, content="수정된 내용")

# TODO 삭제
service.delete_todo(todo.id)

# 통계
stats = service.get_statistics()
```

---

## API 엔드포인트

### TODO 관리
- `GET /api/todos` - 모든 TODO 조회
- `GET /api/todos/<status>` - 상태별 조회
- `POST /api/todos` - TODO 생성
- `GET /api/todos/<id>` - 특정 TODO 조회
- `PUT /api/todos/<id>` - TODO 수정
- `DELETE /api/todos/<id>` - TODO 삭제

### 추가 기능
- `PUT /api/todos/reorder` - 순서 변경
- `PUT /api/todos/sort/date` - 날짜순 정렬
- `GET /api/stats` - 통계 조회

---

## 테스트

### 테스트 구조
```
tests/
├── test_repository.py
│   ├── TestTodoItem      - 모델 테스트
│   ├── TestTodoRepository - 저장소 테스트
│   ├── TestTodoService   - 서비스 테스트
│   └── TestTodoSerializer - 직렬화 테스트
```

### 테스트 실행
```bash
pytest tests/test_repository.py -v
```

---

## 의존성

- Flask 3.0.0 - 웹 프레임워크
- Pydantic 2.5.0 - 데이터 검증
- Pytest 7.4.3 - 테스트 프레임워크

---

## 프로젝트 확장

### 데이터베이스 연동
기존 코드 수정 없이 새로운 Repository 구현:
```python
class DatabaseRepository(TodoRepository):
    """데이터베이스 기반 Repository"""
    def create(self, content, target_date, status):
        # 데이터베이스에 저장
        pass
```

### 추가 기능
- 태그/카테고리 지원
- 우선순위 레벨
- 반복 작업
- 알림 기능

---

## 파일 구조

```
MiniProject2/
├── app.py                 # 애플리케이션 진입점
├── app_factory.py         # 애플리케이션 팩토리
├── views.py               # Flask 라우트
├── requirements.txt       # 의존성
├── models/
│   ├── __init__.py
│   ├── todo.py           # 모델 정의
│   ├── repository.py     # 저장소 계층
│   ├── service.py        # 비즈니스 로직 계층
│   ├── serializer.py     # 직렬화
│   ├── dtos.py           # 데이터 전송 객체
│   └── exceptions.py     # 커스텀 예외
├── tests/
│   ├── __init__.py
│   └── test_repository.py # 테스트
├── templates/
│   └── index.html
└── static/
    ├── css/
    │   └── style.css
    └── js/
        └── script.js
```

---

## 라이선스
MIT License
