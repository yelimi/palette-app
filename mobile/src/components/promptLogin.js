import { Alert } from 'react-native';

// 비로그인 상태에서 로그인이 필요한 기능을 누르면 띄우는 안내 창
export function promptLogin(router) {
  Alert.alert('로그인이 필요합니다', '로그인하고 사진으로 어울리는 색과 옷을 추천받아 보세요.', [
    { text: '취소', style: 'cancel' },
    { text: '회원가입', onPress: () => router.push('/register') },
    { text: '로그인', onPress: () => router.push('/login') },
  ]);
}
