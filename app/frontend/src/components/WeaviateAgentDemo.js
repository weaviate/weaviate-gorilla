// components/WeaviateAgentDemo.js
import { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { ArrowLeft, Send, Eye, EyeOff, Database } from 'lucide-react';

const WeaviateAgentDemo = () => {
  const navigate = useNavigate();
  const [formData, setFormData] = useState({
    weaviateUrl: '',
    weaviateApiKey: '',
    openaiApiKey: '',
    naturalLanguageQuery: ''
  });
  const [showKeys, setShowKeys] = useState(false);
  const [predictedQuery, setPredictedQuery] = useState(null);
  const [isLoading, setIsLoading] = useState(false);

  const handleInputChange = (e) => {
    const { name, value } = e.target;
    setFormData(prev => ({
      ...prev,
      [name]: value
    }));
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    setIsLoading(true);

    // Simulate API call delay
    await new Promise(resolve => setTimeout(resolve, 1000));

    // Mock predicted query
    setPredictedQuery({
      "database_schema": "{\"weaviate_collections\":[{\"name\":\"Restaurants\",\"properties\":[{\"name\":\"name\",\"data_type\":[\"string\"],\"description\":\"The name of the restaurant.\"},{\"name\":\"description\",\"data_type\":[\"string\"],\"description\":\"A detailed description and summary of the restaurant, including cuisine type and ambiance.\"},{\"name\":\"averageRating\",\"data_type\":[\"number\"],\"description\":\"The average rating score out of 5 for the restaurant.\"},{\"name\":\"openNow\",\"data_type\":[\"boolean\"],\"description\":\"A flag indicating whether the restaurant is currently open.\"}],\"envisioned_use_case_overview\":\"This schema focuses on enabling users to discover restaurants based on a comprehensive profile. With semantic search, users can find restaurants by cuisine, ambiance, or special features.\"}]}",
      "query": {
        "corresponding_natural_language_query": "What is the average rating of romantic Italian restaurants that have a rating of 4 or above?",
        "target_collection": "Restaurants",
        "search_query": "romantic Italian restaurants",
        "integer_property_filter": {
          "property_name": "averageRating",
          "operator": ">=",
          "value": 4
        },
        "text_property_filter": null,
        "boolean_property_filter": null,
        "integer_property_aggregation": {
          "property_name": "averageRating",
          "metrics": "MEAN"
        },
        "text_property_aggregation": null,
        "boolean_property_aggregation": null,
        "groupby_property": null
      }
    });

    setIsLoading(false);
  };

  return (
    <div className="w-full min-h-screen p-6 bg-cover bg-center" style={{ backgroundImage: 'url("/background.png")' }}>
      <div className="max-w-4xl mx-auto">
        <div className="flex items-center justify-between mb-8">
          <div className="flex items-center gap-4">
            <button
              onClick={() => navigate('/')}
              className="p-2 rounded hover:bg-gray-100"
            >
              <ArrowLeft size={24} />
            </button>
            <h1 className="text-3xl font-bold text-[#1c1468]">Weaviate Agent Demo</h1>
          </div>
          <button
            onClick={() => navigate('/')}
            className="px-4 py-2 bg-[#1c1468] text-white rounded-lg hover:bg-[#130e4a] flex items-center gap-2"
          >
            <Database size={16} />
            DB Gorilla
          </button>
        </div>

        <div className="bg-white rounded-lg shadow-md p-6 mb-6">
          <form onSubmit={handleSubmit} className="space-y-4">
            <div className="space-y-2">
              <label className="block text-sm font-medium text-gray-700">Weaviate URL</label>
              <input
                type="url"
                name="weaviateUrl"
                value={formData.weaviateUrl}
                onChange={handleInputChange}
                className="w-full p-2 border rounded"
                placeholder="https://your-weaviate-instance.com"
                required
              />
            </div>

            <div className="space-y-2 relative">
              <label className="block text-sm font-medium text-gray-700">Weaviate API Key</label>
              <div className="relative">
                <input
                  type={showKeys ? "text" : "password"}
                  name="weaviateApiKey"
                  value={formData.weaviateApiKey}
                  onChange={handleInputChange}
                  className="w-full p-2 border rounded"
                  required
                />
                <button
                  type="button"
                  onClick={() => setShowKeys(!showKeys)}
                  className="absolute right-2 top-1/2 -translate-y-1/2 text-gray-500 hover:text-gray-700"
                >
                  {showKeys ? <EyeOff size={16} /> : <Eye size={16} />}
                </button>
              </div>
            </div>

            <div className="space-y-2">
              <label className="block text-sm font-medium text-gray-700">OpenAI API Key</label>
              <div className="relative">
                <input
                  type={showKeys ? "text" : "password"}
                  name="openaiApiKey"
                  value={formData.openaiApiKey}
                  onChange={handleInputChange}
                  className="w-full p-2 border rounded"
                  required
                />
              </div>
            </div>

            <div className="space-y-2">
              <label className="block text-sm font-medium text-gray-700">Natural Language Query</label>
              <textarea
                name="naturalLanguageQuery"
                value={formData.naturalLanguageQuery}
                onChange={handleInputChange}
                className="w-full p-2 border rounded h-24"
                placeholder="Describe what you want to find out..."
                required
              />
            </div>

            <div className="flex justify-end">
              <button
                type="submit"
                disabled={isLoading}
                className="px-4 py-2 bg-[#1c1468] text-white rounded hover:bg-[#130e4a] flex items-center gap-2 disabled:opacity-50"
              >
                <Send size={16} />
                {isLoading ? 'Generating...' : 'Generate Query'}
              </button>
            </div>
          </form>
        </div>

        {predictedQuery && (
          <div className="bg-white rounded-lg shadow-md p-6">
            <h2 className="text-xl font-bold mb-4">Predicted Query</h2>
            <div className="space-y-2 font-mono text-sm bg-gray-50 p-4 rounded">
              <p><span className="font-semibold">Collection:</span> {predictedQuery.query.target_collection}</p>
              <p><span className="font-semibold">Search Query:</span> {predictedQuery.query.search_query}</p>
              {predictedQuery.query.integer_property_filter && (
                <p>
                  <span className="font-semibold">Filter:</span>{' '}
                  {predictedQuery.query.integer_property_filter.property_name}{' '}
                  {predictedQuery.query.integer_property_filter.operator}{' '}
                  {predictedQuery.query.integer_property_filter.value}
                </p>
              )}
              {predictedQuery.query.integer_property_aggregation && (
                <p>
                  <span className="font-semibold">Aggregation:</span>{' '}
                  {predictedQuery.query.integer_property_aggregation.metrics} of{' '}
                  {predictedQuery.query.integer_property_aggregation.property_name}
                </p>
              )}
            </div>
          </div>
        )}
      </div>
    </div>
  );
};

export default WeaviateAgentDemo;