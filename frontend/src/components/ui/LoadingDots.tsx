/** ER-001: 타이핑 애니메이션 (globals.css .typing-dot 사용) */
export function LoadingDots() {
  return (
    <div className="flex items-center gap-1.5 px-4 py-3">
      <span className="typing-dot" />
      <span className="typing-dot" />
      <span className="typing-dot" />
    </div>
  );
}
