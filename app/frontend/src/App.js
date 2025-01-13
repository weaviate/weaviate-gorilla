// App.js
import { BrowserRouter as Router, Routes, Route } from 'react-router-dom';
import QueryVisualizer from './components/QueryVisualizer';
import QuerySearcher from './components/QuerySearcher';

function App() {
  return (
    <Router>
      <div className="min-h-screen bg-gray-100">
        <Routes>
          <Route path="/" element={<QueryVisualizer />} />
          <Route path="/search" element={<QuerySearcher />} />
        </Routes>
      </div>
    </Router>
  );
}

export default App;