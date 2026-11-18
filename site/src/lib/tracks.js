// 트랙 메뉴·트랙 페이지 — 그날 재학 중인 코호트(02 사이트맵 1절 M2, 표기 S3 "고3 · 2028 수능").
// 학년 규칙: 3월 1일에 새 학년. 코호트 Y(= Y학년도 수능 응시)는 (Y-1)학년도에 고3이다 → 학년 = 학년도 - Y + 4.
// 결정 2(2028·2029 코호트로 시작, 2027-03-01 2030 추가)·결정 9(2027 코호트 미제공) → 2028 코호트부터 제공.
// 2026-11-17 B-05. 2026-11-18 B-06: 슬롯(고1~고3) 안내·트랙 설명·코호트 시험일 추가.
// B-09(cohorts.yaml)·B-11(학년도·트랙 계산)에서 데이터 기준 계산으로 바꾼다.
import { EXAMS } from './content.js';

export const FIRST_COHORT = 2028;

// 한국 시간(KST) 기준 오늘 날짜 'YYYY-MM-DD'
export function kstToday(now = new Date()) {
  return new Date(now.getTime() + 9 * 3600 * 1000).toISOString().slice(0, 10);
}

// 날짜가 속한 학년도(3월 1일 시작)
export function schoolYear(date) {
  const [y, m] = date.split('-').map(Number);
  return m >= 3 ? y : y - 1;
}

// 트랙 설명 2줄(03 화면설계 2절 T1 머리글) — 범위·난이도, 과목당 문항 수(Q2: 고1 3·고2 4·고3 5)
export const TRACK_INFO = {
  1: { scope: '공통과목 6과목(국어·수학·영어·한국사·통합사회·통합과학)의 기본 개념', level: '기본 — 개념을 처음 정리하는 단계', count: 3 },
  2: { scope: '수능 범위 과목의 개념(예: 수학 대수·미적분Ⅰ·확률과 통계)과 통합사회·통합과학', level: '응용 — 개념을 문제에 적용하는 단계', count: 4 },
  3: { scope: '그 해 수능 범위 전체', level: '실전 — 수능 형식·배점으로 연습하는 단계', count: 5 },
};

const label = (grade, cohort) => `고${grade} · ${cohort} 수능`;

// 그날 제공하는 트랙 목록(고1 → 고3)
export function tracksOn(date) {
  const sy = schoolYear(date);
  const out = [];
  for (let grade = 1; grade <= 3; grade += 1) {
    const cohort = sy - grade + 4;
    if (cohort >= FIRST_COHORT) out.push({ grade, cohort, href: `/g${grade}/`, label: label(grade, cohort) });
  }
  return out;
}

// 고1~고3 슬롯 전부 — 제공하지 않는 슬롯은 언제 어느 코호트로 시작하는지 함께 준다(03 1절 ② "고3 트랙 2027-03-01 시작")
export function slotsOn(date) {
  const sy = schoolYear(date);
  const out = [];
  for (let grade = 1; grade <= 3; grade += 1) {
    const cohort = sy - grade + 4;
    if (cohort >= FIRST_COHORT) {
      out.push({ grade, cohort, active: true, href: `/g${grade}/`, label: label(grade, cohort) });
    } else {
      let next = sy + 1;
      while (next - grade + 4 < FIRST_COHORT) next += 1;
      out.push({ grade, cohort: next - grade + 4, active: false, href: `/g${grade}/`, label: `고${grade} 트랙`, start: `${next}-03-01` });
    }
  }
  return out;
}

// 코호트의 수능 시험일 — 확정만 날짜를 준다(R11). 없으면 미확정.
export function examFor(cohort) {
  return EXAMS.find((e) => e.year === cohort) ?? null;
}

// 날짜 더하기(KST 날짜 문자열)
export function addDays(date, n) {
  const t = Date.parse(`${date}T00:00:00Z`) + n * 86400000;
  return new Date(t).toISOString().slice(0, 10);
}
