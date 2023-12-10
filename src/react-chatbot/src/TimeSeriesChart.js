import React from 'react';
import Plot from 'react-plotly.js';

const TimeSeriesChart = ({ data, layout }) => {
  const chartData = {
    x: data ? data[0].x.map((timestamp) => new Date(timestamp)) : [],
    y: data ? data[0].y: [],
    type: 'scatter',
    mode: 'lines+markers',
    marker: { color: 'blue' },
  };

  return <Plot data={[chartData]} layout={layout} />;
};

export default TimeSeriesChart;
