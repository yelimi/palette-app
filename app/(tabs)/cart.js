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
