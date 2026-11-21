"""수능랩 콘텐츠 검사(V-1 형식 검사, 02_설계 11_구축백로그 B-10, 04 데이터모델 7·8·8-1·9·10절, 06 1·5절).
검사 대상: 학습 파일(*.md, YAML 머리말), 공지(*.jsonl, data/notices/), 검증 로그(*.jsonl, logs/verify/).
스키마: content/schema/*.schema.json (JSON Schema 2020-12) + 아래 추가 규칙.
사용: python tools/validate_content.py              (content/lessons, data/notices, logs/verify, content/schema/examples 전체)
      python tools/validate_content.py 파일1 파일2 ...
종료 코드: 0 통과, 1 오류. 경고는 표시만 한다.
필요: pip install -r tools/requirements.txt (jsonschema, pyyaml)"""
import datetime as dt
import json
import re
import sys
from pathlib import Path

import yaml
from jsonschema import Draft202012Validator, FormatChecker

ROOT = Path(__file__).resolve().parent.parent
SCHEMA = ROOT / "content" / "schema"
SUBJECTS = ["korean", "math", "english", "history", "social", "science"]
# 행동 영역 코드 — site/src/lib/content.js BEHAVIOR 와 같다(03_참고자료 수능_평가기준_2028 2절)
BEHAVIOR = {
    "korean": {"vocab", "literal", "inferential", "critical", "apply"},
    "math": {"calc", "understand", "reason", "solve"},
    "english": {"main", "detail", "implied", "context", "speak", "write", "form"},
    "history": {"knowledge", "chrono", "issue", "inquiry", "source", "judge"},
    "social": {"concept", "problem", "design", "analyze", "conclude", "value"},
    "science": {"understand", "apply", "hypothesis", "design", "collect", "transform", "generalize", "communicate"},
}
POINTS = {"math": {2, 3, 4}, "social": {1.5, 2, 2.5}, "science": {1.5, 2, 2.5}, "korean": {2, 3}, "english": {2, 3}, "history": {2, 3}}
PER_DAY = {1: 3, 2: 4, 3: 5}            # 04 5절 problems_per_day
DIFF = {3: [1, 1, 2], 4: [1, 2, 2, 3], 5: [1, 2, 2, 3, 3]}  # 06 5절 D2 하루 배치(문항 수별)
MARKS = "①②③④⑤"


def _schema(name):
    return Draft202012Validator(json.loads((SCHEMA / name).read_text(encoding="utf-8")), format_checker=FormatChecker())


def grade(cohort, date):
    """04 4-1절: 학교 연도 Y(3/1 시작), 학년 = Y − 코호트 + 4."""
    y = date.year if (date.month, date.day) >= (3, 1) else date.year - 1
    return y - cohort + 4


def front_matter(text):
    m = re.match(r"^---\r?\n(.*?)\r?\n---\r?\n?", text, re.S)
    if not m:
        raise ValueError("YAML 머리말(--- … ---)이 없음")
    return yaml.safe_load(m.group(1))


def _jsonable(o):
    if isinstance(o, dict):
        return {k: _jsonable(v) for k, v in o.items()}
    if isinstance(o, list):
        return [_jsonable(v) for v in o]
    if isinstance(o, dt.datetime):
        return o.isoformat()
    if isinstance(o, dt.date):
        return o.isoformat()
    return o


def check_lesson(path, data, errors, warns):
    data = _jsonable(data)
    for e in sorted(_schema("lesson.schema.json").iter_errors(data), key=lambda e: list(e.path)):
        errors.append(f"스키마 {'/'.join(map(str, e.path)) or '(최상위)'}: {e.message}")
    if errors:
        return
    cohort, date = data["cohort"], dt.date.fromisoformat(data["date"])
    lid = f"{cohort}-{data['date']}"
    if data["id"] != lid:
        errors.append(f"id는 '{lid}'여야 함(코호트-날짜)")
    p = path.as_posix()
    m = re.search(r"lessons/(\d{4})/(\d{4})/(\d{2})/(\d{4}-\d{2}-\d{2})\.md$", p)
    if not m:
        errors.append("경로는 lessons/{코호트}/{YYYY}/{MM}/{YYYY-MM-DD}.md (04 10-1절)")
    elif (int(m.group(1)), m.group(4)) != (cohort, data["date"]) or m.group(2) != data["date"][:4] or m.group(3) != data["date"][5:7]:
        errors.append("경로의 코호트·날짜가 머리말과 다름")
    if "/examples/" in p and data.get("example") is not True:
        errors.append("examples 폴더의 파일은 example: true 여야 함")
    if "/examples/" not in p and data.get("example"):
        errors.append("example: true 파일은 content/schema/examples/ 밖에 둘 수 없음(게시 금지)")
    g = grade(cohort, date)
    if g not in (1, 2, 3):
        errors.append(f"{data['date']}에 {cohort} 코호트는 재학 중이 아님(학년 {g})")
        return
    subs = [s["subject"] for s in data["subjects"]]
    if len(set(subs)) != len(subs):
        errors.append("과목 중복")
    if data["status"] in ("게시", "예비분") and sorted(subs) != sorted(SUBJECTS):
        errors.append("게시·예비분은 6과목 모두 있어야 함(04 7절)")
    if data["status"] == "보류" and not data.get("hold_reason"):
        warns.append("보류 사유(hold_reason) 없음")
    for s in data["subjects"]:
        sub, probs = s["subject"], s["problems"]
        tag = sub
        c = s["concept"]
        if g == 1 and any(not x.startswith("[10") for x in c["standards"]):
            errors.append(f"{tag}: 고1 트랙(g1) 성취기준은 [10…] 코드(04 5절)")
        _check_copyright(tag + " 개념", c["copyright"], data["status"], errors)
        _textbook(tag, c["textbook_ref"], errors)
        if len(probs) != PER_DAY[g]:
            errors.append(f"{tag}: g{g} 문항 수는 {PER_DAY[g]}개(04 5절) — 현재 {len(probs)}")
        nums = [q["num"] for q in probs]
        if nums != list(range(1, len(probs) + 1)):
            errors.append(f"{tag}: num은 1부터 차례대로(F1) — 현재 {nums}")
        if sorted(q["difficulty"] for q in probs) != DIFF.get(len(probs), []):
            warns.append(f"{tag}: 난이도 배치가 06 5절 D2({DIFF.get(len(probs))})와 다름")
        beh = [q["behavior"] for q in probs]
        for b in set(beh):
            if b not in BEHAVIOR[sub]:
                errors.append(f"{tag}: 행동 영역 코드 '{b}'는 {sub}에 없음")
            elif beh.count(b) > 2:
                errors.append(f"{tag}: 같은 행동 영역 '{b}' {beh.count(b)}문항 — 최대 2(F3)")
        answers = []
        for q in probs:
            qt = f"{tag}-{q['num']}"
            if q.get("id") and q["id"] != f"{lid}-{sub}-{q['num']}":
                errors.append(f"{qt}: id는 '{lid}-{sub}-{q['num']}'")
            if q["points"] not in POINTS[sub]:
                errors.append(f"{qt}: 배점 {q['points']}는 {sub}에서 허용 안 됨({sorted(POINTS[sub])})")
            if g == 1 and not q["standard"].startswith("[10"):
                errors.append(f"{qt}: 고1 트랙 성취기준은 [10…]")
            if q["standard"] not in c["standards"]:
                warns.append(f"{qt}: 문항 성취기준이 개념 카드 standards에 없음")
            if q["format"] == "5지선다":
                ch = q.get("choices") or []
                if len(ch) != 5:
                    errors.append(f"{qt}: 5지선다 선지는 5개")
                elif not all(x in MARKS for x in ch) and any(x.strip()[:1] in MARKS for x in ch):
                    errors.append(f"{qt}: 선지에 번호 기호를 붙이지 않음(F15) — 밑줄 번호 고르기 문항만 기호 5개")
                if not (isinstance(q["answer"], str) and len(q["answer"]) == 1 and q["answer"] in MARKS):
                    errors.append(f"{qt}: 5지선다 정답은 ①~⑤ 한 글자(F5)")
                else:
                    answers.append(q["answer"])
            else:
                if sub != "math":
                    errors.append(f"{qt}: 단답형은 수학만(06 5절)")
                if q.get("choices"):
                    errors.append(f"{qt}: 단답형에는 선지가 없음")
                a = q["answer"]
                if isinstance(a, str) and re.fullmatch(r"[0-9]+", a):
                    a = int(a)
                if not (isinstance(a, int) and 1 <= a <= 999):
                    errors.append(f"{qt}: 단답형 정답은 1~999 자연수(F5)")
            if data["status"] == "게시" and q["verification"]["result"] != "일치":
                errors.append(f"{qt}: 검증 불일치 문항은 게시할 수 없음(06 7절)")
            _check_copyright(qt, q["copyright"], data["status"], errors)
        for a in set(answers):
            if answers.count(a) > 2:
                errors.append(f"{tag}: 정답 {a}가 {answers.count(a)}문항 — 최대 2(F20)")


def _check_copyright(tag, cp, status, errors):
    if status == "게시" and (cp["overlap_check"] != "통과" or cp["exam_variant"] != "아님"):
        errors.append(f"{tag}: 저작권 검사(V-5·V-6) 미통과 — 게시 금지(결정 17)")
    if cp["overlap_check"] == "통과" and (cp["max_overlap_words"] >= 8 or cp["max_overlap_chars"] >= 30):
        errors.append(f"{tag}: 최대 일치 8어절 또는 30자 이상인데 '통과'로 표시됨(06 6-1)")


def _textbook(tag, ref, errors):
    if ref != "교과서 미입력" and not re.search(r"p\.\s?\d", ref):
        errors.append(f"{tag}: textbook_ref는 '교과서 미입력' 또는 '출판사 과목 p.쪽'(F18)")


def check_jsonl(path, schema_name, errors):
    v = _schema(schema_name)
    for i, line in enumerate(path.read_text(encoding="utf-8").splitlines(), 1):
        if not line.strip():
            continue
        try:
            obj = json.loads(line)
        except json.JSONDecodeError as e:
            errors.append(f"{i}행 JSON 오류: {e}")
            continue
        for e in v.iter_errors(obj):
            errors.append(f"{i}행 {'/'.join(map(str, e.path)) or '(최상위)'}: {e.message}")
        if "/examples/" in path.as_posix() and obj.get("example") is not True:
            errors.append(f"{i}행: examples 폴더의 줄은 example: true")


def check_file(path):
    errors, warns = [], []
    p = path.as_posix()
    try:
        if p.endswith(".md"):
            check_lesson(path, front_matter(path.read_text(encoding="utf-8")), errors, warns)
        elif p.endswith(".jsonl") and "/notices/" in p:
            check_jsonl(path, "notice.schema.json", errors)
        elif p.endswith(".jsonl") and "/logs/verify/" in p:
            check_jsonl(path, "verify_log.schema.json", errors)
        else:
            warns.append("검사 규칙이 없는 파일 — 건너뜀")
    except (ValueError, yaml.YAMLError) as e:
        errors.append(str(e))
    return errors, warns


def default_targets():
    out = []
    for base, pat in [("content/lessons", "**/*.md"), ("data/notices", "**/*.jsonl"), ("logs/verify", "*.jsonl"),
                      ("content/schema/examples/lessons", "**/*.md"), ("content/schema/examples/notices", "**/*.jsonl"),
                      ("content/schema/examples/logs/verify", "*.jsonl")]:
        d = ROOT / base
        if d.is_dir():
            out += sorted(d.glob(pat))
    return out


def main(argv):
    targets = [Path(a).resolve() for a in argv[1:]] or default_targets()
    bad = 0
    for t in targets:
        errors, warns = check_file(t)
        rel = t.relative_to(ROOT).as_posix() if t.is_relative_to(ROOT) else t.as_posix()
        for w in warns:
            print(f"[경고] {rel} — {w}")
        for e in errors:
            print(f"[오류] {rel} — {e}")
        if errors:
            bad += 1
        else:
            print(f"[통과] {rel}")
    print(f"검사 {len(targets)}개 파일, 오류 파일 {bad}개")
    return 1 if bad else 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))
