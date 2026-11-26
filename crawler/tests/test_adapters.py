"""B-15 특수 어댑터 오프라인 시험(2026-11-26): 교육부(여러 쪽·상세 주소·제외어), 대교협(어디가 제외),
평가원 소식 감지(분류 보정·신호), 예비 경로(주 경로 3일 연속 이상 시 정책브리핑) + 같은 글 중복 제거(05 7-4).
실행: python crawler/tests/test_adapters.py"""
import datetime as dt, json, os, shutil, sys, tempfile
import yaml
HERE = os.path.dirname(os.path.abspath(__file__)); ROOT = os.path.dirname(HERE)
sys.path.insert(0, ROOT); sys.path.insert(0, HERE)
import run as R
from adapters import kice
from test_core import serve, read_all, SCHEMA, KST


def main():
    # 1) 규칙 단위 시험
    assert kice.detect("2028학년도 대학수학능력시험 시행 기본계획 발표") == ("policy", "plan")
    assert kice.detect("2028학년도 대학수학능력시험 시행세부계획 공고") == ("policy", "plan")
    assert kice.detect("2029학년도 대학수학능력시험 시행일 안내") == ("schedule", "exam_date")
    assert kice.detect("2027학년도 대학수학능력시험 채점 결과 발표") == ("schedule", "score")
    assert kice.detect("2027학년도 수능 채점 결과") == ("result", "score")
    assert kice.detect("2028학년도 6월 모의평가 시행 안내") == ("mock", "mock")
    assert kice.detect("초등 돌봄 교실 확대 방안 발표") == (None, None)

    d = tempfile.mkdtemp(); fx = os.path.join(HERE, "fixtures")
    for f in os.listdir(fx): shutil.copy(os.path.join(fx, f), d)
    open(os.path.join(d, "robots.txt"), "w").write("User-agent: *\nAllow: /\n")
    srv = serve(d); base = f"http://127.0.0.1:{srv.server_port}"
    moe = {"id": "moe-press", "org": "교육부", "org_id": "moe", "board": "보도자료", "board_id": "press", "url": base + "/moe_p1.html",
           "keywords": "A", "category_default": "policy", "adapter": "moe", "kice_watch": True,
           "onclick_re": "goView\\('(\\d+)', '(\\d+)'", "link_template": "https://www.moe.go.kr/boardCnts/viewRenew.do?boardID={0}&boardSeq={1}&lev=0&m=020402&s=moe"}
    kcue = {"id": "kcue-press", "org": "한국대학교육협의회", "org_id": "kcue", "board": "보도자료", "board_id": "press", "url": base + "/kcue.html",
            "keywords": None, "category_default": "policy", "adapter": "kcue", "kice_watch": True}
    work = tempfile.mkdtemp(); sp = os.path.join(work, "s.yaml")
    notices, st_dir = os.path.join(work, "pub", "data", "notices"), os.path.join(work, "private", "state"); os.makedirs(st_dir)
    a = R.args(["--sources", sp, "--notices", notices, "--state", st_dir, "--no-sleep", "--no-retry"])
    day = lambda n: dt.datetime(2027, 6, n, 5, 0, tzinfo=KST)

    # 2) 교육부 2쪽(page_param) — 정적 서버라 ?page=2도 1쪽 파일이 오므로, 2쪽 주소 생성만 따로 확인하고 수집은 1쪽+중복 제거 확인
    from adapters.moe import page_url
    assert page_url("https://x.kr/list.do?boardID=294&page=1", "page", 2) == "https://x.kr/list.do?boardID=294&page=2"
    yaml.safe_dump([dict(moe, pages=2, page_param="page"), kcue], open(sp, "w"), allow_unicode=True)
    R.run(a, day(1))
    st = json.load(open(os.path.join(st_dir, "crawl_status.json"), encoding="utf-8")); r = {s["id"]: s for s in st["sources"]}
    items = read_all(notices); t = {i["title"]: i for i in items}
    for it in items:
        assert not list(SCHEMA.iter_errors(it)), it
    assert r["moe-press"]["items"] == 2, r                         # 제외어(채용) 1·키워드 없음(돌봄) 1 제외, 2쪽은 같은 글이라 중복 제거
    p = t["2028학년도 대학수학능력시험 시행 기본계획 발표"]
    assert p["url"].endswith("boardID=294&boardSeq=1001&lev=0&m=020402&s=moe") and p["category"] == "policy"
    assert t["2028학년도 6월 모의평가 시행 안내"]["category"] == "mock"
    assert r["kcue-press"]["items"] == 2 and "대입정보포털 어디가 서비스 개편 안내" not in t   # 어디가 링크 제외
    assert t["2028학년도 8월 모의평가 이후 대입 상담 운영"]["category"] == "mock"
    sig = json.load(open(os.path.join(st_dir, "kice_signals.json"), encoding="utf-8"))["signals"]
    assert sorted(x["kind"] for x in sig) == ["mock", "mock", "plan"], sig
    alerts = open(os.path.join(st_dir, "alerts.txt"), encoding="utf-8").read()
    assert "[정보] 평가원 관련 공지 감지(plan)" in alerts and "[주의]" not in alerts

    # 3) 2쪽 실제 수집: 2쪽 파일을 쪽 주소로 흉내(page_url이 만드는 주소를 서버 파일로 매핑)
    import adapters.moe as am
    orig = am.page_url; am.page_url = lambda url, param, n: base + "/moe_p2.html"
    R.run(a, day(2)); am.page_url = orig
    t = {i["title"]: i for i in read_all(notices)}
    assert t["2027학년도 대학수학능력시험 채점 결과 발표"]["category"] == "schedule"
    assert t["2029학년도 대학수학능력시험 시행일 안내"]["category"] == "schedule"
    sig = json.load(open(os.path.join(st_dir, "kice_signals.json"), encoding="utf-8"))["signals"]
    assert {"score", "exam_date"} <= {x["kind"] for x in sig}

    # 4) 예비 경로: 교육부가 3일 연속 실패 → 4일차부터 정책브리핑 수집, 같은 글(제목+게시일)은 중복 제거
    korea = {"id": "korea-press", "org": "교육부(정책브리핑)", "board": "보도자료", "url": base + "/korea_press.html", "keywords": "A", "category_default": "policy", "kice_watch": True}
    yaml.safe_dump([dict(moe, url=base + "/nope.html", fallback=korea), kcue], open(sp, "w"), allow_unicode=True)
    for n in (3, 4, 5):
        R.run(a, day(n))
    st = json.load(open(os.path.join(st_dir, "crawl_status.json"), encoding="utf-8"))
    assert not any(s.get("fallback_of") for s in st["sources"])          # 3일째까지는 예비 경로 안 씀
    R.run(a, day(6)); st = json.load(open(os.path.join(st_dir, "crawl_status.json"), encoding="utf-8"))
    fb = [s for s in st["sources"] if s.get("fallback_of") == "moe-press"]
    assert fb and fb[0]["result"] == "ok" and st["dup"] >= 1, st          # 시행 기본계획 글은 교육부 것과 같아 중복 제거
    t = read_all(notices)
    assert sum(i["title"] == "2028학년도 대학수학능력시험 시행 기본계획 발표" for i in t) == 1
    assert any(i["title"] == "2028학년도 수시모집 원서접수 일정 안내" and i["org"] == "moe" for i in t)
    sk = json.load(open(os.path.join(st_dir, "streak.json"), encoding="utf-8"))
    assert "korea-press" not in sk and sk["moe-press"]["days"] == 4       # 예비 경로는 연속 일수에 넣지 않음, 주 경로 이상은 계속 셈
    srv.shutdown(); print("ALL PASS — 교육부(상세 주소·제외어·2쪽)·대교협(어디가 제외)·평가원 감지 6규칙·예비 경로·중복 제거·스키마")


if __name__ == "__main__":
    main()
