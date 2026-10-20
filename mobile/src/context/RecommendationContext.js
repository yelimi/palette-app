import { createContext, useCallback, useContext, useState } from 'react';
import { Alert } from 'react-native';
import { extractColor } from '../api/colors';
import { getProductsByColor } from '../api/products';
import { ApiError } from '../api/client';

const RecommendationContext = createContext(null);

// 컬러 찾기 탭에서 분석한 결과를 추천 탭과 공유한다.
// 요청 처리 방식은 기존 홈 화면과 동일하다 (이전 요청을 취소하지 않음).
export function RecommendationProvider({ children }) {
  const [imageUri, setImageUri] = useState(null);
  const [extractedColor, setExtractedColor] = useState(null);
  const [loading, setLoading] = useState(false);
  const [sections, setSections] = useState([]);

  const analyze = useCallback(async (asset) => {
    setImageUri(asset.uri);
    setLoading(true);
    setSections([]);
    try {
      const result = await extractColor(asset);
      setExtractedColor(result.extracted_color);
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
      return withProducts.length > 0;
    } catch (err) {
      if (err instanceof ApiError && err.handled) return false;
      const message = err instanceof ApiError ? err.message : '이미지 처리 중 오류가 발생했습니다.';
      Alert.alert('오류', message);
      return false;
    } finally {
      setLoading(false);
    }
  }, []);

  return (
    <RecommendationContext.Provider value={{ imageUri, extractedColor, loading, sections, analyze }}>
      {children}
    </RecommendationContext.Provider>
  );
}

export function useRecommendation() {
  return useContext(RecommendationContext);
}
