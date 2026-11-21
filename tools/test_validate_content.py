"""validate_content.py 시험 — 견본 3개 통과, 일부러 틀린 예는 실패해야 한다(B-10).
실행: python tools/test_validate_content.py"""
import copy
import json
import re
import sys
import tempfile
from pathlib import Path

import yaml

sys.path.insert(0, str(Path(__file__).resolve().parent))
import validate_content as vc  # noqa: E402

EX = vc.ROOT / "content" / "schema" / "examples"
LESSON = EX / "lessons" / "2029" / "2027" / "01" / "2027-01-25.md"


def lesson_errors(mutate, rel="examples/lessons/2029/2027/01/2027-01-25.md"):
    data = vc.front_matter(LESSON.read_text(encoding="utf-8"))
    data = copy.deepcopy(data)
    mutate(data)
    errors, warns = [], []
    vc.check_lesson(Path("/x/content/schema/" + rel), data, errors, warns)
    return errors


def jsonl_errors(src, mutate, schema):
    rows = [json.loads(l) for l in src.read_text(encoding="utf-8").splitlines() if l.strip()]
    mutate(rows)
    with tempfile.TemporaryDirectory() as d:
        sub = Path(d) / ("notices" if "notice" in schema else "logs/verify") / "examples_fail"
        sub.mkdir(parents=True)
        f = sub / "t.jsonl"
        f.write_text("\n".join(json.dumps(r, ensure_ascii=False) for r in rows), encoding="utf-8")
        errors = []
        vc.check_jsonl(f, schema, errors)
        return errors


def m(path, value):
    def f(d):
        cur = d
        for k in path[:-1]:
            cur = cur[k]
        cur[path[-1]] = value
    return f


CASES = [
    ("정답 기호 아님(F5)", m(["subjects", 0, "problems", 0, "answer"], "3")),
    ("단답형 범위 밖", m(["subjects", 0, "problems", 1, "answer"], 1000)),
    ("format 허용 값 밖", m(["subjects", 0, "problems", 0, "format"], "mcq5")),
    ("선지에 번호 기호(F15)", m(["subjects", 0, "problems", 0, "choices"], ["① 6", "② 7", "③ 8", "④ 9", "⑤ 10"])),
    ("선지 4개", m(["subjects", 0, "problems", 0, "choices"], ["6", "7", "8", "9"])),
    ("영어 단답형", m(["subjects", 1, "problems", 0, "format"], "단답형")),
    ("행동 영역 코드 잘못", m(["subjects", 0, "problems", 0, "behavior"], "main")),
    ("수학 배점 1.5", m(["subjects", 0, "problems", 0, "points"], 1.5)),
    ("num 이 no(F1)", lambda d: d["subjects"][0]["problems"][0].update({"no": 1})),
    ("num 순서", m(["subjects", 0, "problems", 2, "num"], 5)),
    ("g1 문항 수 4", lambda d: d["subjects"][0]["problems"].append(copy.deepcopy(d["subjects"][0]["problems"][2]) | {"num": 4})),
    ("id 불일치", m(["id"], "2028-2027-01-25")),
    ("과목 중복", lambda d: d["subjects"].append(copy.deepcopy(d["subjects"][0]))),
    ("게시인데 6과목 아님", m(["status"], "게시")),
    ("textbook_ref 형식(F18)", m(["subjects", 0, "concept", "textbook_ref"], "없음")),
    ("고1에 [12…] 코드", m(["subjects", 0, "concept", "standards"], ["[12대수01-01]"])),
    ("겹침 30자인데 통과 표시", m(["subjects", 0, "problems", 0, "copyright", "max_overlap_chars"], 30)),
    ("같은 정답 3개(F20)", lambda d: [q.update({"answer": "②"}) for q in d["subjects"][1]["problems"]]),
    ("같은 행동 영역 3개(F3)", lambda d: [q.update({"behavior": "detail"}) for q in d["subjects"][1]["problems"]]),
    ("example 빠짐", lambda d: d.pop("example")),
    ("재학 아닌 코호트(2027 코호트 고3 졸업 뒤)", lambda d: d.update({"cohort": 2027, "id": "2027-2027-01-25"})),
]


def main():
    fail = 0
    for t in vc.default_targets():
        e, _ = vc.check_file(t)
        if "/examples/" in t.as_posix():
            ok = not e
            print(("ok  " if ok else "FAIL") + f" 견본 통과: {t.name}")
            fail += not ok
    for name, fn in CASES:
        e = lesson_errors(fn)
        ok = bool(e)
        print(("ok  " if ok else "FAIL") + f" 실패해야 함: {name}" + ("" if ok else " (오류 없음)"))
        fail += not ok
    nf = EX / "notices" / "2027" / "01.jsonl"
    for name, fn in [("공지 분류 밖", lambda r: r[0].update({"category": "news"})),
                     ("요약에 '원문 확인' 없음", lambda r: r[0].update({"summary": "요약"})),
                     ("id 16자 아님", lambda r: r[0].update({"id": "abc"}))]:
        ok = bool(jsonl_errors(nf, fn, "notice.schema.json"))
        print(("ok  " if ok else "FAIL") + f" 실패해야 함: {name}")
        fail += not ok
    lf = EX / "logs" / "verify" / "2027-01-25.jsonl"
    ok = bool(jsonl_errors(lf, lambda r: r[0]["checks"].pop("V-5"), "verify_log.schema.json"))
    print(("ok  " if ok else "FAIL") + " 실패해야 함: 검증 로그 V-5 빠짐")
    fail += not ok
    print(f"실패 {fail}건")
    return 1 if fail else 0


if __name__ == "__main__":
    sys.exit(main())
