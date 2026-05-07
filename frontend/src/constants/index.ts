// ============================================================
// SPARKY 상수 정의
// ============================================================

export const API = {
  AI_SERVER:  process.env.NEXT_PUBLIC_AI_SERVER_URL  || 'http://localhost:8000',
  LOG_SERVER: process.env.NEXT_PUBLIC_LOG_SERVER_URL || 'http://localhost:8081',
} as const;

export const CRYPTO_KEY = process.env.NEXT_PUBLIC_CRYPTO_KEY || 'sparky-default-key-change-me';

export const LOG_API_KEY = process.env.NEXT_PUBLIC_LOG_API_KEY || '';

/** SC-001: localStorage 저장 키 */
export const STORAGE_KEY = {
  USER_PROFILE: 'yp_profile',
} as const;

/** OB-002: 연령대 옵션 */
export const AGE_GROUP_OPTIONS = [
  { value: 'youth_19_24', label: '19~24세' },
  { value: 'youth_25_29', label: '25~29세' },
  { value: 'youth_30_34', label: '30~34세' },
  { value: 'youth_35_up', label: '35세 이상' },
] as const;

/** OB-003: 성별 옵션 (선택 안 함 포함) */
export const GENDER_OPTIONS = [
  { value: 'male',   label: '남성' },
  { value: 'female', label: '여성' },
  { value: 'none',   label: '선택 안 함' },
] as const;

/** OB-004: 지역 옵션 */
export const REGION_OPTIONS = [
  { value: 'seoul',    label: '서울' },
  { value: 'gyeonggi', label: '경기' },
  { value: 'busan',    label: '부산' },
  { value: 'incheon',  label: '인천' },
  { value: 'daegu',    label: '대구' },
  { value: 'gwangju',  label: '광주' },
  { value: 'daejeon',  label: '대전' },
  { value: 'ulsan',    label: '울산' },
  { value: 'sejong',   label: '세종' },
  { value: 'gangwon',  label: '강원' },
  { value: 'chungbuk', label: '충북' },
  { value: 'chungnam', label: '충남' },
  { value: 'jeonbuk',  label: '전북' },
  { value: 'jeonnam',  label: '전남' },
  { value: 'gyeongbuk',label: '경북' },
  { value: 'gyeongnam',label: '경남' },
  { value: 'jeju',     label: '제주' },
] as const;

/** CH-008: 근로 상태 선택 칩 */
export const EMPLOYMENT_OPTIONS = [
  { value: 'employed',   label: '재직 중 (이직 준비 포함)' },
  { value: 'unemployed', label: '미취업 (구직 중 포함)' },
] as const;

/** CH-007: 빠른 질문 칩버튼 (도메인 5종) */
export const QUICK_CHIPS = [
  { domain: '취업', label: '취업·일자리', query: '청년 취업 지원 정책 알려줘' },
  { domain: '주거', label: '주거·부동산', query: '청년 주거 지원 정책 알려줘' },
  { domain: '금융', label: '금융·대출',   query: '청년 금융 지원 정책 알려줘' },
  { domain: '교육', label: '교육·훈련',   query: '청년 교육 지원 정책 알려줘' },
  { domain: '복지', label: '복지·지원',   query: '청년 복지 지원 정책 알려줘' },
] as const;

/** 환영 메시지 */
export const WELCOME_MESSAGE = `안녕하세요! 저는 SPARKY예요 :)\n맞춤 청년정책을 찾아드릴게요.\n무엇이 궁금하신가요?`;

/** CH-002: 입력 최대 글자 수 */
export const MAX_INPUT_LENGTH = 500;

/** 도메인 라벨 → 색상 (라이트 / 다크 모드 동시 적용) */
export const DOMAIN_COLOR: Record<string, string> = {
  '취업': 'bg-blue-100   text-blue-700   dark:bg-[#1E3A5F] dark:text-[#60A5FA]',
  '주거': 'bg-green-100  text-green-700  dark:bg-[#1E3A2F] dark:text-[#4ADE80]',
  '금융': 'bg-yellow-100 text-yellow-700 dark:bg-[#3A2E10] dark:text-[#FBBF24]',
  '교육': 'bg-purple-100 text-purple-700 dark:bg-[#3D3185] dark:text-[#A78BFA]',
  '복지': 'bg-pink-100   text-pink-700   dark:bg-[#3D1F35] dark:text-[#F472B6]',
  '판단불가': 'bg-gray-100 text-gray-600 dark:bg-[#3A3A3A] dark:text-[#999999]',
};
