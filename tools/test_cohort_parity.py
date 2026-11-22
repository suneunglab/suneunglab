"""학년도·트랙 계산 시험 — Python(tools/cohort.py)과 JS(site/src/lib/calendar.js)가 경계일마다 같은 답을 내는지,
그리고 04 데이터모델 11-2절 전환 시간표의 기대값과 맞는지 본다. 2026-11-22 B-11.
실행: python tools/test_cohort_parity.py   (node와 site/node_modules(js-yaml) 필요)"""
import datetime as dt
import json
import subprocess
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import cohort as co  # noqa: E402

ROOT = Path(__file__).resolve().parent.parent
EX, CH = co.load_rows()


def boundary_dates():
    out = {"2026-11-22", "2027-01-24", "2027-01-25"}
    for y in range(2027, 2032):
        out |= {f"{y}-02-28", f"{y}-03-01"}
        if y % 4 == 0:
            out.add(f"{y}-02-29")
    for cohort in range(2027, 2033):  # 그 학년도 수능 당일·다음 날
        d = dt.date.fromisoformat(co.exam_of(cohort, EX)["date"])
        out |= {d.isoformat(), (d + dt.timedelta(days=1)).isoformat(), (d - dt.timedelta(days=1)).isoformat()}
    return sorted(out)


def g(s, grade):
    return next(x for x in s["slots"] if x["grade"] == grade)


# 04 데이터모델 11-2절 전환 시간표 + E-4·E-5 기대값
EXPECT = [
    ("2027-01-24", lambda s: s["generate"] == [], "소프트 오픈 전날: 생성 없음(active_from)"),
    ("2027-01-25", lambda s: [x["cohort"] for x in s["generate"]] == [2029, 2028], "소프트 오픈: g1=2029, g2=2028 생성"),
    ("2027-03-01", lambda s: [x["cohort"] for x in s["generate"]] == [2030, 2029, 2028], "3/1: g1=2030, g2=2029, g3=2028(3트랙)"),
    ("2027-11-18", lambda s: g(s, 3)["phase"] == "학습" and 2028 in [b["year"] for b in s["band"]], "2028 수능 당일: 아직 학습·띠에 있음"),
    ("2027-11-19", lambda s: g(s, 3)["phase"] == "정시" and 2028 not in [b["year"] for b in s["band"]] and 2028 not in [x["cohort"] for x in s["generate"]], "수능 다음 날: 2028 정시 모드·띠 제외·생성 중단"),
    ("2028-02-28", lambda s: g(s, 3)["cohort"] == 2028 and g(s, 3)["phase"] == "정시", "2/28까지 정시 유지(E-5)"),
    ("2028-03-01", lambda s: [x["cohort"] for x in s["generate"]] == [2031, 2030, 2029], "2028 졸업, 2031 고1(E-2·E-3)"),
    ("2028-11-17", lambda s: g(s, 3)["phase"] == "정시", "2029 수능 다음 날 정시"),
    ("2030-11-21", lambda s: co.exam_of(2031, EX) == {"year": 2031, "date": "2030-11-21", "status": "예상"}, "2031 시험일은 관례 계산(11월 셋째 목요일)·예상"),
]


def main():
    dates = boundary_dates()
    js = json.loads(subprocess.run(["node", str(ROOT / "tools" / "cohort_js_dump.mjs"), *dates],
                                   capture_output=True, text=True, check=True).stdout)
    fail = 0
    for j in js:
        p = co.summary(j["date"], EX, CH)
        same = p == j
        if not same:
            print(f"FAIL 불일치 {j['date']}\n  py={p}\n  js={j}")
            fail += 1
    print(f"Python·JS 대조 {len(js)}개 날짜, 불일치 {fail}")
    for date, check, name in EXPECT:
        ok = check(co.summary(date, EX, CH))
        print(("ok  " if ok else "FAIL") + f" {date} {name}")
        fail += not ok
    for y in range(2027, 2040):  # 관례 계산이 실제로 셋째 목요일인지
        d = dt.date.fromisoformat(co.third_thursday_nov(y))
        if not (d.weekday() == 3 and 15 <= d.day <= 21):
            print(f"FAIL 셋째 목요일 아님 {y} {d}")
            fail += 1
    print(f"실패 {fail}건")
    return 1 if fail else 0


if __name__ == "__main__":
    sys.exit(main())
