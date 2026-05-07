'use client';

import { useState, useCallback } from 'react';
import { useStore } from '@/contexts/store';
import { queryAiServer } from '@/services/aiService';
import { sendLog } from '@/services/logService';
import type { ChatMessage } from '@/types';

export function useChat() {
  const { userProfile, messages, addMessage, setDomain, candidateIds, setCandidateIds } = useStore();
  const [loading,      setLoading]      = useState(false);
  const [error,        setError]         = useState<string | null>(null);
  const [lastQuestion, setLastQuestion]  = useState<string>('');

  const send = useCallback(async (question: string) => {
    if (!userProfile || loading) return;
    setError(null);
    setLoading(true);
    setLastQuestion(question);

    const userMsg: ChatMessage = {
      id: `u_${Date.now()}`,
      role: 'user',
      content: question,
      timestamp: Date.now(),
    };
    addMessage(userMsg);

    const startTime = Date.now();
    try {
      const res = await queryAiServer({
        question,
        userProfile,
        conversationHistory: messages,
        candidateIds,           // 이전 턴 후보 풀 전달
      });
      const responseTimeMs = Date.now() - startTime;

      const assistantMsg: ChatMessage = {
        id: `a_${Date.now()}`,
        role: 'assistant',
        content: res.answer,
        policyCards:   res.is_clarifying ? [] : res.cards,
        isClarifying:  res.is_clarifying,
        domain: res.domain,
        timestamp: Date.now(),
        chips: (res.chips as ChatMessage['chips']) ?? undefined,
      };
      addMessage(assistantMsg);
      setDomain(res.domain);
      setCandidateIds(res.candidateIds);  // 현재 턴 후보 풀 저장

      // fire-and-forget 로그 전송 (LG-003)
      const turnNo = messages.filter(m => m.role === 'user').length + 1;
      sendLog({
        uuid:           userProfile.uuid,
        turnNo,
        question,
        answer:         res.answer,
        domain:         res.domain,
        policyIds:      res.policyIds,
        userProfile,
        isClarifying:   res.is_clarifying,
        responseTimeMs,
      });
    } catch {
      setError('AI 서버 연결에 실패했어요. 잠시 후 다시 시도해 주세요.');
    } finally {
      setLoading(false);
    }
  }, [userProfile, messages, loading]);

  return { send, loading, error, retry: () => { setError(null); if (lastQuestion) send(lastQuestion); } };
}
