"""Flask 애플리케이션 설정 및 초기화"""
import os
from flask import Flask
from datetime import datetime
from models import TodoStatus
from repositories import TodoRepository
from services import TodoService
from utils import TodoSerializer
from api import register_routes


class TodoApp:
    """TODO 애플리케이션 클래스"""

    def __init__(self, app_name: str = __name__):
        """
        애플리케이션 초기화
        
        Args:
            app_name: Flask 앱 이름
        """
        # 프로젝트 루트 경로
        base_path = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        
        self.app = Flask(
            app_name,
            template_folder=os.path.join(base_path, 'templates'),
            static_folder=os.path.join(base_path, 'static')
        )
        self._configure_app()
        
        # 의존성 주입
        self.repository = TodoRepository()
        self.service = TodoService(self.repository)
        self.serializer = TodoSerializer()
        
        # 라우트 등록
        self._register_routes()

    def _configure_app(self) -> None:
        """Flask 앱 설정"""
        self.app.config['JSON_AS_ASCII'] = False  # 한글 지원

    def _register_routes(self) -> None:
        """라우트 등록"""
        register_routes(self.app, self.service, self.serializer)

    def initialize_sample_data(self) -> None:
        """샘플 데이터 초기화"""
        self.service.create_todo(
            "Python Flask 학습",
            datetime(2026, 1, 20),
            TodoStatus.IN_PROGRESS
        )
        self.service.create_todo(
            "TODO 앱 완성",
            datetime(2026, 1, 30),
            TodoStatus.SCHEDULED
        )
        self.service.create_todo(
            "테스트 코드 작성",
            datetime(2026, 1, 15),
            TodoStatus.COMPLETED
        )

    def run(self, debug: bool = True, host: str = '0.0.0.0', port: int = 5000) -> None:
        """
        애플리케이션 실행
        
        Args:
            debug: 디버그 모드 활성화 여부
            host: 바인드할 호스트
            port: 바인드할 포트
        """
        self.app.run(debug=debug, host=host, port=port)
