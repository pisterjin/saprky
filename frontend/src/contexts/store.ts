import { create } from 'zustand';
import type { UserProfile, ChatMessage, PolicyDomain } from '@/types';

interface AppState {
  userProfile: UserProfile | null;
  setUserProfile: (profile: UserProfile | null) => void;

  messages: ChatMessage[];
  addMessage: (msg: ChatMessage) => void;
  clearMessages: () => void;

  currentDomain: PolicyDomain | null;
  setDomain: (domain: PolicyDomain) => void;

  // AND 교집합용 후보 풀
  candidateIds: string[];
  setCandidateIds: (ids: string[]) => void;
}

export const useStore = create<AppState>((set) => ({
  userProfile: null,
  setUserProfile: (profile) => set({ userProfile: profile }),

  messages: [],
  addMessage: (msg) => set((s) => ({ messages: [...s.messages, msg] })),
  clearMessages: () =>
    set({
      messages: [],
      currentDomain: null,
      candidateIds: [],   // 대화 초기화 시 후보 풀도 리셋
    }),

  currentDomain: null,
  setDomain: (domain) => set({ currentDomain: domain }),

  candidateIds: [],
  setCandidateIds: (ids) => set({ candidateIds: ids }),
}));
