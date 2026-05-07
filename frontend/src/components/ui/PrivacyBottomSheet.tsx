'use client';

import { useRef, useState, useEffect } from 'react';

interface Props {
  open: boolean;
  onClose: () => void;
}

const DEFAULT_HEIGHT = 60; // 기본 높이 (뷰포트 %)
const MIN_HEIGHT     = 30; // 이 아래로 내리면 닫힘
const MAX_HEIGHT     = 90; // 최대 높이

export function PrivacyBottomSheet({ open, onClose }: Props) {
  const [heightPct, setHeightPct] = useState(DEFAULT_HEIGHT);
  const [dragging, setDragging]   = useState(false);

  // ref: 포인터 이벤트 핸들러 안에서 동기적으로 읽어야 하므로 ref 병행 사용
  const draggingRef  = useRef(false);
  const startY       = useRef<number | null>(null);
  const startHeight  = useRef(DEFAULT_HEIGHT);
  const scrollRef    = useRef<HTMLDivElement>(null);

  // 열릴 때마다 기본 높이 및 스크롤 위치 리셋
  useEffect(() => {
    if (open) {
      setHeightPct(DEFAULT_HEIGHT);
      if (scrollRef.current) scrollRef.current.scrollTop = 0;
    }
  }, [open]);

  const handlePointerDown = (e: React.PointerEvent<HTMLDivElement>) => {
    startY.current      = e.clientY;
    startHeight.current = heightPct;
    draggingRef.current = true;
    setDragging(true);
    (e.currentTarget as HTMLElement).setPointerCapture(e.pointerId);
  };

  const handlePointerMove = (e: React.PointerEvent<HTMLDivElement>) => {
    if (!draggingRef.current || startY.current === null) return;
    const delta    = e.clientY - startY.current;           // 양수 = 아래로
    const deltaPct = (delta / window.innerHeight) * 100;
    const next     = Math.max(5, Math.min(MAX_HEIGHT, startHeight.current - deltaPct));
    setHeightPct(next);
  };

  const handlePointerUp = () => {
    draggingRef.current = false;
    setDragging(false);
    startY.current = null;
    if (heightPct < MIN_HEIGHT) {
      onClose();
      // 닫힘 애니메이션 후 기본 높이 복원
      setTimeout(() => setHeightPct(DEFAULT_HEIGHT), 320);
    }
  };

  const dragHandlers = {
    onPointerDown:  handlePointerDown,
    onPointerMove:  handlePointerMove,
    onPointerUp:    handlePointerUp,
    onPointerCancel: handlePointerUp,
  };

  return (
    // 클리핑 컨테이너
    <div
      className="absolute inset-0 overflow-hidden pointer-events-none"
      style={{ zIndex: 40 }}
    >
      {/* 딤 배경 */}
      <div
        onClick={onClose}
        className="absolute inset-0 transition-opacity duration-300"
        style={{
          background: 'rgba(0,0,0,0.45)',
          opacity: open ? 1 : 0,
          pointerEvents: open ? 'auto' : 'none',
        }}
      />

      {/* 슬라이드업 시트 — height로 크기 제어 */}
      <div
        className="absolute bottom-0 left-0 right-0 bg-white dark:bg-[#1E1E1E] rounded-t-2xl shadow-2xl flex flex-col overflow-hidden"
        style={{
          height: open ? `${heightPct}%` : '0%',
          transition: dragging ? 'none' : 'height 0.3s ease',
          pointerEvents: open ? 'auto' : 'none',
        }}
      >
        {/* 드래그 핸들 */}
        <div
          className="flex justify-center pt-3 pb-2 flex-shrink-0 cursor-grab active:cursor-grabbing touch-none select-none"
          {...dragHandlers}
        >
          <div className="w-10 h-1 rounded-full bg-warm-300 dark:bg-[#444444]" />
        </div>

        {/* 헤더 — 드래그 가능 */}
        <div
          className="flex items-center justify-between px-5 py-3 border-b border-warm-200 dark:border-[#333333] flex-shrink-0 cursor-grab active:cursor-grabbing touch-none select-none"
          {...dragHandlers}
        >
          <span className="text-sm font-semibold text-warm-900 dark:text-[#F3F3F3]">개인정보처리방침</span>
          <button
            onClick={(e) => { e.stopPropagation(); onClose(); }}
            onPointerDown={(e) => e.stopPropagation()}
            className="text-warm-600 dark:text-[#999999] hover:text-warm-900 dark:hover:text-[#F3F3F3] transition-colors p-1 cursor-pointer"
            aria-label="닫기"
          >
            <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2.5" strokeLinecap="round">
              <line x1="18" y1="6" x2="6" y2="18"/>
              <line x1="6" y1="6" x2="18" y2="18"/>
            </svg>
          </button>
        </div>

        {/* 스크롤 가능한 본문 */}
        <div ref={scrollRef} className="flex-1 overflow-y-auto scrollbar-themed px-5 py-4 text-xs text-warm-900 dark:text-[#CCCCCC] leading-relaxed space-y-4">

          <p className="text-[10px] text-warm-600 dark:text-[#777777]">시행일: 2025년 04월 &nbsp;|&nbsp; 기관: HumanAI Institute</p>

          <section>
            <h3 className="font-semibold text-sm mb-1 text-warm-900 dark:text-[#F3F3F3]">제1조 (개인정보의 처리 목적)</h3>
            <p>SPARKY(이하 "서비스")는 맞춤형 청년정책 상담을 위해 아래의 개인정보를 처리합니다. 회원가입, 로그인 등 별도의 개인정보 수집은 없으며, 서비스 이용에 필요한 최소한의 정보만을 처리합니다.</p>
          </section>

          <section>
            <h3 className="font-semibold text-sm mb-1 text-warm-900 dark:text-[#F3F3F3]">제2조 (처리하는 개인정보 항목 및 수집 방법)</h3>
            <p className="mb-1 font-medium">수집 항목</p>
            <ul className="list-disc pl-4 space-y-0.5 text-warm-600 dark:text-[#AAAAAA]">
              <li>연령대 코드값 (예: 19~24세)</li>
              <li>성별 코드값 (예: 남성/여성/선택안함)</li>
              <li>거주지역 코드값 (예: 서울)</li>
              <li>익명 식별자 UUID (브라우저 자동 생성)</li>
              <li>챗봇 대화 내용 (마스킹 처리 후 저장, 제4조 참고)</li>
            </ul>
            <p className="mt-2 font-medium">수집 방법</p>
            <ul className="list-disc pl-4 space-y-0.5 text-warm-600 dark:text-[#AAAAAA]">
              <li>서비스 내 칩버튼 선택을 통한 직접 입력</li>
              <li>챗봇 대화 중 자동 수집</li>
            </ul>
            <p className="mt-2 font-medium">수집하지 않는 정보</p>
            <ul className="list-disc pl-4 space-y-0.5 text-warm-600 dark:text-[#AAAAAA]">
              <li>이름, 이메일, 전화번호, 주소 등 직접 식별 가능한 개인정보</li>
              <li>회원가입 정보 (서비스는 비회원 방식으로 운영됩니다)</li>
              <li>결제 정보</li>
            </ul>
          </section>

          <section>
            <h3 className="font-semibold text-sm mb-1 text-warm-900 dark:text-[#F3F3F3]">제3조 (개인정보의 처리 및 보유 기간)</h3>
            <p className="mb-1 font-medium">기기 내 저장 정보 (localStorage)</p>
            <ul className="list-disc pl-4 space-y-0.5 text-warm-600 dark:text-[#AAAAAA]">
              <li>항목: 연령대·성별·지역 코드값, UUID</li>
              <li>보유 기간: 사용자가 직접 삭제(내 정보 초기화)하거나 브라우저 캐시를 삭제할 때까지</li>
              <li>저장 방식: AES-256 암호화 적용, 기기 외부로 전송되지 않음</li>
            </ul>
            <p className="mt-2 font-medium">서버 저장 정보 (대화 로그)</p>
            <ul className="list-disc pl-4 space-y-0.5 text-warm-600 dark:text-[#AAAAAA]">
              <li>항목: 마스킹 처리된 대화 내용, UUID, 도메인 분류값, 수집 일시</li>
              <li>보유 기간: 수집일로부터 1년 후 자동 파기</li>
              <li>저장 방식: PostgreSQL 데이터베이스 (Log 서버)</li>
            </ul>
          </section>

          <section>
            <h3 className="font-semibold text-sm mb-1 text-warm-900 dark:text-[#F3F3F3]">제4조 (민감정보 자동 탐지 및 마스킹)</h3>
            <p>사용자가 챗봇 대화 중 아래 항목을 입력할 경우, 서버에 저장되기 전 자동으로 탐지하여 마스킹 처리합니다. 원문은 저장되지 않습니다.</p>
            <ul className="list-disc pl-4 mt-1 space-y-0.5 text-warm-600 dark:text-[#AAAAAA]">
              <li>주민등록번호 (예: 123456-******* 형태로 저장)</li>
              <li>전화번호 (예: 010-****-**** 형태로 저장)</li>
              <li>계좌번호 (숫자 10~14자리 연속)</li>
              <li>카드번호 (4자리-4자리-4자리-4자리 패턴)</li>
            </ul>
            <p className="mt-1 text-warm-600 dark:text-[#AAAAAA]">단, 마스킹은 로그 저장 단계에서만 적용되며, AI 서버의 응답 생성 과정에서는 입력 원문이 사용될 수 있습니다. 개인식별정보를 채팅에 입력하지 않도록 권장합니다.</p>
          </section>

          <section>
            <h3 className="font-semibold text-sm mb-1 text-warm-900 dark:text-[#F3F3F3]">제5조 (개인정보의 제3자 제공)</h3>
            <p>서비스는 수집한 개인정보를 제3자에게 제공하지 않습니다. 단, 정책 검색을 위해 공공 API(온통청년, 보조금24)를 호출할 때 연령대·지역 등의 조건값이 파라미터로 전달됩니다. 이는 개인을 식별할 수 없는 코드값이며, 해당 기관의 개인정보처리방침에 따라 처리됩니다.</p>
          </section>

          <section>
            <h3 className="font-semibold text-sm mb-1 text-warm-900 dark:text-[#F3F3F3]">제6조 (개인정보의 파기 절차 및 방법)</h3>
            <p className="mb-1 font-medium">기기 내 저장 정보</p>
            <p className="text-warm-600 dark:text-[#AAAAAA]">파기 방법: 서비스 내 [내 정보 초기화] 버튼 클릭 또는 브라우저 캐시 삭제</p>
            <p className="mt-1 font-medium">서버 저장 정보 (대화 로그)</p>
            <p className="text-warm-600 dark:text-[#AAAAAA]">파기 시점: 수집일로부터 1년 경과 시 자동 파기 / 파기 방법: 데이터베이스에서 복구 불가능한 방식으로 영구 삭제</p>
          </section>

          <section>
            <h3 className="font-semibold text-sm mb-1 text-warm-900 dark:text-[#F3F3F3]">제7조 (정보주체의 권리)</h3>
            <p>사용자는 언제든지 아래 방법으로 개인정보를 직접 삭제할 수 있습니다.</p>
            <ul className="list-disc pl-4 mt-1 space-y-0.5 text-warm-600 dark:text-[#AAAAAA]">
              <li>서비스 내 [내 정보 초기화] 버튼: 기기 저장 정보(코드값, UUID) 즉시 삭제</li>
              <li>브라우저 캐시 삭제: 기기 내 모든 저장 정보 삭제</li>
            </ul>
            <p className="mt-1 text-warm-600 dark:text-[#AAAAAA]">서버 저장 정보(대화 로그)의 삭제를 요청하시려면 아래 연락처로 문의해 주십시오.</p>
          </section>

          <section>
            <h3 className="font-semibold text-sm mb-1 text-warm-900 dark:text-[#F3F3F3]">제8조 (개인정보 보호를 위한 기술적 조치)</h3>
            <ul className="list-disc pl-4 space-y-0.5 text-warm-600 dark:text-[#AAAAAA]">
              <li>localStorage 저장 데이터: AES-256 암호화 적용</li>
              <li>서버 통신: HTTPS 암호화 전송</li>
              <li>CORS 설정: 허가된 도메인에서만 접근 허용</li>
              <li>민감정보: 서버 저장 전 자동 마스킹, 원문 미저장</li>
              <li>API Key: 서버 환경변수로 격리, 클라이언트 미노출</li>
            </ul>
          </section>

          <section>
            <h3 className="font-semibold text-sm mb-1 text-warm-900 dark:text-[#F3F3F3]">제9조 (개인정보 처리방침의 변경)</h3>
            <p>본 방침은 법령 또는 서비스 변경에 따라 개정될 수 있습니다. 변경 시 서비스 내 공지를 통해 사전 안내합니다.</p>
          </section>

          <section>
            <h3 className="font-semibold text-sm mb-1 text-warm-900 dark:text-[#F3F3F3]">제10조 (개인정보 보호 담당)</h3>
            <p className="text-warm-600 dark:text-[#AAAAAA]">기관명: HumanAI Institute<br/>문의: 서비스 내 챗봇 또는 이메일로 문의 가능</p>
          </section>

          <div className="h-4" />
        </div>
      </div>
    </div>
  );
}
