import { Platform } from 'react-native';
import Constants from 'expo-constants';

const DEV_PORT = 8000;

function resolveBaseUrl() {
  const override = Constants.expoConfig?.extra?.apiBaseUrl;
  if (override) return override;
  if (Platform.OS === 'android') return `http://10.0.2.2:${DEV_PORT}`;
  return `http://localhost:${DEV_PORT}`;
}

export const API_BASE_URL = resolveBaseUrl();

export class ApiError extends Error {
  constructor(status, data, message) {
    super(message || ApiError.extractMessage(status, data));
    this.status = status;
    this.data = data;
  }

  static extractMessage(status, data) {
    if (!data) return `요청 실패 (${status})`;
    if (typeof data.detail === 'string') return data.detail;
    if (Array.isArray(data.detail)) {
      return data.detail
        .map((e) => String(e.msg || '').replace(/^Value error,\s*/, ''))
        .join('\n');
    }
    return `요청 실패 (${status})`;
  }
}

let authToken = null;
let onUnauthorized = null;

export function setAuthToken(token) {
  authToken = token;
}

export function setUnauthorizedHandler(handler) {
  onUnauthorized = handler;
}

export async function apiFetch(path, options = {}) {
  const headers = { ...(options.headers || {}) };
  if (!(options.body instanceof FormData)) {
    headers['Content-Type'] = 'application/json';
  }
  if (authToken) {
    headers['Authorization'] = `Bearer ${authToken}`;
  }

  let response;
  try {
    response = await fetch(`${API_BASE_URL}${path}`, { ...options, headers });
  } catch (err) {
    throw new ApiError(0, null, '네트워크 연결을 확인해주세요.');
  }

  if (response.status === 204) {
    return null;
  }

  const data = await response.json().catch(() => null);

  if (!response.ok) {
    if (response.status === 401 && onUnauthorized) {
      onUnauthorized();
    }
    throw new ApiError(response.status, data);
  }

  return data;
}
