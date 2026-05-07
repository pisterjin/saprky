import { useEffect } from 'react';
import { useStore } from '@/contexts/store';
import { loadUserProfile, saveUserProfile, clearUserProfile } from '@/utils/storage';
import type { UserProfile } from '@/types';

/** 사용자 프로필 로드/저장/초기화 훅 */
export function useUserProfile() {
  const { userProfile, setUserProfile } = useStore();

  // 마운트 시 localStorage 복호화 로드
  useEffect(() => {
    if (!userProfile) {
      const loaded = loadUserProfile();
      if (loaded) setUserProfile(loaded);
    }
  }, []);

  const save = (profile: UserProfile) => {
    saveUserProfile(profile);
    setUserProfile(profile);
  };

  const clear = () => {
    clearUserProfile();
    setUserProfile(null);
  };

  return { userProfile, save, clear };
}
