import React from 'react';
import { RadarChart, PolarGrid, PolarAngleAxis, PolarRadiusAxis, Radar, Legend } from 'recharts';

const ComponentAnalysis = () => {
  const data = [
    { component: 'Search\nQueries', 'GPT-4o': 76.77, 'GPT-4o-mini': 72.48 },
    { component: 'Integer\nFilters', 'GPT-4o': 79.28, 'GPT-4o-mini': 76.31 },
    { component: 'Text\nFilters', 'GPT-4o': 84.53, 'GPT-4o-mini': 85.16 },
    { component: 'Boolean\nFilters', 'GPT-4o': 91.44, 'GPT-4o-mini': 88.13 },
    { component: 'Integer\nAggregations', 'GPT-4o': 82.38, 'GPT-4o-mini': 82.69 },
    { component: 'Text\nAggregations', 'GPT-4o': 83.16, 'GPT-4o-mini': 78.78 },
    { component: 'Boolean\nAggregations', 'GPT-4o': 87.03, 'GPT-4o-mini': 84.59 },
    { component: 'GroupBy\nOperations', 'GPT-4o': 83.53, 'GPT-4o-mini': 80.03 }
  ];

  return (
    <div className="w-full max-w-5xl mx-auto bg-white rounded-xl shadow-lg p-8">
      <h2 className="text-2xl font-semibold text-center text-gray-800 mb-8">
        Component Performance Analysis
      </h2>
      <div className="flex justify-center items-center">
        <RadarChart 
          width={900} 
          height={700} 
          data={data} 
          className="bg-white"
          margin={{ top: 40, right: 80, bottom: 40, left: 80 }}
        >
          <PolarGrid 
            stroke="#e5e7eb" 
            strokeDasharray="3 3"
          />
          <PolarAngleAxis 
            dataKey="component" 
            tick={{ 
              fill: '#374151',
              fontSize: 13,
              fontWeight: 500,
              lineHeight: 1.4,
            }}
            tickLine={false}
            radius={220}  // Significantly increased radius for labels
            cx={450}     // Centered X coordinate
            cy={350}     // Centered Y coordinate
          />
          <PolarRadiusAxis 
            angle={90} 
            domain={[50, 90]}
            tick={{ 
              fill: '#374151',
              fontSize: 12 
            }}
            tickCount={9}
            stroke="#e5e7eb"
            cx={450}     // Centered X coordinate
            cy={350}     // Centered Y coordinate
          />
          <Radar
            name="GPT-4o"
            dataKey="GPT-4o"
            stroke="#38d611"
            fill="#38d611"
            fillOpacity={0.15}
            strokeWidth={2}
          />
          <Radar
            name="GPT-4o-mini"
            dataKey="GPT-4o-mini"
            stroke="#1c1468"
            fill="#1c1468"
            fillOpacity={0.15}
            strokeWidth={2}
          />
          <Legend 
            wrapperStyle={{ 
              paddingTop: '24px',
              fontWeight: 500
            }}
            iconSize={12}
            formatter={(value) => (
              <span className="text-sm font-medium text-gray-700">{value}</span>
            )}
          />
        </RadarChart>
      </div>
    </div>
  );
};

export default ComponentAnalysis;