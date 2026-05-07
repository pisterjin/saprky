#!/bin/bash
# ============================================================
# SPARKY - Frontend Project Initializer (Sub-directory Version)
# 실행 위치: sparky/frontend/ 폴더 안에서 실행
# ============================================================

set -e

# 스크립트가 실행되는 현재 폴더(frontend/)를 프로젝트 루트로 설정
PROJECT_ROOT="$(pwd)"

echo ""
echo "🚀 SPARKY 프론트엔드 프로젝트 초기화 시작..."
echo "📂 설치 경로: $PROJECT_ROOT"
echo "=============================================="

# ── 1. Next.js 14 프로젝트 생성 (임시 폴더 활용) ──────────────────
echo ""
echo "📦 [1/5] Next.js 14 보일러플레이트 설치 중..."

# 현재 폴더에 직접 설치 시 발생하는 충돌을 피하기 위해 임시 폴더 생성
npx create-next-app@14.2.35 tmp-install \
  --typescript \
  --tailwind \
  --app \
  --src-dir \
  --import-alias "@/*" \
  --eslint \
  --no-git \
  --yes

echo "🚚 프로젝트 파일 이동 및 구성 중..."
# 임시 폴더의 내용물을 현재 폴더(frontend/)로 이동 (빠른 이동을 위해 mv 사용)
shopt -s dotglob
mv tmp-install/* . 2>/dev/null || true
shopt -u dotglob
rm -rf tmp-install

# 기본 생성 파일 중 SPARKY 설정과 충돌하거나 불필요한 파일 삭제
rm -rf src/app/page.tsx src/app/layout.tsx src/app/globals.css
rm -f next.config.mjs

# ── 2. 추가 패키지 설치 ───────────────────────────────────────
echo ""
echo "📦 [2/5] SPARKY 필수 의존성 패키지 설치 중..."
npm install \
  zustand \
  crypto-js \
  embla-carousel-react \
  embla-carousel-autoplay \
  uuid \
  axios \
  clsx \
  tailwind-merge

npm install -D \
  @types/crypto-js \
  @types/uuid

# ── 3. 폴더 구조 생성 ─────────────────────────────────────────
echo ""
echo "📁 [3/5] 폴더 구조 생성 중..."

# src/ 하위 구조
mkdir -p src/components/ui
mkdir -p src/components/chat
mkdir -p src/components/onboarding
mkdir -p src/components/policy
mkdir -p src/components/layout
mkdir -p src/constants
mkdir -p src/contexts
mkdir -p src/hooks
mkdir -p src/pages
mkdir -p src/services
mkdir -p src/types
mkdir -p src/utils

# app 라우팅 폴더
mkdir -p src/app/chat
mkdir -p src/app/onboarding

echo "   ✅ 폴더 구조 생성 완료"

# ── 4. 기본 파일 생성 ─────────────────────────────────────────
echo ""
echo "📝 [4/5] 기본 파일 생성 중..."

# ─────────────── types/index.ts ───────────────────────────────
cat > src/types/index.ts << 'EOF'
// ============================================================
// SPARKY 공통 타입 정의
// ============================================================

/** 연령대 코드 */
export type AgeGroup = 'youth_19_24' | 'youth_25_29' | 'youth_30_34';

/** 성별 코드 */
export type Gender = 'male' | 'female';

/** 거주지역 코드 */
export type Region =
  | 'seoul' | 'busan' | 'daegu' | 'incheon' | 'gwangju'
  | 'daejeon' | 'ulsan' | 'sejong' | 'gyeonggi' | 'gangwon'
  | 'chungbuk' | 'chungnam' | 'jeonbuk' | 'jeonnam'
  | 'gyeongbuk' | 'gyeongnam' | 'jeju';

/** 사용자 프로필 (온보딩 입력값) */
export interface UserProfile {
  ageGroup: AgeGroup;
  gender: Gender;
  region: Region;
  uuid: string;
}

/** 도메인 분류 */
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
}

/** 채팅 메시지 */
export interface ChatMessage {
  id: string;
  role: 'user' | 'assistant';
  content: string;
  policyCards?: PolicyCard[];
  timestamp: number;
  domain?: PolicyDomain;
}

/** AI 서버 요청 */
export interface AiRequestBody {
  question: string;
  userProfile: UserProfile;
  conversationHistory: ChatMessage[];
}

/** AI 서버 응답 */
export interface AiResponseBody {
  answer: string;
  policyIds: string[];
  domain: PolicyDomain;
  cards: PolicyCard[];
}

/** 로그 서버 요청 */
export interface LogRequestBody {
  uuid: string;
  question: string;
  answer: string;
  domain: PolicyDomain;
  policyIds: string[];
  userProfile: UserProfile;
}
EOF

cat > src/app/globals.css << 'EOF'
@tailwind base;
@tailwind components;
@tailwind utilities;

:root {
  --foreground-rgb: 0, 0, 0;
  --background-start-rgb: 214, 219, 220;
  --background-end-rgb: 255, 255, 255;
}

body {
  color: rgb(var(--foreground-rgb));
  background: white;
}
EOF

# ─────────────── constants/index.ts ───────────────────────────
cat > src/constants/index.ts << 'EOF'
// ============================================================
// SPARKY 상수 정의
// ============================================================

/** API 엔드포인트 */
export const API = {
  AI_SERVER: process.env.NEXT_PUBLIC_AI_SERVER_URL || 'http://localhost:8000',
  LOG_SERVER: process.env.NEXT_PUBLIC_LOG_SERVER_URL || 'http://localhost:8080',
} as const;

/** crypto-js AES 암호화 키 (환경변수 필수) */
export const CRYPTO_KEY = process.env.NEXT_PUBLIC_CRYPTO_KEY || 'sparky-default-key-change-me';

/** localStorage 키 */
export const STORAGE_KEY = {
  USER_PROFILE: 'sparky_up',
} as const;

/** 연령대 옵션 */
export const AGE_GROUP_OPTIONS = [
  { value: 'youth_19_24', label: '19~24세' },
  { value: 'youth_25_29', label: '25~29세' },
  { value: 'youth_30_34', label: '30~34세' },
] as const;

/** 성별 옵션 */
export const GENDER_OPTIONS = [
  { value: 'male', label: '남성' },
  { value: 'female', label: '여성' },
] as const;

/** 지역 옵션 */
export const REGION_OPTIONS = [
  { value: 'seoul', label: '서울' },
  { value: 'busan', label: '부산' },
  { value: 'daegu', label: '대구' },
  { value: 'incheon', label: '인천' },
  { value: 'gwangju', label: '광주' },
  { value: 'daejeon', label: '대전' },
  { value: 'ulsan', label: '울산' },
  { value: 'sejong', label: '세종' },
  { value: 'gyeonggi', label: '경기' },
  { value: 'gangwon', label: '강원' },
  { value: 'chungbuk', label: '충북' },
  { value: 'chungnam', label: '충남' },
  { value: 'jeonbuk', label: '전북' },
  { value: 'jeonnam', label: '전남' },
  { value: 'gyeongbuk', label: '경북' },
  { value: 'gyeongnam', label: '경남' },
  { value: 'jeju', label: '제주' },
] as const;

/** 빠른 질문 칩버튼 */
export const QUICK_CHIPS = [
  { domain: '취업', label: '💼 취업', query: '청년 취업 지원 정책 알려줘' },
  { domain: '주거', label: '🏠 주거', query: '청년 주거 지원 정책 알려줘' },
  { domain: '금융', label: '💰 금융', query: '청년 금융 지원 정책 알려줘' },
  { domain: '교육', label: '📚 교육', query: '청년 교육 지원 정책 알려줘' },
  { domain: '복지', label: '🌱 복지', query: '청년 복지 지원 정책 알려줘' },
] as const;

/** 환영 메시지 */
export const WELCOME_MESSAGE = `안녕하세요! 저는 청년 정책 전문 AI **SPARKY**예요 ✨\n\n취업, 주거, 금융, 교육, 복지 분야의 청년 정책을 맞춤으로 안내해 드려요.\n아래 버튼을 누르거나 자유롭게 질문해 주세요!`;
EOF

# ─────────────── utils/storage.ts ─────────────────────────────
cat > src/utils/storage.ts << 'EOF'
import CryptoJS from 'crypto-js';
import { CRYPTO_KEY, STORAGE_KEY } from '@/constants';
import type { UserProfile } from '@/types';

/** localStorage AES-256 암호화 저장 */
export function saveUserProfile(profile: UserProfile): void {
  const json = JSON.stringify(profile);
  const encrypted = CryptoJS.AES.encrypt(json, CRYPTO_KEY).toString();
  localStorage.setItem(STORAGE_KEY.USER_PROFILE, encrypted);
}

/** localStorage AES-256 복호화 로드 */
export function loadUserProfile(): UserProfile | null {
  try {
    const encrypted = localStorage.getItem(STORAGE_KEY.USER_PROFILE);
    if (!encrypted) return null;
    const bytes = CryptoJS.AES.decrypt(encrypted, CRYPTO_KEY);
    const json = bytes.toString(CryptoJS.enc.Utf8);
    if (!json) return null;
    return JSON.parse(json) as UserProfile;
  } catch {
    return null;
  }
}

/** localStorage 초기화 (내 정보 파기) */
export function clearUserProfile(): void {
  localStorage.removeItem(STORAGE_KEY.USER_PROFILE);
}
EOF

# ─────────────── utils/uuid.ts ────────────────────────────────
cat > src/utils/uuid.ts << 'EOF'
import { v4 as uuidv4 } from 'uuid';

/** 새 세션 UUID 생성 */
export function generateUUID(): string {
  return uuidv4();
}
EOF

# ─────────────── utils/cn.ts ──────────────────────────────────
cat > src/utils/cn.ts << 'EOF'
import { clsx, type ClassValue } from 'clsx';
import { twMerge } from 'tailwind-merge';

/** Tailwind 클래스 병합 유틸 */
export function cn(...inputs: ClassValue[]): string {
  return twMerge(clsx(inputs));
}
EOF

# ─────────────── services/aiService.ts ────────────────────────
cat > src/services/aiService.ts << 'EOF'
import axios from 'axios';
import { API } from '@/constants';
import type { AiRequestBody, AiResponseBody } from '@/types';

/**
 * AI 서버(FastAPI/Colab ngrok)에 RAG 질의
 */
export async function queryAiServer(body: AiRequestBody): Promise<AiResponseBody> {
  const { data } = await axios.post<AiResponseBody>(
    `${API.AI_SERVER}/api/chat`,
    body,
    { timeout: 30000 }
  );
  return data;
}
EOF

# ─────────────── services/logService.ts ───────────────────────
cat > src/services/logService.ts << 'EOF'
import { API } from '@/constants';
import type { LogRequestBody } from '@/types';

/**
 * Log 서버(Spring Boot)에 대화 로그 비동기 전송 (fire-and-forget)
 * AI 응답 속도에 영향 없도록 await 없이 호출
 */
export function sendLog(body: LogRequestBody): void {
  fetch(`${API.LOG_SERVER}/api/logs`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(body),
  }).catch((err) => {
    console.warn('[LogService] 로그 전송 실패 (무시됨):', err);
  });
}
EOF

# ─────────────── hooks/useUserProfile.ts ──────────────────────
cat > src/hooks/useUserProfile.ts << 'EOF'
import { useEffect } from 'react';
import { useStore } from '@/contexts/store';
import { loadUserProfile, saveUserProfile, clearUserProfile } from '@/utils/storage';
import type { UserProfile } from '@/types';

/** 사용자 프로필 로드/저장/초기화 훅 */
export function useUserProfile() {
  const { userProfile, setUserProfile } = useStore();

  // 마운트 시 localStorage 복호화 로드
  useEffect(() => {
    if (!userProfile) {
      const loaded = loadUserProfile();
      if (loaded) setUserProfile(loaded);
    }
  }, []);

  const save = (profile: UserProfile) => {
    saveUserProfile(profile);
    setUserProfile(profile);
  };

  const clear = () => {
    clearUserProfile();
    setUserProfile(null);
  };

  return { userProfile, save, clear };
}
EOF

# ─────────────── hooks/useChat.ts ─────────────────────────────
cat > src/hooks/useChat.ts << 'EOF'
import { useState, useCallback } from 'react';
import { useStore } from '@/contexts/store';
import { queryAiServer } from '@/services/aiService';
import { sendLog } from '@/services/logService';
import type { ChatMessage } from '@/types';

/** 채팅 전송 및 대화이력 관리 훅 */
export function useChat() {
  const { userProfile, messages, addMessage, setDomain } = useStore();
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const send = useCallback(async (question: string) => {
    if (!userProfile || loading) return;
    setError(null);
    setLoading(true);

    // 사용자 메시지 추가
    const userMsg: ChatMessage = {
      id: `u_${Date.now()}`,
      role: 'user',
      content: question,
      timestamp: Date.now(),
    };
    addMessage(userMsg);

    try {
      const res = await queryAiServer({
        question,
        userProfile,
        conversationHistory: messages,
      });

      const assistantMsg: ChatMessage = {
        id: `a_${Date.now()}`,
        role: 'assistant',
        content: res.answer,
        policyCards: res.cards,
        domain: res.domain,
        timestamp: Date.now(),
      };
      addMessage(assistantMsg);
      setDomain(res.domain);

      // fire-and-forget 로그 전송
      sendLog({
        uuid: userProfile.uuid,
        question,
        answer: res.answer,
        domain: res.domain,
        policyIds: res.policyIds,
        userProfile,
      });
    } catch (err) {
      setError('AI 서버 연결에 실패했어요. 잠시 후 다시 시도해 주세요.');
      console.error('[useChat]', err);
    } finally {
      setLoading(false);
    }
  }, [userProfile, messages, loading]);

  return { send, loading, error };
}
EOF

# ─────────────── contexts/store.ts ────────────────────────────
cat > src/contexts/store.ts << 'EOF'
import { create } from 'zustand';
import type { UserProfile, ChatMessage, PolicyDomain } from '@/types';
import { WELCOME_MESSAGE } from '@/constants';
import { generateUUID } from '@/utils/uuid';

interface AppState {
  // 사용자 프로필
  userProfile: UserProfile | null;
  setUserProfile: (profile: UserProfile | null) => void;

  // 채팅 메시지
  messages: ChatMessage[];
  addMessage: (msg: ChatMessage) => void;
  clearMessages: () => void;

  // 도메인 분류 결과
  currentDomain: PolicyDomain | null;
  setDomain: (domain: PolicyDomain) => void;
}

const welcomeMsg: ChatMessage = {
  id: 'welcome',
  role: 'assistant',
  content: WELCOME_MESSAGE,
  timestamp: Date.now(),
};

export const useStore = create<AppState>((set) => ({
  userProfile: null,
  setUserProfile: (profile) => set({ userProfile: profile }),

  messages: [welcomeMsg],
  addMessage: (msg) => set((s) => ({ messages: [...s.messages, msg] })),
  clearMessages: () =>
    set({
      messages: [{ ...welcomeMsg, timestamp: Date.now() }],
      currentDomain: null,
    }),

  currentDomain: null,
  setDomain: (domain) => set({ currentDomain: domain }),
}));
EOF

# ─────────────── components/ui/Chip.tsx ───────────────────────
cat > src/components/ui/Chip.tsx << 'EOF'
import { cn } from '@/utils/cn';

interface ChipProps {
  label: string;
  selected?: boolean;
  onClick?: () => void;
  className?: string;
}

export function Chip({ label, selected, onClick, className }: ChipProps) {
  return (
    <button
      type="button"
      onClick={onClick}
      className={cn(
        'px-4 py-2 rounded-full text-sm font-medium border transition-colors',
        selected
          ? 'bg-blue-600 text-white border-blue-600'
          : 'bg-white text-gray-700 border-gray-300 hover:border-blue-400 hover:text-blue-600',
        className
      )}
    >
      {label}
    </button>
  );
}
EOF

# ─────────────── components/ui/LoadingDots.tsx ────────────────
cat > src/components/ui/LoadingDots.tsx << 'EOF'
export function LoadingDots() {
  return (
    <div className="flex items-center gap-1 px-4 py-3">
      {[0, 1, 2].map((i) => (
        <span
          key={i}
          className="w-2 h-2 bg-gray-400 rounded-full animate-bounce"
          style={{ animationDelay: `${i * 0.15}s` }}
        />
      ))}
    </div>
  );
}
EOF

# ─────────────── components/layout/Header.tsx ────────────────
cat > src/components/layout/Header.tsx << 'EOF'
'use client';

import { useStore } from '@/contexts/store';
import { useUserProfile } from '@/hooks/useUserProfile';

export function Header() {
  const { clearMessages } = useStore();
  const { userProfile, clear: clearProfile } = useUserProfile();

  return (
    <header className="sticky top-0 z-10 bg-white border-b border-gray-200 px-4 py-3 flex items-center justify-between">
      <div className="flex items-center gap-2">
        <span className="text-xl font-bold text-blue-600">⚡ SPARKY</span>
        <span className="text-xs text-gray-400 hidden sm:block">청년 정책 AI 안내</span>
      </div>
      <div className="flex items-center gap-2 text-sm">
        <button
          onClick={clearMessages}
          className="text-gray-500 hover:text-blue-600 transition-colors px-2 py-1 rounded"
        >
          대화 초기화
        </button>
        {userProfile && (
          <button
            onClick={clearProfile}
            className="text-gray-500 hover:text-red-500 transition-colors px-2 py-1 rounded"
          >
            내 정보 초기화
          </button>
        )}
      </div>
    </header>
  );
}
EOF

# ─────────────── pages/OnboardingPage.tsx ─────────────────────
cat > src/pages/OnboardingPage.tsx << 'EOF'
'use client';

import { useState } from 'react';
import { useRouter } from 'next/navigation';
import { Chip } from '@/components/ui/Chip';
import { useUserProfile } from '@/hooks/useUserProfile';
import { AGE_GROUP_OPTIONS, GENDER_OPTIONS, REGION_OPTIONS } from '@/constants';
import { generateUUID } from '@/utils/uuid';
import type { AgeGroup, Gender, Region } from '@/types';

export default function OnboardingPage() {
  const router = useRouter();
  const { save } = useUserProfile();

  const [ageGroup, setAgeGroup] = useState<AgeGroup | null>(null);
  const [gender, setGender] = useState<Gender | null>(null);
  const [region, setRegion] = useState<Region | null>(null);

  const isReady = ageGroup && gender && region;

  const handleStart = () => {
    if (!isReady) return;
    save({ ageGroup, gender, region, uuid: generateUUID() });
    router.push('/chat');
  };

  return (
    <div className="min-h-screen bg-gradient-to-br from-blue-50 to-white flex flex-col items-center justify-center px-4 py-10">
      <div className="w-full max-w-md bg-white rounded-2xl shadow-lg p-8 space-y-6">
        <div className="text-center">
          <h1 className="text-2xl font-bold text-blue-600">⚡ SPARKY</h1>
          <p className="text-gray-500 text-sm mt-1">맞춤 청년 정책을 찾아드려요</p>
        </div>

        {/* 연령대 */}
        <div>
          <p className="text-sm font-semibold text-gray-700 mb-2">연령대</p>
          <div className="flex flex-wrap gap-2">
            {AGE_GROUP_OPTIONS.map((o) => (
              <Chip
                key={o.value}
                label={o.label}
                selected={ageGroup === o.value}
                onClick={() => setAgeGroup(o.value)}
              />
            ))}
          </div>
        </div>

        {/* 성별 */}
        <div>
          <p className="text-sm font-semibold text-gray-700 mb-2">성별</p>
          <div className="flex gap-2">
            {GENDER_OPTIONS.map((o) => (
              <Chip
                key={o.value}
                label={o.label}
                selected={gender === o.value}
                onClick={() => setGender(o.value)}
              />
            ))}
          </div>
        </div>

        {/* 거주지역 */}
        <div>
          <p className="text-sm font-semibold text-gray-700 mb-2">거주지역</p>
          <div className="flex flex-wrap gap-2">
            {REGION_OPTIONS.map((o) => (
              <Chip
                key={o.value}
                label={o.label}
                selected={region === o.value}
                onClick={() => setRegion(o.value as Region)}
              />
            ))}
          </div>
        </div>

        <button
          onClick={handleStart}
          disabled={!isReady}
          className="w-full py-3 rounded-xl font-semibold text-white bg-blue-600 hover:bg-blue-700 disabled:bg-gray-300 disabled:cursor-not-allowed transition-colors"
        >
          시작하기
        </button>
      </div>
    </div>
  );
}
EOF

# ─────────────── pages/ChatPage.tsx ───────────────────────────
cat > src/pages/ChatPage.tsx << 'EOF'
'use client';

import { useEffect, useRef } from 'react';
import { useRouter } from 'next/navigation';
import { Header } from '@/components/layout/Header';
import { LoadingDots } from '@/components/ui/LoadingDots';
import { Chip } from '@/components/ui/Chip';
import { useUserProfile } from '@/hooks/useUserProfile';
import { useChat } from '@/hooks/useChat';
import { useStore } from '@/contexts/store';
import { QUICK_CHIPS } from '@/constants';

export default function ChatPage() {
  const router = useRouter();
  const { userProfile } = useUserProfile();
  const { messages } = useStore();
  const { send, loading, error } = useChat();
  const inputRef = useRef<HTMLInputElement>(null);
  const bottomRef = useRef<HTMLDivElement>(null);

  // 온보딩 미완료 시 리다이렉트
  useEffect(() => {
    if (!userProfile) router.replace('/onboarding');
  }, [userProfile]);

  // 스크롤 하단 유지
  useEffect(() => {
    bottomRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, [messages, loading]);

  const handleSend = () => {
    const val = inputRef.current?.value.trim();
    if (!val) return;
    send(val);
    if (inputRef.current) inputRef.current.value = '';
  };

  return (
    <div className="flex flex-col h-screen bg-gray-50">
      <Header />

      {/* 메시지 목록 */}
      <main className="flex-1 overflow-y-auto px-4 py-4 space-y-4">
        {messages.map((msg) => (
          <div key={msg.id} className={`flex ${msg.role === 'user' ? 'justify-end' : 'justify-start'}`}>
            <div
              className={`max-w-[85%] rounded-2xl px-4 py-3 text-sm whitespace-pre-wrap ${
                msg.role === 'user'
                  ? 'bg-blue-600 text-white'
                  : 'bg-white text-gray-800 shadow-sm border border-gray-100'
              }`}
            >
              {msg.content}
            </div>
          </div>
        ))}

        {loading && (
          <div className="flex justify-start">
            <div className="bg-white rounded-2xl shadow-sm border border-gray-100">
              <LoadingDots />
            </div>
          </div>
        )}
        {error && (
          <div className="text-center text-sm text-red-500 py-2">{error}</div>
        )}
        <div ref={bottomRef} />
      </main>

      {/* 빠른 질문 칩 */}
      <div className="px-4 py-2 flex gap-2 overflow-x-auto scrollbar-hide bg-white border-t border-gray-100">
        {QUICK_CHIPS.map((chip) => (
          <Chip
            key={chip.domain}
            label={chip.label}
            onClick={() => send(chip.query)}
            className="whitespace-nowrap"
          />
        ))}
      </div>

      {/* 입력 영역 */}
      <div className="px-4 py-3 bg-white border-t border-gray-200 flex gap-2">
        <input
          ref={inputRef}
          type="text"
          placeholder="청년 정책에 대해 질문해 보세요..."
          className="flex-1 px-4 py-2 rounded-full border border-gray-300 text-sm focus:outline-none focus:border-blue-400"
          onKeyDown={(e) => e.key === 'Enter' && handleSend()}
          disabled={loading}
        />
        <button
          onClick={handleSend}
          disabled={loading}
          className="px-5 py-2 rounded-full bg-blue-600 text-white text-sm font-medium hover:bg-blue-700 disabled:bg-gray-300 transition-colors"
        >
          전송
        </button>
      </div>
    </div>
  );
}
EOF

# ─────────────── app/page.tsx (루트 리다이렉트) ───────────────
cat > src/app/page.tsx << 'EOF'
import { redirect } from 'next/navigation';

export default function RootPage() {
  redirect('/onboarding');
}
EOF

# ─────────────── app/onboarding/page.tsx ─────────────────────
cat > src/app/onboarding/page.tsx << 'EOF'
import OnboardingPage from '@/pages/OnboardingPage';

export const metadata = { title: 'SPARKY - 내 정보 입력' };

export default function Page() {
  return <OnboardingPage />;
}
EOF

# ─────────────── app/chat/page.tsx ────────────────────────────
cat > src/app/chat/page.tsx << 'EOF'
import ChatPage from '@/pages/ChatPage';

export const metadata = { title: 'SPARKY - 청년 정책 AI' };

export default function Page() {
  return <ChatPage />;
}
EOF

# ─────────────── app/layout.tsx ───────────────────────────────
cat > src/app/layout.tsx << 'EOF'
import type { Metadata } from 'next';
import { Inter } from 'next/font/google';
import './globals.css';

const inter = Inter({ subsets: ['latin'] });

export const metadata: Metadata = {
  title: 'SPARKY - 청년 정책 AI',
  description: 'Smart Policy AI Recommend for Korean Youth',
};

export default function RootLayout({ children }: { children: React.ReactNode }) {
  return (
    <html lang="ko">
      <body className={inter.className}>{children}</body>
    </html>
  );
}
EOF

# ─────────────── .env.local ───────────────────────────────────
cat > .env.local << 'EOF'
# AI 서버 (Google Colab ngrok URL 또는 로컬 FastAPI)
NEXT_PUBLIC_AI_SERVER_URL=http://localhost:8000

# Log 서버 (Spring Boot)
NEXT_PUBLIC_LOG_SERVER_URL=http://localhost:8080

# AES-256 암호화 키 (32자 이상 랜덤 문자열로 변경 필수!)
NEXT_PUBLIC_CRYPTO_KEY=sparky-change-this-key-to-random-32chars
EOF

# ─────────────── .env.example ────────────────────────────────
cat > .env.example << 'EOF'
NEXT_PUBLIC_AI_SERVER_URL=https://xxxx-xx-xx.ngrok-free.app
NEXT_PUBLIC_LOG_SERVER_URL=https://your-log-server.railway.app
NEXT_PUBLIC_CRYPTO_KEY=your-random-32-char-secret-key-here
EOF

# ─────────────── .gitignore 보완 ─────────────────────────────
echo ".env.local" >> .gitignore
echo ".env*.local" >> .gitignore

# ─────────────── Dockerfile (AWS EC2 배포용) ──────────────────
cat > Dockerfile << 'EOF'
FROM node:20-alpine AS deps
WORKDIR /app
COPY package*.json ./
RUN npm ci

FROM node:20-alpine AS builder
WORKDIR /app
COPY --from=deps /app/node_modules ./node_modules
COPY . .
RUN npm run build

FROM node:20-alpine AS runner
WORKDIR /app
ENV NODE_ENV=production
COPY --from=builder /app/.next/standalone ./
COPY --from=builder /app/.next/static ./.next/static
COPY --from=builder /app/public ./public
EXPOSE 3000
CMD ["node", "server.js"]
EOF

# ─────────────── next.config.js (standalone output) ──────────
# --- next.config.js (standalone 설정) ---
cat > next.config.js << 'EOF'
/** @type {import('next').NextConfig} */
const nextConfig = {
  output: 'standalone',
};
module.exports = nextConfig;
EOF

# ── 5. 완료 메시지 ────────────────────────────────────────────
echo ""
echo "=============================================="
echo "✅ [5/5] SPARKY 프로젝트 초기화 완료!"
echo "=============================================="
echo ""
echo "📁 생성된 구조:"
echo "   src/"
echo "   ├── app/           (Next.js App Router)"
echo "   ├── components/    (UI/Chat/Onboarding/Layout)"
echo "   ├── constants/     (API, 상수, 칩 옵션)"
echo "   ├── contexts/      (Zustand store)"
echo "   ├── hooks/         (useUserProfile, useChat)"
echo "   ├── pages/         (OnboardingPage, ChatPage)"
echo "   ├── services/      (aiService, logService)"
echo "   ├── types/         (공통 타입 정의)"
echo "   └── utils/         (storage AES, uuid, cn)"
echo ""
echo "🔧 다음 단계:"
echo "   1. .env.local 에서 CRYPTO_KEY 변경"
echo "   2. npm run dev  →  http://localhost:3000"
echo "   3. AI 서버(FastAPI) / Log 서버(Spring Boot) 실행"
echo ""
echo "🐳 AWS 배포 시:"
echo "   docker build -t sparky-fe ."
echo "   docker run -p 3000:3000 sparky-fe"
echo ""
