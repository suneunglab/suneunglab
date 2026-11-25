"""공지 1건 = content/schema/notice.schema.json(04 데이터모델 9절). 목록 메타데이터만(C1) — 본문·첨부 없음."""
import hashlib

CATEGORY_KO = {"policy": "정책·제도", "schedule": "일정", "mock": "모의평가·학력평가", "early": "수시",
               "regular": "정시", "result": "결과·경쟁률", "etc": "기타"}


def classify(title, cats):
    for c in cats:
        if any(k in title for k in c["keywords"]):
            return c["code"]
    return None


def keep(title, words, exclude):
    if any(x in title for x in exclude):
        return False
    return True if not words else any(k in title for k in words)


def notice_id(org_id, url, title, list_url):
    """같은 글 = 같은 id. 상세 주소가 없어 목록 주소를 공유하면 제목까지 키에 넣는다(시제품 규칙)."""
    key = org_id + url + ("|" + title if url == list_url else "")
    return hashlib.sha256(key.encode()).hexdigest()[:16]


def content_hash(title, posted):
    return hashlib.sha256((title + "|" + (posted or "")).encode()).hexdigest()


def summary(org, board, category):
    """한 줄 요약 — 제목·분류만으로 만든 안내(본문 요약 아님). 스키마상 '원문 확인' 문구 필수."""
    return f"{org} {board}에 올라온 {CATEGORY_KO.get(category, '기타')} 공지입니다. 자세한 내용은 원문 확인."


def build(src, title_raw, title, url, posted, category, now_iso, today):
    """posted가 없으면(목록에 날짜 없음) 수집한 날을 쓴다 — 화면에는 '게시일 미표기'를 표시하지 않고 수집일 기준으로 정렬."""
    return {
        "id": notice_id(src["org_id"], url, title, src["url"]),
        "org": src["org_id"], "board": src["board_id"],
        "title": title, "title_raw": title_raw,
        "posted": posted or today, "url": url, "category": category,
        "summary": summary(src["org"], src["board"], category),
        "content_hash": content_hash(title, posted),
        "first_seen": now_iso, "last_seen": now_iso,
    }
