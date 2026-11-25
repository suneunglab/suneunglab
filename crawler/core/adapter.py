"""어댑터 틀(05 10절 확장 구조). 대상 1곳 = 어댑터 1개: rows(session, src) → ([(제목, href, 날짜글)], 방식).
일반 게시판은 ListAdapter(설정만으로 동작). 평가원 소식 감지 등 특수 어댑터는 B-15에서 REGISTRY에 이름으로 등록."""
from . import extract, net


class ListAdapter:
    name = "list"

    def rows(self, s, src):
        html, err = net.fetch(s, src["url"], () if src.get("_no_retry") else net.RETRY_WAITS)
        if html is None:
            return None, err, None
        raw, mode = extract.extract(html, src)
        return extract.post(raw, src), None, (mode, len(raw))


REGISTRY = {"list": ListAdapter}


def get(src):
    name = src.get("adapter") or "list"
    if name not in REGISTRY:
        raise SystemExit(f"{src['id']}: 등록되지 않은 어댑터 {name}")
    return REGISTRY[name]()
