// 트랙 메뉴·트랙 페이지 — 그날 재학 중인 코호트(02 사이트맵 1절 M2, 표기 S3 "고3 · 2028 수능").
// 학년 규칙: 3월 1일에 새 학년. 코호트 Y(= Y학년도 수능 응시)는 (Y-1)학년도에 고3이다 → 학년 = 학년도 - Y + 4.
// 결정 2(2028·2029 코호트로 시작, 2027-03-01 2030 추가)·결정 9(2027 코호트 미제공) → 2028 코호트부터 제공.
// 2026-11-17 B-05. 2026-11-18 B-06: 슬롯(고1~고3) 안내·트랙 설명·코호트 시험일 추가.
// 2026-11-20 B-09: 첫 코호트는 data/cohorts.yaml에서.
// 2026-11-22 B-11: 계산은 calendar.js(순수 함수) 한 곳으로 모으고, 이 파일은 설정 데이터를 붙여 페이지에 넘긴다.
import { COHORT_ROWS, EXAM_YEAR_ROWS } from './data.js';
import * as cal from './calendar.js';

export { kstToday, schoolYear } from './calendar.js';

// 제공하는 첫 코호트 — data/cohorts.yaml에서 읽는다(현재 2028)
export const FIRST_COHORT = Math.min(...COHORT_ROWS.map((c) => c.id));

// 트랙 설명 2줄(03 화면설계 2절 T1 머리글) — 범위·난이도, 과목당 문항 수(Q2: 고1 3·고2 4·고3 5)
export const TRACK_INFO = {
  1: { scope: '공통과목 6과목(국어·수학·영어·한국사·통합사회·통합과학)의 기본 개념', level: '기본 — 개념을 처음 정리하는 단계', count: 3 },
  2: { scope: '수능 범위 과목의 개념(예: 수학 대수·미적분Ⅰ·확률과 통계)과 통합사회·통합과학', level: '응용 — 개념을 문제에 적용하는 단계', count: 4 },
  3: { scope: '그 해 수능 범위 전체', level: '실전 — 수능 형식·배점으로 연습하는 단계', count: 5 },
};

const label = (grade, cohort) => `고${grade} · ${cohort} 수능`;

// 고1~고3 슬롯 전부 — 제공하지 않는 슬롯은 언제 어느 코호트로 시작하는지 함께 준다(03 1절 ② "고3 트랙 2027-03-01 시작")
export function slotsOn(date) {
  return cal.slotsOf(date, FIRST_COHORT, EXAM_YEAR_ROWS).map((s) => (s.active
    ? { ...s, href: `/g${s.grade}/`, label: label(s.grade, s.cohort) }
    : { ...s, href: `/g${s.grade}/`, label: `고${s.grade} 트랙` }));
}

// 그날 제공하는 트랙 목록(고1 → 고3). phase: 학습 | 정시(수능 다음 날~2/28, E-4)
export const tracksOn = (date) => slotsOn(date).filter((s) => s.active);

// 코호트의 수능 시험일 {year, date, status} — 확정/예상(관례 계산 포함)
export const examFor = (cohort) => cal.examOf(cohort, EXAM_YEAR_ROWS);

// 그날 생성할 코호트·트랙(생성 파이프라인 입력, B-11) — tools/cohort.py와 같은 결과
export const generationOn = (date) => cal.generationCohorts(date, FIRST_COHORT, EXAM_YEAR_ROWS, COHORT_ROWS);

// 홈 D-day 띠(E-4: 수능 다음 날 빠진다)
export const bandOn = (date) => cal.bandCohorts(date, FIRST_COHORT, EXAM_YEAR_ROWS);

// 날짜 더하기(KST 날짜 문자열)
export function addDays(date, n) {
  const t = Date.parse(`${date}T00:00:00Z`) + n * 86400000;
  return new Date(t).toISOString().slice(0, 10);
}
