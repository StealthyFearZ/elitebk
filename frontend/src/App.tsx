import { Link, Route, Routes } from 'react-router-dom'
import ChatWindow from './components/ChatWindow'

function HomePage() {
  return (
    <main style={{ padding: '2rem', maxWidth: 900, margin: '0 auto' }}>
      <h1>EliteBK</h1>
      <p>Use the chat route to interact with the assistant.</p>
      <Link to="/chat">Go to Chat</Link>
    </main>
  )
}

function App() {
  return (
    <Routes>
      <Route path="/" element={<HomePage />} />
      <Route path="/chat" element={<ChatWindow />} />
    </Routes>
  )
}

export default App
