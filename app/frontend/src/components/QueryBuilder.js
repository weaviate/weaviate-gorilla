import { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { ArrowLeft, Plus, Save, X } from 'lucide-react';

const COLLECTIONS = [
  'Appointments', 'ArtPieces', 'Clinics', 'Courses', 'Doctors',
  'Exhibitions', 'Instructors', 'Menus', 'Museums', 'Reservations',
  'Restaurants', 'Students', 'TravelAgents', 'TravelDestinations', 'TravelPackages'
];

const QueryBuilder = () => {
  const navigate = useNavigate();
  const [query, setQuery] = useState({
    corresponding_natural_language_query: '',
    target_collection: '',
    search_query: false,
    integer_property_filter: null,
    text_property_filter: null,
    boolean_property_filter: null,
    integer_property_aggregation: null,
    text_property_aggregation: null,
    boolean_property_aggregation: null,
    groupby_property: ''
  });

  const [showIntegerFilter, setShowIntegerFilter] = useState(false);
  const [showTextFilter, setShowTextFilter] = useState(false);
  const [showBooleanFilter, setShowBooleanFilter] = useState(false);
  const [showIntegerAggregation, setShowIntegerAggregation] = useState(false);
  const [showTextAggregation, setShowTextAggregation] = useState(false);
  const [showBooleanAggregation, setShowBooleanAggregation] = useState(false);
  const [generatedQuery, setGeneratedQuery] = useState('');
  const [isGenerating, setIsGenerating] = useState(false);
  const [collectionProperties, setCollectionProperties] = useState([]);

  useEffect(() => {
    const fetchProperties = async () => {
      if (query.target_collection) {
        try {
          const response = await fetch(`http://localhost:8000/collection-properties?collection_name=${query.target_collection}`);
          if (response.ok) {
            const data = await response.json();
            setCollectionProperties(data.properties);
          }
        } catch (error) {
          console.error('Error fetching collection properties:', error);
        }
      }
    };

    fetchProperties();
  }, [query.target_collection]);

  const generateNaturalLanguageQuery = async (queryConfig) => {
    setIsGenerating(true);
    try {
      // Clean up the query config before sending
      const cleanedConfig = {
        target_collection: queryConfig.target_collection,
        search_query: queryConfig.search_query || false,
        integer_property_filter: queryConfig.integer_property_filter?.property_name ? queryConfig.integer_property_filter : null,
        text_property_filter: queryConfig.text_property_filter?.property_name ? queryConfig.text_property_filter : null,
        boolean_property_filter: queryConfig.boolean_property_filter?.property_name ? queryConfig.boolean_property_filter : null,
        integer_property_aggregation: queryConfig.integer_property_aggregation?.property_name ? queryConfig.integer_property_aggregation : null,
        text_property_aggregation: queryConfig.text_property_aggregation?.property_name ? queryConfig.text_property_aggregation : null,
        boolean_property_aggregation: queryConfig.boolean_property_aggregation?.property_name ? queryConfig.boolean_property_aggregation : null,
        groupby_property: queryConfig.groupby_property || null
      };

      console.log('Sending query config:', JSON.stringify(cleanedConfig, null, 2)); // Pretty print the data

      const response = await fetch('http://localhost:8000/generate-nl-query', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify(cleanedConfig),
      });
  
      if (!response.ok) {
        const errorText = await response.text(); // Get raw error response
        console.error('Response status:', response.status);
        console.error('Response text:', errorText);
        
        try {
          const errorData = JSON.parse(errorText);
          console.error('Parsed error data:', errorData);
        } catch (e) {
          console.error('Could not parse error response as JSON');
        }
        
        throw new Error(`Failed to generate natural language query: ${errorText}`);
      }

      const data = await response.json();
      setGeneratedQuery(data.natural_language_query);
      return data.natural_language_query;
    } catch (error) {
      console.error('Error generating natural language query:', error);
      setGeneratedQuery(''); // Clear any previous query on error
      return '';
    } finally {
      setIsGenerating(false);
    }
  };

  const handleSubmit = async (e) => {
    e.preventDefault();

    // Generate natural language query first
    const nlQuery = await generateNaturalLanguageQuery(query);
    const finalQuery = {
      ...query,
      corresponding_natural_language_query: nlQuery
    };

    try {
      const response = await fetch('http://localhost:8000/add-query', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({ query: finalQuery }),
      });

      if (response.ok) {
        navigate('/visualizer');
      } else {
        console.error('Failed to add query');
      }
    } catch (error) {
      console.error('Error adding query:', error);
    }
  };

  return (
    <div className="w-full min-h-screen p-6 bg-cover bg-center" style={{ backgroundImage: 'url("/background.png")' }}>
      <div className="max-w-4xl mx-auto bg-white rounded-lg shadow-md p-6">
        <div className="flex justify-between items-center mb-6">
          <h1 className="text-2xl font-bold text-[#1c1468]">Query Builder</h1>
          <button
            onClick={() => navigate('/visualizer')}
            className="px-4 py-2 bg-[#1c1468] text-white rounded hover:bg-[#130e4a] flex items-center gap-2"
          >
            <ArrowLeft size={16} />
            Back to Visualizer
          </button>
        </div>

        <form onSubmit={handleSubmit} className="space-y-6">
          <div>
            <label className="block text-sm font-medium mb-2">Target Collection</label>
            <select
              value={query.target_collection}
              onChange={(e) => setQuery({...query, target_collection: e.target.value})}
              className="w-full p-2 border rounded"
              required
            >
              <option value="">Select a collection</option>
              {COLLECTIONS.map(collection => (
                <option key={collection} value={collection}>{collection}</option>
              ))}
            </select>

            {collectionProperties.length > 0 && (
              <div className="mt-4 p-4 bg-gray-50 rounded-lg">
                <h3 className="font-medium mb-2">Collection Properties:</h3>
                <ul className="list-disc pl-5 space-y-1">
                  {collectionProperties.map((prop, index) => (
                    <li key={index}>
                      <span className="font-medium">{prop.name}</span>
                      <span className="text-gray-600"> ({prop.data_type})</span>
                    </li>
                  ))}
                </ul>
              </div>
            )}
          </div>

          <div className="flex items-center gap-2">
            <button
              type="button"
              onClick={() => setQuery({...query, search_query: !query.search_query})}
              className={`px-3 py-1 ${query.search_query ? 'bg-indigo-600 text-white' : 'bg-indigo-100 text-indigo-800'} rounded text-sm`}
            >
              Enable Search Query
            </button>
          </div>

          {/* Filters */}
          <div className="space-y-4">
            <div className="flex items-center justify-between">
              <h2 className="text-lg font-medium">Filters</h2>
              <div className="space-x-2">
                <button
                  type="button"
                  onClick={() => setShowIntegerFilter(!showIntegerFilter)}
                  className="px-3 py-1 bg-blue-100 text-blue-800 rounded text-sm"
                >
                  {showIntegerFilter ? <X size={14} /> : <Plus size={14} />} Integer Filter
                </button>
                <button
                  type="button"
                  onClick={() => setShowTextFilter(!showTextFilter)}
                  className="px-3 py-1 bg-green-100 text-green-800 rounded text-sm"
                >
                  {showTextFilter ? <X size={14} /> : <Plus size={14} />} Text Filter
                </button>
                <button
                  type="button"
                  onClick={() => setShowBooleanFilter(!showBooleanFilter)}
                  className="px-3 py-1 bg-yellow-100 text-yellow-800 rounded text-sm"
                >
                  {showBooleanFilter ? <X size={14} /> : <Plus size={14} />} Boolean Filter
                </button>
              </div>
            </div>

            {showIntegerFilter && (
              <div className="p-4 bg-blue-50 rounded">
                <h3 className="font-medium mb-2">Integer Filter</h3>
                <div className="grid grid-cols-3 gap-2">
                  <input
                    type="text"
                    placeholder="Property name"
                    value={query.integer_property_filter?.property_name || ''}
                    onChange={(e) => setQuery({
                      ...query,
                      integer_property_filter: {
                        ...query.integer_property_filter,
                        property_name: e.target.value
                      }
                    })}
                    className="p-2 border rounded"
                  />
                  <select
                    value={query.integer_property_filter?.operator || ''}
                    onChange={(e) => setQuery({
                      ...query,
                      integer_property_filter: {
                        ...query.integer_property_filter,
                        operator: e.target.value
                      }
                    })}
                    className="p-2 border rounded"
                  >
                    <option value="">Select operator</option>
                    <option value=">">&gt;</option>
                    <option value=">=">&gt;=</option>
                    <option value="<">&lt;</option>
                    <option value="<=">&lt;=</option>
                    <option value="=">=</option>
                  </select>
                  <input
                    type="number"
                    placeholder="Value"
                    value={query.integer_property_filter?.value || ''}
                    onChange={(e) => setQuery({
                      ...query,
                      integer_property_filter: {
                        ...query.integer_property_filter,
                        value: parseInt(e.target.value)
                      }
                    })}
                    className="p-2 border rounded"
                  />
                </div>
              </div>
            )}

            {showTextFilter && (
              <div className="p-4 bg-green-50 rounded">
                <h3 className="font-medium mb-2">Text Filter</h3>
                <div className="grid grid-cols-3 gap-2">
                  <input
                    type="text"
                    placeholder="Property name"
                    value={query.text_property_filter?.property_name || ''}
                    onChange={(e) => setQuery({
                      ...query,
                      text_property_filter: {
                        ...query.text_property_filter,
                        property_name: e.target.value
                      }
                    })}
                    className="p-2 border rounded"
                  />
                  <select
                    value={query.text_property_filter?.operator || ''}
                    onChange={(e) => setQuery({
                      ...query,
                      text_property_filter: {
                        ...query.text_property_filter,
                        operator: e.target.value
                      }
                    })}
                    className="p-2 border rounded"
                  >
                    <option value="">Select operator</option>
                    <option value="contains">Contains</option>
                    <option value="equals">Equals</option>
                  </select>
                  <input
                    type="text"
                    placeholder="Value"
                    value={query.text_property_filter?.value || ''}
                    onChange={(e) => setQuery({
                      ...query,
                      text_property_filter: {
                        ...query.text_property_filter,
                        value: e.target.value
                      }
                    })}
                    className="p-2 border rounded"
                  />
                </div>
              </div>
            )}

            {showBooleanFilter && (
              <div className="p-4 bg-yellow-50 rounded">
                <h3 className="font-medium mb-2">Boolean Filter</h3>
                <div className="grid grid-cols-2 gap-2">
                  <input
                    type="text"
                    placeholder="Property name"
                    value={query.boolean_property_filter?.property_name || ''}
                    onChange={(e) => setQuery({
                      ...query,
                      boolean_property_filter: {
                        ...query.boolean_property_filter,
                        property_name: e.target.value
                      }
                    })}
                    className="p-2 border rounded"
                  />
                  <select
                    value={query.boolean_property_filter?.value?.toString() || ''}
                    onChange={(e) => setQuery({
                      ...query,
                      boolean_property_filter: {
                        ...query.boolean_property_filter,
                        value: e.target.value === 'true'
                      }
                    })}
                    className="p-2 border rounded"
                  >
                    <option value="">Select value</option>
                    <option value="true">True</option>
                    <option value="false">False</option>
                  </select>
                </div>
              </div>
            )}
          </div>

          {/* Aggregations */}
          <div className="space-y-4">
            <div className="flex items-center justify-between">
              <h2 className="text-lg font-medium">Aggregations</h2>
              <div className="space-x-2">
                <button
                  type="button"
                  onClick={() => setShowIntegerAggregation(!showIntegerAggregation)}
                  className="px-3 py-1 bg-purple-100 text-purple-800 rounded text-sm"
                >
                  {showIntegerAggregation ? <X size={14} /> : <Plus size={14} />} Integer Aggregation
                </button>
                <button
                  type="button"
                  onClick={() => setShowTextAggregation(!showTextAggregation)}
                  className="px-3 py-1 bg-pink-100 text-pink-800 rounded text-sm"
                >
                  {showTextAggregation ? <X size={14} /> : <Plus size={14} />} Text Aggregation
                </button>
                <button
                  type="button"
                  onClick={() => setShowBooleanAggregation(!showBooleanAggregation)}
                  className="px-3 py-1 bg-orange-100 text-orange-800 rounded text-sm"
                >
                  {showBooleanAggregation ? <X size={14} /> : <Plus size={14} />} Boolean Aggregation
                </button>
              </div>
            </div>

            {showIntegerAggregation && (
              <div className="p-4 bg-purple-50 rounded">
                <h3 className="font-medium mb-2">Integer Aggregation</h3>
                <div className="grid grid-cols-2 gap-2">
                  <input
                    type="text"
                    placeholder="Property name"
                    value={query.integer_property_aggregation?.property_name || ''}
                    onChange={(e) => setQuery({
                      ...query,
                      integer_property_aggregation: {
                        ...query.integer_property_aggregation,
                        property_name: e.target.value
                      }
                    })}
                    className="p-2 border rounded"
                  />
                  <select
                    value={query.integer_property_aggregation?.metrics || ''}
                    onChange={(e) => setQuery({
                      ...query,
                      integer_property_aggregation: {
                        ...query.integer_property_aggregation,
                        metrics: e.target.value
                      }
                    })}
                    className="p-2 border rounded"
                  >
                    <option value="">Select metrics</option>
                    <option value="mean">Mean</option>
                    <option value="sum">Sum</option>
                    <option value="min">Min</option>
                    <option value="max">Max</option>
                  </select>
                </div>
              </div>
            )}

            {showTextAggregation && (
              <div className="p-4 bg-pink-50 rounded">
                <h3 className="font-medium mb-2">Text Aggregation</h3>
                <div className="grid grid-cols-2 gap-2">
                  <input
                    type="text"
                    placeholder="Property name"
                    value={query.text_property_aggregation?.property_name || ''}
                    onChange={(e) => setQuery({
                      ...query,
                      text_property_aggregation: {
                        ...query.text_property_aggregation,
                        property_name: e.target.value
                      }
                    })}
                    className="p-2 border rounded"
                  />
                  <select
                    value={query.text_property_aggregation?.metrics || ''}
                    onChange={(e) => setQuery({
                      ...query,
                      text_property_aggregation: {
                        ...query.text_property_aggregation,
                        metrics: e.target.value
                      }
                    })}
                    className="p-2 border rounded"
                  >
                    <option value="">Select metrics</option>
                    <option value="unique">Unique Values</option>
                    <option value="most_common">Most Common</option>
                  </select>
                </div>
              </div>
            )}

            {showBooleanAggregation && (
              <div className="p-4 bg-orange-50 rounded">
                <h3 className="font-medium mb-2">Boolean Aggregation</h3>
                <div className="grid grid-cols-2 gap-2">
                  <input
                    type="text"
                    placeholder="Property name"
                    value={query.boolean_property_aggregation?.property_name || ''}
                    onChange={(e) => setQuery({
                      ...query,
                      boolean_property_aggregation: {
                        ...query.boolean_property_aggregation,
                        property_name: e.target.value
                      }
                    })}
                    className="p-2 border rounded"
                  />
                  <select
                    value={query.boolean_property_aggregation?.metrics || ''}
                    onChange={(e) => setQuery({
                      ...query,
                      boolean_property_aggregation: {
                        ...query.boolean_property_aggregation,
                        metrics: e.target.value
                      }
                    })}
                    className="p-2 border rounded"
                  >
                    <option value="">Select metrics</option>
                    <option value="count_true">Count True</option>
                    <option value="count_false">Count False</option>
                  </select>
                </div>
              </div>
            )}
          </div>

          <div>
            <label className="block text-sm font-medium mb-2">Group By Property (Optional)</label>
            <input
              type="text"
              value={query.groupby_property}
              onChange={(e) => setQuery({...query, groupby_property: e.target.value})}
              className="w-full p-2 border rounded"
            />
          </div>

          {generatedQuery && (
            <div className="p-4 bg-gray-50 rounded-lg mb-4">
              <h3 className="font-medium mb-2">Generated Natural Language Query:</h3>
              <p className="text-gray-700">{generatedQuery}</p>
            </div>
          )}

          {/* Then your button group */}
          <div className="flex justify-end space-x-2">
            <button
              type="button"
              onClick={() => generateNaturalLanguageQuery(query)}
              className="px-4 py-2 bg-green-600 text-white rounded hover:bg-green-700 flex items-center gap-2"
              disabled={isGenerating}
            >
              {isGenerating ? 'Generating...' : 'Generate Query'}
            </button>
          </div>
        </form>
      </div>
    </div>
  );
};

export default QueryBuilder;
