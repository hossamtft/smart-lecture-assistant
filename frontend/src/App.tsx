import { BrowserRouter as Router, Routes, Route, Link } from 'react-router-dom'
import './App.css'

// Placeholder components (to be implemented)
const Dashboard = () => <div><h1>Dashboard</h1><p>Topic maps and analytics will appear here</p></div>
const Upload = () => <div><h1>Upload Lectures</h1><p>Drag and drop interface coming soon</p></div>
const Topics = () => <div><h1>Topics</h1><p>Cross-lecture topics will be displayed here</p></div>
const Query = () => <div><h1>Q&A</h1><p>Chat interface for RAG-based queries</p></div>

function App() {
  return (
    <Router>
      <div className="app">
        <nav className="navbar">
          <div className="nav-brand">
            <h1>Smart Lecture Assistant</h1>
          </div>
          <ul className="nav-links">
            <li><Link to="/">Dashboard</Link></li>
            <li><Link to="/upload">Upload</Link></li>
            <li><Link to="/topics">Topics</Link></li>
            <li><Link to="/query">Q&A</Link></li>
          </ul>
        </nav>

        <main className="main-content">
          <Routes>
            <Route path="/" element={<Dashboard />} />
            <Route path="/upload" element={<Upload />} />
            <Route path="/topics" element={<Topics />} />
            <Route path="/query" element={<Query />} />
          </Routes>
        </main>
      </div>
    </Router>
  )
}

export default App
