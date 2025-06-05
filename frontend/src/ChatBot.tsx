import React, { useEffect, useState } from 'react';
import { Box, TextField, IconButton, Paper, Typography, Button } from '@mui/material';
import SendIcon from '@mui/icons-material/Send';
import './styles.css';

interface Question {
  id: number;
  text: string;
  guideline?: string | null;
}

interface Message {
  from: 'user' | 'bot';
  text: string;
}

interface Props {
  token?: string;
}

export default function ChatBot({ token: initialToken }: Props) {
  const [questions, setQuestions] = useState<Question[]>([]);
  const [token, setToken] = useState<string>(initialToken || '');
  const [messages, setMessages] = useState<Message[]>([]);
  const [input, setInput] = useState('');
  const [step, setStep] = useState(0);
  const [done, setDone] = useState(false);

  useEffect(() => {
    const init = async () => {
      const qResp = await fetch('/api/questions');
      const qs = await qResp.json();
      setQuestions(qs);
      let t = initialToken;
      if (!t) {
        const lResp = await fetch('/api/links', { method: 'POST' });
        const data = await lResp.json();
        t = data.token;
      }
      setToken(t);
      if (qs.length > 0) {
        setMessages([{ from: 'bot', text: qs[0].text }]);
      }
    };
    init();
  }, [initialToken]);

  const send = async () => {
    if (!input || done || step >= questions.length || !token) return;
    const userMsg: Message = { from: 'user', text: input };
    const q = questions[step];
    setMessages(prev => [...prev, userMsg]);
    setInput('');
    await fetch(`/api/links/${token}/answers/${q.id}`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ text: input })
    });
    const nextStep = step + 1;
    if (nextStep < questions.length) {
      setMessages(prev => [...prev, { from: 'bot', text: questions[nextStep].text }]);
      setStep(nextStep);
    } else {
      setMessages(prev => [...prev, { from: 'bot', text: 'Thank you for completing the survey!' }]);
      setDone(true);
    }
  };

  const handleKey = (e: React.KeyboardEvent) => {
    if (e.key === 'Enter') {
      send();
    }
  };

  if (questions.length === 0) {
    return <Typography>Loading...</Typography>;
  }

  return (
    <Box sx={{ maxWidth: 600, margin: '0 auto' }}>
      <Paper className="chat-container">
        {messages.map((m, i) => (
          <Typography key={i} className={`message ${m.from}`}>{m.text}</Typography>
        ))}
      </Paper>
      {!done && (
        <Box sx={{ display: 'flex', mt: 2 }}>
          <TextField
            fullWidth
            value={input}
            onChange={e => setInput(e.target.value)}
            onKeyDown={handleKey}
            placeholder="Type your answer..."
          />
          <IconButton color="primary" onClick={send} aria-label="send">
            <SendIcon />
          </IconButton>
        </Box>
      )}
      {done && (
        <Box sx={{ textAlign: 'center', mt: 2 }}>
          <Button variant="contained" onClick={() => window.location.reload()}>Start Again</Button>
        </Box>
      )}
    </Box>
  );
}
