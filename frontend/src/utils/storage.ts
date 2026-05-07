import CryptoJS from 'crypto-js';
import { CRYPTO_KEY, STORAGE_KEY } from '@/constants';
import type { UserProfile } from '@/types';

/** localStorage AES-256 암호화 저장 */
export function saveUserProfile(profile: UserProfile): void {
  const json = JSON.stringify(profile);
  const encrypted = CryptoJS.AES.encrypt(json, CRYPTO_KEY).toString();
  localStorage.setItem(STORAGE_KEY.USER_PROFILE, encrypted);
}

/** localStorage AES-256 복호화 로드 */
export function loadUserProfile(): UserProfile | null {
  try {
    const encrypted = localStorage.getItem(STORAGE_KEY.USER_PROFILE);
    if (!encrypted) return null;
    const bytes = CryptoJS.AES.decrypt(encrypted, CRYPTO_KEY);
    const json = bytes.toString(CryptoJS.enc.Utf8);
    if (!json) return null;
    return JSON.parse(json) as UserProfile;
  } catch {
    return null;
  }
}

/** localStorage 초기화 (내 정보 파기) */
export function clearUserProfile(): void {
  localStorage.removeItem(STORAGE_KEY.USER_PROFILE);
}
