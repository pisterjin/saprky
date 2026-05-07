import { cn } from '@/utils/cn';

interface ChipProps {
  label: string;
  selected?: boolean;
  disabled?: boolean;
  onClick?: () => void;
  className?: string;
  size?: 'sm' | 'md';
}

/** SPARKY 디자인 토큰 기반 칩버튼 */
export function Chip({ label, selected, disabled, onClick, className, size = 'md' }: ChipProps) {
  return (
    <button
      type="button"
      disabled={disabled}
      onClick={disabled ? undefined : onClick}
      className={cn(
        'rounded-md font-normal border transition-colors',
        size === 'sm' ? 'px-2.5 py-0.5 text-[10px]' : 'px-3 py-1.5 text-xs',
        selected
          ? 'bg-primary-500 dark:bg-[#F94224] text-white border-primary-500 dark:border-[#F94224]'
          : disabled
            ? 'bg-warm-100 dark:bg-[#0C2432] text-warm-600 dark:text-[#9AB6C0] border-warm-200 dark:border-[#20485E] cursor-not-allowed opacity-50'
            : 'bg-warm-200 dark:bg-[#20485E] text-warm-900 dark:text-[#EBF7F3] border-warm-200 dark:border-[#41728B] hover:border-primary-400 dark:hover:border-[#F94224] hover:text-primary-400 dark:hover:text-[#F94224]',
        className
      )}
    >
      {label}
    </button>
  );
}
