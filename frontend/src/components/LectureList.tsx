import { useState, useEffect } from 'react';
import { getLectures, deleteLecture } from '../services/api';
import type { Lecture } from '../types';
import './LectureList.css';

interface LectureListProps {
  moduleCode?: string;
  onModuleChange?: (moduleCode: string) => void;
}

export default function LectureList({ moduleCode, onModuleChange }: LectureListProps) {
  const [lectures, setLectures] = useState<Lecture[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [deleting, setDeleting] = useState<string | null>(null);
  const [filter, setFilter] = useState(moduleCode || '');

  useEffect(() => {
    loadLectures();
  }, [filter]);

  const loadLectures = async () => {
    setLoading(true);
    setError(null);

    try {
      const data = await getLectures(filter || undefined);
      setLectures(data);
    } catch (err: any) {
      setError(err.response?.data?.detail || 'Failed to load lectures');
    } finally {
      setLoading(false);
    }
  };

  const handleDelete = async (lecture: Lecture) => {
    if (!confirm(`Delete "${lecture.title}"?\n\nThis will also delete all chunks and embeddings.`)) {
      return;
    }

    setDeleting(lecture.id);

    try {
      await deleteLecture(lecture.id);
      setLectures(prev => prev.filter(l => l.id !== lecture.id));
    } catch (err: any) {
      alert(err.response?.data?.detail || 'Failed to delete lecture');
    } finally {
      setDeleting(null);
    }
  };

  const handleFilterChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    setFilter(e.target.value.toUpperCase());
    if (onModuleChange) {
      onModuleChange(e.target.value.toUpperCase());
    }
  };

  // Group lectures by module
  const lecturesByModule = lectures.reduce((acc, lecture) => {
    const code = lecture.module_code;
    if (!acc[code]) {
      acc[code] = [];
    }
    acc[code].push(lecture);
    return acc;
  }, {} as Record<string, Lecture[]>);

  // Get unique modules
  const modules = Object.keys(lecturesByModule).sort();

  return (
    <div className="lecture-list-container">
      <div className="lecture-list-header">
        <h2>Uploaded Lectures</h2>
        <div className="filter-input">
          <input
            type="text"
            placeholder="Filter by module code..."
            value={filter}
            onChange={handleFilterChange}
          />
          {filter && (
            <button className="clear-filter" onClick={() => setFilter('')}>
              ×
            </button>
          )}
        </div>
      </div>

      {loading ? (
        <div className="lecture-list-loading">
          <div className="loading-spinner"></div>
          <p>Loading lectures...</p>
        </div>
      ) : error ? (
        <div className="lecture-list-error">
          <p>{error}</p>
          <button onClick={loadLectures}>Retry</button>
        </div>
      ) : lectures.length === 0 ? (
        <div className="lecture-list-empty">
          <span className="empty-icon">📚</span>
          <p>No lectures uploaded yet</p>
          <p className="empty-hint">
            Go to the Upload page to add your first lecture
          </p>
        </div>
      ) : (
        <div className="lecture-modules">
          {modules.map(moduleCode => (
            <div key={moduleCode} className="module-section">
              <div className="module-header">
                <h3>{moduleCode}</h3>
                <span className="lecture-count">
                  {lecturesByModule[moduleCode].length} lecture{lecturesByModule[moduleCode].length !== 1 ? 's' : ''}
                </span>
              </div>

              <div className="lecture-grid">
                {lecturesByModule[moduleCode]
                  .sort((a, b) => a.week_number - b.week_number)
                  .map(lecture => (
                    <div key={lecture.id} className="lecture-card">
                      <div className="lecture-week">Week {lecture.week_number}</div>
                      <h4 className="lecture-title">{lecture.title}</h4>
                      <div className="lecture-meta">
                        <span className="lecture-pages">
                          📄 {lecture.num_pages || '?'} pages
                        </span>
                        <span className="lecture-date">
                          {new Date(lecture.upload_date).toLocaleDateString()}
                        </span>
                      </div>
                      <div className="lecture-actions">
                        <button
                          className="delete-btn"
                          onClick={() => handleDelete(lecture)}
                          disabled={deleting === lecture.id}
                        >
                          {deleting === lecture.id ? 'Deleting...' : '🗑️ Delete'}
                        </button>
                      </div>
                    </div>
                  ))}
              </div>
            </div>
          ))}
        </div>
      )}

      {/* Stats footer */}
      {!loading && lectures.length > 0 && (
        <div className="lecture-stats">
          <div className="stat">
            <span className="stat-value">{lectures.length}</span>
            <span className="stat-label">Total Lectures</span>
          </div>
          <div className="stat">
            <span className="stat-value">{modules.length}</span>
            <span className="stat-label">Modules</span>
          </div>
          <div className="stat">
            <span className="stat-value">
              {lectures.reduce((sum, l) => sum + (l.num_pages || 0), 0)}
            </span>
            <span className="stat-label">Total Pages</span>
          </div>
        </div>
      )}
    </div>
  );
}
