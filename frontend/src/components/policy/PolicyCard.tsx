'use client';

import { useState, useRef, useLayoutEffect } from 'react';
import { cn } from '@/utils/cn';
import type { PolicyCard as PolicyCardType } from '@/types';
import { sendPolicyClick } from '@/services/logService';

interface Props {
  card: PolicyCardType;
  sessionId?: string;
}

const BADGE_COLOR: Record<string, string> = {
  '취업':    'bg-[#D6E8C8] text-[#18341D] dark:bg-[#1E3A5F] dark:text-[#60A5FA]',
  '주거':    'bg-[#EAE1BD] text-[#5E3B1D] dark:bg-[#1E3A2F] dark:text-[#4ADE80]',
  '금융':    'bg-[#F0E8D0] text-[#5E3B1D] dark:bg-[#3A2E10] dark:text-[#FBBF24]',
  '교육':    'bg-[#D6E8C8] text-[#011B12] dark:bg-[#3D3185] dark:text-[#8888B8]',
  '복지':    'bg-[#EAE1BD] text-[#18341D] dark:bg-[#3D1F35] dark:text-[#F472B6]',
  '판단불가': 'bg-[#E8E4D8] text-[#8E8051] dark:bg-[#2A2A2A] dark:text-[#999999]',
};

export function calcDday(endDate?: string, period?: string): string | null {
  // endDate: raw bizPrdEndYmd (YYYYMMDD or YYYYMM)
  // period:  formatted string (e.g. "20260101 ~ 20261231", "상시", "2026.07")
  let raw = (endDate || '').trim();

  if (!raw && period) {
    const p = period.trim();
    const rangeMatch = p.match(/~\s*(.+)$/);
    if (rangeMatch) {
      raw = rangeMatch[1].trim();
    } else if (/상시|연중|수시|별도|미정/.test(p)) {
      return '상시';
    } else {
      raw = p;
    }
  }

  if (!raw) return '상시';
  if (/상시|연중|수시|별도/.test(raw)) return '상시';

  // 점(.) 제거 후 숫자만 있는지 확인
  const normalized = raw.replace(/\./g, '');

  // YYYYMMDD (8자리) → 일단위 D-day
  if (/^\d{8}$/.test(normalized)) {
    const y = normalized.slice(0, 4);
    const m = normalized.slice(4, 6);
    const d = normalized.slice(6, 8);
    const end = new Date(`${y}-${m}-${d}`);
    if (isNaN(end.getTime())) return '상시';
    const diff = Math.ceil((end.getTime() - Date.now()) / 86400000);
    if (diff < 0)  return '마감';
    if (diff === 0) return 'D-day';
    return `D-${diff}`;
  }

  // YYYYMM (6자리) → 월단위 D-x월
  if (/^\d{6}$/.test(normalized)) {
    const year  = parseInt(normalized.slice(0, 4));
    const month = parseInt(normalized.slice(4, 6)) - 1; // 0-indexed
    const now   = new Date();
    const diff  = (year - now.getFullYear()) * 12 + (month - now.getMonth());
    if (diff < 0)  return '마감';
    if (diff === 0) return 'D-0월';
    return `D-${diff}월`;
  }

  return '상시';
}

export function PolicyCard({ card, sessionId }: Props) {
  const [open, setOpen] = useState(false);
  const textRef = useRef<HTMLParagraphElement>(null);
  const [isOverflow, setIsOverflow] = useState(false);

  useLayoutEffect(() => {
    if (textRef.current) {
      setIsOverflow(textRef.current.scrollHeight > textRef.current.clientHeight);
    }
  }, [card.summary]);

  const dday   = calcDday(card.endDate, card.period);
  const isOver = dday === '마감';

  return (
    <div className="relative w-[280px] min-h-[260px] bg-[#F5F0E0] dark:bg-[#1C1B2E] rounded-2xl shadow-lg border border-[#C8B99A] dark:border-[#38374E] p-4 flex flex-col gap-3">
      {/* 헤더: 도메인 태그 + D-day 배지 */}
      <div className="flex items-center justify-between">
        <span className={cn('text-xs font-semibold px-2 py-0.5 rounded-full', BADGE_COLOR[card.domain] ?? BADGE_COLOR['판단불가'])}>
          {card.domain}
        </span>
        {dday && (
          <span className={cn(
            'text-xs font-bold px-2 py-0.5 rounded-full',
            isOver
              ? 'bg-[#E8E4D8] text-[#8E8051] dark:bg-[#3A3A3A] dark:text-[#888888]'
              : dday === '상시'
                ? 'bg-[#D6E8C8] text-[#18341D] dark:bg-[#1E3A2F] dark:text-[#4ADE80]'
                : 'bg-[#EAE1BD] text-[#5E3B1D] dark:bg-[#3D3185] dark:text-[#8888B8]'
          )}>
            {dday}
          </span>
        )}
      </div>

      {/* 정책명 */}
      <h3 className="text-sm font-bold text-[#011B12] dark:text-white leading-snug line-clamp-2 min-h-[2.75em]">
        {card.title}
      </h3>

      {/* 정보 그리드 */}
      <div className="grid grid-cols-2 gap-y-1.5 text-xs">
        <span className="text-[#8E8051] dark:text-[#888898]">신청기간</span>
        <span className="text-[#18341D] dark:text-[#D2D1DE] font-medium truncate">{card.period}</span>
        <span className="text-[#8E8051] dark:text-[#888898]">지원대상</span>
        <span className="text-[#18341D] dark:text-[#D2D1DE] font-medium truncate">{card.target}</span>
        <span className="text-[#8E8051] dark:text-[#888898]">지원내용</span>
        <span className="text-[#18341D] dark:text-[#D2D1DE] font-medium truncate">{card.benefit}</span>
      </div>

      {/* 측정용 숨김 요소 (overflow 감지) */}
      <p
        ref={textRef}
        className="text-xs leading-relaxed line-clamp-1 invisible absolute w-full pointer-events-none"
        aria-hidden
      >
        {card.summary}
      </p>

      {/* 상세 내용: 1줄 이하면 그대로, 넘치면 아코디언 */}
      <div className="border-t border-[#C8B99A] dark:border-[#38374E] pt-2">
        {isOverflow ? (
          <div className={cn(
            'rounded-xl border transition-colors duration-200',
            open
              ? 'border-[#8E8051] bg-[#D6E8C8] dark:border-[#484768] dark:bg-[#232235]'
              : 'border-[#C8B99A] bg-[#EAE1BD] dark:border-[#38374E] dark:bg-[#191826]'
          )}>
            <button
              onClick={() => setOpen(o => !o)}
              className="w-full flex items-center justify-between text-xs text-[#18341D] dark:text-[#8888B8] font-semibold px-3 py-2 hover:text-[#5E3B1D] dark:hover:text-[#A9A9C4] transition-colors active:scale-[0.98]"
            >
              <span>상세 내용</span>
              <img
                src="/plus.svg"
                alt="toggle"
                width={14}
                height={14}
                className={cn(
                  'policy-icon transition-transform duration-300',
                  open ? 'rotate-45' : 'rotate-0'
                )}
              />
            </button>
            <div className={cn(
              'grid transition-all duration-300 ease-in-out',
              open ? 'grid-rows-[1fr] opacity-100' : 'grid-rows-[0fr] opacity-0'
            )}>
              <div className="overflow-hidden">
                <div className="px-3 pb-3">
                  <div className="border-t border-[#C8B99A] dark:border-[#38374E] pt-2">
                    <p className="text-xs text-[#5E3B1D] dark:text-[#AEADBE] leading-relaxed">
                      {card.summary}
                    </p>
                  </div>
                </div>
              </div>
            </div>
          </div>
        ) : (
          <p className="text-xs text-[#5E3B1D] dark:text-[#AEADBE] leading-relaxed">
            {card.summary}
          </p>
        )}
      </div>

      {/* 신청 링크 */}
      {card.applyUrl ? (
        <a
          href={card.applyUrl}
          target="_blank"
          rel="noopener noreferrer"
          onClick={() => sessionId && sendPolicyClick(sessionId, card.id, card.title, card.domain)}
          className="mt-auto block text-center text-xs font-semibold text-[#18341D] dark:text-[#8888B8] border border-[#8E8051] dark:border-[#484768] rounded-xl py-2 hover:bg-[#D6E8C8] dark:hover:bg-[#323148] transition-colors"
        >
          공식 사이트 바로가기
        </a>
      ) : (
        <button disabled className="mt-auto block text-center text-xs text-[#8E8051] dark:text-[#555577] border border-[#C8B99A] dark:border-[#333355] rounded-xl py-2 cursor-not-allowed opacity-50">
          링크 없음
        </button>
      )}
    </div>
  );
}
