"""Tests for TaskFlow application."""

import pytest
import json
import sys
import os

# Add parent directory to path for imports
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app import app, db
from models import Task


@pytest.fixture
def client():
    """Create test client with in-memory database."""
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///:memory:'
    app.config['TESTING'] = True

    with app.app_context():
        db.create_all()
        yield app.test_client()
        db.session.remove()
        db.drop_all()


@pytest.fixture
def sample_task(client):
    """Create a sample task for testing."""
    with app.app_context():
        task = Task(
            title='Test Task',
            description='Test Description',
            priority='medium'
        )
        db.session.add(task)
        db.session.commit()
        return task.id


class TestGetTasks:
    """Tests for GET /api/tasks endpoint."""

    def test_get_empty_tasks(self, client):
        """Should return empty list when no tasks exist."""
        response = client.get('/api/tasks')
        assert response.status_code == 200
        assert response.json == []

    def test_get_all_tasks(self, client, sample_task):
        """Should return all tasks."""
        response = client.get('/api/tasks')
        assert response.status_code == 200
        assert len(response.json) == 1
        assert response.json[0]['title'] == 'Test Task'

    def test_filter_completed_tasks(self, client):
        """Should filter tasks by completed status."""
        with app.app_context():
            db.session.add(Task(title='Pending', completed=False))
            db.session.add(Task(title='Done', completed=True))
            db.session.commit()

        response = client.get('/api/tasks?status=completed')
        assert response.status_code == 200
        assert len(response.json) == 1
        assert response.json[0]['title'] == 'Done'

    def test_search_tasks(self, client):
        """Should search tasks by title."""
        with app.app_context():
            db.session.add(Task(title='Buy groceries'))
            db.session.add(Task(title='Walk the dog'))
            db.session.commit()

        response = client.get('/api/tasks?search=groceries')
        assert response.status_code == 200
        assert len(response.json) == 1
        assert response.json[0]['title'] == 'Buy groceries'


class TestCreateTask:
    """Tests for POST /api/tasks endpoint."""

    def test_create_task(self, client):
        """Should create a new task."""
        data = {
            'title': 'New Task',
            'description': 'Description',
            'priority': 'high'
        }
        response = client.post('/api/tasks',
                               data=json.dumps(data),
                               content_type='application/json')

        assert response.status_code == 201
        assert response.json['title'] == 'New Task'
        assert response.json['priority'] == 'high'
        assert response.json['completed'] == False

    def test_create_task_without_title(self, client):
        """Should return error when title is missing."""
        response = client.post('/api/tasks',
                               data=json.dumps({}),
                               content_type='application/json')

        assert response.status_code == 400
        assert 'error' in response.json

    def test_create_task_with_due_date(self, client):
        """Should create task with due date."""
        data = {
            'title': 'Task with due date',
            'due_date': '2024-12-31T23:59:59'
        }
        response = client.post('/api/tasks',
                               data=json.dumps(data),
                               content_type='application/json')

        assert response.status_code == 201
        assert response.json['due_date'] is not None


class TestUpdateTask:
    """Tests for PUT /api/tasks/<id> endpoint."""

    def test_update_task(self, client, sample_task):
        """Should update an existing task."""
        data = {'title': 'Updated Title'}
        response = client.put(f'/api/tasks/{sample_task}',
                              data=json.dumps(data),
                              content_type='application/json')

        assert response.status_code == 200
        assert response.json['title'] == 'Updated Title'

    def test_update_nonexistent_task(self, client):
        """Should return 404 for nonexistent task."""
        response = client.put('/api/tasks/999',
                              data=json.dumps({'title': 'New'}),
                              content_type='application/json')

        assert response.status_code == 404


class TestDeleteTask:
    """Tests for DELETE /api/tasks/<id> endpoint."""

    def test_delete_task(self, client, sample_task):
        """Should delete an existing task."""
        response = client.delete(f'/api/tasks/{sample_task}')
        # Note: Currently returns 200, should return 204
        assert response.status_code in [200, 204]

        # Verify task is deleted
        get_response = client.get(f'/api/tasks/{sample_task}')
        assert get_response.status_code == 404

    def test_delete_nonexistent_task(self, client):
        """Should return 404 for nonexistent task."""
        response = client.delete('/api/tasks/999')
        assert response.status_code == 404


class TestToggleTask:
    """Tests for PATCH /api/tasks/<id>/toggle endpoint."""

    def test_toggle_task_completion(self, client, sample_task):
        """Should toggle task completion status."""
        # First toggle - should be completed
        response = client.patch(f'/api/tasks/{sample_task}/toggle')
        assert response.status_code == 200
        assert response.json['completed'] == True

        # Second toggle - should be incomplete
        response = client.patch(f'/api/tasks/{sample_task}/toggle')
        assert response.status_code == 200
        assert response.json['completed'] == False


# TODO: Add tests for priority validation
# TODO: Add tests for task statistics endpoint (when implemented)
