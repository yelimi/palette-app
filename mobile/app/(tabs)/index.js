import { ScrollView, View, Text, StyleSheet } from 'react-native';
import { useRouter } from 'expo-router';
import AppButton from '../../src/components/AppButton';
import { colors, radius, shadow } from '../../src/theme';

const TODAY_PALETTES = [
  { name: '봄 산책', hexes: ['#F4A79D', '#F7D9C4', '#FAF3DD', '#C8D5B9', '#8FB996'] },
  { name: '차분한 오피스', hexes: ['#2B2B2B', '#5C6B73', '#9DB4C0', '#C2DFE3', '#E0FBFC'] },
  { name: '따뜻한 주말', hexes: ['#9C6644', '#B08968', '#DDB892', '#E6CCB2', '#EDE0D4'] },
];

const STEPS = [
  { title: '사진 올리기', desc: '오늘 입은 옷이나 좋아하는 사진을 올려요' },
  { title: '대표 색 찾기', desc: '사진에서 가장 잘 드러나는 색을 뽑아요' },
  { title: '어울리는 옷 추천', desc: '그 색과 어울리는 5가지 색의 옷을 보여 줘요' },
];

export default function HomeScreen() {
  const router = useRouter();

  return (
    <ScrollView contentContainerStyle={styles.container}>
      <View style={styles.hero}>
        <Text style={styles.heroTitle}>사진 한 장으로{'\n'}나에게 어울리는 색 찾기</Text>
        <Text style={styles.heroDesc}>사진 속 대표 색을 분석해 함께 입기 좋은 색과 옷을 추천해 드려요.</Text>
        <AppButton title="사진으로 색 찾기" icon="camera-outline" onPress={() => router.push('/upload')} />
      </View>

      <Text style={styles.sectionTitle}>오늘의 컬러 조합</Text>
      <ScrollView horizontal showsHorizontalScrollIndicator={false} contentContainerStyle={styles.paletteRow}>
        {TODAY_PALETTES.map((palette) => (
          <View key={palette.name} style={styles.paletteCard}>
            <View style={styles.paletteStripes}>
              {palette.hexes.map((hex) => (
                <View key={hex} style={[styles.stripe, { backgroundColor: hex }]} />
              ))}
            </View>
            <Text style={styles.paletteName}>{palette.name}</Text>
          </View>
        ))}
      </ScrollView>

      <Text style={styles.sectionTitle}>이렇게 사용해요</Text>
      {STEPS.map((step, i) => (
        <View key={step.title} style={styles.step}>
          <View style={[styles.stepNumber, { backgroundColor: colors.accents[i] }]}>
            <Text style={styles.stepNumberText}>{i + 1}</Text>
          </View>
          <View style={styles.stepBody}>
            <Text style={styles.stepTitle}>{step.title}</Text>
            <Text style={styles.stepDesc}>{step.desc}</Text>
          </View>
        </View>
      ))}
    </ScrollView>
  );
}

const styles = StyleSheet.create({
  container: { padding: 20, paddingBottom: 40 },
  hero: { backgroundColor: colors.surface, borderRadius: radius.lg, padding: 24, marginBottom: 32 },
  heroTitle: { fontSize: 26, fontWeight: '800', color: colors.text, lineHeight: 36 },
  heroDesc: { fontSize: 15, color: colors.subtext, lineHeight: 22, marginTop: 12, marginBottom: 24 },
  sectionTitle: { fontSize: 18, fontWeight: '800', color: colors.text, marginBottom: 14 },
  paletteRow: { paddingBottom: 32 },
  paletteCard: { width: 160, marginRight: 12, backgroundColor: colors.background, borderRadius: radius.md, ...shadow },
  paletteStripes: { flexDirection: 'row', height: 96, borderTopLeftRadius: radius.md, borderTopRightRadius: radius.md, overflow: 'hidden' },
  stripe: { flex: 1 },
  paletteName: { fontSize: 14, fontWeight: '700', color: colors.text, padding: 12 },
  step: { flexDirection: 'row', alignItems: 'center', marginBottom: 16 },
  stepNumber: { width: 36, height: 36, borderRadius: 18, alignItems: 'center', justifyContent: 'center', marginRight: 14 },
  stepNumberText: { fontSize: 15, fontWeight: '800', color: colors.text },
  stepBody: { flex: 1 },
  stepTitle: { fontSize: 15, fontWeight: '700', color: colors.text },
  stepDesc: { fontSize: 13, color: colors.subtext, marginTop: 2 },
});
