'use client';

import { useState, useEffect } from 'react';
import { useStore } from '@/contexts/store';
import { loadUserProfile } from '@/utils/storage';
import { PrivacyBottomSheet } from '@/components/ui/PrivacyBottomSheet';
import OnboardingPage from '@/pages/OnboardingPage';
import ChatPage from '@/pages/ChatPage';

/**
 * AppShell — 온보딩 ↔ 챗 화면을 페이지 이동 없이 조건부 렌더링
 * 애니메이션 없이 즉시 전환 — 흐름이 끊기지 않는 느낌
 */
export function AppShell() {
  const { userProfile, setUserProfile } = useStore();
  const [ready, setReady] = useState(false);
  const [showPrivacy, setShowPrivacy] = useState(false);

  useEffect(() => {
    if (!userProfile) {
      const loaded = loadUserProfile();
      if (loaded) setUserProfile(loaded);
    }
    setReady(true);
  }, []);

  if (!ready) {
    return <div className="flex-1 bg-warm-100 dark:bg-[#191919]" />;
  }

  return (
    <>
      <div className="flex-1 flex flex-col min-h-0">
        {userProfile ? <ChatPage /> : <OnboardingPage />}
      </div>

      {/* 개인정보처리방침 풋터 — 온보딩·챗 공통 고정 */}
      <div className="flex-shrink-0 px-4 py-2 bg-surface-card dark:bg-[#2B2B2B] border-t border-warm-200 dark:border-[#252525] text-center">
        <p className="text-[11px] text-warm-600 dark:text-[#999999]">
          연령대·성별·지역 코드만 저장됩니다.{' '}
          <button
            onClick={() => setShowPrivacy(true)}
            className="underline hover:text-primary-500 dark:hover:text-[#A78BFA] transition-colors"
          >
            개인정보처리방침
          </button>
        </p>
      </div>

      <PrivacyBottomSheet open={showPrivacy} onClose={() => setShowPrivacy(false)} />
    </>
  );
}
