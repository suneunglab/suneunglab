"""오프라인 시험(B-14, 2026-11-25): 로컬 HTTP 서버로 5경우(표·목록·구조 변경·robots 금지·접속 실패)
+ 이어 쓰기(재실행 중복 0·수정 감지·first_seen 유지) + 3일 연속 [주의] + 상태 폴더 공개 저장소 차단 + notice.schema 통과.
실행: python crawler/tests/test_core.py (requests·bs4·pyyaml·jsonschema 필요)"""
import datetime as dt, functools, http.server, json, os, shutil, sys, tempfile, threading
import yaml
HERE = os.path.dirname(os.path.abspath(__file__)); ROOT = os.path.dirname(HERE); REPO = os.path.dirname(ROOT)
sys.path.insert(0, ROOT)
import run as R
from core import state, alerts
from jsonschema import Draft202012Validator, FormatChecker

KST = dt.timezone(dt.timedelta(hours=9))
SCHEMA = Draft202012Validator(json.load(open(os.path.join(REPO, "content", "schema", "notice.schema.json"), encoding="utf-8")), format_checker=FormatChecker())


def serve(d):
    class Quiet(http.server.SimpleHTTPRequestHandler):
        def log_message(self, *a):
            pass
    srv = http.server.ThreadingHTTPServer(("127.0.0.1", 0), functools.partial(Quiet, directory=d))
    threading.Thread(target=srv.serve_forever, daemon=True).start(); return srv


def read_all(root):
    out = []
    for dp, _, fs in os.walk(root):
        for f in fs:
            out += [json.loads(l) for l in open(os.path.join(dp, f), encoding="utf-8") if l.strip()]
    return out


def main():
    d = tempfile.mkdtemp(); fx = os.path.join(HERE, "fixtures")
    for f in os.listdir(fx): shutil.copy(os.path.join(fx, f), d)
    os.makedirs(os.path.join(d, "blocked")); open(os.path.join(d, "blocked", "x.html"), "w").write("<a>x</a>")
    open(os.path.join(d, "robots.txt"), "w").write("User-agent: *\nDisallow: /blocked/\n")
    srv = serve(d); base = f"http://127.0.0.1:{srv.server_port}"
    src = [{"id": "t-table", "org": "가", "org_id": "ga", "board": "표", "board_id": "table", "url": base + "/table.html", "keywords": "A", "category_default": "policy"},
           {"id": "t-list", "org": "나", "org_id": "na", "board": "목록", "board_id": "list", "url": base + "/list.html", "keywords": None, "category_default": "etc"},
           {"id": "t-empty", "org": "다", "org_id": "da", "board": "구조변경", "board_id": "empty", "url": base + "/empty.html", "keywords": None},
           {"id": "t-robots", "org": "라", "org_id": "ra", "board": "금지", "board_id": "blocked", "url": base + "/blocked/x.html", "keywords": None},
           {"id": "t-404", "org": "마", "org_id": "ma", "board": "없음", "board_id": "none", "url": base + "/nope.html", "keywords": None}]
    work = tempfile.mkdtemp(); sp = os.path.join(work, "s.yaml"); yaml.safe_dump(src, open(sp, "w"), allow_unicode=True)
    notices, st_dir = os.path.join(work, "pub", "data", "notices"), os.path.join(work, "private", "crawler-state")
    os.makedirs(st_dir)
    a = R.args(["--sources", sp, "--notices", notices, "--state", st_dir, "--no-sleep", "--no-retry"])
    day = lambda n, h=5: dt.datetime(2026, 12, n, h, 0, tzinfo=KST)

    # 1일차
    rc = R.run(a, day(1)); st = json.load(open(os.path.join(st_dir, "crawl_status.json"), encoding="utf-8"))
    r = {s["id"]: s for s in st["sources"]}
    assert rc == 0, "1일차는 [정보]만 — 종료 코드 0"
    assert r["t-table"]["result"] == "ok" and r["t-table"]["items"] == 2          # 제외어(채용) 1건 제외
    assert r["t-list"]["items"] == 2 and r["t-list"]["mode"] == "auto"
    assert r["t-empty"]["result"] == "zero_match" and r["t-robots"]["result"] == "robots_blocked"
    assert r["t-404"]["result"] == "fetch_fail" and r["t-404"]["error"] == "HTTP 404"
    items = read_all(notices); assert len(items) == 4 and st["new"] == 4
    for it in items:
        errs = [e.message for e in SCHEMA.iter_errors(it)]; assert not errs, (it, errs)
    t = {i["title"]: i for i in items}
    k = t["2028학년도 대학수학능력시험 시행 기본계획 발표"]
    assert k["posted"] == "2026-10-30" and "utm_source" not in k["url"] and k["category"] == "policy" and k["org"] == "ga"
    assert t["고교학점제 운영 현황 보도자료"]["posted"] == "2026-10-28"
    assert t["2028학년도 수시모집 원서접수 안내"]["category"] == "schedule"
    assert t["2028학년도 정시모집 경쟁률 현황"]["url"] == base + "/list.html"       # JS 링크 → 목록 주소
    assert os.path.exists(os.path.join(notices, "2026", "10.jsonl"))                # 게시 월 기준 파일
    assert not any(os.path.exists(os.path.join(work, "pub", "data", x)) for x in ("streak.json", "crawl_status.json"))   # 상태는 공개 쪽에 없음
    assert open(os.path.join(st_dir, "alerts.txt"), encoding="utf-8").read().count("[정보]") == 3

    # 같은 날 재실행: 새 글 0, 연속 일수 그대로
    R.run(a, day(1, 9)); st = json.load(open(os.path.join(st_dir, "crawl_status.json"), encoding="utf-8"))
    assert st["new"] == 0 and st["total_saved"] == 4
    assert json.load(open(os.path.join(st_dir, "streak.json"), encoding="utf-8"))["t-empty"]["days"] == 1

    # 2일차: 제목 1건 수정 → changed 1, first_seen 유지 / 이어 쓰기는 저장된 파일에서(메모리 아님)
    p = os.path.join(d, "list.html"); h = open(p, encoding="utf-8").read()
    open(p, "w", encoding="utf-8").write(h.replace("수시모집 원서접수 안내", "수시모집 원서접수 안내(일정 변경)"))
    R.run(a, day(2)); st = json.load(open(os.path.join(st_dir, "crawl_status.json"), encoding="utf-8"))
    assert st["new"] == 0 and st["changed"] == 1 and st["total_saved"] == 4, st
    m = {i["title"]: i for i in read_all(notices)}["2028학년도 수시모집 원서접수 안내(일정 변경)"]
    assert m["first_seen"].startswith("2026-12-01") and m["last_seen"].startswith("2026-12-02")

    # 3일차: 이상 3곳이 3일 연속 → [주의] 3건, 종료 코드 1. [긴급]은 크롤러가 내지 않음
    rc = R.run(a, day(3)); msgs = open(os.path.join(st_dir, "alerts.txt"), encoding="utf-8").read().splitlines()
    assert rc == 1 and sum(x.startswith("[주의]") for x in msgs) == 3 and not any(x.startswith("[긴급]") for x in msgs), msgs
    assert all(w in " ".join(msgs) for w in ("zero_match", "robots_blocked", "fetch_fail"))

    # 복구: 구조 변경 대상이 다시 정상 → 0일
    open(os.path.join(d, "empty.html"), "w", encoding="utf-8").write(open(os.path.join(fx, "list.html"), encoding="utf-8").read())
    R.run(a, day(4)); sk = json.load(open(os.path.join(st_dir, "streak.json"), encoding="utf-8"))
    assert sk["t-empty"]["days"] == 0 and sk["t-empty"]["last_ok"] == "2026-12-04" and sk["t-404"]["days"] == 4

    # 상태 폴더를 공개 저장소 안에 주면 멈춤
    try:
        state.guard_private(os.path.join(REPO, "data", "state"), REPO); raise AssertionError("공개 저장소 안 상태 폴더가 통과됨")
    except SystemExit:
        pass
    # 운영 설정 8곳: org_id·board_id가 스키마 형식에 맞는지
    import re
    cfg = yaml.safe_load(open(os.path.join(ROOT, "sources.yaml"), encoding="utf-8"))
    assert len(cfg) == 8 and all(re.fullmatch(r"[a-z0-9-]+", c["org_id"]) and re.fullmatch(r"[a-z0-9-]+", c["board_id"]) for c in cfg)
    srv.shutdown(); print("ALL PASS — 5경우·이어 쓰기·수정 감지·3일 [주의]·복구·공개 차단·스키마")


if __name__ == "__main__":
    main()
