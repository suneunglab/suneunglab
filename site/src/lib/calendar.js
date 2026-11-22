// 학년도·트랙·D-day 계산 — 순수 함수(파일·시계를 읽지 않음). 2026-11-22 B-11(계획서 60행 앞당김).
// 근거: 02_설계 04_데이터모델 v1.0 4-1절(학년 = 학교 연도 − 코호트 + 4, 3월 1일 새 학년)·11절 E-1~E-5·E-8.
// 같은 규칙을 Python으로 옮긴 것이 tools/cohort.py(생성 파이프라인용) — 두 쪽 결과는 tools/test_cohort_parity.py가 경계일마다 대조한다.
// 날짜는 모두 KST 기준 'YYYY-MM-DD' 문자열. 문자열 비교로 순서를 정한다.

// 한국 시간(KST) 기준 오늘 날짜
export function kstToday(now = new Date()) {
  return new Date(now.getTime() + 9 * 3600 * 1000).toISOString().slice(0, 10);
}

// 학교 연도(3월 1일 시작) — E-1
export function schoolYear(date) {
  const [y, m] = date.split('-').map(Number);
  return m >= 3 ? y : y - 1;
}

// 그날 코호트의 학년(1~3이면 재학, 0 이하는 입학 전, 4 이상은 졸업) — 4-1절
export const gradeOf = (cohort, date) => schoolYear(date) - cohort + 4;

// 그 학년도 수능의 관례 시험일: (학년도 − 1)년 11월 셋째 목요일 — E-2 '예상' 값
export function thirdThursdayNov(cohort) {
  const y = cohort - 1;
  const first = new Date(Date.UTC(y, 10, 1)).getUTCDay(); // 0 = 일
  const firstThu = 1 + ((4 - first + 7) % 7);
  return `${y}-11-${String(firstThu + 14).padStart(2, '0')}`;
}

// 코호트의 수능 시험일 — exam_years에 있으면 그 값(확정·예상 그대로), 없으면 관례로 계산한 '예상'
export function examOf(cohort, examRows) {
  const row = examRows.find((e) => e.year === cohort);
  if (row && row.exam_date) return { year: cohort, date: row.exam_date, status: row.status };
  return { year: cohort, date: thirdThursdayNov(cohort), status: '예상' };
}

// 코호트의 그날 상태 — '입학 전' | '학습' | '정시'(수능 다음 날 ~ 2/28, E-4·E-5) | '졸업'(E-3)
export function phaseOf(cohort, date, examRows) {
  const g = gradeOf(cohort, date);
  if (g < 1) return '입학 전';
  if (g > 3) return '졸업';
  if (g === 3 && date > examOf(cohort, examRows).date) return '정시';
  return '학습';
}

// D-day 표기 — 같은 날 'D-day', 이전 'D-n', 이후 'D+n'
export function dday(from, to) {
  const d = Math.round((Date.parse(`${to}T00:00:00Z`) - Date.parse(`${from}T00:00:00Z`)) / 86400000);
  return d === 0 ? 'D-day' : d > 0 ? `D-${d}` : `D+${-d}`;
}

// 고1~고3 슬롯 — 제공하는 코호트(첫 코호트 이상)면 active, 아니면 그 슬롯이 처음 열리는 날(3/1)을 준다
export function slotsOf(date, firstCohort, examRows) {
  const sy = schoolYear(date);
  const out = [];
  for (let grade = 1; grade <= 3; grade += 1) {
    const cohort = sy - grade + 4;
    if (cohort >= firstCohort) {
      out.push({ grade, cohort, active: true, phase: phaseOf(cohort, date, examRows) });
    } else {
      let next = sy + 1;
      while (next - grade + 4 < firstCohort) next += 1;
      out.push({ grade, cohort: next - grade + 4, active: false, start: `${next}-03-01` });
    }
  }
  return out;
}

// 그날 학습 콘텐츠를 생성할 코호트(생성 입력 cohort 자동 계산, 백로그 B-11·F22)
// = 재학 중(학습 상태, 정시 모드 제외) + 첫 코호트 이상 + cohorts.yaml의 active_from 이후(없는 코호트는 3/1 자동 생성분이라 제한 없음)
export function generationCohorts(date, firstCohort, examRows, cohortRows) {
  return slotsOf(date, firstCohort, examRows)
    .filter((s) => s.active && s.phase === '학습')
    .filter((s) => {
      const row = cohortRows.find((c) => c.id === s.cohort);
      return !row || !row.active_from || date >= row.active_from;
    })
    .map((s) => ({ grade: s.grade, cohort: s.cohort, track: `g${s.grade}` }));
}

// 홈 D-day 띠에 올릴 코호트 — 제공 슬롯 중 시험일이 아직 지나지 않은 것(E-4: 수능 다음 날 빠진다)
export function bandCohorts(date, firstCohort, examRows) {
  return slotsOf(date, firstCohort, examRows)
    .filter((s) => s.active && date <= examOf(s.cohort, examRows).date)
    .map((s) => examOf(s.cohort, examRows))
    .sort((a, b) => a.year - b.year); // 가까운 시험부터
}
