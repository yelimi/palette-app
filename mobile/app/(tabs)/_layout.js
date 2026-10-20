import { Tabs, useRouter } from 'expo-router';
import { Ionicons } from '@expo/vector-icons';
import { useAuth } from '../../src/context/AuthContext';
import { promptLogin } from '../../src/components/promptLogin';
import { colors } from '../../src/theme';

const tabIcon = (name) => ({ color, focused }) => (
  <Ionicons name={focused ? name : `${name}-outline`} size={24} color={color} />
);

export default function TabsLayout() {
  const router = useRouter();
  const { token } = useAuth();

  return (
    <Tabs
      screenOptions={{
        headerShadowVisible: false,
        headerStyle: { backgroundColor: colors.background },
        headerTitleStyle: { fontSize: 20, fontWeight: '800', color: colors.text },
        headerTitleAlign: 'left',
        sceneStyle: { backgroundColor: colors.background },
        tabBarActiveTintColor: colors.text,
        tabBarInactiveTintColor: '#B5B5B0',
        tabBarLabelStyle: { fontSize: 11, fontWeight: '600' },
        tabBarStyle: { borderTopColor: colors.border, height: 64, paddingTop: 6 },
      }}
    >
      <Tabs.Screen name="index" options={{ title: '홈', headerTitle: 'palette', tabBarIcon: tabIcon('home') }} />
      <Tabs.Screen name="upload" options={{ title: '컬러 찾기', tabBarIcon: tabIcon('camera') }} />
      <Tabs.Screen name="recommend" options={{ title: '추천', tabBarIcon: tabIcon('color-palette') }} />
      <Tabs.Screen
        name="cart"
        options={{ title: '장바구니', tabBarIcon: tabIcon('bag') }}
        listeners={{
          tabPress: (e) => {
            if (!token) {
              e.preventDefault();
              promptLogin(router);
            }
          },
        }}
      />
      <Tabs.Screen name="my" options={{ title: '마이', tabBarIcon: tabIcon('person') }} />
      <Tabs.Screen name="product/[id]" options={{ href: null, title: '상품 상세' }} />
    </Tabs>
  );
}

