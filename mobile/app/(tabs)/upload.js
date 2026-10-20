import { View, Text, Image, StyleSheet, ActivityIndicator, Alert, Pressable } from 'react-native';
import * as ImagePicker from 'expo-image-picker';
import { useRouter } from 'expo-router';
import { Ionicons } from '@expo/vector-icons';
import { useAuth } from '../../src/context/AuthContext';
import { useRecommendation } from '../../src/context/RecommendationContext';
import { promptLogin } from '../../src/components/promptLogin';
import AppButton from '../../src/components/AppButton';
import { colors, radius } from '../../src/theme';

export default function UploadScreen() {
  const router = useRouter();
  const { token } = useAuth();
  const { imageUri, loading, analyze } = useRecommendation();

  const handleResult = async (asset) => {
    const ok = await analyze(asset);
    if (ok) router.push('/recommend');
  };

  const pickFromGallery = async () => {
    if (!token) {
      promptLogin(router);
      return;
    }
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
    if (!token) {
      promptLogin(router);
      return;
    }
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
      <Text style={styles.title}>어떤 사진의 색을 찾아볼까요?</Text>
      <Text style={styles.desc}>옷이나 풍경처럼 색이 잘 보이는 사진일수록 정확해요.</Text>

      <Pressable style={styles.dropzone} onPress={pickFromGallery}>
        {imageUri ? (
          <Image source={{ uri: imageUri }} style={styles.preview} />
        ) : (
          <View style={styles.placeholder}>
            <Ionicons name="image-outline" size={44} color="#B5B5B0" />
            <Text style={styles.placeholderText}>눌러서 사진 선택</Text>
          </View>
        )}
        {loading && (
          <View style={styles.loadingOverlay}>
            <ActivityIndicator size="large" color={colors.onPrimary} />
            <Text style={styles.loadingText}>색을 분석하고 있어요</Text>
          </View>
        )}
      </Pressable>

      <View style={styles.buttonRow}>
        <AppButton title="촬영하기" icon="camera-outline" variant="outline" onPress={takePhoto} style={styles.button} />
        <AppButton title="앨범에서 선택" icon="images-outline" onPress={pickFromGallery} style={styles.button} />
      </View>
    </View>
  );
}

const styles = StyleSheet.create({
  container: { flex: 1, padding: 20 },
  title: { fontSize: 22, fontWeight: '800', color: colors.text },
  desc: { fontSize: 14, color: colors.subtext, marginTop: 8, marginBottom: 24 },
  dropzone: {
    flex: 1,
    maxHeight: 380,
    borderRadius: radius.lg,
    borderWidth: 2,
    borderStyle: 'dashed',
    borderColor: colors.border,
    backgroundColor: colors.surface,
    overflow: 'hidden',
    marginBottom: 24,
  },
  placeholder: { flex: 1, alignItems: 'center', justifyContent: 'center' },
  placeholderText: { fontSize: 15, color: colors.subtext, marginTop: 10, fontWeight: '600' },
  preview: { width: '100%', height: '100%' },
  loadingOverlay: {
    ...StyleSheet.absoluteFillObject,
    backgroundColor: 'rgba(43,43,43,0.45)',
    alignItems: 'center',
    justifyContent: 'center',
  },
  loadingText: { color: colors.onPrimary, fontSize: 15, fontWeight: '700', marginTop: 12 },
  buttonRow: { flexDirection: 'row' },
  button: { flex: 1, marginHorizontal: 4 },
});
