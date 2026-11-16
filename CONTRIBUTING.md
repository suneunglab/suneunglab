# 저장소 운영 규칙 (브랜치·커밋)

## 브랜치
- `main` 하나를 기준으로 한다. 사이트 배포는 `main` 커밋 때 자동(Cloudflare Pages).
- 큰 변경(구조 개편·의존성 교체)만 `work/<주제>` 브랜치에서 하고 확인 뒤 `main`에 합친다. 매일 콘텐츠 커밋은 `main`에 바로.

## 커밋 메시지
- 형식: `<종류>: <요약>` — 종류는 `content`(매일 게시물), `notice`(공지 수집 결과), `site`, `crawler`, `generator`, `docs`, `fix`, `chore`.
- 예: `content: 2026-12-18 g1·g2 6과목`, `crawler: 경기교육청 onclick 링크 규칙`.
- 작성자: `suneunglab <suneunglab@users.noreply.github.com>`. Claude가 만든 커밋은 끝에 `Co-Authored-By` 줄을 단다.

## 커밋 전 검사(필수)
- `python tools/precommit_check.py` — `04_비공개` 경로, 교과서·OCR 파일, PDF, 검수·예비분·상태 파일, 비공개 표시가 있는 파일이 있으면 커밋을 막는다.
- git hook로 걸기: `.git/hooks/pre-commit`에 `python tools/precommit_check.py` 한 줄.

## 비밀값
- Cloudflare 토큰 등은 GitHub Secrets에만 둔다. 코드·로그·커밋에 남기지 않는다.
