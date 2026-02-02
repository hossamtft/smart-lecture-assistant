import { useState } from 'react';
import TopicMap from '../components/TopicMap';
import Timeline from '../components/Timeline';
import SummaryViewer from '../components/SummaryViewer';
import './Topics.css';

type TabType = 'map' | 'timeline' | 'summaries';

export default function Topics() {
  const [moduleCode, setModuleCode] = useState('');
  const [activeModule, setActiveModule] = useState('');
  const [activeTab, setActiveTab] = useState<TabType>('map');

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    setActiveModule(moduleCode.toUpperCase());
  };

  return (
    <div className="topics-page">
      {/* Module Input */}
      <div className="topics-header">
        <form onSubmit={handleSubmit} className="module-form">
          <input
            type="text"
            placeholder="Enter module code (e.g., COMP3001)"
            value={moduleCode}
            onChange={(e) => setModuleCode(e.target.value)}
            className="module-input"
          />
          <button type="submit" disabled={!moduleCode} className="load-btn">
            Load Topics
          </button>
        </form>

        {activeModule && (
          <div className="tabs">
            <button
              className={`tab ${activeTab === 'map' ? 'active' : ''}`}
              onClick={() => setActiveTab('map')}
            >
              🗺️ Topic Map
            </button>
            <button
              className={`tab ${activeTab === 'timeline' ? 'active' : ''}`}
              onClick={() => setActiveTab('timeline')}
            >
              📅 Timeline
            </button>
            <button
              className={`tab ${activeTab === 'summaries' ? 'active' : ''}`}
              onClick={() => setActiveTab('summaries')}
            >
              📝 Summaries
            </button>
          </div>
        )}
      </div>

      {/* Tab Content */}
      <div className="tab-content">
        {activeTab === 'map' && <TopicMap moduleCode={activeModule} />}
        {activeTab === 'timeline' && <Timeline moduleCode={activeModule} />}
        {activeTab === 'summaries' && <SummaryViewer moduleCode={activeModule} />}
      </div>
    </div>
  );
}
