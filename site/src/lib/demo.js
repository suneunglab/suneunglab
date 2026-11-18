// B-06(2026-11-18) 템플릿 확인용 예시 데이터 — 생성 콘텐츠·공지 수집 결과를 연결하는 B-13·B-15 전까지만 쓴다.
// 화면에는 '예시'라고 밝힌다. 문구는 새로 쓴 것(교과서 원문 없음, 지침 5).

// 학년별 과목 개념 제목(예시)
export const DEMO_TITLES = {
  1: { korean: '논증의 타당성 판단하기', math: '다항식의 곱셈과 나눗셈', english: '글의 중심 내용 찾기', history: '근대 국민 국가 수립 운동', social: '행복의 기준과 삶의 질', science: '원소의 주기성과 규칙성' },
  2: { korean: '음운의 변동', math: '지수와 로그의 성질', english: '함축 의미 추론하기', history: '조선 후기 사회 변동', social: '시장 경제와 금융 생활', science: '생명 시스템의 구성 단위' },
  3: { korean: '현대시의 표현과 감상', math: '미분계수와 도함수', english: '빈칸에 들어갈 말 추론', history: '일제 강점기 민족 운동', social: '세계화와 평화', science: '화학 반응에서의 에너지 출입' },
};

// 다가오는 일정(03 1절 ⑤) — 확정만 날짜, 나머지는 '추정'(R11). 평가원 일정은 시행기본계획(2027-03 말 예상) 전까지 추정.
export const DEMO_SCHEDULE = [
  { date: '2027-03', title: '3월 전국연합학력평가(교육청)', status: '추정' },
  { date: '2027-06', title: '6월 모의평가(평가원)', status: '추정' },
  { date: '2027-08', title: '하반기 모의평가(평가원, 2028학년도부터 8월)', status: '추정' },
  { date: '2027-11-18', title: '2028학년도 수능', status: '확정' },
  { date: '2028-11-16', title: '2029학년도 수능', status: '확정' },
];

// 최신 공지(03 1절 ④) — 2026-11-11 실험 3 확대 실측 결과에서 고른 메타데이터(제목·날짜·기관·원문 링크만, S1)
export const DEMO_NOTICES = [
  ['2026-10-26', '연세대학교', '일정', '2027학년도 수시모집 [국제인재, 기회균형, 체육인재] 2단계 면접대상자 발표', 'https://www2.yonsei.ac.kr/entrance/2027/susi/pass_1st_bdbhcc/pass.asp'],
  ['2026-10-07', '연세대학교', '수시', '2027학년도 수시모집 논술전형 논술시험 고사장 안내', 'https://www2.yonsei.ac.kr/entrance/2027/susi/room_direction/room.asp'],
  ['2026-09-17', '인천광역시교육청', '학력평가', '2026학년도 9월 고1,2 전국연합학력평가 성적 분석 및 통계 자료 활용 안내', 'https://www.ice.go.kr/ice/na/ntt/selectNttList.do?mi=10910&bbsId=1703'],
  ['2026-09-01', '연세대학교', '일정', '2027학년도 수시모집 면접 일정 및 시간 안내', 'https://admission.yonsei.ac.kr/seoul/admission/html/rolling/notice.asp'],
  ['2026-07-20', '인천광역시교육청', '학력평가', '2026학년도 7월 고3 전국연합학력평가 성적 분석 및 통계 자료 활용 안내', 'https://www.ice.go.kr/ice/na/ntt/selectNttList.do?mi=10910&bbsId=1703'],
];

// 다가오는 일정 3건: 오늘 이후(월만 있는 추정 일정은 그 달 말일까지 유효)
export function upcoming(today, n = 3) {
  return DEMO_SCHEDULE.filter((e) => (e.date.length === 7 ? `${e.date}-31` : e.date) >= today).slice(0, n);
}
