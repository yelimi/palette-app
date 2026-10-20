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
      const settled = await Promise.allSettled(
        result.recommendations.map(async (rec) => {
          const productPage = await getProductsByColor(rec.hex);
          return { ...rec, products: productPage.items };
        })
      );
      const withProducts = settled
        .filter((r) => r.status === 'fulfilled')
        .map((r) => r.value);
      const failedCount = settled.length - withProducts.length;
      setSections(withProducts);
      if (failedCount > 0 && withProducts.length === 0) {
        Alert.alert('오류', '상품을 불러오지 못했습니다. 다시 시도해주세요.');
      }
    } catch (err) {
      if (err instanceof ApiError && err.handled) return;
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
