from flask import Flask, render_template, request, jsonify
from models import db, Task
from datetime import datetime
import os

app = Flask(__name__)

# Configuration
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///tasks.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# Initialize database
db.init_app(app)


@app.route('/')
def index():
    """Serve the main page.

    Renders the application's main HTML interface where users can view and
    manage their tasks.

    Returns:
        str: Rendered HTML template for the main page.
    """
    return render_template('index.html')


@app.route('/api/tasks', methods=['GET'])
def get_tasks():
    """Get all tasks, optionally filtered by status or search query.

    Retrieves tasks from the database with optional filtering by completion
    status and text search. The search query matches against task titles.

    Query Parameters:
        status (str, optional): Filter by task status. Valid values are:
            - 'completed': Show only completed tasks
            - 'pending': Show only pending tasks
            - 'all' or None: Show all tasks
        search (str, optional): Search query to filter tasks by title.

    Returns:
        Response: JSON array of task objects, each containing task details
        (id, title, description, completed, priority, due_date, etc.).
    """
    status = request.args.get('status')  # all, completed, pending
    search = request.args.get('search', '')

    query = Task.query

    if status == 'completed':
        query = query.filter_by(completed=True)
    elif status == 'pending':
        query = query.filter_by(completed=False)

    if search:
        query = query.filter(Task.title.contains(search))

    tasks = query.all()

    return jsonify([task.to_dict() for task in tasks])


@app.route('/api/tasks', methods=['POST'])
def create_task():
    """Create a new task.

    Creates a new task in the database with the provided details. The task
    title is required, while other fields are optional with default values.

    Request Body (JSON):
        title (str, required): The task title.
        description (str, optional): Detailed description of the task.
        priority (str, optional): Task priority level ('low', 'medium', 'high').
            Defaults to 'medium'.
        due_date (str, optional): Due date in ISO format (e.g., '2024-12-31T23:59:59').

    Returns:
        Response: JSON object of the newly created task with HTTP status 201.

    Error Responses:
        400: If title is missing or date format is invalid.
    """
    data = request.get_json()

    if not data or not data.get('title'):
        return jsonify({'error': 'Title is required'}), 400

    priority = data.get('priority', 'medium')

    due_date = None
    if data.get('due_date'):
        try:
            due_date = datetime.fromisoformat(data['due_date'])
        except ValueError:
            return jsonify({'error': 'Invalid date format'}), 400

    task = Task(
        title=data['title'],
        description=data.get('description', ''),
        priority=priority,
        due_date=due_date
    )

    db.session.add(task)
    db.session.commit()

    return jsonify(task.to_dict()), 201


@app.route('/api/tasks/<int:task_id>', methods=['GET'])
def get_task(task_id):
    """Get a specific task by ID.

    Retrieves detailed information about a single task from the database.

    Path Parameters:
        task_id (int): The unique identifier of the task to retrieve.

    Returns:
        Response: JSON object containing the task details.

    Error Responses:
        404: If the task with the specified ID does not exist.
    """
    task = Task.query.get(task_id)

    if not task:
        return jsonify({'error': 'Task not found'}), 404

    return jsonify(task.to_dict())


@app.route('/api/tasks/<int:task_id>', methods=['PUT'])
def update_task(task_id):
    """Update an existing task.

    Updates one or more fields of an existing task. Only the fields provided
    in the request body will be updated; other fields remain unchanged.

    Path Parameters:
        task_id (int): The unique identifier of the task to update.

    Request Body (JSON, all fields optional):
        title (str): Updated task title.
        description (str): Updated task description.
        completed (bool): Updated completion status.
        priority (str): Updated priority level ('low', 'medium', 'high').
        due_date (str or None): Updated due date in ISO format, or null to clear.

    Returns:
        Response: JSON object of the updated task.

    Error Responses:
        404: If the task with the specified ID does not exist.
        400: If the date format is invalid.
    """
    task = Task.query.get(task_id)

    if not task:
        return jsonify({'error': 'Task not found'}), 404

    data = request.get_json()

    if 'title' in data:
        task.title = data['title']
    if 'description' in data:
        task.description = data['description']
    if 'completed' in data:
        task.completed = data['completed']
    if 'priority' in data:
        task.priority = data['priority']
    if 'due_date' in data:
        if data['due_date']:
            try:
                task.due_date = datetime.fromisoformat(data['due_date'])
            except ValueError:
                return jsonify({'error': 'Invalid date format'}), 400
        else:
            task.due_date = None

    db.session.commit()

    return jsonify(task.to_dict())


@app.route('/api/tasks/<int:task_id>', methods=['DELETE'])
def delete_task(task_id):
    """Delete a task.

    Permanently removes a task from the database.

    Path Parameters:
        task_id (int): The unique identifier of the task to delete.

    Returns:
        Response: JSON object with a success message.

    Error Responses:
        404: If the task with the specified ID does not exist.
    """
    task = Task.query.get(task_id)

    if not task:
        return jsonify({'error': 'Task not found'}), 404

    db.session.delete(task)
    db.session.commit()

    return jsonify({'message': 'Task deleted'})


@app.route('/api/tasks/<int:task_id>/toggle', methods=['PATCH'])
def toggle_task(task_id):
    """Toggle the completion status of a task.

    Switches the task's completion status between completed and pending.
    If the task is completed, it becomes pending; if pending, it becomes completed.

    Path Parameters:
        task_id (int): The unique identifier of the task to toggle.

    Returns:
        Response: JSON object of the task with its updated completion status.

    Error Responses:
        404: If the task with the specified ID does not exist.
    """
    task = Task.query.get(task_id)

    if not task:
        return jsonify({'error': 'Task not found'}), 404

    task.completed = not task.completed
    db.session.commit()

    return jsonify(task.to_dict())

if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    app.run(debug=True, host='0.0.0.0', port=5000)
