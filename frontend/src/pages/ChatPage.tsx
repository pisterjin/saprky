"use client";

import { useEffect, useRef, useState } from "react";
import { Header } from "@/components/layout/Header";
import { LoadingDots } from "@/components/ui/LoadingDots";
import { PolicyCarousel } from "@/components/policy/PolicyCarousel";
import { Chip } from "@/components/ui/Chip";
import { TypewriterText, splitFirstSentence } from "@/components/ui/TypewriterText";
import { useChat } from "@/hooks/useChat";
import { useStore } from "@/contexts/store";
import { maskText } from "@/utils/maskText";
import {
  MAX_INPUT_LENGTH,
  WELCOME_MESSAGE,
  AGE_GROUP_OPTIONS,
  GENDER_OPTIONS,
  REGION_OPTIONS,
  EMPLOYMENT_OPTIONS,
} from "@/constants";

function formatTime(ts: number): string {
  const d = new Date(ts);
  const h = d.getHours();
  const ampm = h < 12 ? '오전' : '오후';
  const h12 = h % 12 || 12;
  const mm = String(d.getMinutes()).padStart(2, '0');
  const ss = String(d.getSeconds()).padStart(2, '0');
  return `${ampm} ${h12}:${mm}:${ss}`;
}

export default function ChatPage() {
  const { messages, addMessage, userProfile } = useStore();
  const { send, loading, error, retry } = useChat();

  const inputRef = useRef<HTMLInputElement>(null);
  const bottomRef = useRef<HTMLDivElement>(null);
  const [charCount, setCharCount] = useState(0);

  // 최초 렌더 시 존재하던 메시지 ID → 애니메이션 없이 즉시 표시
  const seenIdsRef = useRef<Set<string> | null>(null);
  if (seenIdsRef.current === null) {
    seenIdsRef.current = new Set(messages.map((m) => m.id));
  }

  // 타이핑 애니메이션이 완료된 메시지 ID → 칩 표시 트리거
  const [doneIds, setDoneIds] = useState<Set<string>>(
    () => new Set(messages.map((m) => m.id)),
  );
  const markDone = (id: string) =>
    setDoneIds((prev) => new Set(Array.from(prev).concat(id)));

  // employment / income 칩 선택 추적 (msgId → selectedValue)
  const [chipSelections, setChipSelections] = useState<Record<string, string>>({});
  const handleChipSend = (msgId: string, value: string, label: string) => {
    setChipSelections((prev) => ({ ...prev, [msgId]: value }));
    send(label);
  };

  // 재방문(localStorage에 프로필 있음)시 메시지가 비어 있으면 채팅 welcome 추가
  useEffect(() => {
    if (useStore.getState().messages.length === 0) {
      addMessage({
        id: "welcome",
        role: "assistant",
        content: WELCOME_MESSAGE,
        timestamp: Date.now(),
      });
    }
  }, []);

  useEffect(() => {
    bottomRef.current?.scrollIntoView({ behavior: "smooth" });
  }, [messages, loading, doneIds]);

  useEffect(() => {
    if (!loading && window.innerWidth >= 640) inputRef.current?.focus();
  }, [loading]);

  const handleSend = () => {
    const val = inputRef.current?.value.trim();
    if (!val || loading) return;
    send(val);
    if (inputRef.current) {
      inputRef.current.value = "";
      setCharCount(0);
      inputRef.current.focus();
    }
  };

  return (
    <div className="flex-1 flex flex-col overflow-hidden min-h-0 bg-warm-100 dark:bg-[#0B0F15]">
      <Header />

      {/* ── 메시지 목록 ─────────────────────────────────────── */}
      <main className="flex-1 min-h-0 overflow-y-auto scrollbar-themed px-4 py-4 space-y-4">
        {messages.map((msg) => (
          <div key={msg.id} className="space-y-2">
            {/* 봇 아이콘 — 어시스턴트 말풍선 위 */}
            {msg.role === "assistant" && (
              <div className="flex justify-start pl-1">
                <img src="/bot.svg" alt="SPARKY" width={36} height={36} />
              </div>
            )}

            {/* 말풍선 */}
            <div
              className={`flex ${msg.role === "user" ? "justify-end" : "justify-start"}`}
            >
              {msg.role === "assistant" ? (
                <div className="flex flex-col items-start gap-1 max-w-[82%]">
                  <div className="rounded-2xl px-4 py-3 text-sm whitespace-pre-wrap leading-relaxed bg-surface-ai text-warm-900 dark:bg-[#0C2432] dark:text-[#EBF7F3]">
                    {!seenIdsRef.current!.has(msg.id) ? (
                      <TypewriterText
                        text={msg.content}
                        onDone={() => markDone(msg.id)}
                        boldFirstSentence
                      />
                    ) : (
                      (() => {
                        const [first, rest] = splitFirstSentence(msg.content);
                        return <><strong>{first}</strong>{rest ? <><br />{rest}</> : null}</>;
                      })()
                    )}
                  </div>
                  <p className="text-[10px] text-warm-300 dark:text-[#9AB6C0] pl-1">
                    {formatTime(msg.timestamp)}
                  </p>
                </div>
              ) : (
                <div className="max-w-[82%] rounded-2xl px-4 py-3 text-sm whitespace-pre-wrap leading-relaxed bg-surface-user text-warm-900 dark:bg-[#20485E] dark:text-[#EBF7F3]">
                  {maskText(msg.content)}
                </div>
              )}
            </div>

            {/* 온보딩 칩 — 챗 진입 후 disabled 상태로 표시 (애니메이션 완료 후) */}
            {msg.chips === "age" && doneIds.has(msg.id) && (
              <div className="flex flex-wrap gap-2 pl-1">
                {AGE_GROUP_OPTIONS.map((o) => (
                  <Chip
                    key={o.value}
                    label={o.label}
                    selected={userProfile?.ageGroup === o.value}
                    disabled
                  />
                ))}
              </div>
            )}
            {msg.chips === "gender" && doneIds.has(msg.id) && (
              <div className="flex flex-wrap gap-2 pl-1">
                {GENDER_OPTIONS.map((o) => (
                  <Chip
                    key={o.value}
                    label={o.label}
                    selected={userProfile?.gender === o.value}
                    disabled
                  />
                ))}
              </div>
            )}
            {msg.chips === "region" && doneIds.has(msg.id) && (
              <div className="flex flex-wrap gap-2 pl-1">
                {REGION_OPTIONS.map((o) => (
                  <Chip
                    key={o.value}
                    label={o.label}
                    selected={userProfile?.region === o.value}
                    disabled
                  />
                ))}
              </div>
            )}

            {msg.chips === "employment" && doneIds.has(msg.id) && (
              <div className="flex flex-wrap gap-2 pl-1">
                {EMPLOYMENT_OPTIONS.map((o) => (
                  <Chip
                    key={o.value}
                    label={o.label}
                    selected={chipSelections[msg.id] === o.value}
                    disabled={!!chipSelections[msg.id] || loading}
                    onClick={() => handleChipSend(msg.id, o.value, o.label)}
                  />
                ))}
              </div>
            )}


            {/* 정책 카드 캐러셀 */}
            {msg.role === "assistant" &&
              !msg.isClarifying &&
              msg.policyCards &&
              msg.policyCards.length > 0 && (
                <div className="pl-1">
                  <PolicyCarousel cards={msg.policyCards} sessionId={userProfile?.uuid} />
                </div>
              )}

            {/* ER-003: 빈 결과 안내 */}
            {msg.role === "assistant" &&
              !msg.isClarifying &&
              msg.policyCards !== undefined &&
              msg.policyCards.length === 0 &&
              msg.id !== "welcome" && (
                <div className="pl-1 flex items-center gap-2 text-xs text-warm-600 dark:text-[#9AB6C0] py-1">
                  <span>🔍</span>
                  <span>조건에 맞는 정책을 찾지 못했어요.</span>
                </div>
              )}
          </div>
        ))}

        {/* ER-001: 로딩 */}
        {loading && (
          <div className="flex justify-start">
            <div className="bg-surface-ai dark:bg-[#0C2432] rounded-2xl">
              <LoadingDots />
            </div>
          </div>
        )}

        {/* ER-002: 에러 + 재시도 */}
        {error && (
          <div className="flex justify-start">
            <div className="bg-surface-ai dark:bg-[#0C2432] rounded-2xl px-4 py-3 text-sm text-warm-900 dark:text-[#EBF7F3] flex items-center gap-3">
              <span>⚠️ {error}</span>
              <button
                onClick={retry}
                className="text-primary-500 dark:text-[#F94224] font-semibold text-xs underline"
              >
                재시도
              </button>
            </div>
          </div>
        )}

        <div ref={bottomRef} />
      </main>

      {/* ── 입력 영역 ─────────────────────────────────────── */}
      <div className="flex-shrink-0 px-4 py-3 bg-surface-card dark:bg-[#0C2432] border-t border-warm-200 dark:border-[#20485E]">
        <div className="flex items-center gap-2">
          <div className="flex-1 relative">
            <input
              ref={inputRef}
              type="text"
              maxLength={MAX_INPUT_LENGTH}
              placeholder="궁금한 정책을 물어보세요..."
              className="w-full px-4 py-2.5 rounded-full border border-warm-300 dark:border-[#20485E] text-sm
                         bg-warm-100 dark:bg-[#0B0F15] text-warm-900 dark:text-[#EBF7F3] placeholder:text-warm-600 dark:placeholder:text-[#9AB6C0]
                         focus:outline-none focus:border-primary-400 dark:focus:border-[#F94224] transition-colors"
              onKeyDown={(e) => e.key === "Enter" && handleSend()}
              onChange={(e) => setCharCount(e.target.value.length)}
              disabled={loading}
            />
            {charCount >= 400 && (
              <span
                className={`
                absolute right-4 top-1/2 -translate-y-1/2 text-[10px] font-medium
                ${charCount >= MAX_INPUT_LENGTH ? "text-status-error" : "text-warm-600 dark:text-[#9AB6C0]"}
              `}
              >
                {charCount}/{MAX_INPUT_LENGTH}
              </span>
            )}
          </div>
          <button
            onClick={handleSend}
            onMouseDown={(e) => e.preventDefault()}
            disabled={loading || charCount === 0}
            className="px-5 py-2.5 rounded-full bg-primary-500 dark:bg-[#F94224] text-white text-sm font-semibold
                       hover:bg-primary-400 dark:hover:bg-[#FF6B50] disabled:bg-warm-300 dark:disabled:bg-[#41728B] disabled:cursor-not-allowed
                       transition-colors flex-shrink-0"
          >
            전송
          </button>
        </div>
      </div>
    </div>
  );
}
