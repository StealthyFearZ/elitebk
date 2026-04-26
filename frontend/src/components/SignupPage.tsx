import { useState, FormEvent } from 'react';
import { Link, useNavigate } from 'react-router-dom';
import { useAuth } from '../context/AuthContext';

export default function SignupPage() {
  const [username, setUsername] = useState('');
  const [password, setPassword] = useState('');
  const [confirmPassword, setConfirmPassword] = useState('');
  const [role, setRole] = useState<'end_user' | 'developer'>('end_user');
  const [error, setError] = useState<string | null>(null);
  const [loading, setLoading] = useState(false);

  const { login } = useAuth();
  const navigate = useNavigate();
  const API_URL = import.meta.env.VITE_API_URL ?? "http://localhost:8000";

  const handleSubmit = async (e: FormEvent) => {
    e.preventDefault();
    setError(null);

    if (password !== confirmPassword) { // Error for passwords not matching here
      setError('Passwords do not match');
      return;
    }

    setLoading(true);
    try {
      //fetch it
      const res = await fetch(`${API_URL}/api/register/`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ username, password, role }),
      });

      const data = await res.json();

      // Check if the registration failed
      if (!res.ok) {
        setError(data.error || 'Registration failed');
        return;
      }

      // Log them in
      login(data.token, data.username, data.role);
      //move them to the chat part of RAG
      navigate('/chat');
    } catch {
      setError('Unable to reach the server. Please try again.');
    } finally {
      setLoading(false);
    }
  };

  // Add the HTML PART
  return (
    <div className="min-h-screen flex items-center justify-center bg-gray-50">
      <div className="bg-white p-8 rounded-xl shadow-lg border border-gray-100 w-full max-w-sm">
        <div className="text-center mb-4">
          {/* Add Basketball logo */}
          <span className="text-4xl">🏀</span>
          <p className="text-xs font-semibold text-gray-400 tracking-widest uppercase mt-1">EliteBK</p>
        </div>
        <h1 className="text-2xl font-bold text-center mb-6" style={{ color: '#111827' }}>Create Account</h1>
        <form onSubmit={handleSubmit} className="flex flex-col gap-4">
          <div>
            {/*Username Block*/}
            <label className="block text-sm font-medium text-gray-700 mb-1">Username</label>
            <input
              type="text"
              value={username}
              onChange={(e) => setUsername(e.target.value)}
              className="w-full border border-gray-300 p-3 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
              required
              disabled={loading}
            />
          </div>
          <div>
            {/*Password Block*/}
            <label className="block text-sm font-medium text-gray-700 mb-1">Password</label>
            <input
              type="password"
              value={password}
              onChange={(e) => setPassword(e.target.value)}
              className="w-full border border-gray-300 p-3 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
              required
              disabled={loading}
            />
          </div>
          <div>
            {/*Confirm password blOck*/}
            <label className="block text-sm font-medium text-gray-700 mb-1">Confirm Password</label>
            <input
              type="password"
              value={confirmPassword}
              onChange={(e) => setConfirmPassword(e.target.value)}
              className="w-full border border-gray-300 p-3 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
              required
              disabled={loading}
            />
          </div>
          <div>
            {/* Choose the role here */}
            <label className="block text-sm font-medium text-gray-700 mb-2">I am a...</label>
            <div className="flex gap-3">
                {/* Dropdown menu */}
                <select
                    value={role}
                    onChange={(e) => setRole(e.target.value as 'end_user' | 'developer')}
                    className="w-full border border-gray-300 p-3 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500 bg-white text-gray-700"
                    disabled={loading}
                    >
                    <option value="end_user">User</option>
                    <option value="developer">Developer</option>
                </select>
            </div>
          </div>
          {error && <p className="text-red-500 text-sm">{error}</p>}
          {/* Button for submitting the info*/}
          <button
            type="submit"
            disabled={loading}
            className="bg-gray-800 hover:bg-gray-700 text-white py-3 rounded-lg font-medium transition-colors disabled:opacity-50 disabled:cursor-not-allowed"
          >
            {loading ? 'Creating account...' : 'Sign Up'}
          </button>
        </form>
        {/* Add link to login page if they don't need to make a new account */}
        <p className="text-center text-sm text-gray-500 mt-4">
          Already have an account?{' '}
          <Link to="/login" className="text-blue-600 hover:underline">Log in</Link>
        </p>
      </div>
    </div>
  );
}