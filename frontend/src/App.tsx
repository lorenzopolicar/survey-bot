import React from 'react';
import { BrowserRouter, Routes, Route, Link, useSearchParams } from 'react-router-dom';
import { AppBar, Toolbar, Typography, Container, Button } from '@mui/material';
import ChatBot from './ChatBot';
import Admin from './Admin';

function ChatWrapper() {
  const [params] = useSearchParams();
  const token = params.get('token');
  // If link was shared, token param will exist; ChatBot handles creating a token otherwise
  return <ChatBot />;
}

export default function App() {
  return (
    <BrowserRouter>
      <AppBar position="static">
        <Toolbar>
          <Typography variant="h6" sx={{ flexGrow: 1 }}>Survey Bot</Typography>
          <Button color="inherit" component={Link} to="/">Survey</Button>
          <Button color="inherit" component={Link} to="/admin">Admin</Button>
        </Toolbar>
      </AppBar>
      <Container sx={{ mt: 3 }}>
        <Routes>
          <Route path="/" element={<ChatWrapper />} />
          <Route path="/admin" element={<Admin />} />
        </Routes>
      </Container>
    </BrowserRouter>
  );
}
