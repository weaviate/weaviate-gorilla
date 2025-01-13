import { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { ChevronLeft, ChevronRight, Database, Search, Check, X, Edit2, Save } from 'lucide-react';

const QueryEditor = ({ query, onSave, onCancel }) => {
  const [editedQuery, setEditedQuery] = useState(query);

  const handleChange = (field, value) => {
    setEditedQuery(prev => ({
      ...prev,
      [field]: value
    }));
  };

  const handleFilterChange = (field, value) => {
    setEditedQuery(prev => ({
      ...prev,
      integer_property_filter: {
        ...prev.integer_property_filter,
        [field]: field === 'value' ? Number(value) : value
      }
    }));
  };

  const handleAggregationChange = (field, value) => {
    setEditedQuery(prev => ({
      ...prev,
      integer_property_aggregation: {
        ...prev.integer_property_aggregation,
        [field]: value
      }
    }));
  };

  return (
    <div className="space-y-4 bg-white p-6 rounded-lg shadow-md">
      <div className="space-y-2">
        <label className="block text-sm font-medium">Collection</label>
        <input
          type="text"
          value={editedQuery.target_collection}
          onChange={(e) => handleChange('target_collection', e.target.value)}
          className="w-full p-2 border rounded"
        />
      </div>

      <div className="space-y-2">
        <label className="block text-sm font-medium">Search Query</label>
        <input
          type="text"
          value={editedQuery.search_query}
          onChange={(e) => handleChange('search_query', e.target.value)}
          className="w-full p-2 border rounded"
        />
      </div>

      {editedQuery.integer_property_filter && (
        <div className="space-y-2">
          <h3 className="font-medium">Integer Property Filter</h3>
          <div className="grid grid-cols-3 gap-2">
            <input
              type="text"
              value={editedQuery.integer_property_filter.property_name}
              onChange={(e) => handleFilterChange('property_name', e.target.value)}
              className="p-2 border rounded"
              placeholder="Property"
            />
            <select
              value={editedQuery.integer_property_filter.operator}
              onChange={(e) => handleFilterChange('operator', e.target.value)}
              className="p-2 border rounded"
            >
              <option value="<">&lt;</option>
              <option value=">">&gt;</option>
              <option value="=">=</option>
            </select>
            <input
              type="number"
              value={editedQuery.integer_property_filter.value}
              onChange={(e) => handleFilterChange('value', e.target.value)}
              className="p-2 border rounded"
            />
          </div>
        </div>
      )}

      {editedQuery.integer_property_aggregation && (
        <div className="space-y-2">
          <h3 className="font-medium">Aggregation</h3>
          <div className="grid grid-cols-2 gap-2">
            <select
              value={editedQuery.integer_property_aggregation.metrics}
              onChange={(e) => handleAggregationChange('metrics', e.target.value)}
              className="p-2 border rounded"
            >
              <option value="MEAN">Mean</option>
              <option value="SUM">Sum</option>
              <option value="COUNT">Count</option>
            </select>
            <input
              type="text"
              value={editedQuery.integer_property_aggregation.property_name}
              onChange={(e) => handleAggregationChange('property_name', e.target.value)}
              className="p-2 border rounded"
              placeholder="Property"
            />
          </div>
        </div>
      )}

      <div className="space-y-2">
        <label className="block text-sm font-medium">Group By Property</label>
        <input
          type="text"
          value={editedQuery.groupby_property || ''}
          onChange={(e) => handleChange('groupby_property', e.target.value)}
          className="w-full p-2 border rounded"
        />
      </div>

      <div className="flex justify-end space-x-2 mt-4">
        <button
          onClick={onCancel}
          className="px-4 py-2 bg-gray-100 rounded hover:bg-gray-200 flex items-center gap-2"
        >
          <X size={16} />
          Cancel
        </button>
        <button
          onClick={() => onSave(editedQuery)}
          className="px-4 py-2 bg-[#1c1468] text-white rounded hover:bg-[#130e4a] flex items-center gap-2"
        >
          <Save size={16} />
          Save Changes
        </button>
      </div>
    </div>
  );
};

const QueryVisualizer = () => {
  const navigate = useNavigate();
  const [currentIndex, setCurrentIndex] = useState(0);
  const [data, setData] = useState([]);
  const [showSchema, setShowSchema] = useState(true);
  const [isEditing, setIsEditing] = useState(false);

  useEffect(() => {
    fetchData();
  }, []);

  const fetchData = async () => {
    try {
      const response = await fetch('http://localhost:8000/data');
      const jsonData = await response.json();
      setData(jsonData);
    } catch (error) {
      console.error('Error fetching data:', error);
    }
  };

  const handleUpdateQuery = async (updatedQuery) => {
    try {
      const response = await fetch('http://localhost:8000/update-query', {
        method: 'PUT',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          index: currentIndex,
          updated_query: updatedQuery,
        }),
      });

      if (response.ok) {
        await fetchData();
        setIsEditing(false);
      } else {
        console.error('Failed to update query');
      }
    } catch (error) {
      console.error('Error updating query:', error);
    }
  };

  if (!data.length) {
    return <div>Loading...</div>;
  }

  const currentItem = data[currentIndex];

  const handlePrevious = () => {
    setCurrentIndex((prev) => (prev > 0 ? prev - 1 : data.length - 1));
    setIsEditing(false);
  };

  const handleNext = () => {
    setCurrentIndex((prev) => (prev < data.length - 1 ? prev + 1 : 0));
    setIsEditing(false);
  };
  return (
    <div className="w-full p-6 min-h-screen bg-cover bg-center" style={{ backgroundImage: 'url("/background.png")' }}>
      <div className="flex items-center mb-12 relative mt-8">
        <h1 className="text-4xl font-bold text-[#1c1468] absolute left-1/2 -translate-x-1/2">Dataset Visualizer</h1>
        <button
          onClick={() => navigate('/search')}
          className="px-4 py-2 bg-[#1c1468] text-white rounded-lg hover:bg-[#130e4a] flex items-center gap-2 ml-auto"
        >
          <Search size={16} />
          Search Queries
        </button>
      </div>

      <div className="flex items-center justify-center mb-6 gap-8">
        <button
          onClick={handlePrevious}
          className="p-2 rounded bg-[#1c1468] text-white hover:bg-[#130e4a]"
        >
          <ChevronLeft size={24} />
        </button>
        <div className="flex items-center">
          <span className="text-2xl font-semibold">
            Query {currentIndex + 1} of {data.length}
          </span>
        </div>
        <button
          onClick={handleNext}
          className="p-2 rounded bg-[#1c1468] text-white hover:bg-[#130e4a]"
        >
          <ChevronRight size={24} />
        </button>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        <div className="space-y-6">
          {JSON.parse(currentItem.database_schema).weaviate_collections.map((collection, idx) => (
            <div key={idx} className="bg-gray-50 p-4 rounded-lg border border-gray-200">
              <div className="flex items-center gap-2 mb-4">
                <Database className="text-[#1c1468]" size={20} />
                <h3 className="text-lg font-semibold">{collection.name}</h3>
              </div>
              <p className="text-sm text-gray-600 mb-4">{collection.envisioned_use_case_overview}</p>
              <div className="space-y-3">
                {collection.properties.map((prop, propIdx) => (
                  <div key={propIdx} className="flex items-start gap-4 p-2 bg-white rounded border border-gray-100">
                    <div className="flex-1">
                      <p className="font-medium">{prop.name}</p>
                      <p className="text-sm text-gray-500">{prop.description}</p>
                    </div>
                    <div className="text-sm px-2 py-1 rounded bg-[#e8fae3] text-[#1c1468]">
                      {prop.data_type[0]}
                    </div>
                  </div>
                ))}
              </div>
            </div>
          ))}
        </div>

        <div className="space-y-6">
          <div className="bg-white p-6 rounded-lg shadow-md">
            <div className="flex justify-between items-center mb-3">
              <h2 className="text-xl font-bold">Query Details</h2>
              {!isEditing && (
                <button
                  onClick={() => setIsEditing(true)}
                  className="p-2 rounded bg-[#1c1468] text-white hover:bg-[#130e4a] flex items-center gap-2"
                >
                  <Edit2 size={16} />
                  Edit Query
                </button>
              )}
            </div>
            
            {isEditing ? (
              <QueryEditor
                query={currentItem.query}
                onSave={handleUpdateQuery}
                onCancel={() => setIsEditing(false)}
              />
            ) : (
              <div className="space-y-2">
                <p><span className="font-semibold">Natural Language Query:</span> {currentItem.query.corresponding_natural_language_query}</p>
                <p><span className="font-semibold">Collection:</span> {currentItem.query.target_collection}</p>
                <p><span className="font-semibold">Search Query:</span> {currentItem.query.search_query}</p>
                {currentItem.query.integer_property_filter && (
                  <p>
                    <span className="font-semibold">Filter:</span>{' '}
                    {currentItem.query.integer_property_filter.property_name}{' '}
                    {currentItem.query.integer_property_filter.operator}{' '}
                    {currentItem.query.integer_property_filter.value}
                  </p>
                )}
                {currentItem.query.integer_property_aggregation && (
                  <p>
                    <span className="font-semibold">Aggregation:</span>{' '}
                    {currentItem.query.integer_property_aggregation.metrics} of{' '}
                    {currentItem.query.integer_property_aggregation.property_name}
                  </p>
                )}
                {currentItem.query.groupby_property && (
                  <p><span className="font-semibold">Group By:</span> {currentItem.query.groupby_property}</p>
                )}
              </div>
            )}
          </div>
        </div>
      </div>
    </div>
  );
};

export default QueryVisualizer;