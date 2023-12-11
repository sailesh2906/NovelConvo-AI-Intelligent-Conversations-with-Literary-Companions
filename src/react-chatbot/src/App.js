import React, { useState } from 'react';


import './App.css';

import Analytics from './Analytics';
import ChatRoom from './ChatRoom';
import analyticsImage from './analytics.png';
import botImage from './bot.png';


import generateSessionId from './util';

function App() {
  const [chatMode, setChatMode] = useState(true);
  const [messages, addMessage] = useState([]);
  const [sessionEnded, setSessionEnded] = useState(false);

  const toggleChatMode = () => {
    setChatMode((chatMode) => !chatMode)
  };

  const sessionId = generateSessionId();
  const buttonTitle = chatMode ? "Go to Analytics" : "Go back to Chatbot"
  return (
    <div className="App">
      <header className="App-header">
        <h1>Query Alchemist 💬</h1>
        <button
         type="submit"
         onClick={toggleChatMode}
         title={buttonTitle}
         >{
          <img src={chatMode ? analyticsImage: botImage} alt="Icon" />
        }</button>
      </header>

      <section>
        {chatMode ? (
            <ChatRoom
              sessionId={sessionId}
              messages={messages}
              addMessage={addMessage}
              sessionEnded={sessionEnded}
              setSessionEnded={setSessionEnded}
            />
          ) : (
            <Analytics />
          )}
      </section>
    </div>
  );
}

export default App;
