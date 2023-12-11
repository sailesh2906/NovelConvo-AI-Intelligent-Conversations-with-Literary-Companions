import React, {useEffect, useState } from 'react';
import axios from 'axios';


import './App.css';

import TimeSeriesChart from './TimeSeriesChart';
import BarGraph from './BarGraph';
import { CLOUD_URL, ANALYTICS_ENDPOINT } from './constants';



function Analytics() {
    const analytics_url = CLOUD_URL + ANALYTICS_ENDPOINT;
    const [analytics, setAnalytics] = useState(false);
  
    useEffect(()  => {
      if (!analytics) {
        fetchAnalytics();
      }
    }, []);
  
    const fetchAnalytics = async () => {
      try {
        const response = await axios.get(analytics_url);
        setAnalytics(response.data);
      } catch (error) {
        console.error('Error sending message:', error);
      }

    };

    const graphWidth = "500"
    const graphHeight = "270"
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
            data={analytics && analytics.response_distribution.data && analytics.response_distribution.data[0]} 
            layout = {{
              title: 'Response Type Distribution',
              xaxis: { title: 'Response Type' },
              yaxis: { title: 'Total Count' },
              width: graphWidth,
              height: graphHeight
            }}
            subBooks={false}
          />
        </div>
        <div className='analytics-item'>
            <label className="analytics-label">
                {`Average Conversations per Session: ${analytics && Math.round(analytics.average_number_of_conversations_in_a_session* 100) / 100}`}
            </label>
        </div>
        <div className='analytics-item'>
            <label className="analytics-label">
                {`Book Classifier Accuracy: ${analytics && Math.round(analytics.book_classifier_accuracy* 100) / 100}`}
            </label>
        </div> 
        <div className='analytics-item'>
            <label className="analytics-label">
                {`Average Solr Docs Retrieved per Session: ${analytics && Math.round(analytics.average_number_of_solr_documents_fetched_in_a_session* 100) / 100}`}
            </label>
        </div>
        <div className='analytics-item'>
            <label className="analytics-label">
                {`Total Sessions Count: ${analytics && analytics.total_number_of_sessions}`}
            </label>
        </div>        
        <div className='analytics-item'>
          <BarGraph
            data={analytics && analytics.book_distribution.data && analytics.book_distribution.data[0]} 
            layout = {{
              title: 'Book Distribution',
              xaxis: { title: 'Book' },
              yaxis: { title: 'Total Count' },
              width: graphWidth,
              height: graphHeight
            }}
            subBooks
          />
        </div>
        <div className='analytics-item'>
          <BarGraph
            data={analytics && analytics.solr_documents_distribution_across_book_distribution.data && analytics.solr_documents_distribution_across_book_distribution.data[0]} 
            layout = {{
              title: 'Solr Document Retrived Distribution',
              xaxis: { title: 'Book' },
              yaxis: { title: 'Total Count' },
              width: graphWidth,
              height: graphHeight
            }}
            subBooks
          />
        </div>
      </div>
    )
  }
export default Analytics;
