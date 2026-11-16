"""수능랩 공개 저장소 커밋 전 검사(02_설계 11_구축백로그 B-02, 08 4절).
막는 것: 04_비공개 경로, 교과서·OCR 파일, 색인·상태 파일, PDF, 비공개 표시가 있는 파일.
사용: python tools/precommit_check.py  (git 저장소 안에서, 스테이징된 파일 검사)
      python tools/precommit_check.py 파일1 파일2 ...  (지정 파일 검사)
종료 코드: 0 통과, 1 차단."""
import re, subprocess, sys
from pathlib import Path

BLOCK_PATH = [r"(^|/)04_비공개(/|$)", r"비공개", r"교과서", r"OCR", r"\.pdf$", r"(^|/)(review|reserve|private)/",
              r"\.(idx|hash)$", r"(^|/)(streak|state)\.json$", r"(^|/)\.env"]
BLOCK_TEXT = [r"\[비공개·공개 금지\]", r"===== PDF p\.\d{3} ====="]
SKIP = ("tools/precommit_check.py", "tools/test_precommit_check.py")  # 규칙 문자열을 담은 검사 도구 자신

def staged():
    out = subprocess.run(["git", "-c", "core.quotepath=false", "diff", "--cached", "--name-only", "--diff-filter=ACMR"],
                         capture_output=True, text=True, check=True).stdout
    return [l for l in out.splitlines() if l.strip()]

def check(paths):
    bad = []
    for p in paths:
        q = p.replace("\\", "/")
        for pat in BLOCK_PATH:
            if re.search(pat, q, re.I):
                bad.append((p, f"경로 규칙 {pat}")); break
        else:
            if q.endswith(SKIP):
                continue
            f = Path(p)
            if f.is_file() and f.stat().st_size < 5_000_000:
                try:
                    t = f.read_text(encoding="utf-8")
                except (UnicodeDecodeError, OSError):
                    continue
                for pat in BLOCK_TEXT:
                    if re.search(pat, t):
                        bad.append((p, f"내용 규칙 {pat}")); break
    return bad

def main(argv):
    paths = argv[1:] or staged()
    bad = check(paths)
    for p, why in bad:
        print(f"[차단] {p} — {why}")
    if bad:
        print(f"커밋 중단: {len(bad)}개 파일이 비공개 규칙에 걸림(지침 5).")
        return 1
    print(f"통과: {len(paths)}개 파일")
    return 0

if __name__ == "__main__":
    sys.exit(main(sys.argv))
