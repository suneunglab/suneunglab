// 수능 제도 페이지(S1·S3·S4)와 공지(N1)가 쓰는 사실 데이터 — 한 곳에서 읽는다(03 화면설계 5절).
// 근거: 03_참고자료 수능_공식자료_정리_2028.md(2026-10-23, 평가원 수험자료 A~M)·프로젝트_현황 2절, 교육부 보도자료(아래 SRC).
// 2026-11-19 B-07(계획서 55행, 11/20 과업 앞당김). 2026-11-20 B-09: 시험일·체제는 저장소 data/*.yaml에서 읽는다(아래 SRC·CHANGES·LINKS·ANNUAL은 페이지 문안이라 여기 둔다).
import { EXAM_YEAR_ROWS, EXAM_SYSTEM_ROWS } from './data.js';

// 표기: status '확정' = 교육부·평가원·대교협 발표가 있음, '예상'·'추정' = 발표 전(지침 4 '미확정/추정').

// 공식 출처(교육부·정책브리핑·평가원·대교협만)
export const SRC = {
  moe2027: { org: '교육부', date: '2024-08-16', title: '2027학년도 수능 시행일 발표', url: 'https://www.moe.go.kr/boardCnts/viewRenew.do?boardID=294&lev=0&statusYN=W&s=moe&m=020402&opType=N&boardSeq=100526' },
  moe2028sys: { org: '교육부', date: '2025-01-21', title: '2028학년도 수능 시험 및 점수 체제 안내', url: 'https://www.moe.go.kr/boardCnts/viewRenew.do?boardID=294&boardSeq=102385&lev=0&statusYN=W&s=moe&m=020402&opType=N' },
  moe2028: { org: '교육부', date: '2025-06-01', title: '2028학년도 수능은 2027년 11월 18일(목)에 시행', url: 'https://www.moe.go.kr/boardCnts/viewRenew.do?boardID=294&boardSeq=103512&lev=0&m=020402&opType=N&s=moe&statusYN=W' },
  moe2029: { org: '교육부(정책브리핑)', date: '2026-08-18', title: '2029학년도 수능 시행일 2028.11.16.(목)', url: 'https://www.korea.kr/multi/visualNewsView.do?newsId=148970336' },
  kiceTime: { org: '평가원', date: '2026-08-25', title: '2028학년도 수능 시험시간표 안내(공지)', url: 'https://www.suneung.re.kr/boardCnts/list.do?boardID=1500229&m=0301&s=suneung' },
  kiceData: { org: '평가원', date: '2025-04', title: '2028학년도 수능 예시문항 안내 등 수험자료', url: 'https://www.suneung.re.kr/sub/info.do?m=0401&s=suneung' },
  kcueBasic: { org: '대교협', date: '2025-08-28', title: '2028학년도 대학입학전형기본사항(하반기 모의평가 8월 말 — 교육부 2025-04-16 보도 인용)', url: 'https://www.kcue.or.kr/_upload/news/2025/08/28/application_b244345d6cc72f7e172df15e831c276e.pdf' },
  kcue2028: { org: '대교협', date: '2026-04-30', title: '2028학년도 대학입학전형시행계획 주요사항', url: 'https://www.kcue.or.kr/news/sub02/sub01.php?pagenumber=1&at=view&idx=2765091' },
};

// 학년도별 시험일(S1 ①)·2028 체제 요약(S1 ②) — 2026-11-20 B-09부터 저장소 data/exam_years.yaml·exam_systems.yaml에서 읽는다.
export const EXAM_YEARS = EXAM_YEAR_ROWS.map((e) => ({
  year: e.year, date: e.exam_date, score: e.result_date, status: e.status, note: e.note, ref: !e.track_provided,
  source: e.source ? { org: e.source_org, date: e.announced, url: e.source } : null,
}));
export const FORMAT_2028 = EXAM_SYSTEM_ROWS.find((x) => x.id === '2028').areas;

// 변경 이력(S3) — 최신순. 발표일·바뀐 항목·이전→새 값·원문.
export const CHANGES = [
  { date: '2026-08-18', year: 2029, item: '시험일·성적 통지일 발표', before: '미정', after: '2028-11-16(목) · 성적 2028-12-08(금), 2028 체제 그대로', src: 'moe2029' },
  { date: '2026-08-25', year: 2028, item: '시험시간표 안내', before: '탐구 2과목 연속(4교시 107분)', after: '한국사 → 사회 → 과학 각각 따로(4교시 140분), 제2외국어/한문 17:35~18:05', src: 'kiceTime' },
  { date: '2026-04-30', year: 2028, item: '대입 전형 일정', before: '미정', after: '수시 원서 2027-09-20~23, 정시 원서 2028-01-03~06', src: 'kcue2028' },
  { date: '2025-06-01', year: 2028, item: '시험일·성적 통지일 발표', before: '미정', after: '2027-11-18(목) · 성적 2027-12-10(금)', src: 'moe2028' },
  { date: '2025-04-16', year: 2028, item: '하반기 모의평가 시기', before: '9월', after: '8월 말(날짜는 미정)', src: 'kcueBasic' },
  { date: '2025-01-21', year: 2028, item: '시험·점수 체제', before: '국어·수학 선택과목, 탐구 17과목 중 선택(20문항 30분)', after: '선택과목 폐지, 통합사회·통합과학 공통(25문항 40분), 제2외국어/한문 20문항 30분', src: 'moe2028sys' },
];

// 기관 바로가기(S4 ①) — 자동 수집하지 않는 곳 포함(결정 16)
export const LINKS = [
  { name: '한국교육과정평가원 수능 누리집', url: 'https://www.suneung.re.kr', what: '시행계획·시험시간표·수험자료·이의신청·성적', auto: false },
  { name: '한국교육과정평가원 본원', url: 'https://www.kice.re.kr', what: '평가원 보도자료·연구', auto: false },
  { name: '대입정보포털 어디가', url: 'https://www.adiga.kr', what: '대학별 전형·성적 산출', auto: false },
  { name: '한국대학교육협의회', url: 'https://www.kcue.or.kr', what: '대입전형 기본사항·시행계획', auto: true },
  { name: '교육부', url: 'https://www.moe.go.kr', what: '수능 시행일·대입 제도 보도자료', auto: true },
  { name: 'EBSi', url: 'https://www.ebsi.co.kr', what: 'EBS 수능 연계 교재·강의(간접 연계 50%)', auto: false },
];

// 연간 일정(S4 ②) — 2028학년도. 평가원 일정은 시행기본계획(2027-03 말 예상) 전까지 추정.
export const ANNUAL_2028 = [
  { when: '2027-03 말', what: '시행기본계획 발표 · 수험자료(이렇게 준비하세요 등)', status: '추정', note: '예년 3월 31일 전후' },
  { when: '2027-06 초', what: '6월 모의평가', status: '추정', note: '' },
  { when: '2027-07 초', what: '시행세부계획 공고', status: '추정', note: '예년 7월 1일 전후' },
  { when: '2027-08 말', what: '하반기 모의평가(2028부터 9월 → 8월)', status: '시기 확정 · 날짜 미정', note: '교육부 2025-04-16 보도' },
  { when: '2027-08 하순~09 초', what: '수능 응시원서 접수', status: '추정', note: '' },
  { when: '2027-09-20~23', what: '수시 원서 접수(대학별 3일 이상)', status: '확정', note: '대교협' },
  { when: '2027-11-18(목)', what: '2028학년도 수능', status: '확정', note: '교육부' },
  { when: '수능일부터 5일', what: '문제·정답 이의신청', status: '추정', note: '예년 방식' },
  { when: '2027-12-10(금)', what: '성적 통지', status: '확정', note: '교육부' },
  { when: '2028-01-03~06', what: '정시 원서 접수(대학별 3일 이상)', status: '확정', note: '대교협' },
];

// 공지 분류 7개(05 크롤러명세 9절)
export const CATEGORIES = [
  ['policy', '제도·정책'], ['schedule', '일정'], ['mock', '모의평가·학평'], ['early', '수시'], ['regular', '정시'], ['result', '결과·통계'], ['etc', '기타'],
];
