import { BrowserRouter as Router, Routes, Route, Link } from 'react-router-dom'
import Dashboard from './pages/Dashboard'
import Upload from './pages/Upload'
import Lectures from './pages/Lectures'
import Topics from './pages/Topics'
import Query from './pages/Query'
import './App.css'

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
            <li><Link to="/lectures">Lectures</Link></li>
            <li><Link to="/topics">Topics</Link></li>
            <li><Link to="/query">Q&A</Link></li>
          </ul>
        </nav>

        <main className="main-content">
          <Routes>
            <Route path="/" element={<Dashboard />} />
            <Route path="/upload" element={<Upload />} />
            <Route path="/lectures" element={<Lectures />} />
            <Route path="/topics" element={<Topics />} />
            <Route path="/query" element={<Query />} />
          </Routes>
        </main>
      </div>
    </Router>
  )
}

export default App
