import { API, LOG_API_KEY } from '@/constants';
import type { LogRequestBody, PolicyDomain } from '@/types';

const LOG_HEADERS = {
  'Content-Type': 'application/json',
  'X-API-Key': LOG_API_KEY,
};

/** LG-003: Log 서버에 대화 로그 비동기 전송 (fire-and-forget) */
export function sendLog(body: LogRequestBody): void {
  fetch(`${API.LOG_SERVER}/api/log`, {
    method: 'POST',
    headers: LOG_HEADERS,
    body: JSON.stringify(body),
  }).catch((err) => {
    console.warn('[LogService] 로그 전송 실패 (무시됨):', err);
  });
}

/** 정책 카드 클릭 이벤트 전송 (fire-and-forget) */
export function sendPolicyClick(sessionId: string, policyId: string, policyTitle: string, category: PolicyDomain): void {
  fetch(`${API.LOG_SERVER}/api/click`, {
    method: 'POST',
    headers: LOG_HEADERS,
    body: JSON.stringify({
      session_id: sessionId,
      policy_id: policyId,
      policy_title: policyTitle,
      category,
      clicked_at: new Date().toISOString().replace('Z', ''),
    }),
  }).catch((err) => {
    console.warn('[LogService] 클릭 이벤트 전송 실패 (무시됨):', err);
  });
}
