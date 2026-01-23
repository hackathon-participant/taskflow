// TaskFlow Frontend JavaScript

const API_BASE = '/api';

// DOM Elements
const taskForm = document.getElementById('task-form');
const taskList = document.getElementById('task-list');
const emptyState = document.getElementById('empty-state');
const statusFilter = document.getElementById('status-filter');
const searchInput = document.getElementById('search');
const editModal = document.getElementById('edit-modal');
const editForm = document.getElementById('edit-form');

// State
let tasks = [];

// Initialize
document.addEventListener('DOMContentLoaded', () => {
    loadTasks();
    setupEventListeners();
});

function setupEventListeners() {
    taskForm.addEventListener('submit', handleCreateTask);
    editForm.addEventListener('submit', handleUpdateTask);
    statusFilter.addEventListener('change', loadTasks);
    searchInput.addEventListener('input', debounce(loadTasks, 300));
}

// API Functions
async function loadTasks() {
    const status = statusFilter.value;
    const search = searchInput.value;

    let url = `${API_BASE}/tasks?`;
    if (status !== 'all') {
        url += `status=${status}&`;
    }
    if (search) {
        url += `search=${encodeURIComponent(search)}`;
    }

    try {
        const response = await fetch(url);
        tasks = await response.json();
        renderTasks();
    } catch (error) {
        console.error('Failed to load tasks:', error);
        showError('Failed to load tasks. Please try again.');
    }
}

async function handleCreateTask(event) {
    event.preventDefault();

    const formData = new FormData(taskForm);
    const data = {
        title: formData.get('title'),
        description: formData.get('description'),
        priority: formData.get('priority'),
        due_date: formData.get('due_date') || null
    };

    try {
        const response = await fetch(`${API_BASE}/tasks`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(data)
        });

        if (!response.ok) {
            const error = await response.json();
            throw new Error(error.error || 'Failed to create task');
        }

        taskForm.reset();
        loadTasks();
    } catch (error) {
        console.error('Failed to create task:', error);
        showError(error.message);
    }
}

async function toggleTask(taskId) {
    try {
        const response = await fetch(`${API_BASE}/tasks/${taskId}/toggle`, {
            method: 'PATCH'
        });

        if (!response.ok) {
            throw new Error('Failed to toggle task');
        }

        loadTasks();
    } catch (error) {
        console.error('Failed to toggle task:', error);
        showError(error.message);
    }
}

async function deleteTask(taskId) {
    if (!confirm('Are you sure you want to delete this task?')) {
        return;
    }

    try {
        const response = await fetch(`${API_BASE}/tasks/${taskId}`, {
            method: 'DELETE'
        });

        if (!response.ok) {
            throw new Error('Failed to delete task');
        }

        loadTasks();
    } catch (error) {
        console.error('Failed to delete task:', error);
        showError(error.message);
    }
}

async function handleUpdateTask(event) {
    event.preventDefault();

    const taskId = document.getElementById('edit-id').value;
    const data = {
        title: document.getElementById('edit-title').value,
        description: document.getElementById('edit-description').value,
        priority: document.getElementById('edit-priority').value,
        due_date: document.getElementById('edit-due-date').value || null
    };

    try {
        const response = await fetch(`${API_BASE}/tasks/${taskId}`, {
            method: 'PUT',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(data)
        });

        if (!response.ok) {
            throw new Error('Failed to update task');
        }

        closeEditModal();
        loadTasks();
    } catch (error) {
        console.error('Failed to update task:', error);
        showError(error.message);
    }
}

// UI Functions
function renderTasks() {
    if (tasks.length === 0) {
        taskList.innerHTML = '';
        emptyState.style.display = 'block';
        return;
    }

    emptyState.style.display = 'none';
    taskList.innerHTML = tasks.map(task => createTaskHTML(task)).join('');
}

function createTaskHTML(task) {
    const priorityClass = `priority-${task.priority}`;
    const completedClass = task.completed ? 'completed' : '';
    const dueDate = task.due_date ? formatDate(task.due_date) : null;

    // BUG #4: Due date display shows "Invalid Date" for some dates
    // The issue is with date parsing - should handle timezone properly

    return `
        <div class="task-item ${completedClass} ${priorityClass}" data-id="${task.id}">
            <div class="task-checkbox">
                <input type="checkbox"
                       ${task.completed ? 'checked' : ''}
                       onchange="toggleTask(${task.id})"
                       aria-label="Mark task as ${task.completed ? 'incomplete' : 'complete'}">
            </div>
            <div class="task-content">
                <div class="task-title">${escapeHtml(task.title)}</div>
                ${task.description ? `<div class="task-description">${escapeHtml(task.description)}</div>` : ''}
                <div class="task-meta">
                    <span class="priority-badge ${task.priority}">${task.priority}</span>
                    ${dueDate ? `<span>Due: ${dueDate}</span>` : ''}
                    <span>Created: ${formatDate(task.created_at)}</span>
                </div>
            </div>
            <div class="task-actions">
                <button class="btn btn-sm btn-secondary" onclick="openEditModal(${task.id})">Edit</button>
                <button class="btn btn-sm btn-danger" onclick="deleteTask(${task.id})">Delete</button>
            </div>
        </div>
    `;
}

function openEditModal(taskId) {
    const task = tasks.find(t => t.id === taskId);
    if (!task) return;

    document.getElementById('edit-id').value = task.id;
    document.getElementById('edit-title').value = task.title;
    document.getElementById('edit-description').value = task.description || '';
    document.getElementById('edit-priority').value = task.priority;
    document.getElementById('edit-due-date').value = task.due_date ? task.due_date.split('T')[0] : '';

    editModal.style.display = 'flex';
}

function closeEditModal() {
    editModal.style.display = 'none';
    editForm.reset();
}

// Utility Functions
function formatDate(dateString) {
    // BUG #5: This doesn't handle ISO date strings correctly
    // Should parse as ISO and display in local format
    const date = new Date(dateString);
    return date.toLocaleDateString();
}

function escapeHtml(text) {
    const div = document.createElement('div');
    div.textContent = text;
    return div.innerHTML;
}

function debounce(func, wait) {
    let timeout;
    return function executedFunction(...args) {
        const later = () => {
            clearTimeout(timeout);
            func(...args);
        };
        clearTimeout(timeout);
        timeout = setTimeout(later, wait);
    };
}

function showError(message) {
    // Simple error display - could be improved with a toast system
    alert(message);
}

// Close modal when clicking outside
editModal.addEventListener('click', (event) => {
    if (event.target === editModal) {
        closeEditModal();
    }
});

// Close modal on Escape key
document.addEventListener('keydown', (event) => {
    if (event.key === 'Escape' && editModal.style.display === 'flex') {
        closeEditModal();
    }
});
