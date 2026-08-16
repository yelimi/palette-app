import { createContext, useCallback, useContext, useEffect, useState } from 'react';
import * as SecureStore from 'expo-secure-store';
import { setAuthToken, setUnauthorizedHandler } from '../api/client';

const TOKEN_KEY = 'palette_access_token';

const AuthContext = createContext(null);

export function AuthProvider({ children }) {
  const [token, setToken] = useState(null);
  const [isReady, setIsReady] = useState(false);

  const logout = useCallback(async () => {
    await SecureStore.deleteItemAsync(TOKEN_KEY);
    setAuthToken(null);
    setToken(null);
  }, []);

  useEffect(() => {
    setUnauthorizedHandler(logout);
  }, [logout]);

  useEffect(() => {
    (async () => {
      const stored = await SecureStore.getItemAsync(TOKEN_KEY);
      if (stored) {
        setAuthToken(stored);
        setToken(stored);
      }
      setIsReady(true);
    })();
  }, []);

  const login = useCallback(async (newToken) => {
    await SecureStore.setItemAsync(TOKEN_KEY, newToken);
    setAuthToken(newToken);
    setToken(newToken);
  }, []);

  return (
    <AuthContext.Provider value={{ token, isReady, login, logout }}>
      {children}
    </AuthContext.Provider>
  );
}

export function useAuth() {
  const ctx = useContext(AuthContext);
  if (!ctx) throw new Error('useAuth must be used within AuthProvider');
  return ctx;
}
