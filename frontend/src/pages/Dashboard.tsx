import { useEffect, useState } from 'react';
import { getDashboardStats } from '../services/api';
import type { DashboardStats } from '../types';
import './Dashboard.css';

export default function Dashboard() {
  const [stats, setStats] = useState<DashboardStats | null>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    loadStats();
  }, []);

  const loadStats = async () => {
    try {
      const data = await getDashboardStats();
      setStats(data);
    } catch (error) {
      console.error('Failed to load dashboard stats:', error);
    } finally {
      setLoading(false);
    }
  };

  if (loading) {
    return (
      <div className="dashboard-loading">
        <div className="loading-spinner"></div>
        <p>Loading dashboard...</p>
      </div>
    );
  }

  return (
    <div className="dashboard">
      <h1>Dashboard</h1>

      {/* Stats Cards */}
      <div className="stats-grid">
        <div className="stat-card">
          <div className="stat-icon">📚</div>
          <div className="stat-content">
            <h3>{stats?.total_lectures || 0}</h3>
            <p>Total Lectures</p>
          </div>
        </div>

        <div className="stat-card">
          <div className="stat-icon">🏷️</div>
          <div className="stat-content">
            <h3>{stats?.total_topics || 0}</h3>
            <p>Topics Detected</p>
          </div>
        </div>

        <div className="stat-card">
          <div className="stat-icon">📖</div>
          <div className="stat-content">
            <h3>{stats?.modules.length || 0}</h3>
            <p>Active Modules</p>
          </div>
        </div>
      </div>

      {/* Modules List */}
      {stats && stats.modules.length > 0 && (
        <div className="dashboard-section">
          <h2>Your Modules</h2>
          <div className="modules-grid">
            {stats.modules.map((module) => (
              <div key={module} className="module-card">
                <h3>{module}</h3>
                <p>Click to view details</p>
              </div>
            ))}
          </div>
        </div>
      )}

      {/* Recent Uploads */}
      {stats && stats.recent_uploads.length > 0 && (
        <div className="dashboard-section">
          <h2>Recent Uploads</h2>
          <div className="recent-uploads">
            {stats.recent_uploads.map((lecture) => (
              <div key={lecture.id} className="upload-item">
                <div className="upload-icon">📄</div>
                <div className="upload-info">
                  <h4>{lecture.title}</h4>
                  <p className="upload-meta">
                    {lecture.module_code} • Week {lecture.week_number} • {lecture.num_pages} pages
                  </p>
                  <p className="upload-date">
                    {new Date(lecture.upload_date).toLocaleDateString('en-US', {
                      year: 'numeric',
                      month: 'short',
                      day: 'numeric'
                    })}
                  </p>
                </div>
              </div>
            ))}
          </div>
        </div>
      )}

      {/* Getting Started */}
      {(!stats || stats.total_lectures === 0) && (
        <div className="getting-started">
          <h2>Get Started</h2>
          <div className="steps">
            <div className="step">
              <div className="step-number">1</div>
              <div className="step-content">
                <h3>Upload Lectures</h3>
                <p>Go to the Upload page and add your lecture PDFs with metadata</p>
              </div>
            </div>
            <div className="step">
              <div className="step-number">2</div>
              <div className="step-content">
                <h3>Detect Topics</h3>
                <p>Visit Topics page to run cross-lecture topic detection</p>
              </div>
            </div>
            <div className="step">
              <div className="step-number">3</div>
              <div className="step-content">
                <h3>Ask Questions</h3>
                <p>Use the Q&A page to query your lecture content with AI</p>
              </div>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}
