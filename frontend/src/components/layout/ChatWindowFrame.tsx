'use client';

import { useEffect, useState } from 'react';
import type { CSSProperties } from 'react';

const SM_BREAKPOINT = 640; // Tailwind sm 기준

/**
 * 모바일: position fixed로 뷰포트 최상단부터 키보드 바로 위까지 꽉 채움.
 *   - visualViewport.height  → 키보드 위 가시 영역 높이
 *   - visualViewport.offsetTop → iOS Safari 스크롤 오프셋 보정
 * sm 이상(데스크탑): CSS 클래스(sm:h-[760px])가 그대로 적용됨.
 */
export function ChatWindowFrame({ children }: { children: React.ReactNode }) {
  const [mobileStyle, setMobileStyle] = useState<CSSProperties | null>(null);

  useEffect(() => {
    const vv = window.visualViewport;

    const update = () => {
      if (window.innerWidth >= SM_BREAKPOINT) {
        setMobileStyle(null);
        return;
      }
      const height    = vv?.height    ?? window.innerHeight;
      const offsetTop = vv?.offsetTop ?? 0;

      setMobileStyle({
        position : 'fixed',
        top      : `${offsetTop}px`,
        left     : 0,
        right    : 0,
        width    : '100%',
        height   : `${height}px`,
      });
    };

    update();
    vv?.addEventListener('resize', update);
    window.addEventListener('resize', update);

    return () => {
      vv?.removeEventListener('resize', update);
      window.removeEventListener('resize', update);
    };
  }, []);

  return (
    <div
      className="
        relative flex flex-col w-full bg-warm-100 dark:bg-[#191919] overflow-hidden
        h-[100dvh]
        sm:w-[430px] sm:h-[760px] sm:max-h-[92dvh]
        sm:rounded-3xl
        sm:shadow-[0_24px_80px_rgba(0,0,0,0.35),0_0_0_1px_rgba(255,255,255,0.08)]
      "
      style={mobileStyle ?? undefined}
    >
      {children}
    </div>
  );
}
