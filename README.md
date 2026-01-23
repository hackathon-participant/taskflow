# TaskFlow - Simple Task Management App

A simple task management application built with Python Flask and vanilla JavaScript.

## Features

- Create, read, update, and delete tasks
- Mark tasks as complete/incomplete
- Filter tasks by status
- Search tasks by title
- Due date tracking
- Priority levels (Low, Medium, High)

## Project Structure

```
taskflow/
├── app.py              # Main Flask application
├── models.py           # Database models
├── requirements.txt    # Python dependencies
├── static/
│   ├── css/
│   │   └── style.css   # Application styles
│   └── js/
│       └── app.js      # Frontend JavaScript
├── templates/
│   └── index.html      # Main HTML template
└── tests/
    └── test_app.py     # Unit tests
```

## Getting Started

### Prerequisites

- Python 3.8 or higher
- pip (Python package manager)

### Installation

1. Clone the repository:
   ```bash
   git clone <repository-url>
   cd taskflow
   ```

2. Create a virtual environment (optional but recommended):
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

4. Run the application:
   ```bash
   python app.py
   ```

5. Open your browser and navigate to `http://localhost:5000`

## Running Tests

```bash
python -m pytest tests/ -v
```

## API Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/api/tasks` | Get all tasks |
| POST | `/api/tasks` | Create a new task |
| GET | `/api/tasks/<id>` | Get a specific task |
| PUT | `/api/tasks/<id>` | Update a task |
| DELETE | `/api/tasks/<id>` | Delete a task |
| PATCH | `/api/tasks/<id>/toggle` | Toggle task completion |

## License

MIT License
