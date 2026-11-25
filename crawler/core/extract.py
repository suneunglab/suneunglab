"""목록 추출·정리(시제품 v0.2의 extract·post·norm_*를 그대로 옮김)."""
import datetime as dt, re
from urllib.parse import urljoin, urlsplit, urlunsplit, parse_qsl, urlencode
from bs4 import BeautifulSoup

TRACKING = re.compile(r"^(utm_|fbclid|gclid)", re.I)
DATE_RE = re.compile(r"(20\d{2}|\d{2})[.\-/년]\s?(\d{1,2})[.\-/월]\s?(\d{1,2})")


def norm_url(base, href):
    u = urlsplit(urljoin(base, href))
    q = [(k, v) for k, v in parse_qsl(u.query, keep_blank_values=True) if not TRACKING.match(k)]
    return urlunsplit((u.scheme, u.netloc, u.path, urlencode(q), ""))


def norm_date(text):
    m = DATE_RE.search(text or "")
    if not m:
        return None
    y, mo, d = m.groups(); y = int(y); y = y + 2000 if y < 100 else y
    try:
        return dt.date(y, int(mo), int(d)).isoformat()
    except ValueError:
        return None


def norm_title(t):
    t = re.sub(r"\s+", " ", t or "").strip()
    return re.sub(r"^\[?(공지|알림|NEW|new)\]?\s*", "", t)


def extract(html, src):
    """선택자가 있으면 그대로, 없으면 자동 추정(행 안에 링크 1개 + 날짜 1개). → ([(제목, href, 날짜글, onclick)], 방식)"""
    soup = BeautifulSoup(html, "html.parser")
    rows = []
    tc = src.get("table_cols")
    if tc:
        for tr in soup.select("tbody tr"):
            td = [c.get_text(" ", strip=True) for c in tr.find_all("td")]
            if len(td) <= max(tc.values()):
                continue
            y, m = td[tc["year"]], td[tc["month"]]
            d = f"{y}-{int(m):02d}-01" if y.isdigit() and m.isdigit() else ""
            rows.append((td[tc["title"]], "", d, ""))
        return rows, "table-cols"
    if src.get("item"):
        for el in soup.select(src["item"]):
            a = el.select_one(src["title"]) if src.get("title") else el.find("a")
            de = el.select_one(src["date"]) if src.get("date") else el
            if a and a.get_text(strip=True):
                rows.append((a.get_text(" ", strip=True), a.get("href") or "", de.get_text(" ", strip=True) if de else "", a.get("onclick") or ""))
        return rows, "selector"
    for el in soup.select("tbody tr, ul li, ol li, div.list li, dl"):
        links = [a for a in el.find_all("a") if len(a.get_text(strip=True)) >= 6]
        txt = el.get_text(" ", strip=True)
        if links and norm_date(txt):
            a = max(links, key=lambda x: len(x.get_text(strip=True)))
            rows.append((a.get_text(" ", strip=True), a.get("href") or "", txt, a.get("onclick") or ""))
    if not rows:
        for a in soup.find_all("a"):
            txt = a.get_text(" ", strip=True)
            if len(txt) >= 12 and norm_date(txt):
                last = list(DATE_RE.finditer(txt))[-1]
                title = (txt[:last.start()] + txt[last.end():]).strip().rstrip(".").strip()
                rows.append((title, a.get("href") or "", txt[last.start():last.end()], a.get("onclick") or ""))
        if rows:
            return rows, "auto-card"
    return rows, "auto"


def post(rows, src):
    """대상별 보정: href 필터, onclick → 상세 주소, 제목 정리, 같은 링크 중복 제거. → [(제목, href, 날짜글)]"""
    out, seen = [], set()
    req = src.get("require_href"); oc = src.get("onclick_re"); tpl = src.get("link_template")
    strip = [re.compile(x) for x in src.get("strip_title", [])]
    for title, href, dtext, onclick in rows:
        if req and req not in (href or ""):
            continue
        if oc and tpl and onclick:
            m = re.search(oc, onclick)
            if m:
                href = tpl.format(*m.groups())
        for rx in strip:
            title = rx.sub("", title).strip()
        key = title + "|" + (dtext or "") if src.get("dedup") == "title_date" else (href or "") + "|" + title
        if key in seen:
            continue
        seen.add(key); out.append((title, href, dtext))
    return out
