"""데이터 전송 객체 (DTO) 클래스"""
from datetime import datetime
from typing import Optional
from pydantic import BaseModel, Field
from .todo import TodoStatus


class CreateTodoRequest(BaseModel):
    """TODO 생성 요청 DTO"""
    content: str = Field(..., min_length=1, description="TODO 내용")
    target_date: str = Field(..., description="목표 날짜 (ISO 형식)")
    status: Optional[str] = Field(default=None, description="상태")


class UpdateTodoRequest(BaseModel):
    """TODO 수정 요청 DTO"""
    content: Optional[str] = Field(None, min_length=1, description="TODO 내용")
    target_date: Optional[str] = Field(None, description="목표 날짜 (ISO 형식)")
    status: Optional[str] = Field(None, description="상태")


class TodoResponse(BaseModel):
    """TODO 응답 DTO"""
    id: str = Field(..., description="고유 ID")
    content: str = Field(..., description="TODO 내용")
    target_date: str = Field(..., description="목표 날짜")
    status: str = Field(..., description="현재 상태")
    created_at: str = Field(..., description="생성 날짜")
    updated_at: str = Field(..., description="수정 날짜")


class TodoListResponse(BaseModel):
    """TODO 목록 응답 DTO"""
    todos: list[TodoResponse] = Field(..., description="TODO 목록")
    total: int = Field(..., description="전체 개수")


class StatsResponse(BaseModel):
    """통계 응답 DTO"""
    total: int = Field(..., description="전체 개수")
    scheduled: int = Field(..., description="예정된 개수")
    in_progress: int = Field(..., description="진행중인 개수")
    completed: int = Field(..., description="완료된 개수")
