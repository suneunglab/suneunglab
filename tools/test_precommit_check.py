import tempfile, os, sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent))
from precommit_check import check

def test_rules():
    d = Path(tempfile.mkdtemp())
    ok = d / "site" / "index.md"; ok.parent.mkdir(parents=True); ok.write_text("공개 문서", encoding="utf-8")
    hidden = d / "notes.md"; hidden.write_text("# [비공개·공개 금지] 교과서 OCR", encoding="utf-8")
    ocr = d / "x.md"; ocr.write_text("===== PDF p.012 =====\n본문", encoding="utf-8")
    paths = [str(ok), "04_비공개/a.yaml", "content/교과서/b.md", "data/streak.json", "a.pdf", "review/g1.yaml", str(hidden), str(ocr), ".env"]
    bad = {p for p, _ in check(paths)}
    assert str(ok) not in bad
    assert len(bad) == len(paths) - 1, bad

if __name__ == "__main__":
    test_rules(); print("test ok")
