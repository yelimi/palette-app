import { View, Text, StyleSheet } from 'react-native';

// 추천 색상 5개를 표현하는 파스텔 톤 점
const DOT_COLORS = ['#F4A79D', '#F2C66D', '#A8C3A0', '#9CC4E4', '#C3B1E1'];

export default function Logo({ size = 44 }) {
  const dotSize = Math.round(size * 0.2);
  return (
    <View style={styles.container}>
      <Text style={[styles.wordmark, { fontSize: size, letterSpacing: -size * 0.04 }]}>
        palette
      </Text>
      <View style={[styles.dots, { marginTop: size * 0.18 }]}>
        {DOT_COLORS.map((color) => (
          <View
            key={color}
            style={{
              width: dotSize,
              height: dotSize,
              borderRadius: dotSize / 2,
              marginHorizontal: dotSize * 0.3,
              backgroundColor: color,
            }}
          />
        ))}
      </View>
    </View>
  );
}

const styles = StyleSheet.create({
  container: { alignItems: 'center' },
  wordmark: { fontWeight: '800', color: '#2B2B2B' },
  dots: { flexDirection: 'row' },
});
