import { useState, useEffect } from 'react';
import { getTopics } from '../services/api';
import type { Topic } from '../types';
import './Timeline.css';

interface TimelineProps {
  moduleCode: string;
}

interface WeekData {
  week: number;
  topics: {
    id: string;
    name: string;
    frequency: number;
    isIntroduced: boolean;
  }[];
}

export default function Timeline({ moduleCode }: TimelineProps) {
  const [weeks, setWeeks] = useState<WeekData[]>([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [selectedTopic, setSelectedTopic] = useState<Topic | null>(null);

  useEffect(() => {
    if (moduleCode) {
      loadTimeline();
    }
  }, [moduleCode]);

  const loadTimeline = async () => {
    setLoading(true);
    setError(null);

    try {
      const topics = await getTopics(moduleCode);

      // Build week-by-week data
      const weekMap = new Map<number, WeekData>();

      // Find first appearance of each topic
      const topicFirstWeek = new Map<string, number>();
      topics.forEach(topic => {
        if (topic.appearances && topic.appearances.length > 0) {
          const firstWeek = Math.min(...topic.appearances.map(a => a.week_number));
          topicFirstWeek.set(topic.id, firstWeek);
        }
      });

      // Populate weeks
      topics.forEach(topic => {
        if (topic.appearances) {
          topic.appearances.forEach(appearance => {
            const weekNum = appearance.week_number;

            if (!weekMap.has(weekNum)) {
              weekMap.set(weekNum, { week: weekNum, topics: [] });
            }

            const weekData = weekMap.get(weekNum)!;
            const isIntroduced = topicFirstWeek.get(topic.id) === weekNum;

            // Avoid duplicates
            if (!weekData.topics.find(t => t.id === topic.id)) {
              weekData.topics.push({
                id: topic.id,
                name: topic.name,
                frequency: appearance.frequency,
                isIntroduced
              });
            }
          });
        }
      });

      // Convert to sorted array
      const sortedWeeks = Array.from(weekMap.values())
        .sort((a, b) => a.week - b.week);

      setWeeks(sortedWeeks);

    } catch (err: any) {
      setError(err.response?.data?.detail || 'Failed to load timeline');
    } finally {
      setLoading(false);
    }
  };

  if (!moduleCode) {
    return (
      <div className="timeline-empty">
        <p>Select a module to view timeline</p>
      </div>
    );
  }

  if (loading) {
    return (
      <div className="timeline-loading">
        <div className="loading-spinner"></div>
        <p>Loading timeline...</p>
      </div>
    );
  }

  if (error) {
    return (
      <div className="timeline-error">
        <p>{error}</p>
      </div>
    );
  }

  if (weeks.length === 0) {
    return (
      <div className="timeline-empty">
        <span className="empty-icon">📅</span>
        <p>No topics detected yet</p>
        <p className="empty-hint">
          Run topic detection on the Topics page first.
        </p>
      </div>
    );
  }

  return (
    <div className="timeline-container">
      <h2>Topic Timeline: {moduleCode}</h2>
      <p className="timeline-subtitle">
        Track how topics are introduced and developed across weeks
      </p>

      <div className="timeline-legend">
        <span className="legend-item">
          <span className="legend-dot introduced"></span>
          Topic introduced
        </span>
        <span className="legend-item">
          <span className="legend-dot continued"></span>
          Topic continued
        </span>
      </div>

      <div className="timeline">
        {weeks.map((weekData) => (
          <div key={weekData.week} className="timeline-week">
            <div className="week-marker">
              <div className="week-number">Week {weekData.week}</div>
              <div className="week-line"></div>
            </div>

            <div className="week-topics">
              {weekData.topics.map((topic) => (
                <div
                  key={topic.id}
                  className={`topic-chip ${topic.isIntroduced ? 'introduced' : 'continued'}`}
                  title={`${topic.name} (${topic.frequency} mentions)`}
                >
                  <span className="topic-name">{topic.name}</span>
                  {topic.isIntroduced && <span className="new-badge">NEW</span>}
                  <span className="topic-freq">{topic.frequency}x</span>
                </div>
              ))}
            </div>
          </div>
        ))}
      </div>

      {/* Summary Stats */}
      <div className="timeline-stats">
        <div className="stat">
          <span className="stat-value">{weeks.length}</span>
          <span className="stat-label">Weeks</span>
        </div>
        <div className="stat">
          <span className="stat-value">
            {new Set(weeks.flatMap(w => w.topics.map(t => t.id))).size}
          </span>
          <span className="stat-label">Topics</span>
        </div>
        <div className="stat">
          <span className="stat-value">
            {weeks.reduce((sum, w) => sum + w.topics.filter(t => t.isIntroduced).length, 0)}
          </span>
          <span className="stat-label">Introductions</span>
        </div>
      </div>
    </div>
  );
}
