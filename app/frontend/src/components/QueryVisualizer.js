import { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { ChevronLeft, ChevronRight, Database, Search, Check, X, Edit2, Save, ChevronDown, ChevronUp, Plus, Trash2, Home } from 'lucide-react';

const QueryEditor = ({ query, onSave, onCancel }) => {
  const [editedQuery, setEditedQuery] = useState(query);

  const handleChange = (field, value) => {
    setEditedQuery(prev => ({
      ...prev,
      [field]: value
    }));
  };

  const handleDelete = (field) => {
    setEditedQuery(prev => ({
      ...prev,
      [field]: null
    }));
  };

  const handleFilterChange = (type, field, value) => {
    setEditedQuery(prev => ({
      ...prev,
      [`${type}_property_filter`]: {
        ...prev[`${type}_property_filter`],
        [field]: type === 'integer' && field === 'value' ? Number(value) : value
      }
    }));
  };

  const addFilter = (type) => {
    const newFilter = {
      property_name: '',
      operator: type === 'integer' ? '>' : '=',
      value: type === 'integer' ? 0 : ''
    };
    
    setEditedQuery(prev => ({
      ...prev,
      [`${type}_property_filter`]: newFilter
    }));
  };

  const removeFilter = (type) => {
    setEditedQuery(prev => ({
      ...prev,
      [`${type}_property_filter`]: null
    }));
  };

  const addAggregation = (type) => {
    const newAggregation = {
      property_name: '',
      metrics: ''
    };
    
    if (type === 'integer') {
      setEditedQuery(prev => ({
        ...prev,
        integer_property_aggregation: newAggregation
      }));
    } else if (type === 'text') {
      setEditedQuery(prev => ({
        ...prev,
        text_property_aggregation: {
          ...newAggregation,
          top_occurrences_limit: 5
        }
      }));
    } else if (type === 'boolean') {
      setEditedQuery(prev => ({
        ...prev,
        boolean_property_aggregation: newAggregation
      }));
    }
  };

  const removeAggregation = (type) => {
    setEditedQuery(prev => ({
      ...prev,
      [`${type}_property_aggregation`]: null
    }));
  };

  const handleAggregationChange = (type, field, value) => {
    setEditedQuery(prev => ({
      ...prev,
      [`${type}_property_aggregation`]: {
        ...prev[`${type}_property_aggregation`],
        [field]: field === 'top_occurrences_limit' ? Number(value) : value
      }
    }));
  };

  return (
    <div className="space-y-4 bg-white p-6 rounded-lg shadow-md">
      <div className="space-y-2">
        <div className="flex justify-between items-center">
          <label className="block text-sm font-medium">Natural Language Query</label>
          <button onClick={() => handleDelete('corresponding_natural_language_query')} className="text-red-600 hover:text-red-700">
            <Trash2 size={14} />
          </button>
        </div>
        <input
          type="text"
          value={editedQuery.corresponding_natural_language_query || ''}
          onChange={(e) => handleChange('corresponding_natural_language_query', e.target.value)}
          className="w-full p-2 border rounded"
        />
      </div>

      <div className="space-y-2">
        <div className="flex justify-between items-center">
          <label className="block text-sm font-medium">Collection</label>
          <button onClick={() => handleDelete('target_collection')} className="text-red-600 hover:text-red-700">
            <Trash2 size={14} />
          </button>
        </div>
        <input
          type="text"
          value={editedQuery.target_collection || ''}
          onChange={(e) => handleChange('target_collection', e.target.value)}
          className="w-full p-2 border rounded"
        />
      </div>

      <div className="space-y-2">
        <div className="flex justify-between items-center">
          <label className="block text-sm font-medium">Search Query</label>
          <button onClick={() => handleDelete('search_query')} className="text-red-600 hover:text-red-700">
            <Trash2 size={14} />
          </button>
        </div>
        <input
          type="text"
          value={editedQuery.search_query || ''}
          onChange={(e) => handleChange('search_query', e.target.value)}
          className="w-full p-2 border rounded"
        />
      </div>

      {/* Filters Section */}
      <div className="space-y-4">
        <div className="flex items-center justify-between">
          <h3 className="font-medium">Filters</h3>
          <div className="space-x-2">
            {!editedQuery.integer_property_filter && (
              <button
                onClick={() => addFilter('integer')}
                className="px-3 py-1 bg-blue-100 text-blue-700 rounded hover:bg-blue-200 text-sm"
              >
                Add Integer Filter
              </button>
            )}
            {!editedQuery.text_property_filter && (
              <button
                onClick={() => addFilter('text')}
                className="px-3 py-1 bg-green-100 text-green-700 rounded hover:bg-green-200 text-sm"
              >
                Add Text Filter
              </button>
            )}
            {!editedQuery.boolean_property_filter && (
              <button
                onClick={() => addFilter('boolean')}
                className="px-3 py-1 bg-yellow-100 text-yellow-700 rounded hover:bg-yellow-200 text-sm"
              >
                Add Boolean Filter
              </button>
            )}
          </div>
        </div>

        {editedQuery.integer_property_filter && (
          <div className="p-3 border rounded-lg bg-blue-50">
            <div className="flex justify-between items-center mb-2">
              <h4 className="text-sm font-medium">Integer Filter</h4>
              <button onClick={() => removeFilter('integer')} className="text-red-600 hover:text-red-700">
                <Trash2 size={14} />
              </button>
            </div>
            <div className="grid grid-cols-3 gap-2">
              <input
                type="text"
                value={editedQuery.integer_property_filter.property_name}
                onChange={(e) => handleFilterChange('integer', 'property_name', e.target.value)}
                className="p-2 border rounded"
                placeholder="Property"
              />
              <select
                value={editedQuery.integer_property_filter.operator}
                onChange={(e) => handleFilterChange('integer', 'operator', e.target.value)}
                className="p-2 border rounded"
              >
                <option value="<">&lt;</option>
                <option value=">">&gt;</option>
                <option value="=">=</option>
              </select>
              <input
                type="number"
                value={editedQuery.integer_property_filter.value}
                onChange={(e) => handleFilterChange('integer', 'value', e.target.value)}
                className="p-2 border rounded"
              />
            </div>
          </div>
        )}

        {editedQuery.text_property_filter && (
          <div className="p-3 border rounded-lg bg-green-50">
            <div className="flex justify-between items-center mb-2">
              <h4 className="text-sm font-medium">Text Filter</h4>
              <button onClick={() => removeFilter('text')} className="text-red-600 hover:text-red-700">
                <Trash2 size={14} />
              </button>
            </div>
            <div className="grid grid-cols-3 gap-2">
              <input
                type="text"
                value={editedQuery.text_property_filter.property_name}
                onChange={(e) => handleFilterChange('text', 'property_name', e.target.value)}
                className="p-2 border rounded"
                placeholder="Property"
              />
              <select
                value={editedQuery.text_property_filter.operator}
                onChange={(e) => handleFilterChange('text', 'operator', e.target.value)}
                className="p-2 border rounded"
              >
                <option value="=">=</option>
                <option value="contains">Contains</option>
                <option value="starts_with">Starts With</option>
                <option value="ends_with">Ends With</option>
              </select>
              <input
                type="text"
                value={editedQuery.text_property_filter.value}
                onChange={(e) => handleFilterChange('text', 'value', e.target.value)}
                className="p-2 border rounded"
              />
            </div>
          </div>
        )}

        {editedQuery.boolean_property_filter && (
          <div className="p-3 border rounded-lg bg-yellow-50">
            <div className="flex justify-between items-center mb-2">
              <h4 className="text-sm font-medium">Boolean Filter</h4>
              <button onClick={() => removeFilter('boolean')} className="text-red-600 hover:text-red-700">
                <Trash2 size={14} />
              </button>
            </div>
            <div className="grid grid-cols-2 gap-2">
              <input
                type="text"
                value={editedQuery.boolean_property_filter.property_name}
                onChange={(e) => handleFilterChange('boolean', 'property_name', e.target.value)}
                className="p-2 border rounded"
                placeholder="Property"
              />
              <select
                value={editedQuery.boolean_property_filter.value}
                onChange={(e) => handleFilterChange('boolean', 'value', e.target.value)}
                className="p-2 border rounded"
              >
                <option value="true">True</option>
                <option value="false">False</option>
              </select>
            </div>
          </div>
        )}
      </div>

      {/* Aggregations Section */}
      <div className="space-y-4">
        <div className="flex items-center justify-between">
          <h3 className="font-medium">Aggregations</h3>
          <div className="space-x-2">
            {!editedQuery.integer_property_aggregation && (
              <button
                onClick={() => addAggregation('integer')}
                className="px-3 py-1 bg-blue-100 text-blue-700 rounded hover:bg-blue-200 text-sm"
              >
                Add Integer Aggregation
              </button>
            )}
            {!editedQuery.text_property_aggregation && (
              <button
                onClick={() => addAggregation('text')}
                className="px-3 py-1 bg-green-100 text-green-700 rounded hover:bg-green-200 text-sm"
              >
                Add Text Aggregation
              </button>
            )}
            {!editedQuery.boolean_property_aggregation && (
              <button
                onClick={() => addAggregation('boolean')}
                className="px-3 py-1 bg-yellow-100 text-yellow-700 rounded hover:bg-yellow-200 text-sm"
              >
                Add Boolean Aggregation
              </button>
            )}
          </div>
        </div>

        {editedQuery.integer_property_aggregation && (
          <div className="p-3 border rounded-lg bg-blue-50">
            <div className="flex justify-between items-center mb-2">
              <h4 className="text-sm font-medium">Integer Aggregation</h4>
              <button
                onClick={() => removeAggregation('integer')}
                className="text-red-600 hover:text-red-700"
              >
                <Trash2 size={14} />
              </button>
            </div>
            <div className="grid grid-cols-2 gap-2">
              <input
                type="text"
                value={editedQuery.integer_property_aggregation.property_name}
                onChange={(e) => handleAggregationChange('integer', 'property_name', e.target.value)}
                className="p-2 border rounded"
                placeholder="Property Name"
              />
              <select
                value={editedQuery.integer_property_aggregation.metrics}
                onChange={(e) => handleAggregationChange('integer', 'metrics', e.target.value)}
                className="p-2 border rounded"
              >
                <option value="">Select Metric</option>
                <option value="MEAN">Mean</option>
                <option value="MEDIAN">Median</option>
                <option value="MODE">Mode</option>
                <option value="MIN">Min</option>
                <option value="MAX">Max</option>
              </select>
            </div>
          </div>
        )}

        {editedQuery.text_property_aggregation && (
          <div className="p-3 border rounded-lg bg-green-50">
            <div className="flex justify-between items-center mb-2">
              <h4 className="text-sm font-medium">Text Aggregation</h4>
              <button
                onClick={() => removeAggregation('text')}
                className="text-red-600 hover:text-red-700"
              >
                <Trash2 size={14} />
              </button>
            </div>
            <div className="grid grid-cols-2 gap-2">
              <input
                type="text"
                value={editedQuery.text_property_aggregation.property_name}
                onChange={(e) => handleAggregationChange('text', 'property_name', e.target.value)}
                className="p-2 border rounded"
                placeholder="Property Name"
              />
              <select
                value={editedQuery.text_property_aggregation.metrics}
                onChange={(e) => handleAggregationChange('text', 'metrics', e.target.value)}
                className="p-2 border rounded"
              >
                <option value="">Select Metric</option>
                <option value="COUNT">Count</option>
                <option value="TYPE">Type</option>
                <option value="TOP_OCCURRENCES">Top Occurrences</option>
              </select>
            </div>
          </div>
        )}

        {editedQuery.boolean_property_aggregation && (
          <div className="p-3 border rounded-lg bg-yellow-50">
            <div className="flex justify-between items-center mb-2">
              <h4 className="text-sm font-medium">Boolean Aggregation</h4>
              <button
                onClick={() => removeAggregation('boolean')}
                className="text-red-600 hover:text-red-700"
              >
                <Trash2 size={14} />
              </button>
            </div>
            <div className="grid grid-cols-2 gap-2">
              <input
                type="text"
                value={editedQuery.boolean_property_aggregation.property_name}
                onChange={(e) => handleAggregationChange('boolean', 'property_name', e.target.value)}
                className="p-2 border rounded"
                placeholder="Property Name"
              />
              <select
                value={editedQuery.boolean_property_aggregation.metrics}
                onChange={(e) => handleAggregationChange('boolean', 'metrics', e.target.value)}
                className="p-2 border rounded"
              >
                <option value="">Select Metric</option>
                <option value="COUNT">Count</option>
                <option value="TYPE">Type</option>
                <option value="TOTAL_TRUE">Total True</option>
                <option value="TOTAL_FALSE">Total False</option>
                <option value="PERCENTAGE_TRUE">Percentage True</option>
                <option value="PERCENTAGE_FALSE">Percentage False</option>
              </select>
            </div>
          </div>
        )}
      </div>

      <div className="space-y-2">
        <div className="flex justify-between items-center">
          <label className="block text-sm font-medium">Group By Property</label>
          <button onClick={() => handleDelete('groupby_property')} className="text-red-600 hover:text-red-700">
            <Trash2 size={14} />
          </button>
        </div>
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
  const [expandedSchemas, setExpandedSchemas] = useState({});
  const [isEditing, setIsEditing] = useState(false);

  useEffect(() => {
    fetchData();
  }, []);

  const fetchData = async () => {
    try {
      const response = await fetch('http://localhost:8000/data');
      const jsonData = await response.json();
      setData(jsonData);
      // Initialize expanded state for each schema to true (expanded by default)
      const initialExpandedState = {};
      jsonData[0]?.database_schema && JSON.parse(jsonData[0].database_schema).weaviate_collections.forEach((_, idx) => {
        initialExpandedState[idx] = true;
      });
      setExpandedSchemas(initialExpandedState);
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

  const toggleSchema = (idx) => {
    setExpandedSchemas(prev => ({
      ...prev,
      [idx]: !prev[idx]
    }));
  };

  const renderQueryResult = (result) => {
    if (!result) return null;
  
    // Attempt to parse JSON; if it fails, just show the string output
    if (typeof result === 'string') {
      try {
        const parsedResult = JSON.parse(result);
        // If parsing succeeded, we can optionally handle old logic here:
        return (
          <div>
            <h3 className="text-lg font-semibold mb-4">Query Result</h3>
            <div className="p-4 bg-gray-50 rounded-lg border border-gray-200">
              {/* If your backend still sometimes returns a structured JSON result: */}
              {parsedResult.integer_aggregation_result !== undefined && (
                <div className="mb-4">
                  <h4 className="font-medium text-sm text-gray-700">Integer Aggregation</h4>
                  <p className="text-lg">{parsedResult.integer_aggregation_result}</p>
                </div>
              )}
  
              {parsedResult.text_aggregation_result && (
                <div className="mb-4">
                  <h4 className="font-medium text-sm text-gray-700">Text Aggregation</h4>
                  {Array.isArray(parsedResult.text_aggregation_result) ? (
                    <ul className="list-disc pl-5">
                      {parsedResult.text_aggregation_result.map((item, idx) => (
                        <li key={idx}>{item}</li>
                      ))}
                    </ul>
                  ) : (
                    <p className="text-lg">{parsedResult.text_aggregation_result}</p>
                  )}
                </div>
              )}
  
              {parsedResult.boolean_aggregation_result !== undefined && (
                <div className="mb-4">
                  <h4 className="font-medium text-sm text-gray-700">Boolean Aggregation</h4>
                  <p className="text-lg">
                    {typeof parsedResult.boolean_aggregation_result === 'boolean'
                      ? parsedResult.boolean_aggregation_result.toString()
                      : parsedResult.boolean_aggregation_result}
                  </p>
                </div>
              )}
  
              {parsedResult.filtered_objects && parsedResult.filtered_objects.length > 0 && (
                <div>
                  <h4 className="font-medium text-sm text-gray-700 mb-2">Filtered Objects</h4>
                  <div className="max-h-60 overflow-y-auto">
                    <pre className="bg-gray-100 p-3 rounded text-sm whitespace-pre-wrap">
                      {JSON.stringify(parsedResult.filtered_objects, null, 2)}
                    </pre>
                  </div>
                </div>
              )}
            </div>
          </div>
        );
      } catch (error) {
        return (
          <div>
            <h3 className="text-xl font-semibold mb-4 mt-6">Query Execution Result</h3>
            <div className="p-4 bg-gray-50 rounded-lg border border-gray-200">
              <pre className="whitespace-pre-wrap">{result}</pre>
            </div>
          </div>
        );
      }
    }
  
    // If it's not a string (e.g., already an object), fall back to your old rendering logic
    const parsedResult = result;
    return (
      <div>
        <h3 className="text-lg font-semibold mb-4">Query Result</h3>
        <div className="p-4 bg-gray-50 rounded-lg border border-gray-200">
          {/* ...same logic as above for parsed objects... */}
        </div>
      </div>
    );
  };

  return (
    <div className="w-full p-6 min-h-screen bg-cover bg-center" style={{ backgroundImage: 'url("/background.png")' }}>
      <div className="flex items-center mb-12 relative mt-8">
        <div className="flex items-center gap-2">
          <button
            onClick={() => navigate('/')}
            className="px-4 py-2 bg-[#1c1468] text-white rounded-lg hover:bg-[#130e4a] flex items-center gap-2"
          >
            <Home size={16} />
            Home
          </button>
          <button
            onClick={() => navigate('/demo')}
            className="px-4 py-2 bg-green-600 text-white rounded-lg hover:bg-green-700 flex items-center gap-2"
          >
            Try it with Weaviate Agents
          </button>
        </div>
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
              <div className="flex items-center justify-between gap-2 mb-4">
                <div className="flex items-center gap-2">
                  <Database className="text-[#1c1468]" size={20} />
                  <h3 className="text-lg font-semibold">{collection.name}</h3>
                </div>
                <button
                  onClick={() => toggleSchema(idx)}
                  className="p-2 rounded bg-[#1c1468] text-white hover:bg-[#130e4a]"
                >
                  {expandedSchemas[idx] ? <ChevronUp size={16} /> : <ChevronDown size={16} />}
                </button>
              </div>
              {expandedSchemas[idx] && (
                <>
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
                </>
              )}
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
              <>
                <div className="space-y-2">
                  {currentItem.query.corresponding_natural_language_query && (
                    <p><span className="font-semibold">Natural Language Query:</span> {currentItem.query.corresponding_natural_language_query}</p>
                  )}
                  {currentItem.query.target_collection && (
                    <p><span className="font-semibold">Collection:</span> {currentItem.query.target_collection}</p>
                  )}
                  {currentItem.query.search_query && (
                    <p><span className="font-semibold">Search Query:</span> {currentItem.query.search_query}</p>
                  )}
                  {currentItem.query.integer_property_filter && (
                    <p>
                      <span className="font-semibold">Integer Filter:</span>{' '}
                      {currentItem.query.integer_property_filter.property_name}{' '}
                      {currentItem.query.integer_property_filter.operator}{' '}
                      {currentItem.query.integer_property_filter.value}
                    </p>
                  )}
                  {currentItem.query.text_property_filter && (
                    <p>
                      <span className="font-semibold">Text Filter:</span>{' '}
                      {currentItem.query.text_property_filter.property_name}{' '}
                      {currentItem.query.text_property_filter.operator}{' '}
                      {currentItem.query.text_property_filter.value}
                    </p>
                  )}
                  {currentItem.query.boolean_property_filter && (
                    <p>
                      <span className="font-semibold">Boolean Filter:</span>{' '}
                      {currentItem.query.boolean_property_filter.property_name} = {' '}
                      {currentItem.query.boolean_property_filter.value}
                    </p>
                  )}
                  {currentItem.query.integer_property_aggregation && (
                    <p>
                      <span className="font-semibold">Integer Aggregation:</span>{' '}
                      {currentItem.query.integer_property_aggregation.metrics} of{' '}
                      {currentItem.query.integer_property_aggregation.property_name}
                    </p>
                  )}
                  {currentItem.query.text_property_aggregation && (
                    <p>
                      <span className="font-semibold">Text Aggregation:</span>{' '}
                      {currentItem.query.text_property_aggregation.metrics} of{' '}
                      {currentItem.query.text_property_aggregation.property_name}
                      {currentItem.query.text_property_aggregation.top_occurrences_limit && 
                        ` (Top ${currentItem.query.text_property_aggregation.top_occurrences_limit})`}
                    </p>
                  )}
                  {currentItem.query.boolean_property_aggregation && (
                    <p>
                      <span className="font-semibold">Boolean Aggregation:</span>{' '}
                      {currentItem.query.boolean_property_aggregation.metrics} of{' '}
                      {currentItem.query.boolean_property_aggregation.property_name}
                    </p>
                  )}
                  {currentItem.query.groupby_property && (
                    <p><span className="font-semibold">Group By:</span> {currentItem.query.groupby_property}</p>
                  )}
                </div>
                {renderQueryResult(currentItem.ground_truth_query_result)}
              </>
            )}
          </div>
        </div>
      </div>
    </div>
  );
};

export default QueryVisualizer;