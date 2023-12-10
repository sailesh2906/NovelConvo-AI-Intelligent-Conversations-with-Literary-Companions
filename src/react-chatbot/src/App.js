import React, { useRef, useEffect, useState } from 'react';


import './App.css';

import Analytics from './Analytics';
import ChatRoom from './ChatRoom';
import analyticsImage from './analytics.png';


import generateSessionId from './util';

function App() {
  const [chatMode, setChatMode] = useState(true);
  
  const toggleChatMode = () => {
    setChatMode((chatMode) => !chatMode)
  };

  const sessionId = generateSessionId();
  return (
    <div className="App">
      <header className="App-header">
        <h1>Query Alchemist 💬</h1>
        <button type="submit" onClick={toggleChatMode}>{
          <img src={analyticsImage} alt="Icon" />
        }</button>
      </header>

      <section>
        {chatMode ? <ChatRoom sessionId={sessionId}/> : <Analytics />}
      </section>
    </div>
  );
}

export default App;
