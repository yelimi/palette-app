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
