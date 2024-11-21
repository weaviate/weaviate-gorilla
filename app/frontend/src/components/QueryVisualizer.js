import { useState, useEffect } from 'react';
import { ChevronLeft, ChevronRight, Database, Search, Check, X } from 'lucide-react';

const SchemaVisualizer = ({ collection }) => (
  <div className="bg-gray-50 p-4 rounded-lg border border-gray-200">
    <div className="flex items-center gap-2 mb-4">
      <Database className="text-[#1c1468]" size={20} />
      <h3 className="text-lg font-semibold">{collection.name}</h3>
    </div>
    <p className="text-sm text-gray-600 mb-4">{collection.envisioned_use_case_overview}</p>
    <div className="space-y-3">
      {collection.properties.map((prop, idx) => (
        <div key={idx} className="flex items-start gap-4 p-2 bg-white rounded border border-gray-100">
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
);

export default function QueryVisualizer() {
  const [currentIndex, setCurrentIndex] = useState(0);
  const [data, setData] = useState([]);
  const [showSchema, setShowSchema] = useState(true);

  useEffect(() => {
    const fetchData = async () => {
      try {
        const response = await fetch('http://localhost:8000/data');
        const jsonData = await response.json();
        setData(jsonData);
      } catch (error) {
        console.error('Error fetching data:', error);
      }
    };

    fetchData();
  }, []);

  if (!data.length) {
    return <div>Loading...</div>;
  }

  const currentItem = data[currentIndex];

  // Add logging to help debug
  console.log('Current item:', currentItem);
  console.log('Current index:', currentIndex);
  console.log('Data length:', data.length);

  // Add null checks
  if (!currentItem) {
    console.error('Current item is null');
    return <div>Error: Invalid data</div>;
  }

  if (!currentItem.ground_truth_query) {
    console.error('Missing ground truth query data:', currentItem);
    return <div>Error: Invalid query data</div>;
  }

  const handlePrevious = () => {
    setCurrentIndex((prev) => (prev > 0 ? prev - 1 : data.length - 1));
  };

  const handleNext = () => {
    setCurrentIndex((prev) => (prev < data.length - 1 ? prev + 1 : 0));
  };

  const handleNextSchema = () => {
    setCurrentIndex((prev) => {
      const nextIndex = prev + 64;
      return nextIndex < data.length ? nextIndex : prev;
    });
  };

  const handlePrevSchema = () => {
    setCurrentIndex((prev) => {
      const prevIndex = prev - 64;
      return prevIndex >= 0 ? prevIndex : prev;
    });
  };

  return (
    <div className="max-w-6xl mx-auto p-6">
      <div className="flex items-center justify-between mb-6">
        <button
          onClick={handlePrevious}
          className="p-2 rounded bg-[#1c1468] text-white hover:bg-[#130e4a]"
        >
          <ChevronLeft size={24} />
        </button>
        <div className="flex items-center gap-4">
          <span className="text-lg font-semibold">
            Query {currentIndex + 1} of {data.length}
          </span>
          <div className="flex gap-2">
            <button
              onClick={handlePrevSchema}
              className="flex items-center gap-2 px-4 py-2 rounded bg-gray-100 hover:bg-gray-200"
            >
              <Database size={16} />
              Prev Schema
            </button>
            <button
              onClick={handleNextSchema}
              className="flex items-center gap-2 px-4 py-2 rounded bg-gray-100 hover:bg-gray-200"
            >
              <Database size={16} />
              Next Schema
            </button>
          </div>
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
          <div className="bg-white p-6 rounded-lg shadow-md">
            <h2 className="text-xl font-bold mb-3">Natural Language Query</h2>
            <p className="text-gray-700">{currentItem.natural_language_query}</p>
          </div>

          <div className="bg-white p-6 rounded-lg shadow-md">
            <h2 className="text-xl font-bold mb-3">Ground Truth Query</h2>
            <div className="space-y-2">
              <p><span className="font-semibold">Collection:</span> {currentItem.ground_truth_query?.target_collection || 'N/A'}</p>
              <p><span className="font-semibold">Search Query:</span> {currentItem.ground_truth_query?.search_query || 'N/A'}</p>
              {currentItem.ground_truth_query?.integer_property_filter && (
                <p>
                  <span className="font-semibold">Filter:</span>{' '}
                  {currentItem.ground_truth_query.integer_property_filter.property_name}{' '}
                  {currentItem.ground_truth_query.integer_property_filter.operator}{' '}
                  {currentItem.ground_truth_query.integer_property_filter.value}
                </p>
              )}
              {currentItem.ground_truth_query?.integer_property_aggregation && (
                <p>
                  <span className="font-semibold">Aggregation:</span>{' '}
                  {currentItem.ground_truth_query.integer_property_aggregation.metrics} of{' '}
                  {currentItem.ground_truth_query.integer_property_aggregation.property_name}
                </p>
              )}
              {currentItem.ground_truth_query?.groupby_property && (
                <p><span className="font-semibold">Group By:</span> {currentItem.ground_truth_query.groupby_property}</p>
              )}
            </div>
          </div>

          <div className="bg-white p-6 rounded-lg shadow-md">
            <h2 className="text-xl font-bold mb-3">Predicted Query</h2>
            {currentItem.predicted_query ? (
              <div className="space-y-2">
                <p><span className="font-semibold">Collection:</span> {currentItem.predicted_query.target_collection || 'N/A'}</p>
                <p><span className="font-semibold">Search Query:</span> {currentItem.predicted_query.search_query || 'N/A'}</p>
                {currentItem.predicted_query.integer_property_filter && (
                  <p>
                    <span className="font-semibold">Filter:</span>{' '}
                    {currentItem.predicted_query.integer_property_filter.property_name}{' '}
                    {currentItem.predicted_query.integer_property_filter.operator}{' '}
                    {currentItem.predicted_query.integer_property_filter.value}
                  </p>
                )}
                {currentItem.predicted_query.integer_property_aggregation && (
                  <p>
                    <span className="font-semibold">Aggregation:</span>{' '}
                    {currentItem.predicted_query.integer_property_aggregation.metrics} of{' '}
                    {currentItem.predicted_query.integer_property_aggregation.property_name}
                  </p>
                )}
                {currentItem.predicted_query.groupby_property && (
                  <p><span className="font-semibold">Group By:</span> {currentItem.predicted_query.groupby_property}</p>
                )}
              </div>
            ) : (
              <div className="text-red-500">No tool called.</div>
            )}
          </div>

          <div className="bg-white p-6 rounded-lg shadow-md">
            <h2 className="text-xl font-bold mb-3">AST Score</h2>
            <div className="relative pt-1">
              <div className="overflow-hidden h-6 text-xs flex rounded bg-[#e8fae3]">
                <div
                  style={{ width: `${(currentItem.ast_score || 0) * 100}%` }}
                  className="shadow-none flex flex-col text-center whitespace-nowrap text-white justify-center bg-[#1c1468]"
                >
                  {((currentItem.ast_score || 0) * 100).toFixed(1)}%
                </div>
              </div>
            </div>
          </div>
        </div>

        <div className="space-y-6">
          <h2 className="text-xl font-bold">Database Schema</h2>
          {currentItem.ground_truth_query.database_schema.weaviate_collections.map((collection, idx) => (
            <SchemaVisualizer key={idx} collection={collection} />
          ))}
        </div>
      </div>
    </div>
  );
}