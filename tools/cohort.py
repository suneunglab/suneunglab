"""학년도·트랙·생성 코호트 계산(Python) — 2026-11-22 B-11(계획서 60행 앞당김).
site/src/lib/calendar.js와 같은 규칙을 옮긴 것이다(02_설계 04_데이터모델 v1.0 4-1절, 11절 E-1~E-5·E-8).
생성 파이프라인(B-23·B-24)은 이 파일로 '그날 어느 트랙·코호트를 만들지'를 정한다(백로그 B-11·F22).
두 언어 결과는 tools/test_cohort_parity.py가 경계일마다 대조한다.

사용: python tools/cohort.py              # 오늘(KST)
      python tools/cohort.py 2027-03-01   # 특정 날짜
출력: JSON — slots(고1~고3), generate(생성 대상), band(홈 D-day 띠)
필요: pyyaml"""
import datetime as dt
import json
import sys
from pathlib import Path

import yaml

ROOT = Path(__file__).resolve().parent.parent
KST = dt.timezone(dt.timedelta(hours=9))


def _iso(v):
    return v.isoformat() if isinstance(v, (dt.date, dt.datetime)) else v


def load_rows(data_dir=ROOT / "data"):
    def read(name):
        rows = yaml.safe_load((Path(data_dir) / f"{name}.yaml").read_text(encoding="utf-8"))
        return [{k: _iso(v) for k, v in r.items()} for r in rows]
    return read("exam_years"), read("cohorts")


def kst_today(now=None):
    return (now or dt.datetime.now(dt.timezone.utc)).astimezone(KST).date().isoformat()


def school_year(date):
    y, m = int(date[:4]), int(date[5:7])
    return y if m >= 3 else y - 1


def grade_of(cohort, date):
    return school_year(date) - cohort + 4


def third_thursday_nov(cohort):
    y = cohort - 1
    first = dt.date(y, 11, 1)
    first_thu = 1 + (3 - first.weekday()) % 7  # 월=0 … 목=3
    return f"{y}-11-{first_thu + 14:02d}"


def exam_of(cohort, exam_rows):
    for e in exam_rows:
        if e["year"] == cohort and e.get("exam_date"):
            return {"year": cohort, "date": e["exam_date"], "status": e["status"]}
    return {"year": cohort, "date": third_thursday_nov(cohort), "status": "예상"}


def phase_of(cohort, date, exam_rows):
    g = grade_of(cohort, date)
    if g < 1:
        return "입학 전"
    if g > 3:
        return "졸업"
    if g == 3 and date > exam_of(cohort, exam_rows)["date"]:
        return "정시"
    return "학습"


def slots_of(date, first_cohort, exam_rows):
    sy = school_year(date)
    out = []
    for grade in (1, 2, 3):
        cohort = sy - grade + 4
        if cohort >= first_cohort:
            out.append({"grade": grade, "cohort": cohort, "active": True, "phase": phase_of(cohort, date, exam_rows)})
        else:
            nxt = sy + 1
            while nxt - grade + 4 < first_cohort:
                nxt += 1
            out.append({"grade": grade, "cohort": nxt - grade + 4, "active": False, "start": f"{nxt}-03-01"})
    return out


def generation_cohorts(date, first_cohort, exam_rows, cohort_rows):
    out = []
    for s in slots_of(date, first_cohort, exam_rows):
        if not (s["active"] and s["phase"] == "학습"):
            continue
        row = next((c for c in cohort_rows if c["id"] == s["cohort"]), None)
        if row and row.get("active_from") and date < row["active_from"]:
            continue
        out.append({"grade": s["grade"], "cohort": s["cohort"], "track": f"g{s['grade']}"})
    return out


def band_cohorts(date, first_cohort, exam_rows):
    out = [exam_of(s["cohort"], exam_rows) for s in slots_of(date, first_cohort, exam_rows)
           if s["active"] and date <= exam_of(s["cohort"], exam_rows)["date"]]
    return sorted(out, key=lambda e: e["year"])


def summary(date, exam_rows=None, cohort_rows=None):
    if exam_rows is None:
        exam_rows, cohort_rows = load_rows()
    first = min(c["id"] for c in cohort_rows)
    return {
        "date": date,
        "slots": slots_of(date, first, exam_rows),
        "generate": generation_cohorts(date, first, exam_rows, cohort_rows),
        "band": band_cohorts(date, first, exam_rows),
    }


if __name__ == "__main__":
    d = sys.argv[1] if len(sys.argv) > 1 else kst_today()
    print(json.dumps(summary(d), ensure_ascii=False, indent=1))
