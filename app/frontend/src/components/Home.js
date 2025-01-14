import { useNavigate } from 'react-router-dom';
import { Database } from 'lucide-react';

const Home = () => {
  const navigate = useNavigate();

  return (
    <div className="w-full min-h-screen p-6 bg-cover bg-center" style={{ backgroundImage: 'url("/background.png")' }}>
      <div className="max-w-4xl mx-auto">
        <div className="text-center mt-20">
          <h1 className="text-5xl font-bold text-[#1c1468] mb-6">DBGorilla Project</h1>
          
          <p className="text-xl text-gray-600 mb-12 max-w-2xl mx-auto">
            A powerful tool for visualizing and exploring your datasets. Use natural language to query your data 
            or try our advanced Weaviate Agents integration for intelligent data analysis.
          </p>

          <div className="flex items-center justify-center gap-6">
            <button
              onClick={() => navigate('/visualizer')}
              className="px-6 py-3 bg-[#1c1468] text-white rounded-lg hover:bg-[#130e4a] flex items-center gap-2 text-lg"
            >
              <Database size={20} />
              Visualize Dataset
            </button>

            <button
              onClick={() => navigate('/demo')}
              className="px-6 py-3 bg-green-600 text-white rounded-lg hover:bg-green-700 text-lg"
            >
              Try it with Weaviate Agents
            </button>
          </div>
        </div>
      </div>
    </div>
  );
};

export default Home;
