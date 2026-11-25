"""수능랩 크롤러 core v1.0(B-14, 2026-11-25) — 시제품 v0.2(2026-11-11)를 모듈로 나눠 운영용으로 올림.
명세: 02_설계 05_크롤러명세 v1.0(C1 목록 메타데이터만·C2 robots·C3 5초 간격·C4 UA 공개·C5 우회 금지, 4·5·9·11절), 07 운영규칙 4절(알림 등급).
모듈: net(robots·요청) · extract(목록 추출·정리) · model(공지 1건 = notice.schema) · store(data/notices 이어 쓰기)
      · state(연속 실패 — 비공개 저장소) · alerts(알림 문구) · adapter(어댑터 틀).
"""
VERSION = "1.0"
