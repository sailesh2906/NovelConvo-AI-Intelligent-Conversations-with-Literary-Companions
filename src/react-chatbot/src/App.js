import React, { useRef, useState } from 'react';
import axios from 'axios';

import './App.css';


const CHAT_URL = 'http://34.168.237.117:5000/chat';
const SMALL_CHAT_URL = 'http://34.168.123.224:5000/chat';

function App() {
  return (
    <div className="App">
      <header className="App-header">
      </header>

      <section>
        {<ChatRoom />}
      </section>
    </div>
  );
}

function ChatRoom() {
  const dummy = useRef();
  const messages = [];

  const [formValue, setFormValue] = useState('');
  const [botResponse, setBotResponse] = useState('');


  const sendMessage = async (e) => {
    e.preventDefault();

    try {
      const response = await axios.post(SMALL_CHAT_URL, {
        message: formValue,
      });
      setBotResponse(response.data.message);
      console.log(response)
    } catch (error) {
      console.error('Error sending message:', error);
    }

    // const { uid, photoURL } = auth.currentUser;

    // await messagesRef.add({
    //   text: formValue,
    //   createdAt: firebase.firestore.FieldValue.serverTimestamp(),
    //   uid,
    //   photoURL
    // })

    setFormValue('');
    dummy.current.scrollIntoView({ behavior: 'smooth' });
  }
  
  return (<>
    <main>

      {messages && messages.map(msg => <ChatMessage key={msg.id} message={msg} />)}

      <span ref={dummy}></span>

    </main>

    <form onSubmit={sendMessage}>

      <input value={formValue} onChange={(e) => setFormValue(e.target.value)} placeholder="say something nice" />

      <button type="submit" disabled={!formValue}>🕊️</button>

    </form>
  </>)
}


function ChatMessage(props) {
  const { text, uid, photoURL, bot } = props.message;

  const messageClass = bot ? 'received': 'sent';

  return (<>
    <div className={`message ${messageClass}`}>
      <img src={photoURL || 'https://api.adorable.io/avatars/23/abott@adorable.png'} />
      <p>{text}</p>
    </div>
  </>)
}
export default App;
