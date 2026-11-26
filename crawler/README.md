# crawler — 수능랩 공지 수집기 core v1.0 (B-14, 2026-11-25)

- 시제품 v0.2(2026-11-11, 비공개 저장소 `suneunglab-crawler-test`·PC `repo\crawler\`)를 운영용 모듈로 올렸다. 수집 규칙은 그대로다.
  - 목록의 제목·날짜·링크만 수집한다(본문·첨부 미수집, C1).
  - robots.txt는 우리 UA 규칙과 `*` 규칙 중 엄격한 쪽을 따른다(C2).
  - 같은 호스트는 5초 간격(C3), UA를 공개하고(C4), 우회하지 않는다(C5).
- 명세: 02_설계 `05_크롤러명세.md` v1.0의 4·5·9·10·11절, `07_운영규칙.md` 4절(알림 등급), `08_기술스택.md` 4절(저장소 구분).

## 바뀐 점(v0.2 → v1.0)
| 항목 | v0.2 | v1.0 |
|---|---|---|
| 3일 연속 이상 알림 | `[긴급]` | **`[주의]`**. 긴급은 게시 0건·저작권 신고일 때만이고 생성·게시 쪽에서 낸다. 하루만 이상이면 `[정보]` |
| 상태 파일(`streak.json`·`crawl_status.json`·`alerts.txt`) | 공지와 같은 폴더(Actions 캐시) | **비공개 저장소**의 `--state` 폴더. 공개 저장소 안 경로를 주면 멈춘다 |
| 공지 파일 | 실행한 달 기준, 자체 형식 | **`data/notices/{YYYY}/{MM}.jsonl`(게시 월 기준) + `content/schema/notice.schema.json` 형식**(org·board 영문 약칭, posted, summary, first_seen·last_seen) |
| 이어 쓰기 | 그 달 파일만 | 저장된 모든 달을 읽어 id로 합친다. 새 글은 추가하고, 같은 글은 last_seen만 고치고, 제목·날짜가 바뀌면 덮어쓴다(first_seen은 유지) |
| 구조 | `crawl.py` 한 파일 | `core/`(net·extract·model·store·state·alerts·adapter) + `run.py` |

## 파일
- `run.py`: 실행
- `sources.yaml`: 운영 대상 8곳. `org_id`·`board_id`는 공지 파일의 약칭이다.
- `keywords.yaml`: 05 7-2절 키워드 사전
- `categories.yaml`: 05 9절 분류표
- `core/adapter.py`: 어댑터 틀. 일반 게시판은 설정만으로 동작한다.
- `adapters/`(B-15, 2026-11-26): 특수 어댑터. 계획서 66~68행이 적은 경로를 따랐다.
  - `moe`: 교육부 보도자료. 상세 주소 규칙을 적용하고, 여러 쪽(`pages`·`page_param`)을 수집한다.
  - `kcue`: 대교협 보도자료. 어디가 링크는 뺀다(결정 16).
  - `kice`: 평가원 소식 감지(05 7-3). 평가원 누리집은 수집하지 않는다. `kice_watch: true`인 교육부·대교협 공지 제목에서 아래 소식을 감지한다.
    - 감지 대상: 시행계획, 시험일, 채점 결과·성적 통지, 모의평가
    - 감지하면 분류를 보정하고, 비공개 `kice_signals.json`에 신호를 남긴다.
    - 시행계획·시험일이면 `[정보]` 알림을 낸다.
- 예비 경로(05 7-4): 원본에 `fallback: {…}`을 두면, 원본이 3일 연속 이상할 때 그 경로로 수집한다. 제목과 게시일이 같은 글은 하나만 저장한다.
  - 정책브리핑 목록 주소와 교육부 2쪽 파라미터는 실제 실행 환경에서 확인한 뒤(B-16) `sources.yaml`에 넣는다.
- `tests/test_adapters.py`: B-15 오프라인 시험이다. 교육부·대교협 어댑터, 평가원 감지 규칙 6개, 예비 경로, 중복 제거를 확인한다.
- `tests/test_core.py`: 오프라인 시험. 아래 항목과 notice 스키마 통과를 확인한다.
  - 다섯 경우(표·목록·구조 변경·robots 금지·접속 실패)
  - 재실행 시 중복 0
  - 수정 감지(first_seen 유지)
  - 3일 연속 `[주의]`
  - 복구 시 연속 일수 0
  - 공개 저장소 안 상태 폴더 차단

## 실행
```
pip install -r crawler/requirements.txt
python crawler/run.py --state ../suneunglab-crawler-test/crawler-state      # 공지는 data/notices/에 쌓인다
python crawler/tests/test_core.py && python crawler/tests/test_adapters.py   # 오프라인 시험(jsonschema 필요)
```
- `[주의]`가 있으면 종료 코드는 1이다. 매일 예약 실행(GitHub Actions), 상태를 비공개 저장소에 커밋하는 절차, 수집 시각 조정은 B-16(12/04)에서 정한다. 텔레그램 발송은 B-17이다.
