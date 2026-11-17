// 사이트 공통 설정 — 이름·주소·태그라인, 상단 메뉴, 바닥글.
// 근거: 태그라인·워드마크(2026-10-29 확정), 02 사이트맵 1절(메뉴 M1~M7·바닥글)·2절(A4~A11 주소), 03 화면설계 0절(공통 틀).
// 2026-11-17 B-05(계획서 53행, 11/18 과업 앞당김)

export const SITE = {
  name: '수능랩',
  url: 'https://suneunglab.com',
  tagline: '수능 개념·문제·입시 소식을 매일 정리하는 연구실',
  // 소프트 오픈(2027-01-25) 전까지 검색 수집을 막는다(noindex). 열 때 true로 바꾸고 notice를 비운다.
  index: false,
  notice: '공개 준비 중인 화면입니다. 검색엔진 수집을 막아 두었습니다.',
};

// 상단 메뉴 7개(M1~M7). 트랙(M2)은 그날 재학 중인 코호트로 그린다(tracks.js).
export const MENU = [
  { id: 'home', href: '/', label: '홈' },
  { id: 'track', label: '트랙' },
  { id: 'concepts', href: '/concepts/', label: '개념 지도' },
  { id: 'system', href: '/system/', label: '수능 제도' },
  { id: 'notices', href: '/notices/', label: '입시·기관 공지' },
  { id: 'subscribe', href: '/subscribe/', label: '구독' },
  { id: 'about', href: '/about/', label: '소개' },
];

// 바닥글(모든 페이지) — 순서는 02 사이트맵 1절, 주소는 2절 A4~A10.
export const FOOTER = [
  ['/privacy/', '개인정보처리방침'],
  ['/about/license/', '라이선스(CC BY-NC-ND 4.0)'],
  ['/about/how-it-works/', '생성·검수 방식'],
  ['/about/corrections/', '정정 로그'],
  ['/about/report/', '오류 제보'],
  ['/about/bot/', '봇 안내'],
  ['/contact/', '연락처'],
];
