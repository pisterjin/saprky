'use client';

import useEmblaCarousel from 'embla-carousel-react';
import { useCallback } from 'react';
import { PolicyCard, calcDday } from './PolicyCard';
import type { PolicyCard as PolicyCardType } from '@/types';

interface Props {
  cards: PolicyCardType[];
  sessionId?: string;
}

/** UI-002: Embla Carousel — 정책 카드 스와이프 */
export function PolicyCarousel({ cards: rawCards, sessionId }: Props) {
  const cards = rawCards.filter(c => calcDday(c.endDate ?? c.period) !== '마감');

  const [emblaRef, emblaApi] = useEmblaCarousel({
    align: 'start',
    dragFree: true,
    active: cards.length > 1,
  });

  const prev = useCallback(() => emblaApi?.scrollPrev(), [emblaApi]);
  const next = useCallback(() => emblaApi?.scrollNext(), [emblaApi]);

  if (cards.length === 0) return null;

  // 단일 카드: 캐러셀 없이 그냥 표시
  if (cards.length === 1) {
    return (
      <div className="mt-2">
        <PolicyCard card={cards[0]} sessionId={sessionId} />
      </div>
    );
  }

  return (
    <div className="mt-2 relative">
      {/* 좌측 화살표 (PC) */}
      <button
        onClick={prev}
        className="hidden sm:flex absolute left-0 top-1/2 -translate-y-1/2 -translate-x-3 z-10
                   w-7 h-7 rounded-full bg-white dark:bg-[#2B2B2B] border border-warm-200 dark:border-[#3A3A3A] shadow items-center justify-center
                   text-warm-600 dark:text-[#999999] hover:bg-primary-100 dark:hover:bg-[#3D3185] transition-colors"
        aria-label="이전"
      >
        ‹
      </button>

      {/* 캐러셀 트랙 */}
      <div className="overflow-hidden" ref={emblaRef}>
        <div className="flex gap-3 px-1 py-1">
          {cards.map((card) => (
            <div key={card.id} className="flex-shrink-0">
              <PolicyCard card={card} sessionId={sessionId} />
            </div>
          ))}
        </div>
      </div>

      {/* 우측 화살표 (PC) */}
      <button
        onClick={next}
        className="hidden sm:flex absolute right-0 top-1/2 -translate-y-1/2 translate-x-3 z-10
                   w-7 h-7 rounded-full bg-white dark:bg-[#2B2B2B] border border-warm-200 dark:border-[#3A3A3A] shadow items-center justify-center
                   text-warm-600 dark:text-[#999999] hover:bg-primary-100 dark:hover:bg-[#3D3185] transition-colors"
        aria-label="다음"
      >
        ›
      </button>
    </div>
  );
}
