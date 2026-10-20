import { useState } from 'react';
import { View, Text, TextInput, StyleSheet, Alert, Pressable } from 'react-native';
import { Link } from 'expo-router';
import { register, login } from '../../src/api/auth';
import { ApiError } from '../../src/api/client';
import { useAuth } from '../../src/context/AuthContext';
import Logo from '../../src/components/Logo';
import AppButton from '../../src/components/AppButton';
import { colors, radius } from '../../src/theme';

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
      if (err instanceof ApiError && err.handled) return;
      const message = err instanceof ApiError ? err.message : '회원가입에 실패했습니다.';
      Alert.alert('회원가입 실패', message);
    } finally {
      setSubmitting(false);
    }
  };

  return (
    <View style={styles.container}>
      <Link href="/" replace asChild>
        <Pressable style={styles.back} hitSlop={8}>
          <Text style={styles.backText}>← 둘러보기</Text>
        </Pressable>
      </Link>
      <View style={styles.logo}>
        <Logo size={32} />
      </View>
      <Text style={styles.title}>회원가입</Text>
      <TextInput style={styles.input} placeholderTextColor="#A0A09B" placeholder="이름" value={name} onChangeText={setName} />
      <TextInput
        style={styles.input}
        placeholderTextColor="#A0A09B"
        placeholder="이메일"
        autoCapitalize="none"
        keyboardType="email-address"
        value={email}
        onChangeText={setEmail}
      />
      <TextInput
        style={styles.input}
        placeholderTextColor="#A0A09B"
        placeholder="비밀번호 (8자 이상)"
        secureTextEntry
        value={password}
        onChangeText={setPassword}
      />
      <AppButton title={submitting ? '가입 중...' : '회원가입'} onPress={handleSubmit} disabled={submitting} style={styles.submit} />
      <Link href="/login" asChild>
        <Pressable style={styles.link}>
          <Text style={styles.linkText}>이미 계정이 있으신가요? 로그인</Text>
        </Pressable>
      </Link>
    </View>
  );
}

const styles = StyleSheet.create({
  container: { flex: 1, justifyContent: 'center', padding: 24, backgroundColor: colors.background },
  title: { fontSize: 24, fontWeight: '800', color: colors.text, marginBottom: 28, textAlign: 'center' },
  input: {
    height: 52,
    backgroundColor: colors.surface,
    borderRadius: radius.md,
    paddingHorizontal: 16,
    fontSize: 16,
    color: colors.text,
    marginBottom: 12,
  },
  submit: { marginTop: 8 },
  link: { marginTop: 20, alignItems: 'center' },
  linkText: { fontSize: 14, color: colors.subtext },
  back: { position: 'absolute', top: 56, left: 24 },
  backText: { fontSize: 15, color: colors.subtext, fontWeight: '600' },
  logo: { marginBottom: 32 },
});
