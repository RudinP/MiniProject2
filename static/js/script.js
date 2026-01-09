// ========================================
// 전역 변수
// ========================================

let currentFilter = 'all';
let currentEditId = null;

// ========================================
// DOM 요소 선택
// ========================================

const todoForm = document.getElementById('todo-form');
const todoContent = document.getElementById('todo-content');
const todoDate = document.getElementById('todo-date');
const todoStatus = document.getElementById('todo-status');
const todoList = document.getElementById('todo-list');
const filterTabs = document.querySelectorAll('.tab-btn');
const editModal = document.getElementById('edit-modal');
const editForm = document.getElementById('edit-form');
const editContent = document.getElementById('edit-content');
const editDate = document.getElementById('edit-date');
const editStatus = document.getElementById('edit-status');
const closeModalBtn = document.getElementById('close-modal');
const cancelEditBtn = document.getElementById('cancel-edit');

// ========================================
// 초기화
// ========================================

document.addEventListener('DOMContentLoaded', () => {
    loadTodos();
    updateStats();
    setupEventListeners();
    setDefaultDate();
});

// ========================================
// 기본 날짜 설정 (내일)
// ========================================

function setDefaultDate() {
    const tomorrow = new Date();
    tomorrow.setDate(tomorrow.getDate() + 1);
    
    const year = tomorrow.getFullYear();
    const month = String(tomorrow.getMonth() + 1).padStart(2, '0');
    const date = String(tomorrow.getDate()).padStart(2, '0');
    const hours = String(tomorrow.getHours()).padStart(2, '0');
    const minutes = String(tomorrow.getMinutes()).padStart(2, '0');
    
    todoDate.value = `${year}-${month}-${date}T${hours}:${minutes}`;
}

// ========================================
// 이벤트 리스너 설정
// ========================================

function setupEventListeners() {
    // 폼 제출
    todoForm.addEventListener('submit', handleAddTodo);

    // 필터 탭
    filterTabs.forEach(tab => {
        tab.addEventListener('click', (e) => {
            filterTabs.forEach(t => t.classList.remove('active'));
            e.target.classList.add('active');
            currentFilter = e.target.dataset.filter;
            loadTodos();
        });
    });

    // 모달 닫기
    closeModalBtn.addEventListener('click', closeModal);
    cancelEditBtn.addEventListener('click', closeModal);
    editModal.addEventListener('click', (e) => {
        if (e.target === editModal) closeModal();
    });

    // 에디트 폼 제출
    editForm.addEventListener('submit', handleEditTodo);
}

// ========================================
// TODO 추가
// ========================================

async function handleAddTodo(e) {
    e.preventDefault();

    if (!todoContent.value.trim() || !todoDate.value) {
        alert('할 일과 목표 날짜를 입력해주세요.');
        return;
    }

    const newTodo = {
        content: todoContent.value.trim(),
        target_date: todoDate.value,
        status: todoStatus.value
    };

    try {
        const response = await fetch('/api/todos', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify(newTodo)
        });

        if (response.ok) {
            todoForm.reset();
            setDefaultDate();
            loadTodos();
            updateStats();
        } else {
            const error = await response.json();
            alert('오류: ' + error.error);
        }
    } catch (error) {
        console.error('Error:', error);
        alert('오류가 발생했습니다.');
    }
}

// ========================================
// TODO 로드
// ========================================

async function loadTodos() {
    try {
        let url = `/api/todos/${currentFilter}`;
        const response = await fetch(url);

        if (!response.ok) throw new Error('Failed to load todos');

        const todos = await response.json();
        renderTodos(todos);
    } catch (error) {
        console.error('Error loading todos:', error);
        todoList.innerHTML = '<div class="empty-state"><div class="empty-state-icon">⚠️</div><div class="empty-state-text">TODO를 불러올 수 없습니다.</div></div>';
    }
}

// ========================================
// TODO 렌더링
// ========================================

function renderTodos(todos) {
    if (todos.length === 0) {
        todoList.innerHTML = '<div class="empty-state"><div class="empty-state-icon">📋</div><div class="empty-state-text">TODO가 없습니다.</div></div>';
        return;
    }

    todoList.innerHTML = todos.map(todo => {
        const targetDate = new Date(todo.target_date);
        const formattedDate = formatDate(targetDate);
        const statusClass = getStatusClass(todo.status);

        return `
            <div class="todo-item ${statusClass}" data-todo-id="${todo.id}" data-todo-content="${escapeHtml(todo.content)}" data-todo-date="${todo.target_date}" data-todo-status="${todo.status}">
                <div class="todo-info">
                    <div class="todo-content">${escapeHtml(todo.content)}</div>
                    <div class="todo-meta">
                        <div class="todo-date">📅 ${formattedDate}</div>
                        <span class="todo-status ${statusClass}">${todo.status}</span>
                    </div>
                </div>
                <div class="todo-actions">
                    <button class="todo-btn edit-btn" onclick="openEditModal('${todo.id}')">편집</button>
                    <button class="todo-btn delete-btn" onclick="deleteTodo('${todo.id}')">삭제</button>
                </div>
            </div>
        `;
    }).join('');
}

// ========================================
// TODO 삭제
// ========================================

async function deleteTodo(todoId) {
    if (!confirm('이 TODO를 삭제하시겠습니까?')) return;

    try {
        const response = await fetch(`/api/todos/${todoId}`, {
            method: 'DELETE'
        });

        if (response.ok) {
            loadTodos();
            updateStats();
        } else {
            alert('오류: TODO를 삭제할 수 없습니다.');
        }
    } catch (error) {
        console.error('Error:', error);
        alert('오류가 발생했습니다.');
    }
}

// ========================================
// 에디트 모달 열기
// ========================================

async function openEditModal(todoId) {
    currentEditId = todoId;

    try {
        // DOM에서 TODO 데이터 찾기
        const todoElement = document.querySelector(`[data-todo-id="${todoId}"]`);
        
        if (!todoElement) {
            throw new Error('TODO element not found');
        }

        const content = todoElement.getAttribute('data-todo-content');
        const targetDateStr = todoElement.getAttribute('data-todo-date');
        const status = todoElement.getAttribute('data-todo-status');

        editContent.value = content;
        editStatus.value = status;

        // datetime-local 형식으로 변환
        const targetDate = new Date(targetDateStr);
        const year = targetDate.getFullYear();
        const month = String(targetDate.getMonth() + 1).padStart(2, '0');
        const date = String(targetDate.getDate()).padStart(2, '0');
        const hours = String(targetDate.getHours()).padStart(2, '0');
        const minutes = String(targetDate.getMinutes()).padStart(2, '0');
        editDate.value = `${year}-${month}-${date}T${hours}:${minutes}`;

        editModal.classList.remove('hidden');
    } catch (error) {
        console.error('Error:', error);
        alert('TODO를 불러올 수 없습니다.');
    }
}

// ========================================
// 모달 닫기
// ========================================

function closeModal() {
    editModal.classList.add('hidden');
    currentEditId = null;
    editForm.reset();
}

// ========================================
// TODO 수정
// ========================================

async function handleEditTodo(e) {
    e.preventDefault();

    if (!editContent.value.trim() || !editDate.value) {
        alert('할 일과 목표 날짜를 입력해주세요.');
        return;
    }

    const updatedTodo = {
        content: editContent.value.trim(),
        target_date: editDate.value,
        status: editStatus.value
    };

    try {
        const response = await fetch(`/api/todos/${currentEditId}`, {
            method: 'PUT',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify(updatedTodo)
        });

        if (response.ok) {
            closeModal();
            loadTodos();
            updateStats();
        } else {
            const error = await response.json();
            alert('오류: ' + error.error);
        }
    } catch (error) {
        console.error('Error:', error);
        alert('오류가 발생했습니다.');
    }
}

// ========================================
// 통계 업데이트
// ========================================

async function updateStats() {
    try {
        const response = await fetch('/api/stats');
        if (!response.ok) throw new Error('Failed to load stats');

        const stats = await response.json();

        document.getElementById('stat-total').textContent = stats.total;
        document.getElementById('stat-scheduled').textContent = stats.scheduled;
        document.getElementById('stat-in-progress').textContent = stats.in_progress;
        document.getElementById('stat-completed').textContent = stats.completed;
    } catch (error) {
        console.error('Error loading stats:', error);
    }
}

// ========================================
// 유틸리티 함수
// ========================================

function formatDate(date) {
    const year = date.getFullYear();
    const month = String(date.getMonth() + 1).padStart(2, '0');
    const day = String(date.getDate()).padStart(2, '0');
    const hours = String(date.getHours()).padStart(2, '0');
    const minutes = String(date.getMinutes()).padStart(2, '0');

    return `${year}년 ${month}월 ${day}일 ${hours}:${minutes}`;
}

function getStatusClass(status) {
    const statusMap = {
        '예정': 'scheduled',
        '진행중': 'in-progress',
        '완료': 'completed'
    };
    return statusMap[status] || 'scheduled';
}

function escapeHtml(text) {
    const map = {
        '&': '&amp;',
        '<': '&lt;',
        '>': '&gt;',
        '"': '&quot;',
        "'": '&#039;'
    };
    return text.replace(/[&<>"']/g, m => map[m]);
}

// ========================================
// 자동 새로고침 (선택사항)
// ========================================

// 페이지가 활성화될 때마다 TODO 새로고침
document.addEventListener('visibilitychange', () => {
    if (!document.hidden) {
        loadTodos();
        updateStats();
    }
});
