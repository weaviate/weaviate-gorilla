import { BrowserRouter as Router, Routes, Route } from 'react-router-dom';
import QueryVisualizer from './components/QueryVisualizer';
import QueryBuilder from './components/QueryBuilder';
import QuerySearcher from './components/QuerySearcher';
import WeaviateAgentDemo from './components/WeaviateAgentDemo';
import Home from './components/Home';

function App() {
  return (
    <Router>
      <div className="min-h-screen bg-gray-100">
        <Routes>
          <Route path="/" element={<Home />} />
          <Route path = "/visualizer" element={<QueryVisualizer />} />
          <Route path = "/query-builder" element={<QueryBuilder />} />
          <Route path="/search" element={<QuerySearcher />} />
          <Route path="/demo" element={<WeaviateAgentDemo />} />
        </Routes>
      </div>
    </Router>
  );
}

export default App;