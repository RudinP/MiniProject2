"""TODO 애플리케이션 엔트리 포인트"""
from app_factory import TodoApp


def main():
    """애플리케이션 실행"""
    # TODO 앱 생성
    todo_app = TodoApp()
    
    # 샘플 데이터 초기화
    todo_app.initialize_sample_data()
    
    # 애플리케이션 실행
    todo_app.run(debug=True, host='0.0.0.0', port=5000)


if __name__ == '__main__':
    main()
