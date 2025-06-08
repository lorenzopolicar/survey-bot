import React, { useEffect, useState } from 'react';
import { Box, Button, TextField, Typography, List, ListItem, ListItemText } from '@mui/material';

interface Question {
  id: number;
  text: string;
  guidelines?: string | null;
}

export default function Admin() {
  const [questions, setQuestions] = useState<Question[]>([]);
  const [text, setText] = useState('');
  const [guidelines, setGuidelines] = useState('');
  const [link, setLink] = useState<string | null>(null);

  const loadQuestions = async () => {
    try {
      const resp = await fetch('/api/questions');
      if (!resp.ok) {
        throw new Error(`HTTP error! status: ${resp.status}`);
      }
      const data = await resp.json();
      setQuestions(Array.isArray(data) ? data : []);
    } catch (error) {
      console.error('Error loading questions:', error);
      setQuestions([]);
    }
  };

  useEffect(() => {
    loadQuestions();
  }, []);

  const addQuestion = async () => {
    if (!text) return;
    await fetch('/api/questions', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ text, guidelines: guidelines || null })
    });
    setText('');
    setGuidelines('');
    loadQuestions();
  };

  const createLink = async () => {
    const resp = await fetch('/api/links', { method: 'POST' });
    const { token } = await resp.json();
    setLink(`${window.location.origin}?token=${token}`);
  };

  return (
    <Box sx={{ maxWidth: 600, mx: 'auto' }}>
      <Typography variant="h5" sx={{ my: 2 }}>Manage Questions</Typography>
      <Box sx={{ display: 'flex', gap: 1, mb: 2 }}>
        <TextField label="Question" value={text} onChange={e => setText(e.target.value)} fullWidth />
        <TextField label="Guideline" value={guidelines} onChange={e => setGuidelines(e.target.value)} fullWidth />
        <Button variant="contained" onClick={addQuestion}>Add</Button>
      </Box>
      <List>
        {questions.map(q => (
          <ListItem key={q.id} divider>
            <ListItemText primary={q.text} secondary={q.guidelines || ''} />
          </ListItem>
        ))}
      </List>
      <Button variant="contained" onClick={createLink} sx={{ mt: 2 }}>Generate Survey Link</Button>
      {link && (
        <Typography sx={{ mt: 1 }}>Share this link: <a href={link}>{link}</a></Typography>
      )}
    </Box>
  );
}
