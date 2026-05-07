'use client';

import { useEffect } from 'react';

/**
 * 모바일 키보드 등장/사라짐 시 실제 가시 영역 높이를 --viewport-height CSS 변수에 동기화.
 * visualViewport API 우선 사용, 미지원 시 window.innerHeight fallback.
 */
export function MobileViewportFix() {
  useEffect(() => {
    const vv = window.visualViewport;

    const update = () => {
      const h = vv ? vv.height : window.innerHeight;
      document.documentElement.style.setProperty('--viewport-height', `${h}px`);
    };

    update();
    vv?.addEventListener('resize', update);
    window.addEventListener('resize', update);

    return () => {
      vv?.removeEventListener('resize', update);
      window.removeEventListener('resize', update);
    };
  }, []);

  return null;
}
