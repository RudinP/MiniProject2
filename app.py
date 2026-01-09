from flask import Flask, render_template, request, jsonify
from datetime import datetime
from models import TodoRepository, TodoStatus

app = Flask(__name__)
app.config['JSON_AS_ASCII'] = False  # 한글 지원

# 전역 저장소 (애플리케이션 실행 중 유지)
todo_repo = TodoRepository()

# 샘플 데이터 추가 (개발용)
def init_sample_data():
    """샘플 데이터 초기화"""
    todo_repo.create("Python Flask 학습", datetime(2026, 1, 20), TodoStatus.IN_PROGRESS)
    todo_repo.create("TODO 앱 완성", datetime(2026, 1, 30), TodoStatus.SCHEDULED)
    todo_repo.create("테스트 코드 작성", datetime(2026, 1, 15), TodoStatus.COMPLETED)


@app.route('/')
def index():
    """메인 페이지"""
    return render_template('index.html')


@app.route('/api/todos', methods=['GET'])
def get_todos():
    """모든 TODO 항목 조회"""
    todos = todo_repo.get_all()
    # 날짜 기준으로 정렬
    todos = sorted(todos, key=lambda x: x.target_date)
    
    return jsonify([{
        'id': todo.id,
        'content': todo.content,
        'target_date': todo.target_date.isoformat(),
        'status': todo.status,
        'created_at': todo.created_at.isoformat(),
        'updated_at': todo.updated_at.isoformat()
    } for todo in todos])


@app.route('/api/todos/<status_filter>', methods=['GET'])
def get_todos_by_status(status_filter):
    """상태별 TODO 항목 조회"""
    if status_filter == 'all':
        todos = todo_repo.get_all()
    elif status_filter == '예정':
        todos = todo_repo.get_by_status(TodoStatus.SCHEDULED)
    elif status_filter == '진행중':
        todos = todo_repo.get_by_status(TodoStatus.IN_PROGRESS)
    elif status_filter == '완료':
        todos = todo_repo.get_by_status(TodoStatus.COMPLETED)
    else:
        return jsonify({'error': '유효하지 않은 상태'}), 400
    
    # 날짜 기준으로 정렬
    todos = sorted(todos, key=lambda x: x.target_date)
    
    return jsonify([{
        'id': todo.id,
        'content': todo.content,
        'target_date': todo.target_date.isoformat(),
        'status': todo.status,
        'created_at': todo.created_at.isoformat(),
        'updated_at': todo.updated_at.isoformat()
    } for todo in todos])


@app.route('/api/todos', methods=['POST'])
def create_todo():
    """새로운 TODO 생성"""
    data = request.get_json()
    
    # 필수 필드 검증
    if not data or 'content' not in data or 'target_date' not in data:
        return jsonify({'error': '필수 필드가 없습니다'}), 400
    
    try:
        target_date = datetime.fromisoformat(data['target_date'])
        status = data.get('status', TodoStatus.SCHEDULED)
        
        todo = todo_repo.create(data['content'], target_date, status)
        
        return jsonify({
            'id': todo.id,
            'content': todo.content,
            'target_date': todo.target_date.isoformat(),
            'status': todo.status,
            'created_at': todo.created_at.isoformat(),
            'updated_at': todo.updated_at.isoformat()
        }), 201
    except ValueError as e:
        return jsonify({'error': str(e)}), 400
    except Exception as e:
        return jsonify({'error': '서버 오류 발생'}), 500


@app.route('/api/todos/<todo_id>', methods=['GET'])
def get_todo(todo_id):
    """특정 TODO 항목 조회"""
    todo = todo_repo.get_by_id(todo_id)
    
    if not todo:
        return jsonify({'error': 'TODO를 찾을 수 없습니다'}), 404
    
    return jsonify({
        'id': todo.id,
        'content': todo.content,
        'target_date': todo.target_date.isoformat(),
        'status': todo.status,
        'created_at': todo.created_at.isoformat(),
        'updated_at': todo.updated_at.isoformat()
    })


@app.route('/api/todos/<todo_id>', methods=['PUT'])
def update_todo(todo_id):
    """TODO 항목 수정"""
    data = request.get_json()
    
    try:
        target_date = None
        if 'target_date' in data:
            target_date = datetime.fromisoformat(data['target_date'])
        
        status = data.get('status')
        content = data.get('content')
        
        todo = todo_repo.update(todo_id, content=content, target_date=target_date, status=status)
        
        if not todo:
            return jsonify({'error': 'TODO를 찾을 수 없습니다'}), 404
        
        return jsonify({
            'id': todo.id,
            'content': todo.content,
            'target_date': todo.target_date.isoformat(),
            'status': todo.status,
            'created_at': todo.created_at.isoformat(),
            'updated_at': todo.updated_at.isoformat()
        })
    except ValueError as e:
        return jsonify({'error': str(e)}), 400
    except Exception as e:
        return jsonify({'error': '서버 오류 발생'}), 500


@app.route('/api/todos/<todo_id>', methods=['DELETE'])
def delete_todo(todo_id):
    """TODO 항목 삭제"""
    result = todo_repo.delete(todo_id)
    
    if not result:
        return jsonify({'error': 'TODO를 찾을 수 없습니다'}), 404
    
    return jsonify({'message': 'TODO가 삭제되었습니다'}), 200


@app.route('/api/todos/reorder', methods=['PUT'])
def reorder_todos():
    """TODO 항목의 순서 변경"""
    data = request.get_json()
    
    if not data or 'order' not in data:
        return jsonify({'error': '순서 정보가 없습니다'}), 400
    
    # 현재는 메모리 저장소이므로 순서를 유지하기 위해 내부 dict를 재구성
    new_order = data['order']
    new_todos = {}
    
    for todo_id in new_order:
        if todo_id in todo_repo._todos:
            new_todos[todo_id] = todo_repo._todos[todo_id]
    
    # 기존 항목들 중 순서 목록에 없는 것들 추가 (만약 있다면)
    for todo_id, todo in todo_repo._todos.items():
        if todo_id not in new_todos:
            new_todos[todo_id] = todo
    
    todo_repo._todos = new_todos
    
    return jsonify({'message': '순서가 업데이트되었습니다'}), 200


@app.route('/api/stats', methods=['GET'])
def get_stats():
    """TODO 통계"""
    all_todos = todo_repo.get_all()
    
    return jsonify({
        'total': len(all_todos),
        'scheduled': len(todo_repo.get_by_status(TodoStatus.SCHEDULED)),
        'in_progress': len(todo_repo.get_by_status(TodoStatus.IN_PROGRESS)),
        'completed': len(todo_repo.get_by_status(TodoStatus.COMPLETED))
    })


@app.errorhandler(404)
def not_found(error):
    """404 에러 처리"""
    return jsonify({'error': '페이지를 찾을 수 없습니다'}), 404


@app.errorhandler(500)
def server_error(error):
    """500 에러 처리"""
    return jsonify({'error': '서버 오류 발생'}), 500


if __name__ == '__main__':
    # 샘플 데이터 초기화
    init_sample_data()
    
    # 개발 서버 실행
    app.run(debug=True, host='0.0.0.0', port=5000)
