# site — 수능랩 정적 사이트 (Astro)

- 도구: Astro 5.18.1(결정 6), KaTeX 0.16.11(빌드 때 수식 → HTML), js-yaml 4.1.0. 정적 출력 → Cloudflare Pages(결정 7, 첫 배포 B-08 11/21).
- 2026-11-17 초기화(계획서 52행, 백로그 B-04): 11/11 사이트 뼈대 시안(Paul 승인 11/12)을 기준 구조로 옮김. 지금 페이지(홈, `/g1/2029/2026-11-09/` 등)는 시안 페이지이며 B-06(11/19)·B-11·B-13에서 실데이터 페이지로 바뀐다.
- 검색엔진 수집은 아직 막아 둠(`noindex`, `src/layouts/Base.astro`) — 소프트 오픈 전에 연다.

## 폴더
| 경로 | 내용 |
|---|---|
| `src/pages/` | 페이지(파일 경로 = 주소) |
| `src/layouts/Base.astro` | 공통 머리·꼬리·메뉴 |
| `src/lib/content.js` | 콘텐츠 YAML 읽기, 수식·표 변환, D-day 계산 |
| `src/styles/site.css` | 화면 스타일(라이트·다크) |
| `public/` | 그대로 복사되는 정적 파일 |
| `tools/shot.cjs` | 점검용 화면 캡처(Playwright — 360px·1280px·다크, 가로 넘침·KaTeX 오류) |

## 빌드
```
cd site
npm ci
npx astro build            # 콘텐츠 없이 빌드(준비 중 표시)
DATA_DIR=<YAML 폴더> npx astro build   # 콘텐츠 넣어 빌드
```
결과는 `site/dist/`(저장소에 올리지 않음).
