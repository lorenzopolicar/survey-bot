import React, { useState } from 'react';

interface Message {
  from: 'user' | 'bot';
  text: string;
}

export default function ChatBot() {
  const [messages, setMessages] = useState<Message[]>([]);
  const [input, setInput] = useState('');

  const send = async () => {
    if (!input) return;
    const userMsg: Message = { from: 'user', text: input };
    setMessages([...messages, userMsg]);
    setInput('');
    const resp = await fetch('/api/chat', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ message: input })
    });
    const data = await resp.json();
    setMessages([...messages, userMsg, { from: 'bot', text: data.message }]);
  };

  return (
    <div>
      <div>
        {messages.map((m, i) => (
          <div key={i}><b>{m.from}:</b> {m.text}</div>
        ))}
      </div>
      <input value={input} onChange={e => setInput(e.target.value)} />
      <button onClick={send}>Send</button>
    </div>
  );
}
