"""대교협 보도자료 어댑터(05 7-1 A3: 키워드 필터 없음). 어디가(adiga.kr) 링크는 수집하지 않는다(결정 16 — robots 금지 대상)."""
from core import adapter

BLOCKED_HOSTS = ("adiga.kr",)


class KcueAdapter(adapter.ListAdapter):
    name = "kcue"

    def rows(self, s, src):
        rows, err, meta = super().rows(s, src)
        if rows is None:
            return rows, err, meta
        return [r for r in rows if not any(h in (r[1] or "") for h in BLOCKED_HOSTS)], None, meta


adapter.REGISTRY["kcue"] = KcueAdapter
