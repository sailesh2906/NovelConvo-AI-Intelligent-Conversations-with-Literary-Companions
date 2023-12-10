import React, {useEffect, useState } from 'react';
import axios from 'axios';


import './App.css';

import TimeSeriesChart from './TimeSeriesChart';
import BarGraph from './BarGraph';
import { CLOUD_URL, INIT_BOOKS, ANALYTICS_ENDPOINT } from './constants';



function Analytics() {
    const analytics_url = CLOUD_URL + ANALYTICS_ENDPOINT;
    const [analytics, setAnalytics] = useState(false);
  
    useEffect(()  => {
      fetchAnalytics();
    }, [])
  
    const fetchAnalytics = async () => {
      try {
        const response = await axios.get(analytics_url);
        setAnalytics(response.data);
      } catch (error) {
        console.error('Error sending message:', error);
      }
    };
    const graphWidth = "500"
    const graphHeight = "360"
    return(
      <div className='analytics-container'>
        <div className='analytics-item'>
          <TimeSeriesChart
            data={analytics && analytics.conversations_over_time.data}
            layout = {{
              title: 'Conversations Over Time',
              xaxis: {
                title: 'Time',
                type: 'date',
              },
              yaxis: {
                title: 'Count',
              },
              width: graphWidth,
              height: graphHeight
            }}
          /> 
        </div>
        <div className='analytics-item'>
          <BarGraph
            data={analytics && analytics.response_distribution.data} 
            layout = {{
              title: 'Response Type Distribution',
              xaxis: { title: 'Response Type' },
              yaxis: { title: 'Total Count' },
              width: graphWidth,
              height: graphHeight
            }}
          />
        </div>
        <div className='analytics-item'>
            <label className="analytics-label">
                {`Average Conversations per Session: ${analytics && analytics.average_number_of_conversations_in_a_session}`}
            </label>
        </div>
        <div className='analytics-item'>
            <label className="analytics-label">
                {`Book Classifier Accuracy: ${analytics && analytics.book_classifier_accuracy}`}
            </label>
        </div>      <div className='analytics-item'>
          <BarGraph
            data={analytics && analytics.book_distribution.data} 
            layout = {{
              title: 'Book Distribution',
              xaxis: { title: 'Book' },
              yaxis: { title: 'Total Count' },
              width: graphWidth,
              height: graphHeight
            }}
          />
        </div>
        <div className='analytics-item'>
          <BarGraph
            data={analytics && analytics.response_distribution.data} 
            layout = {{
              title: 'Response Distribution',
              xaxis: { title: 'Response Type' },
              yaxis: { title: 'Total Count' },
              width: graphWidth,
              height: graphHeight
            }}
          />
        </div>
      </div>
    )
  }
export default Analytics;
