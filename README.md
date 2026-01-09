# Flask 기반 TODO 애플리케이션 - OOP 구조
<img width="1131" height="837" alt="image" src="https://github.com/user-attachments/assets/8824ce45-ed9a-47fa-8e14-eace125a9d96" />

## 프로젝트 개요
**AI Agent 적응 프로젝트**

이 프로젝트는 **AI Agent 개발에 적응하기 위한** Flask 기반의 TODO 관리 애플리케이션입니다.
OOP(객체지향 프로그래밍) 원칙을 따르는 **계층 기반 아키텍처(Layered Architecture)** 로 설계되어 있으며, 명확한 책임 분리와 의존성 주입을 통해 유지보수성과 확장성을 높인 구조입니다.

### 목표
- Flask를 이용한 RESTful API 개발
- OOP 설계 원칙 적용 (SOLID)
- 계층 기반 아키텍처 구현
- AI Agent와의 상호작용을 위한 확장 가능한 구조

---

## 아키텍처

### 계층 기반 아키텍처 (Layered Architecture) - 프로젝트 구조

```
project/
├── app.py                          # 애플리케이션 진입점
│
├── app/
│   ├── __init__.py
│   └── app_factory.py             # ← Application Factory 패턴
│                                    (의존성 주입 및 앱 초기화)
│
├── api/
│   ├── __init__.py
│   └── routes.py                  # ← Presentation Layer
│                                    (HTTP 요청/응답 처리)
│
├── services/
│   ├── __init__.py
│   └── todo_service.py            # ← Business Logic Layer
│                                    (비즈니스 로직 구현)
│
├── repositories/
│   ├── __init__.py
│   └── todo_repository.py         # ← Data Access Layer
│                                    (데이터 영속성)
│
├── models/
│   ├── __init__.py
│   └── todo.py                    # ← Domain Model Layer
│                                    (데이터 정의)
│
├── utils/
│   ├── __init__.py
│   ├── dtos.py                    # ← Data Transfer Objects (DTO)
│   ├── exceptions.py              # ← Custom Exceptions
│   └── serializer.py              # ← Object Serializer
│
├── templates/                      # ← Frontend (HTML)
│   └── index.html
│
└── static/                         # ← Frontend (CSS, JS)
    ├── css/
    │   └── style.css
    └── js/
        └── script.js
```

### 계층 구조도 (Data Flow)

```
┌─────────────────────────────────────────────────────┐
│         Presentation Layer (API Routes)             │  
│  - HTTP 요청 처리                                    │
│  - 응답 직렬화                                       │
│  - 에러 핸들링                                       │
│  (api/routes.py)                                    │
└──────────────────┬──────────────────────────────────┘
                   │ (요청/응답)
                   ▼
┌─────────────────────────────────────────────────────┐
│       Business Logic Layer (Services)               │
│  - 비즈니스 규칙 적용                                │
│  - 유효성 검증                                       │
│  - 예외 처리                                         │
│  (services/todo_service.py)                         │
└──────────────────┬──────────────────────────────────┘
                   │ (데이터 조작)
                   ▼
┌─────────────────────────────────────────────────────┐
│       Data Access Layer (Repositories)              │
│  - CRUD 작업                                        │
│  - 데이터 조회/저장                                  │
│  - 쿼리 실행                                        │
│  (repositories/todo_repository.py)                  │
└──────────────────┬──────────────────────────────────┘
                   │ (데이터 접근)
                   ▼
┌─────────────────────────────────────────────────────┐
│        Domain Model Layer (Models)                  │
│  - 데이터 구조 정의                                  │
│  - 비즈니스 엔티티                                   │
│  (models/todo.py)                                  │
└─────────────────────────────────────────────────────┘
```

---

## 각 계층의 역할 및 책임

### 1. **Presentation Layer** (`api/routes.py`)
- **역할**: HTTP 요청/응답 처리
- **책임**:
  - Flask 라우트 정의
  - HTTP 메서드 처리 (GET, POST, PUT, DELETE)
  - 요청 데이터 유효성 검증
  - 응답 직렬화 및 포매팅
  - 에러 응답 처리
- **의존성**: Service 클래스

### 2. **Business Logic Layer** (`services/todo_service.py`)
- **역할**: 핵심 비즈니스 로직 구현
- **책임**:
  - 고수준의 비즈니스 규칙 적용
  - 데이터 유효성 검증
  - 비즈니스 예외 처리
  - 여러 Repository 작업 조율
- **의존성**: Repository, DTO, Custom Exceptions
- **의존성 주입**: 생성자를 통해 Repository 주입

### 3. **Data Access Layer** (`repositories/todo_repository.py`)
- **역할**: 데이터 접근 및 영속성 관리
- **책임**:
  - CRUD 작업 (Create, Read, Update, Delete)
  - 데이터 조회/저장/수정/삭제
  - 쿼리 실행 및 결과 반환
  - 데이터 필터링 및 정렬
- **캡슐화**: 내부 데이터 구조 추상화

### 4. **Domain Model Layer** (`models/todo.py`)
- **역할**: 비즈니스 엔티티 정의
- **책임**:
  - 데이터 구조 정의
  - 데이터 타입 검증
  - 비즈니스 규칙 포함 (상태, 유효성)
  - 객체 직렬화/역직렬화

### 5. **Utility Layer** (`utils/`)
- **dtos.py**: API 요청/응답 데이터 정의
  - `CreateTodoRequest`: TODO 생성 요청
  - `UpdateTodoRequest`: TODO 수정 요청
  - `TodoResponse`: TODO 응답
- **exceptions.py**: 커스텀 예외 클래스
  - `TodoNotFoundError`, `InvalidTodoError`, `TodoValidationError`
- **serializer.py**: 객체 직렬화
  - Domain Model을 DTO로 변환

### 6. **Application Factory** (`app/app_factory.py`)
- **역할**: Flask 애플리케이션 초기화
- **책임**:
  - 앱 설정 관리
  - 의존성 주입 (Repository, Service)
  - 라우트 등록
  - 초기 데이터 설정
- **패턴**: Factory 패턴 적용

### 7. **Entry Point** (`app.py`)
- **역할**: 애플리케이션 진입점
- **책임**: 애플리케이션 시작

---

## OOP 원칙 적용

### 1. **단일 책임 원칙 (Single Responsibility Principle)**
각 클래스는 하나의 책임만 가집니다.
- `Repository`: 데이터 접근만 담당
- `Service`: 비즈니스 로직만 담당
- `Serializer`: 직렬화만 담당
- `Routes`: HTTP 처리만 담당

### 2. **개방-폐쇄 원칙 (Open-Closed Principle)**
확장에는 열려있고 수정에는 닫혀있습니다.
- 새로운 Repository 구현 추가 가능 (예: 데이터베이스 연동)
- Service는 Repository 인터페이스에만 의존

### 3. **리스코프 치환 원칙 (Liskov Substitution Principle)**
Repository의 다양한 구현이 가능합니다.
- 기존 코드 수정 없이 새로운 Repository 사용 가능

### 4. **인터페이스 분리 원칙 (Interface Segregation Principle)**
작은 크기의 인터페이스를 설계합니다.
- Service는 필요한 메서드만 호출

### 5. **의존성 역전 원칙 (Dependency Inversion Principle)**
Service는 Repository의 구체적 구현이 아닌 추상화에 의존합니다.
- 생성자 주입을 통한 의존성 주입 패턴 사용

---

## 사용 예시

### 애플리케이션 실행
```python
# app.py
from app.app_factory import TodoApp

todo_app = TodoApp()
todo_app.initialize_sample_data()
todo_app.run(debug=True)
```

### Service 사용
```python
from models.todo import TodoStatus
from repositories.todo_repository import TodoRepository
from services.todo_service import TodoService
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

## 라이선스
MIT License
