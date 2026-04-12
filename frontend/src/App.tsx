import { Link, Navigate, Route, Routes } from 'react-router-dom';
import ChatWindow from './components/ChatWindow';
import LoginPage from './components/LoginPage';
import { AuthProvider, useAuth } from './context/AuthContext';

function HomePage() {
  return (
    <main style={{ padding: '2rem', maxWidth: 900, margin: '0 auto' }}>
      <h1>EliteBK</h1>
      <p>Use the chat route to interact with the assistant.</p>
      <Link to="/chat">Go to Chat</Link>
    </main>
  );
}

function ProtectedChat() {
  const { isAuthenticated } = useAuth();
  if (!isAuthenticated) return <Navigate to="/login" replace />;
  return <ChatWindow />;
}

function App() {
  return (
    <AuthProvider>
      <Routes>
        <Route path="/" element={<HomePage />} />
        <Route path="/login" element={<LoginPage />} />
        <Route path="/chat" element={<ProtectedChat />} />
      </Routes>
    </AuthProvider>
  );
}

export default App;
