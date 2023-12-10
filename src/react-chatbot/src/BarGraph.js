// BarGraph.js
import React from 'react';
import Plot from 'react-plotly.js';

const BarGraph = ({ data, layout }) => {
  const chartData = [
    {
      x: data ? data[0].x : [],
      y: data ? data[0].y : [],
      type: 'bar',
      marker: {
        color: 'rgba(75,192,192,0.6)',
        line: {
          color: 'rgba(75,192,192,1)',
          width: 1.5,
        },
      },
    },
  ];
  return (
      <Plot data={chartData} layout={layout} />
  );
};

export default BarGraph;
