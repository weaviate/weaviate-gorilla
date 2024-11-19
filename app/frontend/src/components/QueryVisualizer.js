import { useState } from 'react';
import { ChevronLeft, ChevronRight, Database, Search, Check, X } from 'lucide-react';

// Schema data structure
const schema = {
  weaviate_collections: [
    {
      name: "RestaurantMenu",
      properties: [
        {
          name: "DishName",
          data_type: ["string"],
          description: "The name of the dish offered in the restaurant menu."
        },
        {
          name: "Price",
          data_type: ["number"],
          description: "The price of the dish."
        },
        {
          name: "IsVegetarian",
          data_type: ["boolean"],
          description: "Indicates if the dish is vegetarian."
        }
      ],
      envisioned_use_case_overview: "The RestaurantMenu collection stores details about each dish offered in a restaurant, including their names, prices, and vegetarian status."
    },
    {
      name: "CustomerOrders",
      properties: [
        {
          name: "CustomerName",
          data_type: ["string"],
          description: "The name of the customer who places the order."
        },
        {
          name: "TotalAmount",
          data_type: ["number"],
          description: "The total amount for the customer's order."
        },
        {
          name: "IsTakeaway",
          data_type: ["boolean"],
          description: "Indicates whether the order is for takeaway or dine-in."
        }
      ],
      envisioned_use_case_overview: "The CustomerOrders collection captures details of customer orders, including their names, total amounts, and whether the orders are takeaway."
    },
    {
      name: "StaffMembers",
      properties: [
        {
          name: "StaffName",
          data_type: ["string"],
          description: "The name of the staff member."
        },
        {
          name: "ExperienceYears",
          data_type: ["number"],
          description: "The number of years of experience the staff member has."
        },
        {
          name: "IsOnDuty",
          data_type: ["boolean"],
          description: "Indicates if the staff member is currently on duty."
        }
      ],
      envisioned_use_case_overview: "The StaffMembers collection maintains information about the restaurant's staff, including their names, experience, and current duty status."
    }
  ]
};

const data = [
  {
    query_index: 0,
    database_schema_index: 0,
    natural_language_query: "Find average and maximum prices of vegetarian dishes that mention \"spicy\" in their name or description and group the results by dish category.",
    ground_truth_query: {
      target_collection: "RestaurantMenu",
      search_query: "vegetarian spicy",
      integer_property_filter: {
        property_name: "isVegetarian",
        operator: "=",
        value: 1
      },
      integer_property_aggregation: {
        property_name: "price",
        metrics: "MIN"
      },
      groupby_property: "category"
    },
    predicted_query: {
      target_collection: "RestaurantMenu"
    },
    ast_score: 0.6
  },
  {
    query_index: 1,
    database_schema_index: 0,
    natural_language_query: "Find vegan dishes under $20, understanding 'vegan' in context, and calculate the average price of these dishes.",
    ground_truth_query: {
      target_collection: "RestaurantMenu",
      search_query: "vegan dishes",
      integer_property_filter: {
        property_name: "price",
        operator: "<",
        value: 20
      },
      integer_property_aggregation: {
        property_name: "price",
        metrics: "MEAN"
      }
    },
    predicted_query: {
      target_collection: "RestaurantMenu"
    },
    ast_score: 0.8
  }
];

const SchemaVisualizer = ({ collection }) => (
  <div className="bg-gray-50 p-4 rounded-lg border border-gray-200">
    <div className="flex items-center gap-2 mb-4">
      <Database className="text-blue-500" size={20} />
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
          <div className="text-sm px-2 py-1 rounded bg-blue-100 text-blue-700">
            {prop.data_type[0]}
          </div>
        </div>
      ))}
    </div>
  </div>
);

export default function QueryVisualizer() {
  const [currentIndex, setCurrentIndex] = useState(0);
  const currentItem = data[currentIndex];
  const [showSchema, setShowSchema] = useState(true);

  const handlePrevious = () => {
    setCurrentIndex((prev) => (prev > 0 ? prev - 1 : data.length - 1));
  };

  const handleNext = () => {
    setCurrentIndex((prev) => (prev < data.length - 1 ? prev + 1 : 0));
  };

  return (
    <div className="max-w-6xl mx-auto p-6">
      <div className="flex items-center justify-between mb-6">
        <button
          onClick={handlePrevious}
          className="p-2 rounded bg-blue-500 text-white hover:bg-blue-600"
        >
          <ChevronLeft size={24} />
        </button>
        <div className="flex items-center gap-4">
          <span className="text-lg font-semibold">
            Query {currentIndex + 1} of {data.length}
          </span>
          <button
            onClick={() => setShowSchema(!showSchema)}
            className="flex items-center gap-2 px-4 py-2 rounded bg-gray-100 hover:bg-gray-200"
          >
            <Database size={16} />
            {showSchema ? "Hide Schema" : "Show Schema"}
          </button>
        </div>
        <button
          onClick={handleNext}
          className="p-2 rounded bg-blue-500 text-white hover:bg-blue-600"
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
              <p><span className="font-semibold">Collection:</span> {currentItem.ground_truth_query.target_collection}</p>
              <p><span className="font-semibold">Search Query:</span> {currentItem.ground_truth_query.search_query}</p>
              {currentItem.ground_truth_query.integer_property_filter && (
                <p>
                  <span className="font-semibold">Filter:</span>{' '}
                  {currentItem.ground_truth_query.integer_property_filter.property_name}{' '}
                  {currentItem.ground_truth_query.integer_property_filter.operator}{' '}
                  {currentItem.ground_truth_query.integer_property_filter.value}
                </p>
              )}
              {currentItem.ground_truth_query.integer_property_aggregation && (
                <p>
                  <span className="font-semibold">Aggregation:</span>{' '}
                  {currentItem.ground_truth_query.integer_property_aggregation.metrics} of{' '}
                  {currentItem.ground_truth_query.integer_property_aggregation.property_name}
                </p>
              )}
              {currentItem.ground_truth_query.groupby_property && (
                <p><span className="font-semibold">Group By:</span> {currentItem.ground_truth_query.groupby_property}</p>
              )}
            </div>
          </div>

          <div className="bg-white p-6 rounded-lg shadow-md">
            <h2 className="text-xl font-bold mb-3">Predicted Query</h2>
            <div className="space-y-2">
              <p><span className="font-semibold">Collection:</span> {currentItem.predicted_query.target_collection}</p>
            </div>
          </div>

          <div className="bg-white p-6 rounded-lg shadow-md">
            <h2 className="text-xl font-bold mb-3">AST Score</h2>
            <div className="relative pt-1">
              <div className="overflow-hidden h-6 text-xs flex rounded bg-blue-100">
                <div
                  style={{ width: `${currentItem.ast_score * 100}%` }}
                  className="shadow-none flex flex-col text-center whitespace-nowrap text-white justify-center bg-blue-500"
                >
                  {(currentItem.ast_score * 100).toFixed(1)}%
                </div>
              </div>
            </div>
          </div>
        </div>

        {showSchema && (
          <div className="space-y-6">
            <h2 className="text-xl font-bold">Database Schema</h2>
            {schema.weaviate_collections.map((collection, idx) => (
              <SchemaVisualizer key={idx} collection={collection} />
            ))}
          </div>
        )}
      </div>
    </div>
  );
}