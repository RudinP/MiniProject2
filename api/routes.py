"""Flask 라우트 정의"""
from flask import render_template, request, jsonify
from datetime import datetime
from models import TodoStatus
from services import TodoService
from utils import TodoSerializer, TodoNotFoundError, InvalidTodoError


def register_routes(app, service: TodoService, serializer: TodoSerializer):
    """
    Flask 앱에 라우트 등록
    
    Args:
        app: Flask 애플리케이션
        service: TodoService 인스턴스
        serializer: TodoSerializer 인스턴스
    """

    # ==================== 페이지 라우트 ====================
    @app.route('/')
    def index():
        """메인 페이지"""
        return render_template('index.html')

    # ==================== API 라우트 ====================
    @app.route('/api/todos', methods=['GET'])
    def get_todos():
        """모든 TODO 항목 조회"""
        try:
            todos = service.get_all_todos()
            return jsonify(serializer.to_list(todos)), 200
        except Exception as e:
            return jsonify({'error': '서버 오류 발생', 'details': str(e)}), 500

    @app.route('/api/todos/<status_filter>', methods=['GET'])
    def get_todos_by_status(status_filter):
        """상태별 TODO 항목 조회"""
        try:
            if status_filter == 'all':
                todos = service.get_all_todos()
            elif status_filter == '예정':
                todos = service.get_todos_by_status(TodoStatus.SCHEDULED)
            elif status_filter == '진행중':
                todos = service.get_todos_by_status(TodoStatus.IN_PROGRESS)
            elif status_filter == '완료':
                todos = service.get_todos_by_status(TodoStatus.COMPLETED)
            else:
                return jsonify({'error': '유효하지 않은 상태'}), 400

            return jsonify(serializer.to_list(todos)), 200
        except Exception as e:
            return jsonify({'error': '서버 오류 발생', 'details': str(e)}), 500

    @app.route('/api/todos', methods=['POST'])
    def create_todo():
        """새로운 TODO 생성"""
        try:
            data = request.get_json()

            # 필수 필드 검증
            if not data or 'content' not in data or 'target_date' not in data:
                return jsonify({'error': '필수 필드가 없습니다'}), 400

            target_date = datetime.fromisoformat(data['target_date'])
            status = data.get('status', TodoStatus.SCHEDULED)

            todo = service.create_todo(data['content'], target_date, status)

            return jsonify(serializer.to_dict(todo)), 201
        except InvalidTodoError as e:
            return jsonify({'error': str(e)}), 400
        except ValueError as e:
            return jsonify({'error': f'입력 오류: {str(e)}'}), 400
        except Exception as e:
            return jsonify({'error': '서버 오류 발생', 'details': str(e)}), 500

    @app.route('/api/todos/<todo_id>', methods=['GET'])
    def get_todo(todo_id):
        """특정 TODO 항목 조회"""
        try:
            todo = service.get_todo_by_id(todo_id)
            return jsonify(serializer.to_dict(todo)), 200
        except TodoNotFoundError as e:
            return jsonify({'error': str(e)}), 404
        except Exception as e:
            return jsonify({'error': '서버 오류 발생', 'details': str(e)}), 500

    @app.route('/api/todos/<todo_id>', methods=['PUT'])
    def update_todo(todo_id):
        """TODO 항목 수정"""
        try:
            data = request.get_json()

            target_date = None
            if 'target_date' in data:
                target_date = datetime.fromisoformat(data['target_date'])

            status = data.get('status')
            content = data.get('content')

            todo = service.update_todo(todo_id, content=content, target_date=target_date, status=status)

            return jsonify(serializer.to_dict(todo)), 200
        except TodoNotFoundError as e:
            return jsonify({'error': str(e)}), 404
        except InvalidTodoError as e:
            return jsonify({'error': str(e)}), 400
        except ValueError as e:
            return jsonify({'error': f'입력 오류: {str(e)}'}), 400
        except Exception as e:
            return jsonify({'error': '서버 오류 발생', 'details': str(e)}), 500

    @app.route('/api/todos/<todo_id>', methods=['DELETE'])
    def delete_todo(todo_id):
        """TODO 항목 삭제"""
        try:
            service.delete_todo(todo_id)
            return jsonify({'message': 'TODO가 삭제되었습니다'}), 200
        except TodoNotFoundError as e:
            return jsonify({'error': str(e)}), 404
        except Exception as e:
            return jsonify({'error': '서버 오류 발생', 'details': str(e)}), 500

    @app.route('/api/todos/reorder', methods=['PUT'])
    def reorder_todos():
        """TODO 항목의 순서 변경"""
        try:
            data = request.get_json()

            if not data or 'order' not in data:
                return jsonify({'error': '순서 정보가 없습니다'}), 400

            service.reorder_todos(data['order'])
            return jsonify({'message': '순서가 업데이트되었습니다'}), 200
        except Exception as e:
            return jsonify({'error': '서버 오류 발생', 'details': str(e)}), 500

    @app.route('/api/todos/sort/date', methods=['PUT'])
    def sort_todos_by_date():
        """TODO 항목을 날짜순으로 정렬"""
        try:
            todos = service.sort_by_date()
            return jsonify(serializer.to_list(todos)), 200
        except Exception as e:
            return jsonify({'error': '서버 오류 발생', 'details': str(e)}), 500

    @app.route('/api/stats', methods=['GET'])
    def get_stats():
        """TODO 통계"""
        try:
            stats = service.get_statistics()
            return jsonify(stats), 200
        except Exception as e:
            return jsonify({'error': '서버 오류 발생', 'details': str(e)}), 500

    # ==================== 에러 핸들러 ====================
    @app.errorhandler(404)
    def not_found(error):
        """404 에러 처리"""
        return jsonify({'error': '페이지를 찾을 수 없습니다'}), 404

    @app.errorhandler(500)
    def server_error(error):
        """500 에러 처리"""
        return jsonify({'error': '서버 오류 발생'}), 500
