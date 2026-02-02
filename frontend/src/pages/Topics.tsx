import { useState } from 'react';
import TopicMap from '../components/TopicMap';

export default function Topics() {
  const [moduleCode, setModuleCode] = useState('');
  const [activeModule, setActiveModule] = useState('');

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    setActiveModule(moduleCode.toUpperCase());
  };

  return (
    <div>
      <div style={{ marginBottom: '1rem' }}>
        <form onSubmit={handleSubmit} style={{ display: 'flex', gap: '0.5rem', maxWidth: '500px' }}>
          <input
            type="text"
            placeholder="Enter module code (e.g., COMP3001)"
            value={moduleCode}
            onChange={(e) => setModuleCode(e.target.value)}
            style={{
              flex: 1,
              padding: '0.75rem',
              border: '1px solid #ddd',
              borderRadius: '4px',
              fontSize: '1rem'
            }}
          />
          <button
            type="submit"
            disabled={!moduleCode}
            style={{
              padding: '0.75rem 1.5rem',
              background: '#646cff',
              color: 'white',
              border: 'none',
              borderRadius: '4px',
              cursor: 'pointer',
              fontWeight: '600'
            }}
          >
            Load Topics
          </button>
        </form>
      </div>

      <TopicMap moduleCode={activeModule} />
    </div>
  );
}
