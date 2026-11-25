"""알림 문구(07 4절 등급). 크롤러가 내는 것은 [주의](3일 연속 이상)·[정보](오늘 이상) 두 가지.
[긴급](게시 0건·저작권 신고)은 생성·게시 쪽에서 낸다. 실제 발송(텔레그램 운영 채널)은 B-17."""
from .state import STREAK_DAYS


def build(sources, streak):
    out = []
    for s in sources:
        d = streak.get(s["id"], {}).get("days", 0)
        why = s["result"] + (f" ({s['error']})" if s.get("error") else "")
        if d >= STREAK_DAYS:
            out.append(f"[주의] {s['org']} {s['board']}: {d}일 연속 {why} — 게시판 구조·주소 확인 필요 ({s['url']})")
        elif d > 0:
            out.append(f"[정보] {s['org']} {s['board']}: 오늘 {why} — 연속 {d}일")
    return out
