"use client";

import { useState, useRef, useEffect } from "react";
import { Header } from "@/components/layout/Header";
import { Chip } from "@/components/ui/Chip";
import { TypewriterText } from "@/components/ui/TypewriterText";
import { useUserProfile } from "@/hooks/useUserProfile";
import { useStore } from "@/contexts/store";
import { AGE_GROUP_OPTIONS, GENDER_OPTIONS, REGION_OPTIONS } from "@/constants";
import { generateUUID } from "@/utils/uuid";
import type { AgeGroup, Gender, Region } from "@/types";

type Step = "age" | "gender" | "region" | "done";

export default function OnboardingPage() {
  const { save } = useUserProfile();
  const { messages, addMessage } = useStore();
  const bottomRef = useRef<HTMLDivElement>(null);

  const [step, setStep] = useState<Step>("age");
  const [ageGroup, setAgeGroup] = useState<AgeGroup | null>(null);
  const [gender, setGender] = useState<Gender | null>(null);
  const [region, setRegion] = useState<Region | null>(null);

  // 최초 렌더 시 존재하던 메시지 ID → 애니메이션 없이 즉시 표시
  const seenIdsRef = useRef<Set<string> | null>(null);
  if (seenIdsRef.current === null) {
    seenIdsRef.current = new Set(messages.map((m) => m.id));
  }

  // 타이핑 애니메이션이 완료된 메시지 ID → 칩 표시 트리거
  const [doneIds, setDoneIds] = useState<Set<string>>(
    () => new Set(messages.map((m) => m.id))
  );
  const markDone = (id: string) =>
    setDoneIds((prev) => new Set(Array.from(prev).concat(id)));

  // 첫 마운트 시 메시지가 없으면 온보딩 인사 추가
  useEffect(() => {
    if (useStore.getState().messages.length === 0) {
      addMessage({
        id: "welcome",
        role: "assistant",
        content:
          "안녕하세요! 저는 SPARKY예요 :)\n맞춤 청년정책을 찾아드릴게요.\n먼저 연령대를 알려주세요!",
        chips: "age",
        timestamp: Date.now(),
      });
    }
  }, []);

  useEffect(() => {
    bottomRef.current?.scrollIntoView({ behavior: "smooth" });
  }, [messages]);

  // 연령대 선택
  const handleAgeSelect = (value: AgeGroup, label: string) => {
    if (step !== "age") return;
    setAgeGroup(value);
    addMessage({
      id: `user-age-${Date.now()}`,
      role: "user",
      content: label,
      timestamp: Date.now(),
    });
    setTimeout(() => {
      setStep("gender");
      addMessage({
        id: `bot-gender-${Date.now()}`,
        role: "assistant",
        content: "성별도 알려주세요!",
        chips: "gender",
        timestamp: Date.now(),
      });
    }, 300);
  };

  // 성별 선택
  const handleGenderSelect = (value: Gender, label: string) => {
    if (step !== "gender") return;
    setGender(value);
    addMessage({
      id: `user-gender-${Date.now()}`,
      role: "user",
      content: label,
      timestamp: Date.now(),
    });
    setTimeout(() => {
      setStep("region");
      addMessage({
        id: `bot-region-${Date.now()}`,
        role: "assistant",
        content: "마지막으로 거주지역을 선택해 주세요!",
        chips: "region",
        timestamp: Date.now(),
      });
    }, 300);
  };

  // 거주지역 선택
  const handleRegionSelect = (value: Region, label: string) => {
    if (step !== "region") return;
    setRegion(value);
    addMessage({
      id: `user-region-${Date.now()}`,
      role: "user",
      content: label,
      timestamp: Date.now(),
    });
    setTimeout(() => {
      setStep("done");
      addMessage({
        id: `bot-done-${Date.now()}`,
        role: "assistant",
        content:
          "완벽해요! 이제 맞춤 청년정책을 찾아드릴게요 :) \n찾고 싶은 정책의 키워드를 알려주세요.",
        timestamp: Date.now(),
      });
    }, 300);
  };

  // 프로필 저장 → AppShell이 ChatPage로 즉시 전환
  useEffect(() => {
    if (step === "done" && ageGroup && gender && region) {
      const t = setTimeout(() => {
        save({ ageGroup, gender, region, uuid: generateUUID() });
      }, 900);
      return () => clearTimeout(t);
    }
  }, [step, ageGroup, gender, region]);

  return (
    <div className="flex flex-col h-full bg-warm-100 dark:bg-[#191919]">
      <Header mode="onboarding" />

      {/* ── 메시지 목록 ────────────────────────────────────── */}
      <main className="flex-1 overflow-y-auto scrollbar-themed px-4 py-4 space-y-3">
        {messages.map((msg) => (
          <div key={msg.id} className="space-y-2">
            {/* 봇 아이콘 — 어시스턴트 말풍선 위 */}
            {msg.role === "assistant" && (
              <div className="flex justify-start pl-1">
                <img src="/bot.svg" alt="SPARKY" width={24} height={24} />
              </div>
            )}

            {/* 말풍선 */}
            <div
              className={`flex ${msg.role === "user" ? "justify-end" : "justify-start"}`}
            >
              <div
                className={`
                  max-w-[82%] rounded-2xl px-4 py-3 text-sm whitespace-pre-wrap leading-relaxed
                  ${
                    msg.role === "user"
                      ? "bg-surface-user text-warm-900 dark:bg-[#5D4CD6] dark:text-[#F3F3F3]"
                      : "bg-surface-ai text-warm-900 dark:bg-[#2B2B2B] dark:text-[#F3F3F3]"
                  }
                `}
              >
                {msg.role === "assistant" && !seenIdsRef.current!.has(msg.id)
                  ? <TypewriterText text={msg.content} onDone={() => markDone(msg.id)} />
                  : msg.content}
              </div>
            </div>

            {/* 연령대 칩 — 애니메이션 완료 후 표시 */}
            {msg.chips === "age" && doneIds.has(msg.id) && (
              <div className="flex flex-wrap gap-2 pl-1">
                {AGE_GROUP_OPTIONS.map((o) => (
                  <Chip
                    key={o.value}
                    label={o.label}
                    selected={ageGroup === o.value}
                    disabled={step !== "age"}
                    onClick={() =>
                      handleAgeSelect(o.value as AgeGroup, o.label)
                    }
                  />
                ))}
              </div>
            )}

            {/* 성별 칩 */}
            {msg.chips === "gender" && doneIds.has(msg.id) && (
              <div className="flex flex-wrap gap-2 pl-1">
                {GENDER_OPTIONS.map((o) => (
                  <Chip
                    key={o.value}
                    label={o.label}
                    selected={gender === o.value}
                    disabled={step !== "gender"}
                    onClick={() =>
                      handleGenderSelect(o.value as Gender, o.label)
                    }
                  />
                ))}
              </div>
            )}

            {/* 거주지역 칩 */}
            {msg.chips === "region" && doneIds.has(msg.id) && (
              <div className="flex flex-wrap gap-2 pl-1">
                {REGION_OPTIONS.map((o) => (
                  <Chip
                    key={o.value}
                    label={o.label}
                    selected={region === o.value}
                    disabled={step !== "region"}
                    onClick={() =>
                      handleRegionSelect(o.value as Region, o.label)
                    }
                  />
                ))}
              </div>
            )}
          </div>
        ))}

        <div ref={bottomRef} />
      </main>

      {/* ── 비활성 타이핑 UI ────────────────────────────────── */}
      <div className="flex-shrink-0 px-4 py-3 bg-surface-card dark:bg-[#2B2B2B] border-t border-warm-200 dark:border-[#252525]">
        <div className="flex items-center gap-2 opacity-40 pointer-events-none select-none">
          <div className="flex-1 px-4 py-2.5 rounded-full border border-warm-300 dark:border-[#333333] text-sm bg-warm-100 dark:bg-[#191919] text-warm-600 dark:text-[#666666]">
            정보를 선택하면 채팅을 시작할 수 있어요
          </div>
          <div className="px-5 py-2.5 rounded-full bg-warm-300 dark:bg-[#444444] text-white text-sm font-semibold flex-shrink-0">
            전송
          </div>
        </div>
      </div>
    </div>
  );
}
