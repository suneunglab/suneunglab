"""수능랩 공지 수집 실행(B-14, 2026-11-25 — 시제품 crawl.py v0.2 대체).
사용: python crawler/run.py --notices data/notices --state <비공개 저장소>/crawler-state [--sources crawler/sources.yaml] [--only id1,id2] [--no-sleep] [--no-retry]
결과: 공개 = data/notices/{YYYY}/{MM}.jsonl / 비공개 = state/streak.json·crawl_status.json·alerts.txt. 경보([주의])가 있으면 종료 코드 1.
"""
import argparse, datetime as dt, json, os, sys, time
import yaml
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from core import net, extract, model, store, state, alerts, adapter, VERSION

HERE = os.path.dirname(os.path.abspath(__file__)); REPO = os.path.dirname(HERE)
KST = dt.timezone(dt.timedelta(hours=9))


def load(p):
    with open(p, encoding="utf-8") as f:
        return yaml.safe_load(f)


def run(a, now=None):
    state.guard_private(a.state, REPO)
    cfg = load(a.sources); kw = load(os.path.join(HERE, "keywords.yaml")); cats = load(os.path.join(HERE, "categories.yaml"))
    now = now or dt.datetime.now(KST); today = now.date().isoformat(); now_iso = now.isoformat(timespec="seconds")
    s = net.session(); robots = net.Robots(s); polite = net.Polite(sleep=not a.no_sleep)
    st_all = {"run_at": now_iso, "ua": net.UA, "version": VERSION, "sources": []}
    db = store.NoticeStore(a.notices); counts = {"new": 0, "changed": 0, "same": 0}
    only = set(a.only.split(",")) if a.only else None
    for src in cfg:
        if not src.get("enabled", True) or (only and src["id"] not in only):
            continue
        for k in ("org_id", "board_id"):
            if not src.get(k):
                raise SystemExit(f"{src['id']}: {k} 없음(sources.yaml)")
        src = dict(src, _no_retry=a.no_retry)
        st = {"id": src["id"], "org": src["org"], "board": src["board"], "url": src["url"]}
        polite.wait(src["url"]); t0 = time.time()
        ok, rstate = robots.allowed(src["url"]); st["robots"] = rstate
        if not ok:
            st.update(result="robots_blocked", items=0); st_all["sources"].append(st); continue
        rows, err, meta = adapter.get(src).rows(s, src); polite.done(src["url"]); st["ms"] = int((time.time() - t0) * 1000)
        if rows is None:
            st.update(result="fetch_fail", error=err, items=0); st_all["sources"].append(st); continue
        st["mode"], st["rows_raw"] = meta; st["rows_kept"] = len(rows)
        words = kw["dicts"].get(src.get("keywords") or "", []); n = 0
        for title_raw, href, dtext in rows:
            t = extract.norm_title(title_raw)
            if not t or not model.keep(t, words, kw["exclude"]):
                continue
            js = not href or href == "#" or href.lower().startswith("javascript")
            url = src["url"] if js else extract.norm_url(src["url"], href)
            cat = model.classify(t, cats) or src.get("category_default", "etc")
            it = model.build(src, title_raw, t, url, extract.norm_date(dtext), cat, now_iso, today)
            counts[db.upsert(it)] += 1; n += 1
        st.update(result="ok" if rows else "zero_match", items=n)
        st_all["sources"].append(st)
    months = db.save()
    st_all.update(counts, total_saved=len(db.items), months=months)
    sk = state.update_streak(os.path.join(a.state, "streak.json"), st_all["sources"], today)
    msgs = alerts.build(st_all["sources"], sk); st_all["alert_messages"] = msgs
    with open(os.path.join(a.state, "alerts.txt"), "w", encoding="utf-8") as f:
        f.write("\n".join(msgs) + ("\n" if msgs else ""))
    with open(os.path.join(a.state, "crawl_status.json"), "w", encoding="utf-8") as f:
        json.dump(st_all, f, ensure_ascii=False, indent=2)
    print(json.dumps({k: st_all[k] for k in ("run_at", "new", "changed", "same", "total_saved")}, ensure_ascii=False))
    for x in st_all["sources"]:
        print(f'{x["id"]:12} {x["result"]:15} items={x.get("items")} robots={x.get("robots")} mode={x.get("mode")} ms={x.get("ms")}')
    return 1 if any(m.startswith("[주의]") for m in msgs) else 0


def args(argv=None):
    ap = argparse.ArgumentParser()
    ap.add_argument("--sources", default=os.path.join(HERE, "sources.yaml"))
    ap.add_argument("--notices", default=os.path.join(REPO, "data", "notices"))
    ap.add_argument("--state", required=True, help="비공개 저장소 안 상태 폴더")
    ap.add_argument("--only"); ap.add_argument("--no-sleep", action="store_true"); ap.add_argument("--no-retry", action="store_true")
    return ap.parse_args(argv)


if __name__ == "__main__":
    sys.exit(run(args()))
