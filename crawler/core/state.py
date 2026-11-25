"""연속 실패 상태(05 11절): 상태 파일 streak.json·crawl_status.json·alerts.txt는 비공개 저장소(08 4절).
공개 저장소 안 경로를 주면 멈춘다(상태·오류 기록이 공개되지 않게)."""
import json, os

STREAK_DAYS = 3   # 같은 대상 3일 연속 이상이면 [주의](07 4절 — 긴급은 게시 0건·저작권 신고만)


def guard_private(state_dir, public_root):
    a, b = os.path.realpath(state_dir), os.path.realpath(public_root)
    if a == b or a.startswith(b + os.sep):
        raise SystemExit(f"상태 폴더가 공개 저장소 안에 있습니다: {state_dir} — 비공개 저장소 경로를 주세요(08 4절)")


def is_bad(st):
    """이상 = 수집 실패·robots 금지·목록 0행(구조 변경 의심). 목록은 있었는데 키워드에 맞는 글이 0건인 것은 정상."""
    return st["result"] != "ok" or st.get("rows_kept", 0) == 0


def update_streak(path, sources, today):
    """대상별 연속 이상 일수. 같은 날 여러 번 실행해도 하루로 센다. 정상 수집 1회로 0."""
    st = json.load(open(path, encoding="utf-8")) if os.path.exists(path) else {}
    for s in sources:
        e = st.get(s["id"], {"days": 0, "last": None, "last_ok": None})
        if not is_bad(s):
            e = {"days": 0, "last": today, "last_ok": today}
        elif e.get("last") != today:
            e = {"days": e.get("days", 0) + 1, "last": today, "last_ok": e.get("last_ok")}
        st[s["id"]] = e
    os.makedirs(os.path.dirname(path) or ".", exist_ok=True)
    with open(path, "w", encoding="utf-8") as f:
        json.dump(st, f, ensure_ascii=False, indent=1)
    return st
