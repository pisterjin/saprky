// ============================================================
// SPARKY 공통 타입 정의
// ============================================================

/** 연령대 코드 */
export type AgeGroup = 'youth_15_18' | 'youth_19_24' | 'youth_25_29' | 'youth_30_34' | 'youth_35_up';

/** 성별 코드 (OB-003: 선택 안 함 포함) */
export type Gender = 'male' | 'female' | 'none';

/** 거주지역 코드 */
export type Region =
  | 'seoul' | 'busan' | 'daegu' | 'incheon' | 'gwangju'
  | 'daejeon' | 'ulsan' | 'sejong' | 'gyeonggi' | 'gangwon'
  | 'chungbuk' | 'chungnam' | 'jeonbuk' | 'jeonnam'
  | 'gyeongbuk' | 'gyeongnam' | 'jeju';

/** 사용자 프로필 */
export interface UserProfile {
  ageGroup: AgeGroup;
  gender: Gender;
  region: Region;
  uuid: string;
}

/** 정책 도메인 */
export type PolicyDomain =
  | '취업' | '주거' | '금융' | '교육' | '복지' | '판단불가';

/** 정책 카드 */
export interface PolicyCard {
  id: string;
  title: string;
  summary: string;
  domain: PolicyDomain;
  target: string;
  benefit: string;
  period: string;
  applyUrl: string;
  source: 'youth' | 'subsidy';
  endDate?: string;   // D-day 계산용 (UI-001)
}

/** 채팅 메시지 */
export interface ChatMessage {
  id: string;
  role: 'user' | 'assistant';
  content: string;
  policyCards?: PolicyCard[];
  isClarifying?: boolean;   // CH-004: true → 카드 미렌더링
  timestamp: number;
  domain?: PolicyDomain;
  chips?: 'age' | 'gender' | 'region'; // 온보딩 칩 그룹 (챗에서 disabled 렌더링용)
}

/** AI 서버 요청 */
export interface AiRequestBody {
  question: string;
  userProfile: UserProfile;
  conversationHistory: ChatMessage[];
  candidateIds: string[];          // AND 교집합용 이전 턴 후보 풀
}

/** AI 서버 응답 */
export interface AiResponseBody {
  answer: string;
  policyIds: string[];
  domain: PolicyDomain;
  cards: PolicyCard[];
  is_clarifying: boolean;
  candidateIds: string[];          // 현재 턴 후보 풀 (다음 요청에 전달)
}

/** 로그 서버 요청 */
export interface LogRequestBody {
  uuid: string;
  turnNo: number;
  question: string;
  answer: string;
  domain: PolicyDomain;
  policyIds: string[];
  userProfile: UserProfile;
  isClarifying: boolean;
  responseTimeMs: number;
}
