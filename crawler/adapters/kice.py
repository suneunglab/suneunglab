"""평가원 소식 감지(05 7-3, 결정 16의 대체 경로). 평가원 누리집은 수집하지 않고, 교육부·대교협 공지 제목으로 감지한다.
결과: ① 분류 보정(아래 규칙) ② 신호 목록 — 비공개 상태 폴더 kice_signals.json(사이트 S3 변경 이력·E-6 시험일 확정 검토 후보)
한계: 평가원 누리집에만 올라오는 소식은 놓칠 수 있다 → 사이트 S4 바로가기에 '평가원 공지는 원문에서 확인' 안내(05 7-3)."""
import re

EXAM = re.compile(r"대학수학능력시험|수능")
PLAN = re.compile(r"시행\s?기본\s?계획|시행\s?세부\s?계획")
DATE = re.compile(r"시행일|시험일|시행\s?일자")
SCORE = re.compile(r"채점\s?결과|성적\s?통지")
MOCK = re.compile(r"모의평가")
SCHEDULE_WORDS = ("일정", "접수", "원서", "마감", "발표", "시험일", "시간표", "통지")


def detect(title):
    """→ (분류 보정 또는 None, 신호 종류 또는 None). 순서: 시행계획 > 시험일 > 채점·성적 > 모의평가."""
    if EXAM.search(title) and PLAN.search(title):
        return "policy", "plan"
    if EXAM.search(title) and DATE.search(title):
        return "schedule", "exam_date"            # 04 11절 E-6: 제목·본문 날짜 일치 시 자동 확정(E1) — 확정 처리는 생성·게시 쪽
    if SCORE.search(title):
        return ("schedule" if any(w in title for w in SCHEDULE_WORDS) else "result"), "score"
    if MOCK.search(title):
        return "mock", "mock"
    return None, None


def apply(item):
    """공지 1건에 규칙 적용 → 신호(dict) 또는 None. item['category']는 보정된다."""
    cat, sig = detect(item["title"])
    if cat:
        item["category"] = cat
    if not sig:
        return None
    return {"kind": sig, "id": item["id"], "org": item["org"], "title": item["title"], "posted": item["posted"], "url": item["url"]}
