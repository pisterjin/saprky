import type { Metadata } from 'next';
import './globals.css';

export const metadata: Metadata = {
  title: 'SPARKY - 청년 정책 AI',
  description: 'Smart Policy AI Recommend for Korean Youth',
};

export default function RootLayout({ children }: { children: React.ReactNode }) {
  return (
    <html lang="ko">
      <body className="min-h-[100dvh] flex items-center justify-center">

        {/* ── 배경 페이지 ─────────────────────────────────── */}
        <div className="fixed inset-0 -z-10 overflow-hidden">
          <div className="absolute inset-0 bg-gradient-to-br from-[#3727AB] via-[#4B38CC] to-[#2D1F8F] dark:from-[#0D0D0D] dark:via-[#191919] dark:to-[#0D0D0D]" />
          <div className="absolute -top-32 -left-32 w-80 h-80 rounded-full bg-white/5 blur-2xl" />
          <div className="absolute -bottom-32 -right-32 w-96 h-96 rounded-full bg-white/5 blur-2xl" />
          <div className="absolute inset-0 flex items-center justify-center pointer-events-none select-none">
            <span className="text-white/[0.04] font-black text-[18vw] tracking-widest">SPARKY</span>
          </div>
        </div>

        {/* ── 채팅 윈도우 프레임 ──────────────────────────── */}
        <div
          className="
            relative flex flex-col w-full bg-warm-100 dark:bg-[#191919] overflow-hidden
            h-[100dvh]
            sm:w-[430px] sm:h-[760px] sm:max-h-[92dvh]
            sm:rounded-3xl
            sm:shadow-[0_24px_80px_rgba(0,0,0,0.35),0_0_0_1px_rgba(255,255,255,0.08)]
          "
        >
          {children}
        </div>

      </body>
    </html>
  );
}
