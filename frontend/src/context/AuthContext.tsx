import { createContext, useContext, useState } from 'react';
import type { ReactNode } from 'react';

interface AuthState {
  token: string | null;
  username: string | null;
  role: string | null;
}

interface AuthContextType extends AuthState {
  login: (token: string, username: string, role: string) => void;
  logout: () => void;
  isDeveloper: boolean;
  isAuthenticated: boolean;
}

const AuthContext = createContext<AuthContextType | null>(null);

const STORAGE_KEY = 'auth';

function loadFromStorage(): AuthState {
  try {
    const raw = localStorage.getItem(STORAGE_KEY);
    if (raw) return JSON.parse(raw);
  } catch {
    // ignore ig :(?)
  }
  return { token: null, username: null, role: null };
}

export function AuthProvider({ children }: { children: ReactNode }) {
  const [auth, setAuth] = useState<AuthState>(loadFromStorage);

  const login = (token: string, username: string, role: string) => {
    const next = { token, username, role };
    setAuth(next);
    localStorage.setItem(STORAGE_KEY, JSON.stringify(next));
  };

  const logout = () => {
    setAuth({ token: null, username: null, role: null });
    localStorage.removeItem(STORAGE_KEY);
  };

  // Cheeck if user is a developer / authenticated
  return (
    <AuthContext.Provider
      value={{
        ...auth,
        login,
        logout,
        isDeveloper: auth.role === 'developer',
        isAuthenticated: auth.token !== null,
      }}
    >
      {children}
    </AuthContext.Provider>
  );
}

export function useAuth() {
  const ctx = useContext(AuthContext);
  if (!ctx) throw new Error('useAuth must be used inside AuthProvider');
  return ctx;
}
