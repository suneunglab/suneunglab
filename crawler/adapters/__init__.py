"""특수 어댑터(B-15, 2026-11-26 — 계획서 66~68행 '어댑터' 경로 repo\\crawler\\adapters\\…를 따름).
틀·일반 목록 어댑터는 core/adapter.py, 기관별 특수 처리는 여기에 두고 import 하면 core.adapter.REGISTRY에 이름으로 등록된다.
- moe : 교육부 보도자료(여러 쪽·상세 주소 규칙) — 05 7-1 A1
- kcue: 대교협 보도자료(어디가 링크 제외) — 05 7-1 A3, 결정 16
- kice: 평가원 소식 감지(평가원 누리집 미수집, 교육부·대교협 제목으로 감지) — 05 7-3, 결정 16
"""
from . import moe, kcue, kice  # noqa: F401  (등록 부수효과)
