import { View, Text, Pressable, StyleSheet } from 'react-native';
import { useRouter } from 'expo-router';
import { Ionicons } from '@expo/vector-icons';
import { useAuth } from '../../src/context/AuthContext';
import Logo from '../../src/components/Logo';
import AppButton from '../../src/components/AppButton';
import { colors, radius } from '../../src/theme';

function MenuItem({ icon, label, onPress }) {
  return (
    <Pressable style={styles.menuItem} onPress={onPress}>
      <Ionicons name={icon} size={22} color={colors.text} />
      <Text style={styles.menuLabel}>{label}</Text>
      <Ionicons name="chevron-forward" size={18} color="#B5B5B0" />
    </Pressable>
  );
}

export default function MyScreen() {
  const router = useRouter();
  const { token, logout } = useAuth();

  if (!token) {
    return (
      <View style={styles.guest}>
        <Logo size={36} />
        <Text style={styles.guestTitle}>로그인하고 나에게 어울리는{'\n'}색을 찾아보세요</Text>
        <AppButton title="로그인" onPress={() => router.push('/login')} style={styles.guestButton} />
        <AppButton
          title="회원가입"
          variant="outline"
          onPress={() => router.push('/register')}
          style={styles.guestButton}
        />
      </View>
    );
  }

  const handleLogout = async () => {
    await logout();
    router.replace('/');
  };

  return (
    <View style={styles.container}>
      <View style={styles.profile}>
        <View style={styles.avatar}>
          <Ionicons name="person" size={28} color={colors.text} />
        </View>
        <Text style={styles.profileText}>반가워요!</Text>
      </View>
      <View style={styles.menu}>
        <MenuItem icon="color-palette-outline" label="최근 추천 보기" onPress={() => router.push('/recommend')} />
        <MenuItem icon="log-out-outline" label="로그아웃" onPress={handleLogout} />
      </View>
    </View>
  );
}

const styles = StyleSheet.create({
  guest: { flex: 1, alignItems: 'center', justifyContent: 'center', padding: 24 },
  guestTitle: { fontSize: 18, fontWeight: '700', color: colors.text, textAlign: 'center', lineHeight: 26, marginTop: 24, marginBottom: 32 },
  guestButton: { alignSelf: 'stretch', marginBottom: 10 },
  container: { flex: 1, padding: 20 },
  profile: { flexDirection: 'row', alignItems: 'center', backgroundColor: colors.surface, borderRadius: radius.md, padding: 20, marginBottom: 24 },
  avatar: { width: 52, height: 52, borderRadius: 26, backgroundColor: colors.accents[3], alignItems: 'center', justifyContent: 'center', marginRight: 16 },
  profileText: { fontSize: 18, fontWeight: '800', color: colors.text },
  menu: { borderRadius: radius.md, borderWidth: 1, borderColor: colors.border },
  menuItem: { flexDirection: 'row', alignItems: 'center', padding: 18, borderBottomWidth: 1, borderBottomColor: colors.border },
  menuLabel: { flex: 1, fontSize: 16, fontWeight: '600', color: colors.text, marginLeft: 14 },
});
