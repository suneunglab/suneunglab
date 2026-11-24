# content — 게시 콘텐츠(B-10 스키마, 2026-11-21)

설계 근거: `02_설계\04_데이터모델.md` 7·8·8-1·9·10-1절, `06_생성검증명세.md` 1·5·6절(비공개 설계 폴더, 이 저장소 밖).

| 대상 | 위치 | 형식 | 스키마 |
|---|---|---|---|
| 오늘의 학습(코호트 × 날짜 1파일, 문제 포함) | `content/lessons/{코호트}/{YYYY}/{MM}/{YYYY-MM-DD}.md` | YAML 머리말 + 본문 | `schema/lesson.schema.json` |
| 그림 | `content/lessons/{코호트}/{YYYY}/{MM}/fig/{문제 id}.svg` | SVG(자체 제작만) | — |
| 수집 공지 | `data/notices/{YYYY}/{MM}.jsonl` | 한 줄 = 공지 1건 | `schema/notice.schema.json` |
| 검증 로그 | `logs/verify/{YYYY-MM-DD}.jsonl` | 한 줄 = 문제 1건 | `schema/verify_log.schema.json` |

## 사이트가 읽는 방법(B-13, 2026-11-24)
`site/src/lib/content.js`의 `listLessons`·`loadLesson`이 `content/lessons/{코호트}/…`에서 `status: 게시`이고 `example`이 아닌 파일만 읽는다. 게시된 날짜마다 오늘의 학습 페이지(그날 학년 트랙 주소)·아카이브 목록·최근 7일·전날/다음날 링크가 생긴다. 게시 파일이 없으면 지금처럼 '준비 중'이다.

## 검사
```
pip install -r tools/requirements.txt
python tools/validate_content.py          # 위 위치 + 견본 전체
python tools/test_validate_content.py     # 견본 통과·틀린 예 실패 시험
```
스키마 밖에 추가로 보는 규칙: id = `{코호트}-{날짜}`와 경로 일치, 날짜·코호트로 학년(g1~g3)을 계산해 과목당 문항 수(3·4·5), num 1부터 차례, 5지선다 정답 `①`~`⑤`·선지 5개·선지에 번호 기호 없음, 단답형은 수학만·1~999, 과목별 행동 영역 코드·배점, 같은 행동 영역·같은 정답 최대 2문항, g1은 `[10…]` 성취기준, textbook_ref는 `교과서 미입력` 또는 쪽 표기, 게시는 6과목·검증 일치·저작권 검사 통과만, 겹침 8어절·30자 이상인데 '통과' 표시 금지. 난이도 배치(1·1·2 / 1·2·2·3 / 1·2·2·3·3)는 경고.

## 견본(`schema/examples/`)
`example: true`가 붙은 형식 견본 3개 — 학습 파일(2029 코호트 2027-01-25, 수학·영어 2과목, 보류), 공지 3줄, 검증 로그 6줄. 사이트에 게시하지 않는다. 내용은 모두 새로 쓴 것이고 주소는 `example.org`다.

## 넣지 않는 것(지침 5, 08 4절)
교과서·기출·EBS 원문, 검수 대기·예비분(비공개 저장소), 비공개 색인. 커밋 전 `tools/precommit_check.py`가 막는다.
