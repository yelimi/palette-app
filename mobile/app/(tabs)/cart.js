import { useCallback, useState } from 'react';
import { View, Text, FlatList, Pressable, StyleSheet, Alert } from 'react-native';
import { useFocusEffect } from 'expo-router';
import { getCart, removeFromCart } from '../../src/api/cart';
import { ApiError } from '../../src/api/client';
import { Ionicons } from '@expo/vector-icons';
import { colors, radius, shadow } from '../../src/theme';

export default function CartScreen() {
  const [items, setItems] = useState([]);

  useFocusEffect(
    useCallback(() => {
      getCart()
        .then(setItems)
        .catch((err) => {
          if (err instanceof ApiError && err.handled) return;
          const message = err instanceof ApiError ? err.message : '장바구니를 불러오지 못했습니다.';
          Alert.alert('오류', message);
        });
    }, [])
  );

  const handleRemove = async (cartId) => {
    try {
      await removeFromCart(cartId);
      setItems((prev) => prev.filter((item) => item.id !== cartId));
    } catch (err) {
      if (err instanceof ApiError && err.handled) return;
      const message = err instanceof ApiError ? err.message : '삭제에 실패했습니다.';
      Alert.alert('오류', message);
    }
  };

  const total = items.reduce((sum, item) => sum + item.product.price, 0);

  return (
    <View style={styles.container}>
      <FlatList
        data={items}
        keyExtractor={(item) => String(item.id)}
        contentContainerStyle={styles.list}
        renderItem={({ item }) => (
          <View style={styles.row}>
            <View style={[styles.swatch, { backgroundColor: item.product.hex }]} />
            <View style={styles.info}>
              <Text style={styles.name} numberOfLines={1}>{item.product.name}</Text>
              <Text style={styles.meta}>{item.product.color_name}</Text>
              <Text style={styles.price}>{item.product.price.toLocaleString()}원</Text>
            </View>
            <Pressable onPress={() => handleRemove(item.id)} hitSlop={8}>
              <Ionicons name="close" size={20} color={colors.subtext} />
            </Pressable>
          </View>
        )}
        ListEmptyComponent={
          <View style={styles.emptyBox}>
            <Ionicons name="bag-outline" size={52} color="#B5B5B0" />
            <Text style={styles.empty}>장바구니가 비어있습니다.</Text>
          </View>
        }
      />
      {items.length > 0 && (
        <View style={styles.footer}>
          <Text style={styles.totalLabel}>총 {items.length}개</Text>
          <Text style={styles.total}>{total.toLocaleString()}원</Text>
        </View>
      )}
    </View>
  );
}

const styles = StyleSheet.create({
  container: { flex: 1 },
  list: { padding: 20, flexGrow: 1 },
  row: {
    flexDirection: 'row',
    alignItems: 'center',
    backgroundColor: colors.background,
    borderRadius: radius.md,
    padding: 12,
    marginBottom: 12,
    ...shadow,
  },
  swatch: { width: 64, height: 64, borderRadius: radius.sm, marginRight: 14 },
  info: { flex: 1 },
  name: { fontSize: 15, fontWeight: '700', color: colors.text },
  meta: { fontSize: 13, color: colors.subtext, marginTop: 2 },
  price: { fontSize: 15, fontWeight: '800', color: colors.text, marginTop: 6 },
  emptyBox: { flex: 1, alignItems: 'center', justifyContent: 'center', paddingTop: 80 },
  empty: { textAlign: 'center', marginTop: 12, fontSize: 15, color: colors.subtext },
  footer: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'center',
    padding: 20,
    borderTopWidth: 1,
    borderTopColor: colors.border,
  },
  totalLabel: { fontSize: 15, color: colors.subtext, fontWeight: '600' },
  total: { fontSize: 20, fontWeight: '800', color: colors.text },
});
