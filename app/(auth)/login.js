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
