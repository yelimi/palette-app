import { useEffect, useState } from 'react';
import { View, Text, FlatList, Pressable, StyleSheet, ScrollView } from 'react-native';
import { useRouter } from 'expo-router';
import { Ionicons } from '@expo/vector-icons';
import { useRecommendation } from '../../src/context/RecommendationContext';
import AppButton from '../../src/components/AppButton';
import { colors, radius, shadow } from '../../src/theme';

export default function RecommendScreen() {
  const router = useRouter();
  const { extractedColor, sections } = useRecommendation();
  const [selectedHex, setSelectedHex] = useState(null);

  useEffect(() => {
    setSelectedHex(sections[0]?.hex ?? null);
  }, [sections]);

  if (sections.length === 0) {
    return (
      <View style={styles.empty}>
        <Ionicons name="color-palette-outline" size={56} color="#B5B5B0" />
        <Text style={styles.emptyTitle}>아직 추천받은 색이 없어요</Text>
        <Text style={styles.emptyDesc}>사진을 올리면 어울리는 색과 옷을 추천해 드려요.</Text>
        <AppButton title="사진 올리러 가기" onPress={() => router.push('/upload')} style={styles.emptyButton} />
      </View>
    );
  }

  const selected = sections.find((s) => s.hex === selectedHex) ?? sections[0];

  return (
    <FlatList
      data={selected.products}
      keyExtractor={(p) => String(p.id)}
      numColumns={2}
      columnWrapperStyle={styles.gridRow}
      contentContainerStyle={styles.container}
      ListHeaderComponent={
        <View>
          {extractedColor && (
            <View style={styles.extracted}>
              <View style={[styles.extractedSwatch, { backgroundColor: extractedColor }]} />
              <View>
                <Text style={styles.extractedLabel}>내 사진의 대표 색</Text>
                <Text style={styles.extractedHex}>{extractedColor}</Text>
              </View>
            </View>
          )}

          <Text style={styles.sectionTitle}>함께 입기 좋은 색</Text>
          <ScrollView horizontal showsHorizontalScrollIndicator={false} contentContainerStyle={styles.chipRow}>
            {sections.map((section) => {
              const active = section.hex === selected.hex;
              return (
                <Pressable
                  key={section.hex}
                  onPress={() => setSelectedHex(section.hex)}
                  style={[styles.chip, active && styles.chipActive]}
                >
                  <View style={[styles.chipSwatch, { backgroundColor: section.hex }]} />
                  <Text style={[styles.chipText, active && styles.chipTextActive]}>{section.color_name}</Text>
                </Pressable>
              );
            })}
          </ScrollView>

          <Text style={styles.sectionTitle}>
            {selected.color_name} 아이템 <Text style={styles.count}>{selected.products.length}</Text>
          </Text>
        </View>
      }
      renderItem={({ item: product }) => (
        <Pressable style={styles.card} onPress={() => router.push(`/product/${product.id}`)}>
          <View style={[styles.cardSwatch, { backgroundColor: product.hex }]} />
          <View style={styles.cardBody}>
            <Text style={styles.cardName} numberOfLines={1}>
              {product.name}
            </Text>
            <Text style={styles.cardPrice}>{product.price.toLocaleString()}원</Text>
          </View>
        </Pressable>
      )}
    />
  );
}

const styles = StyleSheet.create({
  container: { padding: 20, paddingBottom: 40 },
  empty: { flex: 1, alignItems: 'center', justifyContent: 'center', padding: 32 },
  emptyTitle: { fontSize: 18, fontWeight: '800', color: colors.text, marginTop: 16 },
  emptyDesc: { fontSize: 14, color: colors.subtext, marginTop: 8, textAlign: 'center' },
  emptyButton: { marginTop: 24, alignSelf: 'stretch' },
  extracted: {
    flexDirection: 'row',
    alignItems: 'center',
    backgroundColor: colors.surface,
    borderRadius: radius.md,
    padding: 16,
    marginBottom: 28,
  },
  extractedSwatch: { width: 56, height: 56, borderRadius: 28, marginRight: 16 },
  extractedLabel: { fontSize: 13, color: colors.subtext },
  extractedHex: { fontSize: 18, fontWeight: '800', color: colors.text, marginTop: 2 },
  sectionTitle: { fontSize: 18, fontWeight: '800', color: colors.text, marginBottom: 14 },
  count: { color: colors.subtext, fontWeight: '600' },
  chipRow: { paddingBottom: 28 },
  chip: {
    flexDirection: 'row',
    alignItems: 'center',
    paddingVertical: 8,
    paddingHorizontal: 14,
    borderRadius: 999,
    borderWidth: 1,
    borderColor: colors.border,
    marginRight: 8,
  },
  chipActive: { backgroundColor: colors.primary, borderColor: colors.primary },
  chipSwatch: { width: 16, height: 16, borderRadius: 8, marginRight: 8 },
  chipText: { fontSize: 14, fontWeight: '600', color: colors.text },
  chipTextActive: { color: colors.onPrimary },
  gridRow: { justifyContent: 'space-between' },
  card: { width: '48%', backgroundColor: colors.background, borderRadius: radius.md, marginBottom: 16, ...shadow },
  cardSwatch: { height: 140, borderTopLeftRadius: radius.md, borderTopRightRadius: radius.md },
  cardBody: { padding: 12 },
  cardName: { fontSize: 14, fontWeight: '600', color: colors.text },
  cardPrice: { fontSize: 15, fontWeight: '800', color: colors.text, marginTop: 4 },
});
