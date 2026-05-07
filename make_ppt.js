const pptxgen = require("C:/Users/human/AppData/Roaming/npm/node_modules/pptxgenjs");

const pres = new pptxgen();
pres.layout = "LAYOUT_16x9";
pres.title = "SPARKY - 청년 정책 AI 챗봇";

// ── Palette ────────────────────────────────────────────
const DARK     = "0F172A";
const NAVY     = "1E3A5F";
const TEAL     = "0891B2";
const TEAL2    = "BAE6FD";
const GREEN    = "059669";
const GREEN_L  = "D1FAE5";
const RED      = "DC2626";
const RED_L    = "FEE2E2";
const AMBER    = "D97706";
const AMBER_L  = "FEF3C7";
const ORANGE   = "EA580C";
const INDIGO   = "4F46E5";
const PURPLE   = "7C3AED";
const WHITE    = "FFFFFF";
const BG       = "F8FAFC";
const CARD     = "F1F5F9";
const SLATE    = "64748B";
const SLATE_L  = "CBD5E1";
const BORDER   = "E2E8F0";
const TEXT     = "1E293B";

const sh   = () => ({ type: "outer", blur: 8, offset: 2, angle: 135, color: "000000", opacity: 0.10 });
const shS  = () => ({ type: "outer", blur: 5, offset: 1, angle: 135, color: "000000", opacity: 0.07 });

// ── Header bar (content slides) ────────────────────────
function addHeader(s, title, num) {
  s.addShape(pres.shapes.RECTANGLE, { x: 0, y: 0, w: 10, h: 0.9, fill: { color: DARK }, line: { color: DARK } });
  s.addShape(pres.shapes.RECTANGLE, { x: 0, y: 0, w: 0.07, h: 5.625, fill: { color: TEAL }, line: { color: TEAL } });
  s.addText(title, { x: 0.35, y: 0.13, w: 8.3, h: 0.64, fontSize: 26, bold: true, color: WHITE, fontFace: "Arial Black", margin: 0, valign: "middle" });
  if (num) s.addText(num, { x: 8.8, y: 0.13, w: 1.0, h: 0.64, fontSize: 22, bold: true, color: TEAL, align: "right", fontFace: "Arial Black", margin: 0, valign: "middle" });
}

// ── "초보자 함정" highlight card ────────────────────────
function trapCard(s, x, y, w, h, title, trap, solution, accent) {
  s.addShape(pres.shapes.RECTANGLE, { x, y, w, h, fill: { color: WHITE }, line: { color: BORDER, width: 1 }, shadow: sh() });
  s.addShape(pres.shapes.RECTANGLE, { x, y, w, h: 0.1, fill: { color: accent }, line: { color: accent } });

  s.addText(title, { x: x + 0.12, y: y + 0.18, w: w - 0.24, h: 0.4, fontSize: 13, bold: true, color: TEXT, fontFace: "Calibri", margin: 0 });

  // Trap row
  const ty = y + 0.66;
  s.addShape(pres.shapes.RECTANGLE, { x: x + 0.12, y: ty, w: w - 0.24, h: 1.0, fill: { color: RED_L }, line: { color: RED_L } });
  s.addShape(pres.shapes.OVAL, { x: x + 0.2, y: ty + 0.1, w: 0.26, h: 0.26, fill: { color: RED }, line: { color: RED } });
  s.addText("!", { x: x + 0.2, y: ty + 0.1, w: 0.26, h: 0.26, fontSize: 13, bold: true, color: WHITE, align: "center", valign: "middle", margin: 0 });
  s.addText("흔한 실수", { x: x + 0.52, y: ty + 0.08, w: w - 0.66, h: 0.28, fontSize: 10, bold: true, color: RED, fontFace: "Calibri", margin: 0, valign: "middle" });
  s.addText(trap, { x: x + 0.2, y: ty + 0.4, w: w - 0.4, h: 0.56, fontSize: 11, color: "7F1D1D", fontFace: "Calibri", lineSpacingMultiple: 1.25, margin: 0 });

  // Solution row
  const sy = ty + 1.1;
  s.addShape(pres.shapes.RECTANGLE, { x: x + 0.12, y: sy, w: w - 0.24, h: 1.0, fill: { color: GREEN_L }, line: { color: GREEN_L } });
  s.addShape(pres.shapes.OVAL, { x: x + 0.2, y: sy + 0.1, w: 0.26, h: 0.26, fill: { color: GREEN }, line: { color: GREEN } });
  s.addText("✓", { x: x + 0.2, y: sy + 0.1, w: 0.26, h: 0.26, fontSize: 13, bold: true, color: WHITE, align: "center", valign: "middle", margin: 0 });
  s.addText("SPARKY의 선택", { x: x + 0.52, y: sy + 0.08, w: w - 0.66, h: 0.28, fontSize: 10, bold: true, color: GREEN, fontFace: "Calibri", margin: 0, valign: "middle" });
  s.addText(solution, { x: x + 0.2, y: sy + 0.4, w: w - 0.4, h: 0.56, fontSize: 11, bold: true, color: "064E3B", fontFace: "Calibri", lineSpacingMultiple: 1.25, margin: 0 });
}

// ══════════════════════════════════════════════════════
// SLIDE 1 : 표지
// ══════════════════════════════════════════════════════
(() => {
  const s = pres.addSlide();
  s.background = { color: DARK };
  s.addShape(pres.shapes.RECTANGLE, { x: 0, y: 0,     w: 10, h: 0.07, fill: { color: TEAL }, line: { color: TEAL } });
  s.addShape(pres.shapes.RECTANGLE, { x: 0, y: 5.555, w: 10, h: 0.07, fill: { color: TEAL }, line: { color: TEAL } });
  s.addShape(pres.shapes.RECTANGLE, { x: 0.55, y: 1.3, w: 0.07, h: 3.1, fill: { color: TEAL }, line: { color: TEAL } });

  s.addText("SPARKY", { x: 0.82, y: 1.15, w: 9, h: 1.55, fontSize: 84, bold: true, color: WHITE, fontFace: "Arial Black", charSpacing: 6, margin: 0 });
  s.addText("청년 정책 AI 챗봇", { x: 0.82, y: 2.82, w: 8, h: 0.65, fontSize: 26, color: TEAL2, fontFace: "Calibri", margin: 0 });
  s.addText("청년을 위한 맞춤형 정부 지원 정책 탐색 서비스", { x: 0.82, y: 3.53, w: 8.5, h: 0.45, fontSize: 15, color: "94A3B8", fontFace: "Calibri", margin: 0 });
  s.addText("2026  |  Advanced Development Project", { x: 0.82, y: 5.08, w: 8, h: 0.35, fontSize: 12, color: "475569", fontFace: "Calibri", margin: 0 });
})();

// ══════════════════════════════════════════════════════
// SLIDE 2 : 목차
// ══════════════════════════════════════════════════════
(() => {
  const s = pres.addSlide();
  s.background = { color: BG };
  addHeader(s, "목  차", "");

  const items = [
    { n: "01", t: "배경 및 목적",      sub: "청년 정책 접근성 문제" },
    { n: "02", t: "프로젝트 개요",     sub: "서비스 소개 · 대상 · 출처" },
    { n: "03", t: "기술 스택",         sub: "언어 · 프레임워크 · 인프라" },
    { n: "04", t: "팀원 소개",         sub: "5명 구성원 및 담당 역할" },
    { n: "05", t: "시스템 아키텍처",   sub: "전체 플로우 & 5개 컴포넌트" },
    { n: "06", t: "Frontend 기능",     sub: "UI 스크린샷 & 화면 구성" },
    { n: "07", t: "시연 (Demo)",       sub: "라이브 데모" },
    { n: "08", t: "주요 기능 상세",    sub: "RAG · 마스킹 · 의도추적 · 분석" },
  ];

  items.forEach((item, i) => {
    const col = i < 4 ? 0 : 1;
    const row = i < 4 ? i : i - 4;
    const bx  = col === 0 ? 0.35 : 5.35;
    const by  = 1.1 + row * 1.07;

    s.addShape(pres.shapes.RECTANGLE, { x: bx, y: by + 0.07, w: 0.55, h: 0.44, fill: { color: TEAL }, line: { color: TEAL } });
    s.addText(item.n, { x: bx, y: by + 0.07, w: 0.55, h: 0.44, fontSize: 13, bold: true, color: WHITE, align: "center", valign: "middle", margin: 0 });
    s.addText(item.t,   { x: bx + 0.68, y: by,        w: 4.4, h: 0.32, fontSize: 16, bold: true, color: TEXT,  fontFace: "Calibri", margin: 0 });
    s.addText(item.sub, { x: bx + 0.68, y: by + 0.31, w: 4.4, h: 0.28, fontSize: 11, color: SLATE, fontFace: "Calibri", margin: 0 });

    const maxRow = 3;
    if (row < maxRow) {
      s.addShape(pres.shapes.LINE, { x: bx + 0.68, y: by + 0.64, w: 4.2, h: 0, line: { color: SLATE_L, width: 0.5 } });
    }
  });
})();

// ══════════════════════════════════════════════════════
// SLIDE 3 : 배경 및 목적
// ══════════════════════════════════════════════════════
(() => {
  const s = pres.addSlide();
  s.background = { color: BG };
  addHeader(s, "배경 및 목적", "01");

  s.addShape(pres.shapes.RECTANGLE, { x: 0.3, y: 1.05, w: 4.45, h: 4.2, fill: { color: WHITE }, line: { color: BORDER, width: 1 }, shadow: sh() });
  s.addShape(pres.shapes.RECTANGLE, { x: 0.3, y: 1.05, w: 4.45, h: 0.45, fill: { color: AMBER_L }, line: { color: AMBER_L } });
  s.addText("문제 상황", { x: 0.45, y: 1.07, w: 4.1, h: 0.41, fontSize: 15, bold: true, color: "92400E", fontFace: "Calibri", margin: 0, valign: "middle" });

  const probs = [
    "청년 지원 정책이 수백 가지지만 어디서 찾는지 모름",
    "온통청년 · 복지로 · 정부24 등 포털이 분산되어 있음",
    "나에게 해당되는 정책인지 스스로 판단하기 어려움",
    "신청 기간·자격 조건이 복잡하고 자주 바뀜",
  ];
  probs.forEach((p, i) => {
    s.addText([{ text: "▪  ", options: { color: ORANGE, bold: true } }, { text: p, options: { color: TEXT } }],
      { x: 0.45, y: 1.62 + i * 0.84, w: 4.15, h: 0.72, fontSize: 13, fontFace: "Calibri", lineSpacingMultiple: 1.3, margin: 0 });
  });

  s.addShape(pres.shapes.RECTANGLE, { x: 5.25, y: 1.05, w: 4.45, h: 4.2, fill: { color: WHITE }, line: { color: BORDER, width: 1 }, shadow: sh() });
  s.addShape(pres.shapes.RECTANGLE, { x: 5.25, y: 1.05, w: 4.45, h: 0.45, fill: { color: "CCFBF1" }, line: { color: "CCFBF1" } });
  s.addText("SPARKY의 해결", { x: 5.4, y: 1.07, w: 4.1, h: 0.41, fontSize: 15, bold: true, color: "065F46", fontFace: "Calibri", margin: 0, valign: "middle" });

  const sols = [
    "자연어 질문 한 번으로 맞춤형 정책 즉시 탐색",
    "온통청년 + 보조금24 API 실시간 연동 및 갱신",
    "정책 카드 형태로 조건·혜택·신청 방법 한눈에",
    "개인정보 자동 마스킹으로 안전하게 보호",
  ];
  sols.forEach((p, i) => {
    s.addText([{ text: "✔  ", options: { color: GREEN, bold: true } }, { text: p, options: { color: TEXT } }],
      { x: 5.4, y: 1.62 + i * 0.84, w: 4.15, h: 0.72, fontSize: 13, fontFace: "Calibri", lineSpacingMultiple: 1.3, margin: 0 });
  });
})();

// ══════════════════════════════════════════════════════
// SLIDE 4 : 프로젝트 개요
// ══════════════════════════════════════════════════════
(() => {
  const s = pres.addSlide();
  s.background = { color: BG };
  addHeader(s, "프로젝트 개요", "02");

  s.addText("SPARKY는 청년(만 19~39세)이 자연어로 질문하면 AI가 맞춤형 정부 지원 정책을 찾아주는 챗봇 서비스입니다.",
    { x: 0.35, y: 1.0, w: 9.3, h: 0.75, fontSize: 16, color: TEXT, fontFace: "Calibri", lineSpacingMultiple: 1.4, margin: 0 });

  const cards = [
    { title: "서비스 대상",  color: TEAL,   items: ["만 19~39세 청년", "취업·주거·금융·교육·복지 전 분야", "정책 정보 접근이 어려운 청년"] },
    { title: "데이터 출처",  color: PURPLE, items: ["온통청년 공공 API", "보조금24 공공 API", "24시간 자동 갱신 스케줄러"] },
    { title: "핵심 가치",   color: GREEN,  items: ["자연어 대화 인터페이스", "RAG 기반 정확한 정책 검색", "개인정보 3중 자동 마스킹"] },
  ];

  cards.forEach((c, i) => {
    const cx = 0.3 + i * 3.23;
    s.addShape(pres.shapes.RECTANGLE, { x: cx, y: 1.95, w: 3.05, h: 3.3, fill: { color: WHITE }, line: { color: BORDER, width: 1 }, shadow: sh() });
    s.addShape(pres.shapes.RECTANGLE, { x: cx, y: 1.95, w: 3.05, h: 0.5, fill: { color: c.color }, line: { color: c.color } });
    s.addText(c.title, { x: cx + 0.05, y: 1.97, w: 2.95, h: 0.46, fontSize: 14, bold: true, color: WHITE, fontFace: "Calibri", align: "center", valign: "middle", margin: 0 });
    c.items.forEach((item, j) => {
      s.addText([{ text: "• ", options: { color: c.color, bold: true } }, { text: item }],
        { x: cx + 0.15, y: 2.57 + j * 0.78, w: 2.75, h: 0.7, fontSize: 13, color: TEXT, fontFace: "Calibri", lineSpacingMultiple: 1.3, margin: 0 });
    });
  });
})();

// ══════════════════════════════════════════════════════
// SLIDE 5 : 기술 스택
// ══════════════════════════════════════════════════════
(() => {
  const s = pres.addSlide();
  s.background = { color: BG };
  addHeader(s, "기술 스택", "03");

  const cats = [
    { t: "Frontend",   c: "0369A1", items: ["Next.js 14", "TypeScript", "React", "Tailwind CSS"] },
    { t: "AI Server",  c: GREEN,    items: ["Python 3.11", "FastAPI", "sentence-transformers", "FAISS"] },
    { t: "Log Server", c: PURPLE,   items: ["Java 21", "Spring Boot 3", "JPA / Hibernate", "Gradle"] },
    { t: "Database",   c: "B45309", items: ["PostgreSQL 15", "Docker Compose", "pgvector", "Docker"] },
    { t: "LLM / AI",   c: RED,      items: ["GPT-4o", "Ollama", "gemma4:e4b", "KR-SBERT"] },
  ];

  const topW = 3.1, botW = 4.45, topY = 1.05, botY = 3.28;
  cats.forEach((cat, i) => {
    let cx, cy, w;
    if (i < 3) { cx = 0.25 + i * 3.25; cy = topY; w = topW; }
    else       { cx = 0.25 + (i - 3) * 4.75; cy = botY; w = botW; }
    s.addShape(pres.shapes.RECTANGLE, { x: cx, y: cy, w, h: 1.95, fill: { color: WHITE }, line: { color: BORDER, width: 1 }, shadow: sh() });
    s.addShape(pres.shapes.RECTANGLE, { x: cx, y: cy, w, h: 0.46, fill: { color: cat.c }, line: { color: cat.c } });
    s.addText(cat.t, { x: cx + 0.05, y: cy + 0.04, w: w - 0.1, h: 0.38, fontSize: 14, bold: true, color: WHITE, fontFace: "Calibri", align: "center", valign: "middle", margin: 0 });
    cat.items.forEach((item, j) => {
      s.addText([{ text: "▸  ", options: { color: cat.c } }, { text: item }],
        { x: cx + 0.15, y: cy + 0.55 + j * 0.35, w: w - 0.3, h: 0.33, fontSize: 12, color: TEXT, fontFace: "Calibri", margin: 0 });
    });
  });
})();

// ══════════════════════════════════════════════════════
// SLIDE 6 : 팀원 소개 (5명)
// ══════════════════════════════════════════════════════
(() => {
  const s = pres.addSlide();
  s.background = { color: BG };
  addHeader(s, "팀원 소개", "04");

  const members = [
    { name: "팀원 1 이름", role: "팀장 · PM",       tasks: ["프로젝트 기획·총괄", "일정·산출물 관리", "기획서 작성"] },
    { name: "팀원 2 이름", role: "AI 서버 (RAG)",  tasks: ["FastAPI 서버 개발", "FAISS 인덱스 구축", "LLM 연동"] },
    { name: "팀원 3 이름", role: "AI 서버 (보안)", tasks: ["마스킹 모듈 개발", "의도 추적 모듈", "shared/ 규칙 관리"] },
    { name: "팀원 4 이름", role: "프론트엔드",     tasks: ["Next.js UI 개발", "PolicyCard/채팅 컴포넌트", "UX/UI 설계"] },
    { name: "팀원 5 이름", role: "로그서버·DB·분석", tasks: ["Spring Boot 로그서버", "PostgreSQL DB 설계", "대시보드 SQL 7종"] },
  ];
  const colors = [TEAL, GREEN, RED, INDIGO, PURPLE];

  // 3 on top row, 2 on bottom row (centered)
  const topW = 3.07, topH = 2.0;
  const botW = 3.07, botH = 2.0;

  members.forEach((m, i) => {
    let cx, cy;
    if (i < 3) { cx = 0.3 + i * 3.23; cy = 1.05; }
    else       { cx = 1.91 + (i - 3) * 3.23; cy = 3.2; }

    const col_c = colors[i];
    s.addShape(pres.shapes.RECTANGLE, { x: cx, y: cy, w: topW, h: topH, fill: { color: WHITE }, line: { color: BORDER, width: 1 }, shadow: sh() });
    s.addShape(pres.shapes.RECTANGLE, { x: cx, y: cy, w: topW, h: 0.06, fill: { color: col_c }, line: { color: col_c } });

    // Avatar
    s.addShape(pres.shapes.OVAL, { x: cx + 0.15, y: cy + 0.3, w: 0.72, h: 0.72, fill: { color: col_c }, line: { color: col_c } });
    s.addText(String(i + 1), { x: cx + 0.15, y: cy + 0.3, w: 0.72, h: 0.72, fontSize: 20, bold: true, color: WHITE, align: "center", valign: "middle", margin: 0 });

    s.addText(m.name, { x: cx + 0.98, y: cy + 0.24, w: topW - 1.05, h: 0.34, fontSize: 14, bold: true, color: TEXT, fontFace: "Calibri", margin: 0 });
    s.addShape(pres.shapes.RECTANGLE, { x: cx + 0.98, y: cy + 0.62, w: topW - 1.15, h: 0.26, fill: { color: col_c }, line: { color: col_c } });
    s.addText(m.role, { x: cx + 0.98, y: cy + 0.62, w: topW - 1.15, h: 0.26, fontSize: 10, color: WHITE, align: "center", valign: "middle", margin: 0 });

    m.tasks.forEach((t, j) => {
      s.addText([{ text: "- ", options: { color: col_c } }, { text: t }],
        { x: cx + 0.15, y: cy + 1.1 + j * 0.28, w: topW - 0.3, h: 0.26, fontSize: 10, color: TEXT, fontFace: "Calibri", margin: 0 });
    });
  });
})();

// ══════════════════════════════════════════════════════
// SLIDE 7 : 시스템 아키텍처
// ══════════════════════════════════════════════════════
(() => {
  const s = pres.addSlide();
  s.background = { color: BG };
  addHeader(s, "시스템 아키텍처", "05");

  function box(x, y, w, h, title, sub, bg, fg) {
    bg = bg || WHITE; fg = fg || TEXT;
    s.addShape(pres.shapes.RECTANGLE, { x, y, w, h, fill: { color: bg }, line: { color: bg === WHITE ? BORDER : bg, width: 1 }, shadow: shS() });
    const th = sub ? h * 0.48 : h;
    s.addText(title, { x: x + 0.05, y, w: w - 0.1, h: th, fontSize: 12, bold: true, color: fg, fontFace: "Calibri", align: "center", valign: "middle", margin: 0 });
    if (sub) s.addText(sub, { x: x + 0.05, y: y + th, w: w - 0.1, h: h - th, fontSize: 10, color: bg === DARK ? TEAL2 : SLATE, fontFace: "Calibri", align: "center", valign: "middle", margin: 0 });
  }
  function line(x1, y1, x2, y2) {
    s.addShape(pres.shapes.LINE, { x: x1, y: y1, w: x2 - x1, h: y2 - y1, line: { color: TEAL, width: 1.5 } });
  }
  function arrT(x, y, t) {
    s.addText(t, { x, y, w: 0.35, h: 0.3, fontSize: 14, color: TEAL, bold: true, align: "center", valign: "middle", margin: 0 });
  }

  // Row 1
  box(0.18, 1.1, 1.35, 0.82, "사용자", ":3000 브라우저", DARK, WHITE);
  arrT(1.56, 1.38, "→"); line(1.53, 1.5, 1.73, 1.5);
  box(1.73, 1.1, 1.75, 0.82, "Frontend", "Next.js :3000");
  arrT(3.51, 1.38, "→"); line(3.48, 1.5, 3.68, 1.5);
  box(3.68, 1.1, 1.9, 0.82, "AI Server", "FastAPI :8000");
  arrT(5.61, 1.38, "→"); line(5.58, 1.5, 5.78, 1.5);
  box(5.78, 1.1, 1.75, 0.82, "LLM", "GPT-4 / Ollama");
  arrT(7.56, 1.38, "→"); line(7.53, 1.5, 7.73, 1.5);
  box(7.73, 1.1, 2.0, 0.82, "FAISS Index", "KR-SBERT 벡터", GREEN_L, "065F46");

  // Vertical links
  arrT(4.58, 1.95, "↓"); line(4.63, 1.92, 4.63, 2.47);
  arrT(2.6, 1.95, "↓"); line(2.6, 1.92, 2.6, 2.6); line(2.6, 2.6, 3.68, 2.6);

  // Row 2
  box(3.68, 2.6, 1.9, 0.82, "Log Server", "Spring Boot :8081");
  arrT(5.61, 2.88, "→"); line(5.58, 3.0, 5.78, 3.0);
  box(5.78, 2.6, 1.75, 0.82, "PostgreSQL", "Docker :5433");

  // Row 3
  arrT(4.58, 3.45, "↓"); line(4.63, 3.42, 4.63, 3.97);
  box(3.68, 4.1, 1.9, 0.82, "Dashboard", "SQL 쿼리 7개");
  box(7.73, 3.5, 2.0, 0.82, "shared/", "마스킹 규칙 공유\n(YAML + JSON)", AMBER_L, "92400E");

  // Legend
  s.addShape(pres.shapes.RECTANGLE, { x: 0.2, y: 3.5, w: 3.3, h: 1.7, fill: { color: CARD }, line: { color: BORDER, width: 1 } });
  s.addText("구성 요소", { x: 0.35, y: 3.55, w: 3.0, h: 0.32, fontSize: 12, bold: true, color: TEXT, fontFace: "Calibri", margin: 0 });
  const legend = [
    { c: DARK,    t: "사용자 / 브라우저" },
    { c: WHITE,   t: "서버 (Next.js, FastAPI, Spring)" },
    { c: GREEN_L, t: "벡터 검색 (FAISS)" },
    { c: AMBER_L, t: "공유 규칙 (shared/)" },
  ];
  legend.forEach((l, i) => {
    const ly = 3.94 + i * 0.3;
    s.addShape(pres.shapes.RECTANGLE, { x: 0.35, y: ly, w: 0.22, h: 0.2, fill: { color: l.c }, line: { color: SLATE_L, width: 0.5 } });
    s.addText(l.t, { x: 0.65, y: ly - 0.02, w: 2.7, h: 0.26, fontSize: 10, color: SLATE, fontFace: "Calibri", margin: 0 });
  });
})();

// ══════════════════════════════════════════════════════
// SLIDE 8 : Frontend 기능 (스크린샷 플레이스홀더)
// ══════════════════════════════════════════════════════
(() => {
  const s = pres.addSlide();
  s.background = { color: BG };
  addHeader(s, "Frontend 기능", "06");

  s.addText("스크린샷은 발표 직전 실제 화면으로 교체 예정", {
    x: 0.35, y: 0.98, w: 9.3, h: 0.3, fontSize: 11, color: SLATE, italic: true, fontFace: "Calibri", margin: 0
  });

  const screens = [
    { title: "① 온보딩 화면",    desc: "최초 방문 시 연령대·지역·관심 분야 선택\n→ 개인화 컨텍스트로 활용" },
    { title: "② 채팅 메인 UI",   desc: "자연어 질문 입력 / 타자기 효과 애니메이션\n로딩 인디케이터 + 세션 관리" },
    { title: "③ PolicyCard + 아코디언", desc: "정책 제목·혜택·조건 요약 카드\n펼치기 버튼으로 상세 내용 확장" },
    { title: "④ 마스킹 토스트",  desc: "개인정보 감지 시 토스트로 즉시 알림\n사용자가 마스킹 여부 인지 가능" },
  ];

  screens.forEach((sc, i) => {
    const col = i % 2, row = Math.floor(i / 2);
    const cx = 0.3 + col * 4.85;
    const cy = 1.38 + row * 2.0;

    // Screenshot placeholder (dashed border)
    s.addShape(pres.shapes.RECTANGLE, { x: cx, y: cy, w: 4.55, h: 1.35, fill: { color: CARD }, line: { color: SLATE_L, width: 1.5, dashType: "dash" } });
    s.addText("📷", { x: cx, y: cy, w: 4.55, h: 0.7, fontSize: 28, color: SLATE_L, align: "center", valign: "bottom", margin: 0 });
    s.addText("스크린샷 삽입 예정", { x: cx, y: cy + 0.7, w: 4.55, h: 0.5, fontSize: 11, color: SLATE, align: "center", valign: "top", italic: true, fontFace: "Calibri", margin: 0 });

    // Caption
    s.addShape(pres.shapes.RECTANGLE, { x: cx, y: cy + 1.4, w: 0.08, h: 0.52, fill: { color: TEAL }, line: { color: TEAL } });
    s.addText(sc.title, { x: cx + 0.15, y: cy + 1.38, w: 4.4, h: 0.26, fontSize: 13, bold: true, color: TEXT, fontFace: "Calibri", margin: 0 });
    s.addText(sc.desc, { x: cx + 0.15, y: cy + 1.62, w: 4.4, h: 0.34, fontSize: 10, color: SLATE, fontFace: "Calibri", lineSpacingMultiple: 1.25, margin: 0 });
  });
})();

// ══════════════════════════════════════════════════════
// SLIDE 9 : 시연 (Demo)
// ══════════════════════════════════════════════════════
(() => {
  const s = pres.addSlide();
  s.background = { color: DARK };
  s.addShape(pres.shapes.RECTANGLE, { x: 0, y: 0,     w: 10, h: 0.07, fill: { color: TEAL }, line: { color: TEAL } });
  s.addShape(pres.shapes.RECTANGLE, { x: 0, y: 5.555, w: 10, h: 0.07, fill: { color: TEAL }, line: { color: TEAL } });

  s.addText("LIVE DEMO", { x: 0.5, y: 1.3, w: 9, h: 1.65, fontSize: 72, bold: true, color: WHITE, fontFace: "Arial Black", align: "center", charSpacing: 10, margin: 0 });
  s.addText("시  연", { x: 0.5, y: 3.0, w: 9, h: 0.55, fontSize: 28, color: TEAL2, align: "center", fontFace: "Calibri", charSpacing: 4, margin: 0 });

  const demos = [
    "청년 정책 자연어 검색 (월세 지원 / 취업 지원 등)",
    "정책 카드 아코디언 & 캐러셀 확인",
    "개인정보 입력 → 마스킹 토스트 확인",
    "같은 주제 재질문 → 의도 추적 동작 확인",
  ];
  demos.forEach((d, i) => {
    s.addText(`${i + 1}.  ${d}`, {
      x: 2.0, y: 3.75 + i * 0.33, w: 6.5, h: 0.3,
      fontSize: 13, color: "94A3B8", align: "center", fontFace: "Calibri", margin: 0
    });
  });
})();

// ══════════════════════════════════════════════════════
// SLIDE 10 : 주요 기능 ① RAG 정책 검색
// ══════════════════════════════════════════════════════
(() => {
  const s = pres.addSlide();
  s.background = { color: BG };
  addHeader(s, "주요 기능 ① RAG 정책 검색", "08");

  // Top: 4-step flow horizontal
  const steps = [
    { n: "1", t: "질문 입력",   d: "개인정보 마스킹 후 수신" },
    { n: "2", t: "벡터 임베딩", d: "KR-SBERT로 질문 벡터화" },
    { n: "3", t: "FAISS 검색",  d: "코사인 유사도 Top-K" },
    { n: "4", t: "LLM 응답",    d: "검색결과 + 프롬프트 → 답변" },
  ];
  steps.forEach((step, i) => {
    const sx = 0.3 + i * 2.4;
    s.addShape(pres.shapes.RECTANGLE, { x: sx, y: 1.05, w: 2.2, h: 1.2, fill: { color: WHITE }, line: { color: BORDER, width: 1 }, shadow: shS() });
    s.addShape(pres.shapes.OVAL, { x: sx + 0.12, y: 1.18, w: 0.42, h: 0.42, fill: { color: TEAL }, line: { color: TEAL } });
    s.addText(step.n, { x: sx + 0.12, y: 1.18, w: 0.42, h: 0.42, fontSize: 13, bold: true, color: WHITE, align: "center", valign: "middle", margin: 0 });
    s.addText(step.t, { x: sx + 0.62, y: 1.2, w: 1.55, h: 0.35, fontSize: 13, bold: true, color: TEXT, fontFace: "Calibri", margin: 0 });
    s.addText(step.d, { x: sx + 0.12, y: 1.65, w: 2.0, h: 0.52, fontSize: 11, color: SLATE, fontFace: "Calibri", lineSpacingMultiple: 1.25, margin: 0 });
    if (i < 3) s.addText("→", { x: sx + 2.2, y: 1.48, w: 0.2, h: 0.3, fontSize: 18, bold: true, color: TEAL, align: "center", valign: "middle", margin: 0 });
  });

  // Section label
  s.addShape(pres.shapes.RECTANGLE, { x: 0.3, y: 2.4, w: 9.4, h: 0.34, fill: { color: DARK }, line: { color: DARK } });
  s.addText("🎯  초보 개발자가 놓치기 쉬운 포인트", { x: 0.4, y: 2.4, w: 9.2, h: 0.34, fontSize: 12, bold: true, color: WHITE, fontFace: "Calibri", valign: "middle", margin: 0 });

  // 3 trap cards
  const traps = [
    { t: "한국어 임베딩 선택",
      bad: "다국어 범용 모델(m-E5 등) 사용",
      good: "KR-SBERT(한국어 특화) → 정책 검색 정확도 대폭 향상" },
    { t: "데이터 최신성 보장",
      bad: "최초 1회 배치 후 정적 사용",
      good: "APScheduler로 24h 자동 갱신 + FAISS 재빌드" },
    { t: "LLM 공급자 락인 회피",
      bad: "특정 LLM API에 하드코딩",
      good: "USE_MODEL 환경변수로 GPT/Ollama 즉시 전환" },
  ];
  traps.forEach((tp, i) => {
    trapCard(s, 0.3 + i * 3.15, 2.85, 3.0, 2.6, tp.t, tp.bad, tp.good, TEAL);
  });
})();

// ══════════════════════════════════════════════════════
// SLIDE 11 : 주요 기능 ② 개인정보 마스킹
// ══════════════════════════════════════════════════════
(() => {
  const s = pres.addSlide();
  s.background = { color: BG };
  addHeader(s, "주요 기능 ② 개인정보 마스킹", "08");

  // Top: rules summary (compact, single row with 5 rule chips)
  s.addShape(pres.shapes.RECTANGLE, { x: 0.3, y: 1.05, w: 9.4, h: 1.25, fill: { color: WHITE }, line: { color: BORDER, width: 1 }, shadow: shS() });
  s.addText("마스킹 규칙 5종 (R1 ~ R5) — Python · Java · TypeScript 3중 적용", {
    x: 0.45, y: 1.1, w: 9.15, h: 0.32, fontSize: 13, bold: true, color: TEXT, fontFace: "Calibri", margin: 0
  });

  const rules = [
    { r: "R1", n: "주민번호", ex: "######-*******" },
    { r: "R2", n: "카드번호", ex: "****-****-****-****" },
    { r: "R3", n: "휴대폰",   ex: "010-****-****" },
    { r: "R4", n: "계좌번호", ex: "[계좌번호]" },
    { r: "R5", n: "이메일",   ex: "[이메일]" },
  ];
  rules.forEach((r, i) => {
    const rx = 0.5 + i * 1.82;
    s.addShape(pres.shapes.RECTANGLE, { x: rx, y: 1.52, w: 1.72, h: 0.72, fill: { color: CARD }, line: { color: BORDER, width: 0.5 } });
    s.addShape(pres.shapes.RECTANGLE, { x: rx, y: 1.52, w: 0.4, h: 0.72, fill: { color: TEAL }, line: { color: TEAL } });
    s.addText(r.r, { x: rx, y: 1.52, w: 0.4, h: 0.72, fontSize: 13, bold: true, color: WHITE, align: "center", valign: "middle", margin: 0 });
    s.addText(r.n, { x: rx + 0.46, y: 1.56, w: 1.22, h: 0.3, fontSize: 11, bold: true, color: TEXT, fontFace: "Calibri", margin: 0 });
    s.addText(r.ex, { x: rx + 0.46, y: 1.85, w: 1.22, h: 0.32, fontSize: 9, color: ORANGE, fontFace: "Consolas", margin: 0 });
  });

  // Section label
  s.addShape(pres.shapes.RECTANGLE, { x: 0.3, y: 2.4, w: 9.4, h: 0.34, fill: { color: DARK }, line: { color: DARK } });
  s.addText("🎯  초보 개발자가 놓치기 쉬운 포인트", { x: 0.4, y: 2.4, w: 9.2, h: 0.34, fontSize: 12, bold: true, color: WHITE, fontFace: "Calibri", valign: "middle", margin: 0 });

  const traps = [
    { t: "3개 언어 규칙 일관성",
      bad: "AI 서버(Python)에서만 마스킹. 다른 서버는 원본 저장",
      good: "Python+Java+TS 3중 방어. shared/masking_cases.yaml 공유 테스트" },
    { t: "계좌번호 오탐 방지",
      bad: "숫자 13자리 패턴을 무조건 매칭 → 정책 금액·날짜도 오인 마스킹",
      good: "R4는 '계좌번호:' 등 키워드가 앞에 있을 때만 매칭 (context-aware)" },
    { t: "시간대 버그 차단",
      bad: "LocalDateTime.now() 사용 → 서버 타임존에 따라 저장 시각 달라짐",
      good: "LocalDateTime.now(ZoneOffset.UTC)로 통일 (DB·로그 분석 안전)" },
  ];
  traps.forEach((tp, i) => {
    trapCard(s, 0.3 + i * 3.15, 2.85, 3.0, 2.6, tp.t, tp.bad, tp.good, GREEN);
  });
})();

// ══════════════════════════════════════════════════════
// SLIDE 12 : 주요 기능 ③ 의도 추적 (Intent Tracker)
// ══════════════════════════════════════════════════════
(() => {
  const s = pres.addSlide();
  s.background = { color: BG };
  addHeader(s, "주요 기능 ③ 의도 추적 (Intent Tracker)", "08");

  // Top: flow diagram
  s.addShape(pres.shapes.RECTANGLE, { x: 0.3, y: 1.05, w: 9.4, h: 1.25, fill: { color: WHITE }, line: { color: BORDER, width: 1 }, shadow: shS() });
  s.addText("같은 주제를 반복 질문하는지 자동 감지 → RAG 품질 개선에 활용", {
    x: 0.45, y: 1.1, w: 9.15, h: 0.3, fontSize: 12, bold: true, color: TEXT, fontFace: "Calibri", margin: 0
  });

  const flow = [
    { t: "질문 임베딩", d: "벡터 변환" },
    { t: "코사인 유사도", d: "직전 질문 비교" },
    { t: "시간차 측정",  d: "마지막 응답 이후" },
    { t: "재시도 분류",  d: "quality / recall" },
  ];
  flow.forEach((f, i) => {
    const fx = 0.5 + i * 2.25;
    s.addShape(pres.shapes.RECTANGLE, { x: fx, y: 1.5, w: 2.0, h: 0.72, fill: { color: CARD }, line: { color: BORDER, width: 0.5 } });
    s.addText(f.t, { x: fx, y: 1.52, w: 2.0, h: 0.32, fontSize: 12, bold: true, color: TEXT, fontFace: "Calibri", align: "center", margin: 0 });
    s.addText(f.d, { x: fx, y: 1.84, w: 2.0, h: 0.36, fontSize: 10, color: SLATE, fontFace: "Calibri", align: "center", margin: 0 });
    if (i < 3) s.addText("→", { x: fx + 2.0, y: 1.65, w: 0.25, h: 0.4, fontSize: 16, bold: true, color: TEAL, align: "center", valign: "middle", margin: 0 });
  });

  // Section label
  s.addShape(pres.shapes.RECTANGLE, { x: 0.3, y: 2.4, w: 9.4, h: 0.34, fill: { color: DARK }, line: { color: DARK } });
  s.addText("🎯  초보 개발자가 놓치기 쉬운 포인트", { x: 0.4, y: 2.4, w: 9.2, h: 0.34, fontSize: 12, bold: true, color: WHITE, fontFace: "Calibri", valign: "middle", margin: 0 });

  const traps = [
    { t: "의미 기반 중복 감지",
      bad: "질문 문자열을 그대로 비교 → 표현만 바뀌어도 '새 질문' 취급",
      good: "임베딩 + 코사인 유사도 ≥ 0.75 → 의미가 같으면 재질문으로 인식" },
    { t: "재질문 원인 분류",
      bad: "재질문을 단순 '중복'으로 한 번만 집계",
      good: "3분 이내 = quality(답변 불만족) / 이후 = recall(기억 재조회) 구분" },
    { t: "메모리 누수 방지",
      bad: "세션별 벡터를 인메모리 dict에 계속 누적 → 장시간 운영 시 OOM",
      good: "_evict_stale() 주기 실행 → 24h 비활성 세션 자동 제거" },
  ];
  traps.forEach((tp, i) => {
    trapCard(s, 0.3 + i * 3.15, 2.85, 3.0, 2.6, tp.t, tp.bad, tp.good, PURPLE);
  });
})();

// ══════════════════════════════════════════════════════
// SLIDE 13 : 주요 기능 ④ 로그 & 분석 대시보드
// ══════════════════════════════════════════════════════
(() => {
  const s = pres.addSlide();
  s.background = { color: BG };
  addHeader(s, "주요 기능 ④ 로그 & 분석 대시보드", "08");

  // Top area: 4 tables + 7 queries summary
  s.addShape(pres.shapes.RECTANGLE, { x: 0.3, y: 1.05, w: 9.4, h: 1.25, fill: { color: WHITE }, line: { color: BORDER, width: 1 }, shadow: shS() });
  s.addText("PostgreSQL 4개 테이블 + SQL 분석 쿼리 7종", {
    x: 0.45, y: 1.1, w: 9.15, h: 0.3, fontSize: 12, bold: true, color: TEXT, fontFace: "Calibri", margin: 0
  });

  const tables = ["chat_logs", "session_meta", "log_policies", "policy_click_events"];
  tables.forEach((t, i) => {
    const tx = 0.5 + i * 2.27;
    s.addShape(pres.shapes.RECTANGLE, { x: tx, y: 1.5, w: 2.15, h: 0.72, fill: { color: GREEN_L }, line: { color: GREEN, width: 0.5 } });
    s.addShape(pres.shapes.RECTANGLE, { x: tx, y: 1.5, w: 0.08, h: 0.72, fill: { color: GREEN }, line: { color: GREEN } });
    s.addText(t, { x: tx + 0.12, y: 1.5, w: 2.0, h: 0.72, fontSize: 12, bold: true, color: "064E3B", fontFace: "Consolas", valign: "middle", margin: 0 });
  });

  // Section label
  s.addShape(pres.shapes.RECTANGLE, { x: 0.3, y: 2.4, w: 9.4, h: 0.34, fill: { color: DARK }, line: { color: DARK } });
  s.addText("🎯  초보 개발자가 놓치기 쉬운 포인트", { x: 0.4, y: 2.4, w: 9.2, h: 0.34, fontSize: 12, bold: true, color: WHITE, fontFace: "Calibri", valign: "middle", margin: 0 });

  const traps = [
    { t: "테이블 역할 분리",
      bad: "모든 로그를 하나의 큰 테이블에 저장 → 조회 느리고 스키마 변경 어려움",
      good: "도메인별 4개 테이블 분리 (chat / session / policy / click)" },
    { t: "응답시간 측정 정확도",
      bad: "평균 응답시간(AVG)만 측정 → 긴 꼬리 장애 누락",
      good: "P50 / P90 / P95 분위수 측정 → 상위 이상치 모니터링" },
    { t: "JPA 관계 탐색 문법",
      bad: "findByChatLogId() → 런타임 에러 (JPA가 필드 인식 못 함)",
      good: "findByChatLog_Id() → 언더스코어로 연관 엔티티 필드 명시" },
  ];
  traps.forEach((tp, i) => {
    trapCard(s, 0.3 + i * 3.15, 2.85, 3.0, 2.6, tp.t, tp.bad, tp.good, INDIGO);
  });
})();

// ── Write file ─────────────────────────────────────────
pres.writeFile({ fileName: "E:/ADV Project/temp/sparky/SPARKY_발표자료_v2.pptx" })
  .then(() => console.log("OK: SPARKY_발표자료.pptx"))
  .catch(err => { console.error("ERR:", err); process.exit(1); });
