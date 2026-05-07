'use client';

import { useState, useEffect } from 'react';
import { useStore } from '@/contexts/store';
import { useUserProfile } from '@/hooks/useUserProfile';
import { ConfirmModal } from '@/components/ui/ConfirmModal';

interface HeaderProps {
  mode?: 'chat' | 'onboarding';
}

/**
 * Header
 * - onboarding: SPARKY 타이틀 + "내 정보 수정" 비활성 버튼 + 다크모드 토글
 * - chat: SPARKY 타이틀 + "내 정보 수정" 활성 버튼 (좌측) + 다크모드 토글 (우측)
 */
export function Header({ mode = 'chat' }: HeaderProps) {
  const { clearMessages } = useStore();
  const { clear: clearProfile } = useUserProfile();
  const [showModal, setShowModal] = useState(false);
  const [isDark, setIsDark] = useState(false);

  useEffect(() => {
    const saved = localStorage.getItem('theme');
    const prefersDark = window.matchMedia('(prefers-color-scheme: dark)').matches;
    if (saved === 'dark' || (!saved && prefersDark)) {
      document.documentElement.classList.add('dark');
      setIsDark(true);
    }
  }, []);

  const toggleDark = () => {
    const html = document.documentElement;
    if (isDark) {
      html.classList.remove('dark');
      localStorage.setItem('theme', 'light');
      setIsDark(false);
    } else {
      html.classList.add('dark');
      localStorage.setItem('theme', 'dark');
      setIsDark(true);
    }
  };

  const handleConfirmClear = () => {
    clearProfile();
    clearMessages();
    setShowModal(false);
  };

  return (
    <>
      <header className="sticky top-0 z-10 bg-[var(--surface-header)] border-b border-warm-200 dark:border-[#20485E] px-4 py-3 grid grid-cols-3 items-center">
        {/* 좌측: 내 정보 수정 */}
        <div className="flex justify-start">
          {mode === 'chat' ? (
            <button
              onClick={() => setShowModal(true)}
              className="text-xs font-medium text-warm-600 dark:text-[var(--warm-600)] border border-warm-600 dark:border-[var(--warm-600)] rounded-lg px-3 py-1.5 hover:bg-warm-200 dark:hover:bg-[#0C2432] hover:text-warm-900 dark:hover:text-[var(--primary)] transition-colors"
            >
              내 정보 수정
            </button>
          ) : (
            /* 온보딩: 비활성 버튼 */
            <button
              disabled
              className="text-xs font-medium text-warm-300 dark:text-[var(--warm-300)] border border-warm-200 dark:border-[#20485E] rounded-lg px-3 py-1.5 cursor-not-allowed opacity-50"
            >
              내 정보 수정
            </button>
          )}
        </div>

        {/* 중앙: SPARKY */}
        <div className="flex justify-center">
          <span
            className="text-[21px] text-[var(--primary)] tracking-wide"
            style={{ fontFamily: "'Paperlogy', sans-serif", fontWeight: 900 }}
          >
            SPARKY
          </span>
        </div>

        {/* 우측: 다크모드 토글 — 필 슬라이더 */}
        <div className="flex justify-end">
          <button
            onClick={toggleDark}
            aria-label={isDark ? '라이트 모드로 전환' : '다크 모드로 전환'}
            className="relative flex items-center w-[60px] h-[24px] rounded-full transition-colors duration-300 overflow-hidden flex-shrink-0"
            style={{ background: isDark ? '#1C1C2E' : '#FFBB00' }}
          >
            {/* 텍스트 */}
            <span
              className="absolute text-[8px] font-bold tracking-wider transition-all duration-300 select-none"
              style={{
                left:  isDark ? 'auto' : '7px',
                right: isDark ? '7px' : 'auto',
                color: isDark ? '#7070A0' : '#FFFFFF',
              }}
            >
              {isDark ? 'NIGHT' : 'DAY'}
            </span>

            {/* 슬라이딩 원형 knob */}
            <span
              className="absolute flex items-center justify-center w-[20px] h-[20px] rounded-full bg-white shadow transition-all duration-300"
              style={{ left: isDark ? '2px' : 'calc(100% - 22px)' }}
            >
              {isDark ? (
                /* 달 아이콘 */
                <svg width="10" height="10" viewBox="0 0 24 24" fill="#1C1C2E">
                  <path d="M21 12.79A9 9 0 1 1 11.21 3 7 7 0 0 0 21 12.79z"/>
                </svg>
              ) : (
                /* 태양 아이콘 */
                <svg width="10" height="10" viewBox="0 0 24 24" fill="none" stroke="#FFBB00" strokeWidth="2.5" strokeLinecap="round">
                  <circle cx="12" cy="12" r="4" fill="#FFBB00"/>
                  <line x1="12" y1="2"  x2="12" y2="5"/>
                  <line x1="12" y1="19" x2="12" y2="22"/>
                  <line x1="2"  y1="12" x2="5"  y2="12"/>
                  <line x1="19" y1="12" x2="22" y2="12"/>
                  <line x1="4.93" y1="4.93" x2="7.05" y2="7.05"/>
                  <line x1="16.95" y1="16.95" x2="19.07" y2="19.07"/>
                  <line x1="4.93" y1="19.07" x2="7.05" y2="16.95"/>
                  <line x1="16.95" y1="7.05" x2="19.07" y2="4.93"/>
                </svg>
              )}
            </span>
          </button>
        </div>
      </header>

      {/* RI-002: 확인 모달 (chat 모드에서만) */}
      {mode === 'chat' && showModal && (
        <ConfirmModal
          message={`내 정보를 초기화하면 처음부터 다시 선택해야 해요.\n정말 초기화할까요?`}
          onConfirm={handleConfirmClear}
          onCancel={() => setShowModal(false)}
        />
      )}
    </>
  );
}
