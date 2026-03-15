import React, { useState, useEffect } from 'react';
import { getURLs, createURL, deleteURL, getURLStats } from './api';
import { BarChart, Bar, XAxis, YAxis, Tooltip, ResponsiveContainer, Cell } from 'recharts';
import './App.css';

const BASE_URL = process.env.REACT_APP_API_URL || 'http://localhost:8000';

export default function App() {
  const [urls, setUrls]           = useState([]);
  const [loading, setLoading]     = useState(true);
  const [form, setForm]           = useState({ original_url: '', custom_code: '', title: '' });
  const [creating, setCreating]   = useState(false);
  const [error, setError]         = useState('');
  const [copied, setCopied]       = useState('');
  const [statsFor, setStatsFor]   = useState(null);
  const [stats, setStats]         = useState(null);
  const [activeTab, setActiveTab] = useState('urls');

  const load = async () => {
    try {
      const res = await getURLs();
      setUrls(res.data);
    } catch { setError('Cannot connect to backend'); }
    finally { setLoading(false); }
  };

  useEffect(() => { load(); }, []);

  const handleCreate = async (e) => {
    e.preventDefault();
    if (!form.original_url.trim()) return;
    setCreating(true);
    setError('');
    try {
      await createURL(form);
      setForm({ original_url: '', custom_code: '', title: '' });
      load();
    } catch (err) {
      setError(err.response?.data?.detail || 'Failed to shorten URL');
    } finally { setCreating(false); }
  };

  const handleDelete = async (code) => {
    try { await deleteURL(code); load(); }
    catch { setError('Failed to delete'); }
  };

  const handleCopy = (code) => {
    navigator.clipboard.writeText(`${BASE_URL}/${code}`);
    setCopied(code);
    setTimeout(() => setCopied(''), 2000);
  };

  const handleStats = async (code) => {
    setStatsFor(code);
    setActiveTab('stats');
    try {
      const res = await getURLStats(code);
      setStats(res.data);
    } catch { setError('Failed to load stats'); }
  };

  // Aggregate browser stats for chart
  const browserData = () => {
    if (!stats?.clicks?.length) return [];
    const counts = {};
    stats.clicks.forEach(c => {
      counts[c.browser || 'Other'] = (counts[c.browser || 'Other'] || 0) + 1;
    });
    return Object.entries(counts).map(([name, value]) => ({ name, value }));
  };

  // Clicks per day for chart
  const clicksByDay = () => {
    if (!stats?.clicks?.length) return [];
    const counts = {};
    stats.clicks.forEach(c => {
      const day = new Date(c.clicked_at).toLocaleDateString();
      counts[day] = (counts[day] || 0) + 1;
    });
    return Object.entries(counts).slice(-7).map(([day, count]) => ({ day, count }));
  };

  const totalClicks = urls.reduce((sum, u) => sum + (u.click_count || 0), 0);
  const topURL = urls.reduce((top, u) => (!top || u.click_count > top.click_count) ? u : top, null);

  const CHART_COLORS = ['#00e5ff', '#ff6b6b', '#00e676', '#ffd740', '#b388ff'];

  return (
    <div className="app">
      {/* ── Header ── */}
      <header className="header">
        <div className="header-inner">
          <div className="logo">
            <span className="logo-mark">✂</span>
            <span className="logo-text">snip</span>
          </div>
          <nav className="nav">
            <button className={activeTab === 'urls' ? 'nav-btn active' : 'nav-btn'} onClick={() => setActiveTab('urls')}>URLs</button>
            <button className={activeTab === 'stats' ? 'nav-btn active' : 'nav-btn'} onClick={() => setActiveTab('stats')}>Analytics</button>
          </nav>
        </div>
      </header>

      <main className="main">
        {error && (
          <div className="error-bar">
            ⚠ {error}
            <button onClick={() => setError('')}>✕</button>
          </div>
        )}

        {/* ── Summary Cards ── */}
        <div className="summary">
          <div className="summary-card">
            <span className="summary-num">{urls.length}</span>
            <span className="summary-label">Total Links</span>
          </div>
          <div className="summary-card">
            <span className="summary-num">{totalClicks}</span>
            <span className="summary-label">Total Clicks</span>
          </div>
          <div className="summary-card">
            <span className="summary-num">{topURL?.short_code || '—'}</span>
            <span className="summary-label">Top Link</span>
          </div>
        </div>

        {/* ── Shorten Form ── */}
        <div className="shorten-box">
          <form onSubmit={handleCreate} className="shorten-form">
            <div className="input-group">
              <input
                type="url"
                placeholder="https://your-long-url.com/paste/here"
                value={form.original_url}
                onChange={e => setForm({ ...form, original_url: e.target.value })}
                required
              />
            </div>
            <div className="input-row">
              <input
                type="text"
                placeholder="Title (optional)"
                value={form.title}
                onChange={e => setForm({ ...form, title: e.target.value })}
              />
              <input
                type="text"
                placeholder="Custom code (optional)"
                value={form.custom_code}
                onChange={e => setForm({ ...form, custom_code: e.target.value })}
                maxLength={20}
              />
              <button type="submit" className="btn-primary" disabled={creating}>
                {creating ? 'Shortening...' : 'Shorten ✂'}
              </button>
            </div>
          </form>
        </div>

        {/* ── URLs Tab ── */}
        {activeTab === 'urls' && (
          <div className="urls-section">
            <h2 className="section-title">Your Links</h2>
            {loading ? (
              <div className="empty">Loading...</div>
            ) : urls.length === 0 ? (
              <div className="empty">No URLs yet. Paste one above!</div>
            ) : (
              <div className="url-list">
                {urls.map(url => (
                  <div key={url.id} className="url-card">
                    <div className="url-left">
                      <div className="url-short">
                        <span className="base">{BASE_URL.replace('http://', '')}/</span>
                        <span className="code">{url.short_code}</span>
                      </div>
                      <div className="url-original" title={url.original_url}>
                        {url.title || url.original_url}
                      </div>
                    </div>
                    <div className="url-right">
                      <span className="click-count">{url.click_count || 0} clicks</span>
                      <button
                        className={`icon-btn ${copied === url.short_code ? 'copied' : ''}`}
                        onClick={() => handleCopy(url.short_code)}
                        title="Copy"
                      >
                        {copied === url.short_code ? '✓' : '⎘'}
                      </button>
                      <button className="icon-btn" onClick={() => handleStats(url.short_code)} title="Analytics">
                        📊
                      </button>
                      <button className="icon-btn danger" onClick={() => handleDelete(url.short_code)} title="Delete">
                        ✕
                      </button>
                    </div>
                  </div>
                ))}
              </div>
            )}
          </div>
        )}

        {/* ── Analytics Tab ── */}
        {activeTab === 'stats' && (
          <div className="stats-section">
            {!statsFor ? (
              <div className="empty">Click 📊 on any link to view analytics</div>
            ) : !stats ? (
              <div className="empty">Loading analytics...</div>
            ) : (
              <>
                <div className="stats-header">
                  <h2 className="section-title">
                    Analytics — <span className="accent">/{stats.url.short_code}</span>
                  </h2>
                  <div className="stats-meta">
                    <span>→ {stats.url.original_url.slice(0, 60)}...</span>
                    <span className="accent">{stats.clicks.length} total clicks</span>
                  </div>
                </div>

                <div className="charts-grid">
                  {/* Clicks per day */}
                  <div className="chart-card">
                    <h3>Clicks Over Time</h3>
                    {clicksByDay().length === 0 ? (
                      <div className="no-data">No clicks yet</div>
                    ) : (
                      <ResponsiveContainer width="100%" height={200}>
                        <BarChart data={clicksByDay()}>
                          <XAxis dataKey="day" tick={{ fill: '#6666aa', fontSize: 11 }} />
                          <YAxis tick={{ fill: '#6666aa', fontSize: 11 }} allowDecimals={false} />
                          <Tooltip
                            contentStyle={{ background: '#111118', border: '1px solid #252530', borderRadius: 8 }}
                            labelStyle={{ color: '#f0f0ff' }}
                          />
                          <Bar dataKey="count" fill="#00e5ff" radius={[4, 4, 0, 0]} />
                        </BarChart>
                      </ResponsiveContainer>
                    )}
                  </div>

                  {/* Browser breakdown */}
                  <div className="chart-card">
                    <h3>Browsers</h3>
                    {browserData().length === 0 ? (
                      <div className="no-data">No data yet</div>
                    ) : (
                      <ResponsiveContainer width="100%" height={200}>
                        <BarChart data={browserData()} layout="vertical">
                          <XAxis type="number" tick={{ fill: '#6666aa', fontSize: 11 }} allowDecimals={false} />
                          <YAxis type="category" dataKey="name" tick={{ fill: '#f0f0ff', fontSize: 12 }} width={60} />
                          <Tooltip
                            contentStyle={{ background: '#111118', border: '1px solid #252530', borderRadius: 8 }}
                          />
                          <Bar dataKey="value" radius={[0, 4, 4, 0]}>
                            {browserData().map((_, i) => (
                              <Cell key={i} fill={CHART_COLORS[i % CHART_COLORS.length]} />
                            ))}
                          </Bar>
                        </BarChart>
                      </ResponsiveContainer>
                    )}
                  </div>
                </div>

                {/* Recent clicks table */}
                <div className="chart-card">
                  <h3>Recent Clicks</h3>
                  {stats.clicks.length === 0 ? (
                    <div className="no-data">No clicks recorded yet</div>
                  ) : (
                    <div className="clicks-table">
                      <div className="clicks-head">
                        <span>Time</span>
                        <span>Browser</span>
                        <span>Referer</span>
                        <span>IP</span>
                      </div>
                      {stats.clicks.slice(0, 10).map(click => (
                        <div key={click.id} className="clicks-row">
                          <span>{new Date(click.clicked_at).toLocaleString()}</span>
                          <span>{click.browser || 'Unknown'}</span>
                          <span>{click.referer || 'Direct'}</span>
                          <span>{click.ip_address || '—'}</span>
                        </div>
                      ))}
                    </div>
                  )}
                </div>
              </>
            )}
          </div>
        )}
      </main>
    </div>
  );
}
