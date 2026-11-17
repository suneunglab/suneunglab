// 트랙 메뉴 — 그날 재학 중인 코호트(02 사이트맵 1절 M2, 표기 S3 "고3 · 2028 수능").
// 학년 규칙: 3월 1일에 새 학년. 코호트 Y(= Y학년도 수능 응시)는 (Y-1)학년도에 고3이다 → 학년 = 학년도 - Y + 4.
// 결정 2(2028·2029 코호트로 시작, 2027-03-01 2030 추가)·결정 9(2027 코호트 미제공) → 2028 코호트부터 제공.
// 2026-11-17 B-05. B-09(cohorts.yaml)·B-11(학년도·트랙 계산)에서 데이터 기준 계산으로 바꾼다.

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

// 그날 제공하는 트랙 목록(고1 → 고3)
export function tracksOn(date) {
  const sy = schoolYear(date);
  const out = [];
  for (let grade = 1; grade <= 3; grade += 1) {
    const cohort = sy - grade + 4;
    if (cohort >= FIRST_COHORT) out.push({ grade, cohort, href: `/g${grade}/`, label: `고${grade} · ${cohort} 수능` });
  }
  return out;
}
