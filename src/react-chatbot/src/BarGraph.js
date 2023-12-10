// BarGraph.js
import React from 'react';
import Plot from 'react-plotly.js';

import { BOOKS_MAP } from './constants';

const BarGraph = ({ data, layout , subBooks}) => {
  // console.log(data)
  const chartData = [
    {
      x: data ? data.x.map((i) => subBooks ? BOOKS_MAP[i] : i) : [],
      y: data ? data.y : [],
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
