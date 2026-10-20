import { useEffect, useRef, useState } from 'react';
import { Animated, StyleSheet, View } from 'react-native';
import { Slot, useRouter, useSegments } from 'expo-router';
import { AuthProvider, useAuth } from '../src/context/AuthContext';
import { RecommendationProvider } from '../src/context/RecommendationContext';
import Logo from '../src/components/Logo';
import { colors } from '../src/theme';

const SPLASH_DURATION_MS = 1200;
const SPLASH_FADE_MS = 300;

function SplashOverlay({ onFinish }) {
  const opacity = useRef(new Animated.Value(1)).current;

  useEffect(() => {
    const timer = setTimeout(() => {
      Animated.timing(opacity, {
        toValue: 0,
        duration: SPLASH_FADE_MS,
        useNativeDriver: true,
      }).start(onFinish);
    }, SPLASH_DURATION_MS);
    return () => clearTimeout(timer);
  }, [opacity, onFinish]);

  return (
    <Animated.View style={[styles.splash, { opacity }]}>
      <Logo size={52} />
    </Animated.View>
  );
}

function RootNavigation() {
  const { token, isReady } = useAuth();
  const segments = useSegments();
  const router = useRouter();
  const [showSplash, setShowSplash] = useState(true);
  const startedRef = useRef(false);

  useEffect(() => {
    if (!isReady) return;
    // 앱을 처음 열면 항상 홈에서 시작한다 (이전에 보던 로그인 화면이 복원되지 않도록)
    if (!startedRef.current) {
      startedRef.current = true;
      if (segments[0] === '(auth)') router.replace('/');
      return;
    }
    // 로그인/회원가입을 마치면 홈으로 돌아간다
    if (token && segments[0] === '(auth)') {
      router.replace('/');
    }
  }, [token, isReady, segments]);

  return (
    <View style={styles.root}>
      {isReady && <Slot />}
      {showSplash && <SplashOverlay onFinish={() => setShowSplash(false)} />}
    </View>
  );
}

export default function RootLayout() {
  return (
    <AuthProvider>
      <RecommendationProvider>
        <RootNavigation />
      </RecommendationProvider>
    </AuthProvider>
  );
}

const styles = StyleSheet.create({
  root: { flex: 1, backgroundColor: colors.background },
  splash: {
    ...StyleSheet.absoluteFillObject,
    backgroundColor: colors.background,
    alignItems: 'center',
    justifyContent: 'center',
  },
});
