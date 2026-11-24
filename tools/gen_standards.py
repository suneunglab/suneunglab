#!/usr/bin/env python3
"""성취기준 코드 → 주소 슬러그 변환표 생성(02 사이트맵 6절, B-13, 2026-11-24).

입력: 비공개 설계 폴더의 03_참고자료/성취기준목록.md(교육부 고시 제2022-33호 별책에서 추출, 317개)
출력: data/standards.yaml — 코드·슬러그·과목·과목명·영역 번호만 담는다.
      성취기준 문장은 넣지 않는다(교육과정 문서 공공누리 제2유형: 상업적 이용 금지 — 광고 사이트라 문장 전재를 피함).
사용: python tools/gen_standards.py <성취기준목록.md 경로> [--check]
      --check: 파일을 쓰지 않고 지금 data/standards.yaml과 같은지만 확인(다르면 종료 코드 1).
"""
import re, sys, pathlib

# 02 사이트맵 6절 표 — 원래 약칭 → (과목 슬러그, 영문 약칭, 과목명)
ABBR = {
    '10공국1': ('korean', 'ck1', '공통국어1'), '10공국2': ('korean', 'ck2', '공통국어2'),
    '12화언': ('korean', 'sl', '화법과 언어'), '12독작': ('korean', 'rw', '독서와 작문'), '12문학': ('korean', 'lit', '문학'),
    '10공수1': ('math', 'cm1', '공통수학1'), '10공수2': ('math', 'cm2', '공통수학2'),
    '12대수': ('math', 'alg', '대수'), '12미적Ⅰ': ('math', 'calc1', '미적분Ⅰ'), '12확통': ('math', 'stat', '확률과 통계'),
    '10공영1': ('english', 'ce1', '공통영어1'), '10공영2': ('english', 'ce2', '공통영어2'),
    '12영Ⅰ': ('english', 'eng1', '영어Ⅰ'), '12영Ⅱ': ('english', 'eng2', '영어Ⅱ'),
    '10한사1': ('history', 'kh1', '한국사1'), '10한사2': ('history', 'kh2', '한국사2'),
    '10통사1': ('social', 'is1', '통합사회1'), '10통사2': ('social', 'is2', '통합사회2'),
    '10통과1': ('science', 'isc1', '통합과학1'), '10통과2': ('science', 'isc2', '통합과학2'),
}


def parse(md: str):
    rows, seen = [], set()
    for ln in md.replace('\r', '').split('\n'):
        m = re.match(r'^\| \[([^\]]+)\] \|', ln)
        if not m:
            continue
        code = m.group(1)
        mm = re.fullmatch(r'(\d{2}[^\-]*?)-?(\d{2})-(\d{2})', code)
        if not mm:
            raise SystemExit(f'형식 밖 코드: [{code}]')
        abbr, a, n = mm.groups()
        if abbr not in ABBR:
            raise SystemExit(f'약칭 대응 없음: {abbr} ([{code}]) — 02 사이트맵 6절 표에 추가')
        if code in seen:
            raise SystemExit(f'코드 중복: [{code}]')
        seen.add(code)
        subj, en, course = ABBR[abbr]
        rows.append({'code': f'[{code}]', 'slug': f'{abbr[:2]}-{en}-{a}-{n}', 'subject': subj, 'course': course, 'area': a})
    return rows


def render(rows):
    head = ('# 성취기준 코드 → 주소 슬러그 변환표 — tools/gen_standards.py가 만든다(손으로 고치지 않음).\n'
            '# 규칙: 02 사이트맵 6절 `[학년 + 과목약칭 + 번호]` → `학년-영문약칭-번호`. 화면에는 원래 코드, 주소에만 슬러그.\n'
            '# 출처: 교육부 고시 제2022-33호 별책(국가교육과정정보센터). 성취기준 문장은 싣지 않는다(공공누리 제2유형).\n'
            f'count: {len(rows)}\nstandards:\n')
    body = ''.join(f'  - {{ code: "{r["code"]}", slug: {r["slug"]}, subject: {r["subject"]}, course: {r["course"]}, area: "{r["area"]}" }}\n' for r in rows)
    return head + body


def main():
    if len(sys.argv) < 2:
        raise SystemExit(__doc__)
    rows = parse(pathlib.Path(sys.argv[1]).read_text(encoding='utf-8'))
    out = pathlib.Path(__file__).resolve().parent.parent / 'data' / 'standards.yaml'
    text = render(rows)
    if '--check' in sys.argv:
        same = out.exists() and out.read_text(encoding='utf-8') == text
        print('일치' if same else '다름'); sys.exit(0 if same else 1)
    out.write_text(text, encoding='utf-8')
    print(f'{len(rows)}개 → {out}')


if __name__ == '__main__':
    main()
