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
      if (err instanceof ApiError && err.handled) return;
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
