import React, { useRef, useEffect, useState } from 'react';

import './App.css';

import axios from 'axios';
import manImage from './man.png';
import botImage from './bot.png';
import sendImage from './send.png';

import { CLOUD_URL, INIT_BOOKS, CHAT_ENDPOINT, PREV_MSG_COUNT } from './constants';


function ChatRoom({ 
  sessionId,
  messages,
  addMessage,
  sessionEnded,
  setSessionEnded 
}) {
    const dummy = useRef();
  
    const [formValue, setFormValue] = useState('');
    const [books, setBooks] = useState(INIT_BOOKS)
    let [msgCounter, setMsgCounter] = useState(0);
    const [waitForResponse, setWaitForResponse] = useState(false);

  
    useEffect(() => {
      dummy.current.scrollIntoView({ behavior: 'smooth' });
    }, [messages]);
  
    const chat_url = CLOUD_URL + CHAT_ENDPOINT;
  
    const sendMessage = async (e) => {
      setFormValue('');
      setWaitForResponse((waitForResponse) => !waitForResponse)
      try {
        const response = await axios.post(chat_url, {
          prompt: formValue,
          books: getBooksToSend(),
          prev_msgs: getPrevMessages(),
          conversation_id: sessionId
        });
        addMessage((messages) => ([
          ...messages,
          {
            text: response.data.output,
            bot: true,
            id: msgCounter + 1,
            chitChat : response.data.chit_chat
          }
        ]));
        setWaitForResponse((waitForResponse) => !waitForResponse)
        setMsgCounter((msgCounter) => (msgCounter += 1))
        
        if (response.data.farewell) {
          setSessionEnded(true)
        }
      } catch (error) {
        addMessage((messages) => ([
          ...messages,
          {
            text: "Cloud Service Down",
            bot: true,
            id: msgCounter + 1,
            chitChat : false
          }
        ]));
        setWaitForResponse((waitForResponse) => !waitForResponse)
        setMsgCounter((msgCounter) => (msgCounter += 1))
        console.error('Error sending message:', error);
      }
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
        if (msg.bot && !msg.chitChat && cntr <= PREV_MSG_COUNT) {
          prevMessages.push(msg.text)
          cntr += 1
        }
  
      });
      
      return prevMessages
    }
  
    const onType = (val) => {
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
    }
  
    const onToggleCheck = (bookId) => {
      const newBooks = books.map((book) => {
        if (book.bookId === bookId) book.checked = !book.checked
        return book
      })
  
      setBooks(newBooks)
    }
  
    const placeholder = sessionEnded ? "Session Ended!! Bye" : "Wanna talk books??";
    const typingLabel = waitForResponse ? "Bot Typing..." : ""
    return (
    <div className="flex-container">
      <div className="flex-child filters">
        {books.map(book => <Checkbox key={`checkbox_book_${book.bookId}`} label={book.bookName} isChecked={book.checked} onChange={() => onToggleCheck(book.bookId)}/>)}
      </div>
      <div className="flex-child chat">
        <main>
  
          {messages && messages.map(msg => (
            <ChatMessage
              key={`chat_${msg.id}`}
              message={msg}
            />
            ))}
  
          <span ref={dummy}></span>
  
        </main>
        <label className="typing-label">{typingLabel}</label>
        <form onSubmit={onClickSend}>
          <input 
            className = "typebox"
            value={formValue}
            onChange={(e) => onType(e.target.value)}
            placeholder={placeholder}
            disabled={sessionEnded || waitForResponse}
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
    if (bot) title = chitChat ? "ChitChat": "RAG";
  
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

  
export default ChatRoom;
