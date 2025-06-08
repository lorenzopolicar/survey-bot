import React, { useEffect, useState } from 'react';
import { Box, TextField, IconButton, Paper, Typography, Button } from '@mui/material';
import SendIcon from '@mui/icons-material/Send';
import './styles.css';

interface Question {
  id: number;
  text: string;
  guidelines?: string | null;
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
  const [token, setToken] = useState<string>(initialToken ?? '');
  const [messages, setMessages] = useState<Message[]>([]);
  const [input, setInput] = useState('');
  const [step, setStep] = useState(0);
  const [done, setDone] = useState(false);
  const [isStarted, setIsStarted] = useState(false);
  const [isLoading, setIsLoading] = useState(false);

  useEffect(() => {
    const init = async () => {
      const qResp = await fetch('/api/questions');
      const qs = await qResp.json();
      setQuestions(qs);
      let t = initialToken ?? '';
      if (!t) {
        const lResp = await fetch('/api/links', { method: 'POST' });
        const data = await lResp.json();
        t = data.token ?? '';
      }
      setToken(t);
      if (qs.length > 0) {
        setMessages([{ from: 'bot', text: qs[0].text }]);
      }
      // Add welcome message
      setMessages([{ 
        from: 'bot', 
        text: 'Welcome to the survey! Click the Start button below to begin.' 
      }]);
    };
    init();
  }, [initialToken]);

  const startSurvey = async () => {
    if (!token) return;
    setIsLoading(true);
    try {
      const response = await fetch(`/api/links/${token}/start`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' }
      });
      const data = await response.json();
      setMessages(prev => [...prev, { from: 'bot', text: data.response }]);
      setIsStarted(true);
    } catch (error) {
      console.error('Error starting survey:', error);
      setMessages(prev => [...prev, { 
        from: 'bot', 
        text: 'Sorry, there was an error starting the survey. Please try again.' 
      }]);
    }
    setIsLoading(false);
  };

  const sendMessage = async () => {
    if (!input || !token || !isStarted) return;
    const userMsg: Message = { from: 'user', text: input };
    setMessages(prev => [...prev, userMsg]);
    setInput('');
    setIsLoading(true);

    try {
      const response = await fetch(`/api/links/${token}/message`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ text: input })
      });
      const data = await response.json();
      setMessages(prev => [...prev, { from: 'bot', text: data.response }]);
    } catch (error) {
      console.error('Error sending message:', error);
      setMessages(prev => [...prev, { 
        from: 'bot', 
        text: 'Sorry, there was an error processing your response. Please try again.' 
      }]);
    }
    setIsLoading(false);
  };

  const handleKey = (e: React.KeyboardEvent) => {
    if (e.key === 'Enter' && !isLoading) {
      if (!isStarted) {
        startSurvey();
      } else {
        sendMessage();
      }
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
      <Box sx={{ display: 'flex', mt: 2 }}>
        {!isStarted ? (
          <Button 
            variant="contained" 
            onClick={startSurvey} 
            disabled={isLoading}
            fullWidth
          >
            {isLoading ? 'Starting...' : 'Start Survey'}
          </Button>
        ) : (
          <>
            <TextField
              fullWidth
              value={input}
              onChange={e => setInput(e.target.value)}
              onKeyDown={handleKey}
              placeholder="Type your answer..."
              disabled={isLoading}
            />
            <IconButton 
              color="primary" 
              onClick={sendMessage} 
              disabled={isLoading}
              aria-label="send"
            >
              <SendIcon />
            </IconButton>
          </>
        )}
      </Box>
      {done && (
        <Box sx={{ textAlign: 'center', mt: 2 }}>
          <Button variant="contained" onClick={() => window.location.reload()}>Start Again</Button>
        </Box>
      )}
    </Box>
  );
}
