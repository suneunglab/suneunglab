"""수능랩 공지 수집 실행(B-14, 2026-11-25 — 시제품 crawl.py v0.2 대체).
사용: python crawler/run.py --notices data/notices --state <비공개 저장소>/crawler-state [--sources crawler/sources.yaml] [--only id1,id2] [--no-sleep] [--no-retry]
결과: 공개 = data/notices/{YYYY}/{MM}.jsonl / 비공개 = state/streak.json·crawl_status.json·alerts.txt·kice_signals.json. 경보([주의])가 있으면 종료 코드 1.
B-15(2026-11-26): 특수 어댑터(adapters/), 평가원 소식 감지(kice_watch), 예비 경로(fallback — 주 경로 3일 연속 이상 시), 같은 글 중복 제거(05 7-4).
"""
import argparse, datetime as dt, json, os, sys, time
import yaml
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from core import net, extract, model, store, state, alerts, adapter, VERSION
import adapters  # noqa: F401 — 특수 어댑터 등록(B-15)
from adapters import kice

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
    db = store.NoticeStore(a.notices); counts = {"new": 0, "changed": 0, "same": 0, "dup": 0}
    only = set(a.only.split(",")) if a.only else None
    # 05 7-4: 주 경로가 3일 연속 이상이면 예비 경로(fallback)로 바꿔 수집(평소에는 예비 경로를 수집하지 않음)
    sk_path = os.path.join(a.state, "streak.json")
    prev = json.load(open(sk_path, encoding="utf-8")) if os.path.exists(sk_path) else {}
    plan = []
    for src in cfg:
        fb = src.get("fallback")
        if fb and prev.get(src["id"], {}).get("days", 0) >= state.STREAK_DAYS:
            plan.append(dict(fb, org_id=fb.get("org_id", src["org_id"]), board_id=fb.get("board_id", src["board_id"]), _fallback_of=src["id"]))
        plan.append(src)
    signals = []
    for src in plan:
        if not src.get("enabled", True) or (only and src["id"] not in only):
            continue
        for k in ("org_id", "board_id"):
            if not src.get(k):
                raise SystemExit(f"{src['id']}: {k} 없음(sources.yaml)")
        src = dict(src, _no_retry=a.no_retry, _polite=polite)
        st = {"id": src["id"], "org": src["org"], "board": src["board"], "url": src["url"]}
        if src.get("_fallback_of"):
            st["fallback_of"] = src["_fallback_of"]
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
            if src.get("kice_watch"):
                sig = kice.apply(it)
                if sig:
                    signals.append(sig)
            if db.same_post(it):
                counts["dup"] += 1; continue
            counts[db.upsert(it)] += 1; n += 1
        st.update(result="ok" if rows else "zero_match", items=n)
        st_all["sources"].append(st)
    months = db.save()
    st_all.update(counts, total_saved=len(db.items), months=months)
    sk = state.update_streak(sk_path, [x for x in st_all["sources"] if not x.get("fallback_of")], today)
    msgs = alerts.build(st_all["sources"], sk)
    with open(os.path.join(a.state, "kice_signals.json"), "w", encoding="utf-8") as f:
        json.dump({"run_at": now_iso, "signals": signals}, f, ensure_ascii=False, indent=1)
    msgs += [f"[정보] 평가원 관련 공지 감지({x['kind']}): {x['title']} ({x['url']})" for x in signals if x["kind"] in ("plan", "exam_date")]
    st_all["alert_messages"] = msgs; st_all["kice_signals"] = len(signals)
    with open(os.path.join(a.state, "alerts.txt"), "w", encoding="utf-8") as f:
        f.write("\n".join(msgs) + ("\n" if msgs else ""))
    with open(os.path.join(a.state, "crawl_status.json"), "w", encoding="utf-8") as f:
        json.dump(st_all, f, ensure_ascii=False, indent=2)
    print(json.dumps({k: st_all[k] for k in ("run_at", "new", "changed", "same", "dup", "total_saved", "kice_signals")}, ensure_ascii=False))
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
