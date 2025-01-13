// components/QuerySearcher.js
import { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { Search, ArrowLeft, Filter, X } from 'lucide-react';

const QuerySearcher = () => {
  const navigate = useNavigate();
  const [queries, setQueries] = useState([]);
  const [searchTerm, setSearchTerm] = useState('');
  const [filters, setFilters] = useState({
    collections: [],
    tags: [],
    hasAggregation: false,
    hasFilter: false
  });
  const [activeFilters, setActiveFilters] = useState([]);

  useEffect(() => {
    fetchQueries();
  }, []);

  const fetchQueries = async () => {
    try {
      const response = await fetch('http://localhost:8000/data');
      const data = await response.json();
      setQueries(data);
    } catch (error) {
      console.error('Error fetching queries:', error);
    }
  };

  const handleSearch = (term) => {
    setSearchTerm(term);
  };

  const applyFilter = (filterType, value) => {
    setActiveFilters(prev => [...prev, { type: filterType, value }]);
  };

  const removeFilter = (index) => {
    setActiveFilters(prev => prev.filter((_, i) => i !== index));
  };

  const filteredQueries = queries.filter(query => {
    let matches = true;
    
    // Apply search term
    if (searchTerm) {
      matches = matches && (
        query.query.search_query.toLowerCase().includes(searchTerm.toLowerCase()) ||
        query.query.target_collection.toLowerCase().includes(searchTerm.toLowerCase()) ||
        query.query.corresponding_natural_language_query.toLowerCase().includes(searchTerm.toLowerCase())
      );
    }

    // Apply active filters
    activeFilters.forEach(filter => {
      switch (filter.type) {
        case 'collection':
          matches = matches && query.query.target_collection === filter.value;
          break;
        case 'hasAggregation':
          matches = matches && !!query.query.integer_property_aggregation;
          break;
        case 'hasFilter':
          matches = matches && !!query.query.integer_property_filter;
          break;
        default:
          break;
      }
    });

    return matches;
  });

  return (
    <div className="p-6 max-w-7xl mx-auto">
      <div className="mb-6 flex items-center justify-between">
        <div className="flex items-center gap-4">
          <h1 className="text-3xl font-bold text-[#1c1468]">Query Search</h1>
        </div>
        <button
          onClick={() => navigate('/')}
          className="px-4 py-2 bg-[#1c1468] text-white rounded-lg hover:bg-[#130e4a] flex items-center gap-2"
        >
          <ArrowLeft size={16} />
          Back to Visualizer
        </button>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-4 gap-6">
        {/* Filters Sidebar */}
        <div className="lg:col-span-1 space-y-6">
          <div className="bg-white p-4 rounded-lg shadow">
            <h2 className="font-semibold mb-4 flex items-center gap-2">
              <Filter size={16} />
              Filters
            </h2>
            
            <div className="space-y-4">
              <div>
                <h3 className="text-sm font-medium mb-2">Query Type</h3>
                <label className="flex items-center gap-2 text-sm">
                  <input
                    type="checkbox"
                    checked={activeFilters.some(f => f.type === 'hasAggregation')}
                    onChange={(e) => {
                      if (e.target.checked) {
                        applyFilter('hasAggregation', true);
                      } else {
                        setActiveFilters(prev => prev.filter(f => f.type !== 'hasAggregation'));
                      }
                    }}
                  />
                  Has Aggregation
                </label>
                <label className="flex items-center gap-2 text-sm mt-2">
                  <input
                    type="checkbox"
                    checked={activeFilters.some(f => f.type === 'hasFilter')}
                    onChange={(e) => {
                      if (e.target.checked) {
                        applyFilter('hasFilter', true);
                      } else {
                        setActiveFilters(prev => prev.filter(f => f.type !== 'hasFilter'));
                      }
                    }}
                  />
                  Has Filter
                </label>
              </div>
              
              <div>
                <h3 className="text-sm font-medium mb-2">Collections</h3>
                <div className="space-y-1">
                  {Array.from(new Set(queries.map(q => q.query.target_collection))).map((collection) => (
                    <label key={collection} className="flex items-center gap-2 text-sm">
                      <input
                        type="checkbox"
                        checked={activeFilters.some(f => f.type === 'collection' && f.value === collection)}
                        onChange={(e) => {
                          if (e.target.checked) {
                            applyFilter('collection', collection);
                          } else {
                            setActiveFilters(prev => prev.filter(f => !(f.type === 'collection' && f.value === collection)));
                          }
                        }}
                      />
                      {collection}
                    </label>
                  ))}
                </div>
              </div>
            </div>
          </div>
        </div>

        {/* Search Results */}
        <div className="lg:col-span-3 space-y-6">
          <div className="relative">
            <input
              type="text"
              value={searchTerm}
              onChange={(e) => handleSearch(e.target.value)}
              placeholder="Search queries..."
              className="w-full p-3 pl-10 border rounded-lg shadow"
            />
            <Search size={20} className="absolute left-3 top-1/2 -translate-y-1/2 text-gray-400" />
          </div>

          <div className="flex flex-wrap gap-2">
            {activeFilters.map((filter, index) => (
              <div
                key={index}
                className="bg-[#1c1468] text-white px-3 py-1 rounded-full text-sm flex items-center gap-2"
              >
                {filter.type === 'collection' ? (
                  <span>Collection: {filter.value}</span>
                ) : (
                  <span>{filter.type}</span>
                )}
                <button onClick={() => removeFilter(index)}>
                  <X size={14} />
                </button>
              </div>
            ))}
          </div>

          <div className="space-y-4">
            {filteredQueries.map((item, index) => (
              <div
                key={index}
                className="bg-white p-4 rounded-lg shadow hover:shadow-md transition-shadow cursor-pointer"
                onClick={() => navigate(`/?query=${index}`)}
              >
                <p className="text-sm text-gray-500 mb-2">Collection: {item.query.target_collection}</p>
                <p className="font-medium mb-2">{item.query.corresponding_natural_language_query}</p>
                <p className="text-sm text-gray-600">{item.query.search_query}</p>
                <div className="mt-2 flex items-center gap-2">
                  {item.query.integer_property_aggregation && (
                    <span className="bg-blue-100 text-blue-800 text-xs px-2 py-1 rounded">
                      Aggregation
                    </span>
                  )}
                  {item.query.integer_property_filter && (
                    <span className="bg-green-100 text-green-800 text-xs px-2 py-1 rounded">
                      Filter
                    </span>
                  )}
                </div>
              </div>
            ))}
          </div>
        </div>
      </div>
    </div>
  );
};

export default QuerySearcher;