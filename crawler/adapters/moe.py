"""교육부 보도자료 어댑터(05 7-1 A1: 쪽당 10건·1~2쪽, 사전 A, 상세 주소 = onclick goView → viewRenew.do).
쪽 이동 파라미터(page_param)는 실제 실행(B-16 Actions)에서 확인한 뒤 sources.yaml에 넣는다. 없으면 1쪽만."""
from urllib.parse import urlsplit, urlunsplit, parse_qsl, urlencode
from core import adapter, extract, net


def page_url(url, param, n):
    u = urlsplit(url); q = [(k, v) for k, v in parse_qsl(u.query, keep_blank_values=True) if k != param] + [(param, str(n))]
    return urlunsplit((u.scheme, u.netloc, u.path, urlencode(q), ""))


class MoeAdapter(adapter.ListAdapter):
    name = "moe"

    def rows(self, s, src):
        pages = int(src.get("pages") or 1) if src.get("page_param") else 1
        out, modes, raw_n, seen = [], set(), 0, set()
        for n in range(1, pages + 1):
            url = src["url"] if n == 1 else page_url(src["url"], src["page_param"], n)
            html, err = net.fetch(s, url, () if src.get("_no_retry") else net.RETRY_WAITS)
            if html is None:
                if n == 1:
                    return None, err, None
                break                                   # 2쪽 실패는 1쪽 결과로 계속
            if n > 1 and src.get("_polite"):
                src["_polite"].wait(url); src["_polite"].done(url)
            raw, mode = extract.extract(html, src); modes.add(mode); raw_n += len(raw)
            for r in extract.post(raw, src):
                key = (r[0], r[1])
                if key not in seen:
                    seen.add(key); out.append(r)
        return out, None, ("+".join(sorted(modes)), raw_n)


adapter.REGISTRY["moe"] = MoeAdapter
