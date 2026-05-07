'use client';

interface Props {
  message: string;
  onConfirm: () => void;
  onCancel: () => void;
}

/** RI-002: 내 정보 초기화 확인 모달 */
export function ConfirmModal({ message, onConfirm, onCancel }: Props) {
  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/30 px-6">
      <div className="bg-[#F5F0E0] dark:bg-[#2B2B2B] rounded-2xl shadow-lg p-6 w-full max-w-xs flex flex-col gap-4">
        <p className="text-sm text-warm-900 dark:text-[#F3F3F3] text-center leading-relaxed">{message}</p>
        <div className="flex gap-2">
          <button
            onClick={onCancel}
            className="flex-1 py-2 rounded-xl border border-warm-300 dark:border-[#444444] text-sm text-warm-600 dark:text-[#999999] hover:bg-warm-100 dark:hover:bg-[#3A3A3A] transition-colors"
          >
            취소
          </button>
          <button
            onClick={onConfirm}
            className="flex-1 py-2 rounded-xl bg-primary-500 dark:bg-[#5D4CD6] text-white text-sm font-semibold hover:bg-primary-400 dark:hover:bg-[#4A3BB5] transition-colors"
          >
            확인
          </button>
        </div>
      </div>
    </div>
  );
}
