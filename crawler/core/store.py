"""공지 저장(05 4절·11절 K-8): 공개 저장소 data/notices/{YYYY}/{MM}.jsonl(게시 월 기준).
이어 쓰기 = 저장소에 이미 커밋된 파일을 읽고, id로 합친다. 새 글 → 추가, 같은 글 → last_seen만, 제목·날짜 바뀜 → 덮어쓰기(first_seen 유지)."""
import json, os


class NoticeStore:
    def __init__(self, root):
        self.root = root            # .../data/notices
        self.items, self.where = {}, {}
        if os.path.isdir(root):
            for y in sorted(os.listdir(root)):
                yd = os.path.join(root, y)
                if not os.path.isdir(yd):
                    continue
                for f in sorted(os.listdir(yd)):
                    if f.endswith(".jsonl"):
                        with open(os.path.join(yd, f), encoding="utf-8") as fh:
                            for line in fh:
                                if line.strip():
                                    o = json.loads(line); self.items[o["id"]] = o
        self.loaded = len(self.items)

    def same_post(self, it):
        """05 7-4: 같은 기관·게시판에서 정규화 제목 + 게시일이 같은 다른 id(예비 경로 정책브리핑 ↔ 교육부)가 있으면 그 id."""
        for o in self.items.values():
            if o["id"] != it["id"] and o["org"] == it["org"] and o["board"] == it["board"] and o["title"] == it["title"] and o["posted"] == it["posted"]:
                return o["id"]
        return None

    def upsert(self, it):
        """→ 'new' | 'changed' | 'same'"""
        o = self.items.get(it["id"])
        if o is None:
            self.items[it["id"]] = it; return "new"
        if o["content_hash"] != it["content_hash"]:
            self.items[it["id"]] = dict(it, first_seen=o["first_seen"]); return "changed"
        o["last_seen"] = it["last_seen"]; return "same"

    def save(self):
        by = {}
        for o in self.items.values():
            by.setdefault(o["posted"][:7], []).append(o)
        for ym, lst in by.items():
            p = os.path.join(self.root, ym[:4], ym[5:7] + ".jsonl"); os.makedirs(os.path.dirname(p), exist_ok=True)
            lst.sort(key=lambda o: (o["posted"], o["first_seen"], o["id"]))
            with open(p, "w", encoding="utf-8", newline="\n") as fh:
                for o in lst:
                    fh.write(json.dumps(o, ensure_ascii=False) + "\n")
        return sorted(by)
