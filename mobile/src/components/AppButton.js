import { Pressable, Text, StyleSheet, View } from 'react-native';
import { Ionicons } from '@expo/vector-icons';
import { colors, radius } from '../theme';

// variant: 'primary'(차콜 채움) | 'outline'(테두리)
export default function AppButton({ title, onPress, disabled, variant = 'primary', icon, style }) {
  const isPrimary = variant === 'primary';
  const textColor = isPrimary ? colors.onPrimary : colors.text;
  return (
    <Pressable
      onPress={onPress}
      disabled={disabled}
      style={({ pressed }) => [
        styles.base,
        isPrimary ? styles.primary : styles.outline,
        (pressed || disabled) && styles.dimmed,
        style,
      ]}
    >
      <View style={styles.content}>
        {icon && <Ionicons name={icon} size={18} color={textColor} style={styles.icon} />}
        <Text style={[styles.text, { color: textColor }]}>{title}</Text>
      </View>
    </Pressable>
  );
}

const styles = StyleSheet.create({
  base: { height: 52, borderRadius: radius.md, alignItems: 'center', justifyContent: 'center', paddingHorizontal: 20 },
  primary: { backgroundColor: colors.primary },
  outline: { backgroundColor: colors.background, borderWidth: 1, borderColor: colors.border },
  dimmed: { opacity: 0.6 },
  content: { flexDirection: 'row', alignItems: 'center' },
  icon: { marginRight: 8 },
  text: { fontSize: 16, fontWeight: '700' },
});
