"""요청·robots(05 C2~C5). 시제품 v0.2와 같은 규칙."""
import time, urllib.robotparser
from urllib.parse import urlsplit
import requests

UA = "SuneungLabBot/1.0 (+https://suneunglab.com/about/bot/)"   # C4: 봇 안내 페이지 주소(사이트 B-07)
TIMEOUT = 20
RETRY_WAITS = (30, 120)   # 05 5절: 재시도 2회
HOST_INTERVAL = 5         # C3: 같은 호스트 5초 이상


def session():
    s = requests.Session()
    s.headers.update({"User-Agent": UA, "Accept-Language": "ko-KR,ko;q=0.9"})
    return s


class Robots:
    """C2: 우리 UA 규칙과 '*' 규칙 중 하나라도 금지면 금지. robots를 못 읽으면 수집하지 않음(없음 404 = 허용)."""
    def __init__(self, s):
        self.s, self.cache = s, {}

    def allowed(self, url):
        p = urlsplit(url); root = f"{p.scheme}://{p.netloc}"
        if root not in self.cache:
            rp = urllib.robotparser.RobotFileParser()
            try:
                r = self.s.get(root + "/robots.txt", timeout=TIMEOUT)
                rp.parse(r.text.splitlines() if r.status_code == 200 else [])
                self.cache[root] = ("ok" if r.status_code == 200 else f"none({r.status_code})", rp)
            except requests.RequestException as e:
                self.cache[root] = (f"error({type(e).__name__})", None)
        state, rp = self.cache[root]
        if rp is None:
            return False, state
        return (rp.can_fetch(UA, url) and rp.can_fetch("*", url)), state


class Polite:
    """C3: 호스트별 마지막 요청 시각을 기억해 5초 간격을 지킨다(sleep=False면 시험용으로 건너뜀)."""
    def __init__(self, sleep=True):
        self.sleep, self.last = sleep, {}

    def wait(self, url):
        h = urlsplit(url).netloc
        if self.sleep and h in self.last:
            time.sleep(max(0, HOST_INTERVAL - (time.time() - self.last[h])))

    def done(self, url):
        self.last[urlsplit(url).netloc] = time.time()


def fetch(s, url, waits=RETRY_WAITS):
    """200이면 (본문, None), 아니면 (None, 오류). 인코딩 추정 보정."""
    last = None
    for i in range(len(waits) + 1):
        try:
            r = s.get(url, timeout=TIMEOUT)
            if r.status_code == 200:
                if not r.encoding or r.encoding.lower() == "iso-8859-1":
                    r.encoding = r.apparent_encoding
                return r.text, None
            last = f"HTTP {r.status_code}"
        except requests.RequestException as e:
            last = type(e).__name__
        if i < len(waits):
            time.sleep(waits[i])
    return None, last
