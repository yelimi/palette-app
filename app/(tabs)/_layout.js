import { Tabs } from 'expo-router';

export default function TabsLayout() {
  return (
    <Tabs>
      <Tabs.Screen name="index" options={{ title: '홈' }} />
      <Tabs.Screen name="cart" options={{ title: '장바구니' }} />
      <Tabs.Screen name="product/[id]" options={{ href: null, title: '상품 상세' }} />
    </Tabs>
  );
}
