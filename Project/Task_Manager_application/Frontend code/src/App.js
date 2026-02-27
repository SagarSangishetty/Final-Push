import React, { useState, useEffect } from 'react';
import './App.css';

// Using relative API path because ingress handles routing
const API_URL = '';

function App() {
  const [tasks, setTasks] = useState([]);
  const [newTask, setNewTask] = useState({ title: '', description: '' });
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');

  // Fetch all tasks
  const fetchTasks = async () => {
    try {
      setLoading(true);
      const response = await fetch(`${API_URL}/api/tasks`);
      if (!response.ok) throw new Error('Failed to fetch tasks');
      const data = await response.json();
      setTasks(data);
      setError('');
    } catch (err) {
      setError('Failed to load tasks');
      console.error(err);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchTasks();
  }, []);

  // Add new task
  const handleAddTask = async (e) => {
    e.preventDefault();
    if (!newTask.title.trim()) return;

    try {
      const response = await fetch(`${API_URL}/api/tasks`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(newTask),
      });

      if (!response.ok) throw new Error('Failed to add task');

      setNewTask({ title: '', description: '' });
      fetchTasks();
    } catch (err) {
      setError('Failed to add task');
      console.error(err);
    }
  };

  // Toggle completion
  const handleToggleComplete = async (task) => {
    try {
      const response = await fetch(`${API_URL}/api/tasks/${task.id}`, {
        method: 'PUT',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ completed: !task.completed }),
      });

      if (!response.ok) throw new Error('Failed to update task');
      fetchTasks();
    } catch (err) {
      setError('Failed to update task');
      console.error(err);
    }
  };

  // Delete task
  const handleDeleteTask = async (id) => {
    try {
      const response = await fetch(`${API_URL}/api/tasks/${id}`, {
        method: 'DELETE',
      });

      if (!response.ok) throw new Error('Failed to delete task');
      fetchTasks();
    } catch (err) {
      setError('Failed to delete task');
      console.error(err);
    }
  };

  return (
    <div className="App">
      <div className="container">
        <header className="app-header">
          <h1>📝 Task Manager</h1>
          <p className="subtitle">DevOps Project by Sagar Shetty</p>
        </header>

        {error && <div className="error-message">{error}</div>}

        <div className="add-task-form">
          <h2>Add New Task</h2>
          <form onSubmit={handleAddTask}>
            <input
              type="text"
              placeholder="Task title *"
              value={newTask.title}
              onChange={(e) =>
                setNewTask({ ...newTask, title: e.target.value })
              }
              required
            />
            <textarea
              placeholder="Task description (optional)"
              value={newTask.description}
              onChange={(e) =>
                setNewTask({ ...newTask, description: e.target.value })
              }
              rows="3"
            />
            <button type="submit" className="btn-add">
              ➕ Add Task
            </button>
          </form>
        </div>

        <div className="tasks-section">
          <h2>Tasks ({tasks.length})</h2>

          {loading ? (
            <div className="loading">Loading tasks...</div>
          ) : tasks.length === 0 ? (
            <div className="no-tasks">No tasks yet. Add one above! 🚀</div>
          ) : (
            <div className="tasks-list">
              {tasks.map((task) => (
                <div
                  key={task.id}
                  className={`task-card ${
                    task.completed ? 'completed' : ''
                  }`}
                >
                  <div className="task-content">
                    <div className="task-header">
                      <input
                        type="checkbox"
                        checked={task.completed}
                        onChange={() => handleToggleComplete(task)}
                      />
                      <h3>{task.title}</h3>
                    </div>

                    {task.description && (
                      <p>{task.description}</p>
                    )}

                    <div className="task-footer">
                      <span>
                        {new Date(task.created_at).toLocaleDateString()}
                      </span>
                      <button
                        onClick={() => handleDeleteTask(task.id)}
                        className="btn-delete"
                      >
                        🗑️ Delete
                      </button>
                    </div>
                  </div>
                </div>
              ))}
            </div>
          )}
        </div>

        <footer className="app-footer">
          <p>Built with React + Express + PostgreSQL</p>
          <p>Deployed using Docker & Kubernetes</p>
        </footer>
      </div>
    </div>
  );
}

export default App;