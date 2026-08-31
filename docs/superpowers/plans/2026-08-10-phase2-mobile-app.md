# Phase 2: 모바일 앱 (React Native) Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Expo Router 기반 React Native 앱 구축 — 로그인/회원가입, 홈(이미지 업로드 → 색상추천 → 상품 그리드), 상품 상세, 장바구니 화면을 완성된 FastAPI 백엔드에 연동한다.

**Architecture:** `app/` 디렉토리의 Expo Router 파일 기반 라우팅으로 `(auth)`(로그인/회원가입)와 `(tabs)`(홈/장바구니) 두 라우트 그룹을 구성하고, 루트 레이아웃이 인증 토큰 유무에 따라 두 그룹 사이를 리다이렉트한다. API 호출은 `src/api/`의 공통 `apiFetch` 래퍼를 통해 이루어지며, 인증 토큰은 `expo-secure-store`에 저장되고 `AuthContext`가 전역 상태로 노출한다.

**Tech Stack:** Expo SDK ~56.0.12, Expo Router 56.2.17, React 19.2.3, React Native 0.85.3, expo-secure-store, expo-image-picker, expo-camera (프로젝트 자바스크립트, TypeScript 미사용 — 기존 `App.js`와 동일한 컨벤션)

**참고 스펙:** `docs/superpowers/specs/2026-08-09-phase2-mobile-app-design.md`

## Global Constraints

- 백엔드 API 개발 서버는 `uvicorn main:app --reload --port 8000` (backend/ 디렉토리, venv 활성화)로 실행. 기본 base URL은 `http://localhost:8000` (iOS 시뮬레이터/웹), Android 에뮬레이터는 `http://10.0.2.2:8000` — `src/api/client.js`에서 플랫폼별로 자동 계산하고, `app.json`의 `extra.apiBaseUrl`로 override 가능
- 네비게이션은 Expo Router만 사용 (`app/` 디렉토리, route groups `(auth)`/`(tabs)`). React Navigation을 별도로 직접 설정하지 않음
- 인증 토큰은 `expo-secure-store`에 키 `palette_access_token`으로 저장, 앱 재실행 시 유지(자동로그인)
- 전체 상품목록/필터 화면(`GET /products` 페이징 UI)은 이번 phase 범위 밖 — 상품은 색상 추천 결과를 통해서만 접근
- RN 쪽 자동화 테스트(Jest 등)는 이 phase에서 신규로 구축하지 않음. 각 태스크는 `npx expo start`로 실행해 수동 확인
- 파일은 JavaScript(`.js`)로 작성 (기존 `App.js`가 JS이므로 TypeScript 미도입)
- FastAPI 422 응답의 `detail`은 커스텀 `HTTPException`이면 문자열, pydantic 필드 검증 실패면 `[{msg: "Value error, ..."}]` 형태의 배열 — API 클라이언트가 두 형태를 모두 사람이 읽을 문자열로 정규화해야 함

---

## 파일 구조

```
palette-app/
├── app.json                       # 수정: expo-router 플러그인/scheme/extra 추가
├── package.json                   # 수정: main을 expo-router/entry로 변경
├── App.js                         # 삭제
├── index.js                       # 삭제
├── app/
│   ├── _layout.js                  # 루트: AuthProvider + 인증 상태 리다이렉트
│   ├── (auth)/
│   │   ├── _layout.js               # 비로그인 스택
│   │   ├── login.js
│   │   └── register.js
│   └── (tabs)/
│       ├── _layout.js               # 로그인 상태 bottom tabs
│       ├── index.js                  # 홈: 이미지 업로드 → 색상추천 → 상품 그리드
│       ├── cart.js                   # 장바구니 + 로그아웃
│       └── product/
│           └── [id].js                # 상품 상세 + 장바구니 담기
└── src/
    ├── api/
    │   ├── client.js                 # apiFetch, ApiError, 토큰/401 훅
    │   ├── auth.js                    # login(), register()
    │   ├── products.js                 # getProductsByColor(), getProduct()
    │   ├── colors.js                    # extractColor()
    │   └── cart.js                       # getCart(), addToCart(), removeFromCart()
    └── context/
        └── AuthContext.js              # AuthProvider, useAuth()
```

---

## Task 1: Expo Router 설치 + 라우트 뼈대

**Files:**
- Modify: `package.json`
- Modify: `app.json`
- Delete: `App.js`
- Delete: `index.js`
- Create: `app/_layout.js`
- Create: `app/(auth)/_layout.js`
- Create: `app/(auth)/login.js`
- Create: `app/(auth)/register.js`
- Create: `app/(tabs)/_layout.js`
- Create: `app/(tabs)/index.js`
- Create: `app/(tabs)/cart.js`
- Create: `app/(tabs)/product/[id].js`

**Interfaces:**
- Produces: 5개 라우트(`/login`, `/register`, `/`, `/cart`, `/product/[id]`)가 각각 플레이스홀더 텍스트를 렌더링하는 동작하는 라우팅 뼈대

- [ ] **Step 1: Expo Router 및 필수 패키지 설치**

```bash
cd /Users/jang-yelim/Desktop/palette-app
npx expo install expo-router expo-secure-store expo-constants expo-linking react-native-screens react-native-safe-area-context react-native-gesture-handler react-native-reanimated
```

Expected: `package.json`의 `dependencies`에 위 패키지들이 SDK 56과 호환되는 버전으로 추가됨 (예: `expo-router` `56.x`)

- [ ] **Step 2: package.json main 엔트리 변경**

`package.json`의 `"main"` 필드를 다음과 같이 수정:

```json
"main": "expo-router/entry",
```

- [ ] **Step 3: app.json에 expo-router 설정 추가**

`app.json`의 `"expo"` 객체에 다음 키를 추가 (기존 `ios`/`android`/`web` 키는 유지):

```json
{
  "expo": {
    "name": "palette-app",
    "slug": "palette-app",
    "version": "1.0.0",
    "orientation": "portrait",
    "icon": "./assets/icon.png",
    "userInterfaceStyle": "light",
    "scheme": "paletteapp",
    "plugins": ["expo-router"],
    "extra": {
      "apiBaseUrl": null
    },
    "ios": {
      "supportsTablet": true
    },
    "android": {
      "adaptiveIcon": {
        "backgroundColor": "#E6F4FE",
        "foregroundImage": "./assets/android-icon-foreground.png",
        "backgroundImage": "./assets/android-icon-background.png",
        "monochromeImage": "./assets/android-icon-monochrome.png"
      }
    },
    "web": {
      "favicon": "./assets/favicon.png",
      "bundler": "metro"
    }
  }
}
```

- [ ] **Step 4: 기존 진입점 삭제**

```bash
cd /Users/jang-yelim/Desktop/palette-app
rm App.js index.js
```

- [ ] **Step 5: 루트 레이아웃 작성 (임시 Slot)**

`app/_layout.js`:

```js
import { Slot } from 'expo-router';

export default function RootLayout() {
  return <Slot />;
}
```

- [ ] **Step 6: (auth) 라우트 그룹 작성**

`app/(auth)/_layout.js`:

```js
import { Stack } from 'expo-router';

export default function AuthLayout() {
  return <Stack screenOptions={{ headerShown: false }} />;
}
```

`app/(auth)/login.js`:

```js
import { Text, View } from 'react-native';

export default function LoginScreen() {
  return (
    <View style={{ flex: 1, alignItems: 'center', justifyContent: 'center' }}>
      <Text>로그인 화면</Text>
    </View>
  );
}
```

`app/(auth)/register.js`:

```js
import { Text, View } from 'react-native';

export default function RegisterScreen() {
  return (
    <View style={{ flex: 1, alignItems: 'center', justifyContent: 'center' }}>
      <Text>회원가입 화면</Text>
    </View>
  );
}
```

- [ ] **Step 7: (tabs) 라우트 그룹 작성**

`app/(tabs)/_layout.js`:

```js
import { Tabs } from 'expo-router';

export default function TabsLayout() {
  return (
    <Tabs>
      <Tabs.Screen name="index" options={{ title: '홈' }} />
      <Tabs.Screen name="cart" options={{ title: '장바구니' }} />
      <Tabs.Screen name="product/[id]" options={{ href: null, title: '상품 상세' }} />
    </Tabs>
  );
}
```

`app/(tabs)/index.js`:

```js
import { Text, View } from 'react-native';

export default function HomeScreen() {
  return (
    <View style={{ flex: 1, alignItems: 'center', justifyContent: 'center' }}>
      <Text>홈</Text>
    </View>
  );
}
```

`app/(tabs)/cart.js`:

```js
import { Text, View } from 'react-native';

export default function CartScreen() {
  return (
    <View style={{ flex: 1, alignItems: 'center', justifyContent: 'center' }}>
      <Text>장바구니</Text>
    </View>
  );
}
```

`app/(tabs)/product/[id].js`:

```js
import { Text, View } from 'react-native';
import { useLocalSearchParams } from 'expo-router';

export default function ProductDetailScreen() {
  const { id } = useLocalSearchParams();
  return (
    <View style={{ flex: 1, alignItems: 'center', justifyContent: 'center' }}>
      <Text>상품 상세 (id: {id})</Text>
    </View>
  );
}
```

- [ ] **Step 8: 실행 확인**

```bash
cd /Users/jang-yelim/Desktop/palette-app
npx expo start --web
```

Expected: 번들링 에러 없이 브라우저가 열리고 "홈" 텍스트가 표시됨 (기본 라우트는 `(tabs)/index.js`). URL에 `/cart`, `/login`, `/product/1`을 직접 입력해 각각 "장바구니", "로그인 화면", "상품 상세 (id: 1)"이 표시되는지 확인. 확인 후 서버 종료(Ctrl+C).

- [ ] **Step 9: Commit**

```bash
cd /Users/jang-yelim/Desktop/palette-app
git add app.json package.json package-lock.json App.js index.js app/
git commit -m "feat: Expo Router 설치 및 라우트 뼈대 구성"
```

---

## Task 2: API 클라이언트 + 인증 컨텍스트

**Files:**
- Create: `src/api/client.js`
- Create: `src/context/AuthContext.js`
- Modify: `app/_layout.js`

**Interfaces:**
- Consumes: 없음 (Task 1의 라우트 뼈대만 사용)
- Produces:
  - `apiFetch(path, options) -> Promise<any>` — 인증 헤더 자동 첨부, 에러 시 `ApiError` throw
  - `ApiError { status, data, message }` — `message`는 문자열/배열 detail을 모두 정규화한 사람이 읽을 문자열
  - `setAuthToken(token)`, `setUnauthorizedHandler(fn)`
  - `useAuth() -> { token, isReady, login(token), logout() }` (Task 3 이후 화면에서 사용)

- [ ] **Step 1: API 클라이언트 작성**

`src/api/client.js`:

```js
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
```

- [ ] **Step 2: 인증 컨텍스트 작성**

`src/context/AuthContext.js`:

```js
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
```

- [ ] **Step 3: 루트 레이아웃에 인증 리다이렉트 연결**

`app/_layout.js`:

```js
import { useEffect } from 'react';
import { Slot, useRouter, useSegments } from 'expo-router';
import { AuthProvider, useAuth } from '../src/context/AuthContext';

function RootNavigation() {
  const { token, isReady } = useAuth();
  const segments = useSegments();
  const router = useRouter();

  useEffect(() => {
    if (!isReady) return;
    const inAuthGroup = segments[0] === '(auth)';
    if (!token && !inAuthGroup) {
      router.replace('/login');
    } else if (token && inAuthGroup) {
      router.replace('/');
    }
  }, [token, isReady, segments]);

  if (!isReady) return null;
  return <Slot />;
}

export default function RootLayout() {
  return (
    <AuthProvider>
      <RootNavigation />
    </AuthProvider>
  );
}
```

- [ ] **Step 4: 리다이렉트 동작 확인**

```bash
cd /Users/jang-yelim/Desktop/palette-app
npx expo start --web
```

Expected: 저장된 토큰이 없으므로 앱 진입 시 자동으로 `/login`으로 리다이렉트되어 "로그인 화면" 텍스트가 표시됨 (기본 라우트 `(tabs)/index.js`로 직접 접근을 시도해도 `/login`으로 튕겨나감). 확인 후 서버 종료.

- [ ] **Step 5: Commit**

```bash
cd /Users/jang-yelim/Desktop/palette-app
git add src/api/client.js src/context/AuthContext.js app/_layout.js
git commit -m "feat: API 클라이언트 및 인증 컨텍스트 추가, 로그인 상태 라우트 가드"
```

---

## Task 3: 로그인 / 회원가입 화면

**Files:**
- Create: `src/api/auth.js`
- Modify: `app/(auth)/login.js`
- Modify: `app/(auth)/register.js`

**Interfaces:**
- Consumes: `apiFetch`, `ApiError` (Task 2), `useAuth()` (Task 2)
- Produces:
  - `login(email, password) -> Promise<{access_token, token_type}>`
  - `register(name, email, password) -> Promise<{id, name, email}>`

- [ ] **Step 1: 인증 API 함수 작성**

`src/api/auth.js`:

```js
import { apiFetch } from './client';

export function login(email, password) {
  return apiFetch('/auth/login', {
    method: 'POST',
    body: JSON.stringify({ email, password }),
  });
}

export function register(name, email, password) {
  return apiFetch('/auth/register', {
    method: 'POST',
    body: JSON.stringify({ name, email, password }),
  });
}
```

- [ ] **Step 2: 로그인 화면 작성**

`app/(auth)/login.js`:

```js
import { useState } from 'react';
import { View, Text, TextInput, Button, StyleSheet, Alert, Pressable } from 'react-native';
import { Link } from 'expo-router';
import { login } from '../../src/api/auth';
import { ApiError } from '../../src/api/client';
import { useAuth } from '../../src/context/AuthContext';

export default function LoginScreen() {
  const { login: setAuthenticated } = useAuth();
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [submitting, setSubmitting] = useState(false);

  const handleSubmit = async () => {
    setSubmitting(true);
    try {
      const result = await login(email, password);
      await setAuthenticated(result.access_token);
    } catch (err) {
      const message = err instanceof ApiError ? err.message : '로그인에 실패했습니다.';
      Alert.alert('로그인 실패', message);
    } finally {
      setSubmitting(false);
    }
  };

  return (
    <View style={styles.container}>
      <Text style={styles.title}>로그인</Text>
      <TextInput
        style={styles.input}
        placeholder="이메일"
        autoCapitalize="none"
        keyboardType="email-address"
        value={email}
        onChangeText={setEmail}
      />
      <TextInput
        style={styles.input}
        placeholder="비밀번호"
        secureTextEntry
        value={password}
        onChangeText={setPassword}
      />
      <Button title={submitting ? '로그인 중...' : '로그인'} onPress={handleSubmit} disabled={submitting} />
      <Link href="/register" asChild>
        <Pressable style={styles.link}>
          <Text>계정이 없으신가요? 회원가입</Text>
        </Pressable>
      </Link>
    </View>
  );
}

const styles = StyleSheet.create({
  container: { flex: 1, justifyContent: 'center', padding: 24 },
  title: { fontSize: 24, fontWeight: '700', marginBottom: 24, textAlign: 'center' },
  input: { borderWidth: 1, borderColor: '#ccc', borderRadius: 8, padding: 12, marginBottom: 12 },
  link: { marginTop: 16, alignItems: 'center' },
});
```

- [ ] **Step 3: 회원가입 화면 작성**

`app/(auth)/register.js`:

```js
import { useState } from 'react';
import { View, Text, TextInput, Button, StyleSheet, Alert, Pressable } from 'react-native';
import { Link } from 'expo-router';
import { register, login } from '../../src/api/auth';
import { ApiError } from '../../src/api/client';
import { useAuth } from '../../src/context/AuthContext';

export default function RegisterScreen() {
  const { login: setAuthenticated } = useAuth();
  const [name, setName] = useState('');
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [submitting, setSubmitting] = useState(false);

  const handleSubmit = async () => {
    setSubmitting(true);
    try {
      await register(name, email, password);
      const result = await login(email, password);
      await setAuthenticated(result.access_token);
    } catch (err) {
      const message = err instanceof ApiError ? err.message : '회원가입에 실패했습니다.';
      Alert.alert('회원가입 실패', message);
    } finally {
      setSubmitting(false);
    }
  };

  return (
    <View style={styles.container}>
      <Text style={styles.title}>회원가입</Text>
      <TextInput style={styles.input} placeholder="이름" value={name} onChangeText={setName} />
      <TextInput
        style={styles.input}
        placeholder="이메일"
        autoCapitalize="none"
        keyboardType="email-address"
        value={email}
        onChangeText={setEmail}
      />
      <TextInput
        style={styles.input}
        placeholder="비밀번호 (8자 이상)"
        secureTextEntry
        value={password}
        onChangeText={setPassword}
      />
      <Button title={submitting ? '가입 중...' : '회원가입'} onPress={handleSubmit} disabled={submitting} />
      <Link href="/login" asChild>
        <Pressable style={styles.link}>
          <Text>이미 계정이 있으신가요? 로그인</Text>
        </Pressable>
      </Link>
    </View>
  );
}

const styles = StyleSheet.create({
  container: { flex: 1, justifyContent: 'center', padding: 24 },
  title: { fontSize: 24, fontWeight: '700', marginBottom: 24, textAlign: 'center' },
  input: { borderWidth: 1, borderColor: '#ccc', borderRadius: 8, padding: 12, marginBottom: 12 },
  link: { marginTop: 16, alignItems: 'center' },
});
```

- [ ] **Step 4: 백엔드 실행 후 동작 확인**

```bash
cd /Users/jang-yelim/Desktop/palette-app/backend
source venv/bin/activate
uvicorn main:app --reload --port 8000
```

새 터미널에서:

```bash
cd /Users/jang-yelim/Desktop/palette-app
npx expo start --web
```

Expected:
- 회원가입 화면에서 이름(한글/영문만)/이메일/8자 이상 비밀번호 입력 후 제출 → 자동 로그인되어 홈 화면("홈" 텍스트)으로 이동
- 같은 이메일로 다시 회원가입 시도 → "이미 사용 중인 이메일입니다." 알럿
- 로그인 화면에서 틀린 비밀번호 3회 입력 → 계정 잠금 메시지("비밀번호를 3회 이상 틀렸습니다...") 알럿

확인 후 두 서버 모두 종료(Ctrl+C).

- [ ] **Step 5: Commit**

```bash
cd /Users/jang-yelim/Desktop/palette-app
git add src/api/auth.js "app/(auth)/login.js" "app/(auth)/register.js"
git commit -m "feat: 로그인/회원가입 화면 구현 및 API 연동"
```

---

## Task 4: 홈 화면 — 이미지 업로드 → 색상 추천 → 상품 그리드

**Files:**
- Create: `src/api/colors.js`
- Create: `src/api/products.js`
- Modify: `app/(tabs)/index.js`

**Interfaces:**
- Consumes: `apiFetch`, `ApiError` (Task 2)
- Produces:
  - `extractColor(imageAsset) -> Promise<{extracted_color, recommendations: [{color_name, hex}]}>`
  - `getProductsByColor(hex) -> Promise<{total, page, limit, total_pages, items: [...]}>`
  - `getProduct(id) -> Promise<ProductResponse>` (Task 5에서 사용)

- [ ] **Step 1: 색상 추출 API 함수 작성**

`src/api/colors.js`:

```js
import { apiFetch } from './client';

export function extractColor(imageAsset) {
  const formData = new FormData();
  formData.append('file', {
    uri: imageAsset.uri,
    name: imageAsset.fileName || 'photo.jpg',
    type: imageAsset.mimeType || 'image/jpeg',
  });
  return apiFetch('/colors/extract', {
    method: 'POST',
    body: formData,
  });
}
```

- [ ] **Step 2: 상품 조회 API 함수 작성**

`src/api/products.js`:

```js
import { apiFetch } from './client';

export function getProductsByColor(hex) {
  return apiFetch(`/products?color=${encodeURIComponent(hex)}&limit=20`);
}

export function getProduct(id) {
  return apiFetch(`/products/${id}`);
}
```

- [ ] **Step 3: 홈 화면 작성**

`app/(tabs)/index.js`:

```js
import { useCallback, useState } from 'react';
import {
  View,
  Text,
  Button,
  FlatList,
  Image,
  StyleSheet,
  ActivityIndicator,
  Alert,
  Pressable,
} from 'react-native';
import * as ImagePicker from 'expo-image-picker';
import { useRouter } from 'expo-router';
import { extractColor } from '../../src/api/colors';
import { getProductsByColor } from '../../src/api/products';
import { ApiError } from '../../src/api/client';

export default function HomeScreen() {
  const router = useRouter();
  const [imageUri, setImageUri] = useState(null);
  const [loading, setLoading] = useState(false);
  const [sections, setSections] = useState([]);

  const handleResult = useCallback(async (asset) => {
    setImageUri(asset.uri);
    setLoading(true);
    setSections([]);
    try {
      const result = await extractColor(asset);
      const withProducts = await Promise.all(
        result.recommendations.map(async (rec) => {
          const productPage = await getProductsByColor(rec.hex);
          return { ...rec, products: productPage.items };
        })
      );
      setSections(withProducts);
    } catch (err) {
      const message = err instanceof ApiError ? err.message : '이미지 처리 중 오류가 발생했습니다.';
      Alert.alert('오류', message);
    } finally {
      setLoading(false);
    }
  }, []);

  const pickFromGallery = async () => {
    const permission = await ImagePicker.requestMediaLibraryPermissionsAsync();
    if (!permission.granted) {
      Alert.alert('권한 필요', '갤러리 접근 권한이 필요합니다.');
      return;
    }
    const result = await ImagePicker.launchImageLibraryAsync({ quality: 0.8 });
    if (!result.canceled) {
      handleResult(result.assets[0]);
    }
  };

  const takePhoto = async () => {
    const permission = await ImagePicker.requestCameraPermissionsAsync();
    if (!permission.granted) {
      Alert.alert('권한 필요', '카메라 접근 권한이 필요합니다.');
      return;
    }
    const result = await ImagePicker.launchCameraAsync({ quality: 0.8 });
    if (!result.canceled) {
      handleResult(result.assets[0]);
    }
  };

  return (
    <View style={styles.container}>
      <View style={styles.buttonRow}>
        <Button title="사진 촬영" onPress={takePhoto} />
        <Button title="갤러리에서 선택" onPress={pickFromGallery} />
      </View>
      {imageUri && <Image source={{ uri: imageUri }} style={styles.preview} />}
      {loading && <ActivityIndicator size="large" style={styles.loading} />}
      <FlatList
        data={sections}
        keyExtractor={(item) => item.hex}
        renderItem={({ item }) => (
          <View style={styles.section}>
            <View style={styles.sectionHeader}>
              <View style={[styles.swatch, { backgroundColor: item.hex }]} />
              <Text style={styles.sectionTitle}>{item.color_name}</Text>
            </View>
            <FlatList
              data={item.products}
              horizontal
              keyExtractor={(p) => String(p.id)}
              renderItem={({ item: product }) => (
                <Pressable
                  style={styles.productCard}
                  onPress={() => router.push(`/product/${product.id}`)}
                >
                  <View style={[styles.productSwatch, { backgroundColor: product.hex }]} />
                  <Text numberOfLines={1}>{product.name}</Text>
                  <Text>{product.price.toLocaleString()}원</Text>
                </Pressable>
              )}
            />
          </View>
        )}
      />
    </View>
  );
}

const styles = StyleSheet.create({
  container: { flex: 1, padding: 16 },
  buttonRow: { flexDirection: 'row', justifyContent: 'space-around', marginBottom: 12 },
  preview: { width: 120, height: 120, borderRadius: 8, alignSelf: 'center', marginBottom: 12 },
  loading: { marginVertical: 12 },
  section: { marginBottom: 20 },
  sectionHeader: { flexDirection: 'row', alignItems: 'center', marginBottom: 8 },
  swatch: { width: 20, height: 20, borderRadius: 10, marginRight: 8 },
  sectionTitle: { fontSize: 16, fontWeight: '600' },
  productCard: { width: 100, marginRight: 12 },
  productSwatch: { width: 100, height: 100, borderRadius: 8, marginBottom: 4 },
});
```

- [ ] **Step 4: 동작 확인**

백엔드(`uvicorn main:app --reload --port 8000`)를 실행한 채로:

```bash
cd /Users/jang-yelim/Desktop/palette-app
npx expo start
```

Expo Go 앱(iOS/Android 실기기 또는 시뮬레이터)으로 접속해 로그인 후 확인:
- "사진 촬영" 또는 "갤러리에서 선택"으로 이미지 선택 → 로딩 인디케이터 표시 후 추천 색상 5개 섹션과 각 색상별 상품 가로 스크롤 목록이 나타남
- 10MB 초과 이미지나 지원하지 않는 형식을 선택하면 알럿으로 에러 메시지 표시 (413/415/422)

확인 후 서버 종료.

- [ ] **Step 5: Commit**

```bash
cd /Users/jang-yelim/Desktop/palette-app
git add src/api/colors.js src/api/products.js "app/(tabs)/index.js"
git commit -m "feat: 홈 화면 - 이미지 업로드 색상추천 및 상품 그리드 구현"
```

---

## Task 5: 상품 상세 + 장바구니 담기

**Files:**
- Create: `src/api/cart.js`
- Modify: `app/(tabs)/product/[id].js`

**Interfaces:**
- Consumes: `apiFetch`, `ApiError` (Task 2), `getProduct` (Task 4)
- Produces:
  - `getCart() -> Promise<CartItemResponse[]>` (Task 6에서 사용)
  - `addToCart(productId) -> Promise<CartItemResponse>`
  - `removeFromCart(cartId) -> Promise<null>` (Task 6에서 사용)

- [ ] **Step 1: 장바구니 API 함수 작성**

`src/api/cart.js`:

```js
import { apiFetch } from './client';

export function getCart() {
  return apiFetch('/cart');
}

export function addToCart(productId) {
  return apiFetch('/cart', {
    method: 'POST',
    body: JSON.stringify({ product_id: productId }),
  });
}

export function removeFromCart(cartId) {
  return apiFetch(`/cart/${cartId}`, { method: 'DELETE' });
}
```

- [ ] **Step 2: 상품 상세 화면 작성**

`app/(tabs)/product/[id].js`:

```js
import { useEffect, useState } from 'react';
import { View, Text, Button, StyleSheet, ActivityIndicator, Alert } from 'react-native';
import { useLocalSearchParams } from 'expo-router';
import { getProduct } from '../../../src/api/products';
import { addToCart } from '../../../src/api/cart';
import { ApiError } from '../../../src/api/client';

export default function ProductDetailScreen() {
  const { id } = useLocalSearchParams();
  const [product, setProduct] = useState(null);
  const [loading, setLoading] = useState(true);
  const [adding, setAdding] = useState(false);

  useEffect(() => {
    getProduct(id)
      .then(setProduct)
      .catch(() => Alert.alert('오류', '상품 정보를 불러오지 못했습니다.'))
      .finally(() => setLoading(false));
  }, [id]);

  const handleAddToCart = async () => {
    setAdding(true);
    try {
      await addToCart(Number(id));
      Alert.alert('완료', '장바구니에 담았습니다.');
    } catch (err) {
      const message = err instanceof ApiError ? err.message : '장바구니 담기에 실패했습니다.';
      Alert.alert('오류', message);
    } finally {
      setAdding(false);
    }
  };

  if (loading) return <ActivityIndicator size="large" style={styles.center} />;
  if (!product) return null;

  return (
    <View style={styles.container}>
      <View style={[styles.swatch, { backgroundColor: product.hex }]} />
      <Text style={styles.name}>{product.name}</Text>
      <Text>{product.color_name}</Text>
      <Text>
        {product.gender} · {product.category} · {product.subcategory}
      </Text>
      <Text style={styles.price}>{product.price.toLocaleString()}원</Text>
      <Button
        title={adding ? '담는 중...' : '장바구니 담기'}
        onPress={handleAddToCart}
        disabled={adding}
      />
    </View>
  );
}

const styles = StyleSheet.create({
  container: { flex: 1, padding: 16 },
  center: { flex: 1, justifyContent: 'center' },
  swatch: { width: '100%', height: 160, borderRadius: 8, marginBottom: 16 },
  name: { fontSize: 20, fontWeight: '700', marginBottom: 4 },
  price: { fontSize: 18, fontWeight: '600', marginVertical: 12 },
});
```

- [ ] **Step 3: 동작 확인**

백엔드 실행 후 앱에서 홈 화면 → 상품 카드 탭 → 상세 화면에 이름/색상/가격 표시 확인 → "장바구니 담기" 탭 → "완료" 알럿 확인.

- [ ] **Step 4: Commit**

```bash
cd /Users/jang-yelim/Desktop/palette-app
git add src/api/cart.js "app/(tabs)/product/[id].js"
git commit -m "feat: 상품 상세 화면 및 장바구니 담기 구현"
```

---

## Task 6: 장바구니 화면 + 로그아웃

**Files:**
- Modify: `app/(tabs)/cart.js`

**Interfaces:**
- Consumes: `getCart`, `removeFromCart` (Task 5), `useAuth` (Task 2)

- [ ] **Step 1: 장바구니 화면 작성**

`app/(tabs)/cart.js`:

```js
import { useCallback, useState } from 'react';
import { View, Text, FlatList, Pressable, StyleSheet, Button, Alert } from 'react-native';
import { useFocusEffect, useRouter } from 'expo-router';
import { getCart, removeFromCart } from '../../src/api/cart';
import { useAuth } from '../../src/context/AuthContext';

export default function CartScreen() {
  const router = useRouter();
  const { logout } = useAuth();
  const [items, setItems] = useState([]);

  useFocusEffect(
    useCallback(() => {
      getCart()
        .then(setItems)
        .catch(() => Alert.alert('오류', '장바구니를 불러오지 못했습니다.'));
    }, [])
  );

  const handleRemove = async (cartId) => {
    try {
      await removeFromCart(cartId);
      setItems((prev) => prev.filter((item) => item.id !== cartId));
    } catch {
      Alert.alert('오류', '삭제에 실패했습니다.');
    }
  };

  const handleLogout = async () => {
    await logout();
    router.replace('/login');
  };

  return (
    <View style={styles.container}>
      <Button title="로그아웃" onPress={handleLogout} />
      <FlatList
        data={items}
        keyExtractor={(item) => String(item.id)}
        renderItem={({ item }) => (
          <View style={styles.row}>
            <View style={[styles.swatch, { backgroundColor: item.product.hex }]} />
            <View style={styles.info}>
              <Text>{item.product.name}</Text>
              <Text>{item.product.price.toLocaleString()}원</Text>
            </View>
            <Pressable onPress={() => handleRemove(item.id)}>
              <Text style={styles.remove}>삭제</Text>
            </Pressable>
          </View>
        )}
        ListEmptyComponent={<Text style={styles.empty}>장바구니가 비어있습니다.</Text>}
      />
    </View>
  );
}

const styles = StyleSheet.create({
  container: { flex: 1, padding: 16 },
  row: {
    flexDirection: 'row',
    alignItems: 'center',
    paddingVertical: 12,
    borderBottomWidth: 1,
    borderColor: '#eee',
  },
  swatch: { width: 48, height: 48, borderRadius: 8, marginRight: 12 },
  info: { flex: 1 },
  remove: { color: '#c33' },
  empty: { textAlign: 'center', marginTop: 40, color: '#888' },
});
```

- [ ] **Step 2: 동작 확인**

백엔드 실행 후 앱에서: 장바구니 탭 진입 시 담은 상품 목록 표시 → "삭제" 탭 시 목록에서 즉시 제거 확인 → "로그아웃" 탭 → 로그인 화면으로 이동 확인 → 앱 재시작(Expo Go 완전 종료 후 재실행) 시 로그인 상태가 유지되는지(자동로그인) 확인, 로그아웃 후 재시작 시에는 로그인 화면부터 시작하는지 확인.

- [ ] **Step 3: Commit**

```bash
cd /Users/jang-yelim/Desktop/palette-app
git add "app/(tabs)/cart.js"
git commit -m "feat: 장바구니 화면 및 로그아웃 구현"
```

---

## 완료 기준 (Phase 2)

- [ ] `npx expo start`로 실행, iOS/Android(Expo Go 또는 시뮬레이터)에서 아래 흐름 확인
  - [ ] 로그인 → 홈 탭 진입, 회원가입 → 자동 로그인 → 홈 탭 진입
  - [ ] 홈에서 카메라 촬영 / 갤러리 선택 둘 다로 이미지 업로드 → 추천 색상 5개 + 각 색상별 상품 그리드 표시
  - [ ] 상품 탭 → 상세 화면 → 장바구니 담기 → 장바구니 탭에서 확인
  - [ ] 장바구니 항목 삭제 정상 동작
  - [ ] 로그아웃 → 로그인 화면 이동, 앱 재실행 시 로그인 유지(자동로그인) 확인
  - [ ] 401(토큰만료)/423(계정잠금)/409(중복이메일)/422(유효성검증)/413·415(이미지오류)/네트워크 오류 각각 의도한 대로 알럿 표시

---

## 다음 단계

- **Phase 3:** 웹 앱 (React)
- **Phase 4:** QA 자동화 테스트 (Postman/Newman, Appium, Selenium)
