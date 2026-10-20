import { useEffect, useState } from 'react';
import { View, Text, ScrollView, StyleSheet, ActivityIndicator, Alert } from 'react-native';
import { useLocalSearchParams } from 'expo-router';
import { getProduct } from '../../../src/api/products';
import { addToCart } from '../../../src/api/cart';
import { ApiError } from '../../../src/api/client';
import AppButton from '../../../src/components/AppButton';
import { colors, radius } from '../../../src/theme';

export default function ProductDetailScreen() {
  const { id } = useLocalSearchParams();
  const [product, setProduct] = useState(null);
  const [loading, setLoading] = useState(true);
  const [adding, setAdding] = useState(false);

  useEffect(() => {
    setLoading(true);
    setProduct(null);
    getProduct(id)
      .then(setProduct)
      .catch((err) => {
        if (err instanceof ApiError && err.handled) return;
        const message = err instanceof ApiError ? err.message : '상품 정보를 불러오지 못했습니다.';
        Alert.alert('오류', message);
      })
      .finally(() => setLoading(false));
  }, [id]);

  const handleAddToCart = async () => {
    setAdding(true);
    try {
      await addToCart(Number(id));
      Alert.alert('완료', '장바구니에 담았습니다.');
    } catch (err) {
      if (err instanceof ApiError && err.handled) return;
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
      <ScrollView contentContainerStyle={styles.scroll}>
        <View style={[styles.swatch, { backgroundColor: product.hex }]} />
        <View style={styles.body}>
          <Text style={styles.meta}>
            {product.gender} · {product.category} · {product.subcategory}
          </Text>
          <Text style={styles.name}>{product.name}</Text>
          <Text style={styles.price}>{product.price.toLocaleString()}원</Text>
          <View style={styles.colorRow}>
            <View style={[styles.colorDot, { backgroundColor: product.hex }]} />
            <Text style={styles.colorText}>
              {product.color_name} · {product.hex}
            </Text>
          </View>
        </View>
      </ScrollView>
      <View style={styles.footer}>
        <AppButton
          title={adding ? '담는 중...' : '장바구니 담기'}
          icon="bag-add-outline"
          onPress={handleAddToCart}
          disabled={adding}
        />
      </View>
    </View>
  );
}

const styles = StyleSheet.create({
  container: { flex: 1 },
  center: { flex: 1, justifyContent: 'center' },
  scroll: { paddingBottom: 24 },
  swatch: { height: 320 },
  body: { padding: 20 },
  meta: { fontSize: 13, color: colors.subtext },
  name: { fontSize: 22, fontWeight: '800', color: colors.text, marginTop: 6 },
  price: { fontSize: 22, fontWeight: '800', color: colors.text, marginTop: 12 },
  colorRow: { flexDirection: 'row', alignItems: 'center', backgroundColor: colors.surface, borderRadius: radius.md, padding: 14, marginTop: 20 },
  colorDot: { width: 22, height: 22, borderRadius: 11, marginRight: 10 },
  colorText: { fontSize: 14, fontWeight: '600', color: colors.text },
  footer: { padding: 20, borderTopWidth: 1, borderTopColor: colors.border },
});
