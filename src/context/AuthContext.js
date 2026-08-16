import { createContext, useCallback, useContext, useEffect, useState } from 'react';
import * as SecureStore from 'expo-secure-store';
import { setAuthToken, setUnauthorizedHandler } from '../api/client';

const TOKEN_KEY = 'palette_access_token';

const AuthContext = createContext(null);

export function AuthProvider({ children }) {
  const [token, setToken] = useState(null);
  const [isReady, setIsReady] = useState(false);

  const logout = useCallback(async () => {
    try {
      await SecureStore.deleteItemAsync(TOKEN_KEY);
    } catch (err) {
      // SecureStore가 지원되지 않는 환경(web)에서 에러 무시
      console.warn('Failed to delete token from SecureStore:', err);
    }
    setAuthToken(null);
    setToken(null);
  }, []);

  useEffect(() => {
    setUnauthorizedHandler(logout);
  }, [logout]);

  useEffect(() => {
    (async () => {
      try {
        const stored = await SecureStore.getItemAsync(TOKEN_KEY);
        if (stored) {
          setAuthToken(stored);
          setToken(stored);
        }
      } catch (err) {
        // SecureStore가 지원되지 않는 환경(web)에서 에러 무시
        console.warn('Failed to load token from SecureStore:', err);
      } finally {
        // 어떤 경우든 초기화 완료로 표시
        setIsReady(true);
      }
    })();
  }, []);

  const login = useCallback(async (newToken) => {
    try {
      await SecureStore.setItemAsync(TOKEN_KEY, newToken);
    } catch (err) {
      // SecureStore가 지원되지 않는 환경(web)에서 에러 무시
      console.warn('Failed to save token to SecureStore:', err);
    }
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
