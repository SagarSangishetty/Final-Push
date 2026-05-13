import React, { useState, useEffect, useCallback } from "react";
import "./App.css";

const API = "/api/tasks";

const PRIORITY_COLORS = {
  high: "#ff4d4d",
  medium: "#f5a623",
  low: "#4caf88",
};

function App() {
  const [tasks, setTasks] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [form, setForm] = useState({ title: "", description: "", priority: "medium" });
  const [submitting, setSubmitting] = useState(false);
  const [apiStatus, setApiStatus] = useState("checking");

  // Health check — shows RDS connectivity status in UI
  useEffect(() => {
    fetch("/api/health/ready")
      .then((r) => r.ok ? setApiStatus("healthy") : setApiStatus("degraded"))
      .catch(() => setApiStatus("down"));
  }, []);

  const fetchTasks = useCallback(async () => {
    try {
      const r = await fetch(API);
      if (!r.ok) throw new Error(`HTTP ${r.status}`);
      setTasks(await r.json());
      setError(null);
    } catch (e) {
      setError("Could not load tasks. Backend may be starting up.");
    } finally {
      setLoading(false);
    }
  }, []);

  useEffect(() => { fetchTasks(); }, [fetchTasks]);

  const handleSubmit = async () => {
    if (!form.title.trim()) return;
    setSubmitting(true);
    try {
      await fetch(API, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(form),
      });
      setForm({ title: "", description: "", priority: "medium" });
      fetchTasks();
    } catch (e) {
      setError("Failed to create task.");
    } finally {
      setSubmitting(false);
    }
  };

  const toggleComplete = async (task) => {
    await fetch(`${API}/${task.id}`, {
      method: "PATCH",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ completed: !task.completed }),
    });
    fetchTasks();
  };

  const deleteTask = async (id) => {
    await fetch(`${API}/${id}`, { method: "DELETE" });
    fetchTasks();
  };

  const statusDot = { healthy: "#4caf88", degraded: "#f5a623", down: "#ff4d4d", checking: "#888" }[apiStatus];

  return (
    <div className="app">
      <header className="header">
        <div className="header-left">
          <span className="logo">TM</span>
          <div>
            <h1>Task Manager</h1>
            <p className="subtitle">EKS · RDS · ALB · CloudWatch</p>
          </div>
        </div>
        <div className="status-badge">
          <span className="dot" style={{ background: statusDot }} />
          <span>API {apiStatus}</span>
        </div>
      </header>

      <main className="main">
        {/* Create form */}
        <section className="card form-card">
          <h2>New Task</h2>
          <input
            className="input"
            placeholder="Task title *"
            value={form.title}
            onChange={(e) => setForm({ ...form, title: e.target.value })}
          />
          <input
            className="input"
            placeholder="Description (optional)"
            value={form.description}
            onChange={(e) => setForm({ ...form, description: e.target.value })}
          />
          <div className="row">
            <select
              className="select"
              value={form.priority}
              onChange={(e) => setForm({ ...form, priority: e.target.value })}
            >
              <option value="low">Low</option>
              <option value="medium">Medium</option>
              <option value="high">High</option>
            </select>
            <button className="btn-primary" onClick={handleSubmit} disabled={submitting}>
              {submitting ? "Adding…" : "+ Add Task"}
            </button>
          </div>
        </section>

        {/* Task list */}
        <section className="card">
          <h2>Tasks <span className="count">{tasks.length}</span></h2>
          {error && <div className="error">{error}</div>}
          {loading ? (
            <div className="loading">Loading…</div>
          ) : tasks.length === 0 ? (
            <div className="empty">No tasks yet. Add one above.</div>
          ) : (
            <ul className="task-list">
              {tasks.map((t) => (
                <li key={t.id} className={`task-item ${t.completed ? "done" : ""}`}>
                  <div className="task-left">
                    <button
                      className="check-btn"
                      onClick={() => toggleComplete(t)}
                      title={t.completed ? "Mark incomplete" : "Mark complete"}
                    >
                      {t.completed ? "✓" : "○"}
                    </button>
                    <div>
                      <div className="task-title">{t.title}</div>
                      {t.description && <div className="task-desc">{t.description}</div>}
                    </div>
                  </div>
                  <div className="task-right">
                    <span className="priority-tag" style={{ color: PRIORITY_COLORS[t.priority] }}>
                      {t.priority}
                    </span>
                    <button className="del-btn" onClick={() => deleteTask(t.id)}>✕</button>
                  </div>
                </li>
              ))}
            </ul>
          )}
        </section>
      </main>
    </div>
  );
}

export default App;
