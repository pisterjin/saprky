import axios from 'axios';
import { API } from '@/constants';
import type { AiRequestBody, AiResponseBody } from '@/types';

const aiClient = axios.create({
  baseURL: API.AI_SERVER,
  timeout: 600000,
});

/**
 * AI 서버(FastAPI/Colab ngrok)에 RAG 질의
 */
export async function queryAiServer(body: AiRequestBody): Promise<AiResponseBody> {
  const { data } = await aiClient.post<AiResponseBody>(
    '/api/chat',
    body
  );
  return data;
}
