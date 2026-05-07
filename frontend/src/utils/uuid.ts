import { v4 as uuidv4 } from 'uuid';

/** 새 세션 UUID 생성 */
export function generateUUID(): string {
  return uuidv4();
}
