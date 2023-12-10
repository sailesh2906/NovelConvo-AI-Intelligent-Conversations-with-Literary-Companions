import React, { useRef, useState } from 'react';
import axios from 'axios';

import './App.css';

import manImage from './man.png';
import botImage from './bot.png';
import sendImage from './send.png';

const LOCAL_URL = 'http://localhost:5000/chat';
const CLOUD_URL = 'http://34.125.179.216:5000/chat';

const PREV_MSG_COUNT = 5;

const INIT_BOOKS = [
  {
    'bookId': 0,
    'bookName': "The Adventures of Sherlock Holmes",
    'checked': false
  },
  {
    'bookId': 1,
    'bookName': "Romeo and Juliet",
    'checked': false
  },
  {
    'bookId': 2,
    'bookName': "The Iliad",
    'checked': false
  },
  {
    'bookId': 3,
    'bookName': "Gulliver's Travels",
    'checked': false
  },
  {
    'bookId': 4,
    'bookName': "Moby Dick",
    'checked': false
  },
  {
    'bookId': 5,
    'bookName': "Hervey Willetts",
    'checked': false
  },
  {
    'bookId': 6,
    'bookName': "Babbitt",
    'checked': false
  },
  {
    'bookId': 7,
    'bookName': "Dracula",
    'checked': false
  },
  {
    'bookId': 8,
    'bookName': "Adventures of Huckleberry Finn",
    'checked': false
  },
  {
    'bookId': 9,
    'bookName': "The Alchemist",
    'checked': false
  }
]

function App() {
  return (
    <div className="App">
      <header className="App-header">
        <h1>Query Alchemist 💬</h1>
      </header>

      <section>
        {<ChatRoom />}
      </section>
    </div>
  );
}

function ChatRoom() {
  const dummy = useRef();

  const [formValue, setFormValue] = useState('');
  const [messages, addMessage] = useState([]);
  const [books, setBooks] = useState(INIT_BOOKS)
  let [msgCounter, setMsgCounter] = useState(0);
  const [sessionEnded, setSessionEnded] = useState(false);

  const cloud_url = CLOUD_URL;

  const sendMessage = async (e) => {
    setFormValue('');
    try {
      const response = await axios.post(cloud_url, {
        prompt: formValue,
        books: getBooksToSend(),
        prev_msgs: getPrevMessages()
      });
      setMsgCounter((msgCounter) => (msgCounter += 1))
      addMessage((messages) => ([
        ...messages,
        {
          text: response.data.output,
          bot: true,
          id: msgCounter,
          chitChat : response.data.chit_chat
        }
      ]));
      
      if (response.data.farewell) {
        setSessionEnded(true)
      }
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

    dummy.current.scrollIntoView({ behavior: 'smooth' });
  }
  
  const getBooksToSend = () => {
    let booksToSend = [];

    books.forEach((book) => {
      if (book.checked) {
        booksToSend = [...booksToSend, book.bookId];
      }
    });

    return booksToSend || null
  }

  const getPrevMessages = () => {
    let cntr = 0;
  
    const prevMessages = [];
    messages.slice(0).reverse().forEach(msg => {
      console.log(msg)
      if (msg.bot && !msg.chitChat && cntr <= PREV_MSG_COUNT) {
        prevMessages.push(msg.text)
        cntr += 1
      }

    });
    
    return prevMessages
  }

  const onType = (val) => {
    console.log(msgCounter)
    setFormValue(val)
  }

  const addUserMsg = () => {
    setMsgCounter((msgCounter) => (msgCounter += 1))
    addMessage((messages) => ([
      ...messages,
      {
        text: formValue,
        bot: false,
        id: msgCounter
      }
    ]));
  }

  const onClickSend = (e) => {
    e.preventDefault();
  
    addUserMsg();
    sendMessage(e);
    console.log(getBooksToSend())
  }

  const onToggleCheck = (bookId) => {
    const newBooks = books.map((book) => {
      if (book.bookId === bookId) book.checked = !book.checked
      return book
    })

    setBooks(newBooks)
  }

  const placeholder = sessionEnded ? "Session Ended!! Bye" : "wanna talk books"
  return (
  <div class="flex-container">
    <div class="flex-child filters">
      {books.map(book => <Checkbox key={`checkbox_book_${book.bookId}`} label={book.bookName} isChecked={book.checked} onChange={() => onToggleCheck(book.bookId)}/>)}
    </div>
    <div class="flex-child chat">
      <main>

        {messages && messages.map(msg => (
          <ChatMessage
            key={`chat_${msg.id}`}
            message={msg}
          />
          ))}

        <span ref={dummy}></span>

      </main>

      <form onSubmit={onClickSend}>
        <input 
          className = "typebox"
          value={formValue}
          onChange={(e) => onType(e.target.value)}
          placeholder={placeholder}
          disabled={sessionEnded}
        />

        <button type="submit" disabled={!formValue || sessionEnded}>{
          <img src={sendImage} alt="Icon" />
        }</button>

      </form>
    </div>
  </div>
  )
}


function ChatMessage(props) {
  const { text, bot, chitChat } = props.message;

  const messageClass = bot ? 'received': 'sent';

  let title = "";
  if (bot) title = chitChat ? "ChitChat": "Novels";

  return (<>
    <div className={`message ${messageClass}`}>
      <img src={bot ? botImage : manImage} alt="Icon" />
      <p title={title}>{text}</p>
    </div>
  </>)
}

const Checkbox = ({ label, isChecked, onChange }) => {
  return (
    <div className='flex-checkbox'>
      <input
        type="checkbox"
        checked={isChecked}
        onChange={onChange}
      />
      <label className='checkbox-label'>{label}</label>
    </div>
  );
};
export default App;
