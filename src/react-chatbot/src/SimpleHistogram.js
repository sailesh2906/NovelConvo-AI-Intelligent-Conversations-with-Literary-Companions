import React from 'react';
import Plot from 'react-plotly.js';

const SimpleHistogram = () => {
  // Sample data for the histogram
  const data = [
    {
      x: [1, 2, 2, 3, 3, 3, 4, 4, 4, 4, 5, 5, 5, 5, 5],
      type: 'histogram',
      marker: { color: 'rgba(255, 100, 102, 0.7)' },
    },
  ];

  const layout = {
    title: 'Simple Histogram',
    xaxis: { title: 'Values' },
    yaxis: { title: 'Frequency' },
  };

  return (
    <div>
      <h2>Simple Histogram</h2>
      <Plot data={data} layout={layout} />
    </div>
  );
};

export default SimpleHistogram;