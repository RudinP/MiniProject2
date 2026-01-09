from enum import Enum
from datetime import datetime
from typing import Optional
from uuid import uuid4
from pydantic import BaseModel, Field, field_validator, ConfigDict


class TodoStatus(str, Enum):
    """TODO 상태 열거형"""
    SCHEDULED = "예정"      # 예정됨
    IN_PROGRESS = "진행중"   # 진행중
    COMPLETED = "완료"      # 완료됨


class TodoItem(BaseModel):
    """TODO 항목 모델"""
    id: str = Field(default_factory=lambda: str(uuid4()), description="고유 ID")
    content: str = Field(..., min_length=1, description="TODO 내용")
    target_date: datetime = Field(..., description="목표 날짜")
    status: TodoStatus = Field(default=TodoStatus.SCHEDULED, description="현재 상태")
    created_at: datetime = Field(default_factory=datetime.now, description="생성 날짜")
    updated_at: datetime = Field(default_factory=datetime.now, description="수정 날짜")

    @field_validator("content")
    @classmethod
    def validate_content(cls, v: str) -> str:
        """내용이 공백이 아닌지 확인"""
        if not v or v.strip() == "":
            raise ValueError("TODO 내용은 비울 수 없습니다.")
        return v.strip()

    @field_validator("target_date")
    @classmethod
    def validate_target_date(cls, v: datetime) -> datetime:
        """목표 날짜가 유효한 날짜인지 확인"""
        if not isinstance(v, datetime):
            raise ValueError("목표 날짜는 datetime 형식이어야 합니다.")
        return v

    def dict(self, **kwargs) -> dict:
        """딕셔너리로 변환 (Flask JSON 응답용)"""
        data = super().model_dump(**kwargs)
        data["created_at"] = self.created_at.isoformat()
        data["updated_at"] = self.updated_at.isoformat()
        data["target_date"] = self.target_date.isoformat()
        return data

    model_config = ConfigDict(
        use_enum_values=True,
        json_schema_extra={
            "example": {
                "id": "550e8400-e29b-41d4-a716-446655440000",
                "content": "프로젝트 완성하기",
                "target_date": "2026-02-15T10:00:00",
                "status": "진행중",
                "created_at": "2026-01-09T15:30:00",
                "updated_at": "2026-01-09T15:30:00"
            }
        }
    )
