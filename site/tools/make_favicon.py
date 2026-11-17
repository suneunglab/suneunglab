"""파비콘 만들기 — 워드마크 축약형(남색 원 #1F3A5F + 주황 '랩' #F28C28, 2026-10-29 확정 A안).
'랩' 글자는 Pretendard ExtraBold(SIL OFL 1.1)의 윤곽선을 경로로 바꿔 넣는다(보는 기기의 글꼴과 무관하게 같은 모양).
사용: python3 tools/make_favicon.py <Pretendard-ExtraBold.otf 경로>
  글꼴 받기: npm pack pretendard@1.3.9 → package/dist/public/static/Pretendard-ExtraBold.otf
결과: public/favicon.svg(원형), public/favicon.ico(16·32·48), public/apple-touch-icon.png(180, 정사각형 — iOS가 모서리를 둥글게 자름).
PNG는 Playwright(Chromium)로 SVG를 그려 만든다. 2026-11-17 B-05."""
import sys
from fontTools.ttLib import TTFont
from fontTools.pens.svgPathPen import SVGPathPen
from fontTools.pens.boundsPen import BoundsPen
from fontTools.pens.transformPen import TransformPen

NAVY, ORANGE = '#1F3A5F', '#F28C28'
font = TTFont(sys.argv[1])
gs = font.getGlyphSet()
name = font.getBestCmap()[ord('랩')]
bp = BoundsPen(gs); gs[name].draw(bp)
x0, y0, x1, y1 = bp.bounds

def glyph_path(size, ratio):
    # 글자 높이를 size*ratio로 맞추고 가운데 정렬(글꼴 좌표는 y가 위로 증가 → 뒤집기)
    s = size * ratio / (y1 - y0)
    tx = size / 2 - s * (x0 + x1) / 2
    ty = size / 2 + s * (y0 + y1) / 2
    sp = SVGPathPen(gs, ntos=lambda v: ('%.2f' % v).rstrip('0').rstrip('.'))
    gs[name].draw(TransformPen(sp, (s, 0, 0, -s, tx, ty)))
    return sp.getCommands()

circle = (f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 64 64">'
          f'<circle cx="32" cy="32" r="32" fill="{NAVY}"/><path fill="{ORANGE}" d="{glyph_path(64, 0.56)}"/></svg>\n')
square = (f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 180 180">'
          f'<rect width="180" height="180" fill="{NAVY}"/><path fill="{ORANGE}" d="{glyph_path(180, 0.52)}"/></svg>\n')
open('public/favicon.svg', 'w').write(circle)

import io
from PIL import Image
from playwright.sync_api import sync_playwright
def render(svg, px):
    with sync_playwright() as pw:
        b = pw.chromium.launch(); pg = b.new_page(viewport={'width': px, 'height': px})
        pg.set_content(f'<html><body style="margin:0;background:transparent">{svg.replace("<svg ", f"<svg width={px} height={px} ", 1)}</body></html>')
        png = pg.screenshot(omit_background=True, clip={'x': 0, 'y': 0, 'width': px, 'height': px}); b.close()
    return Image.open(io.BytesIO(png)).convert('RGBA')
big = render(circle, 256)
big.save('public/favicon.ico', sizes=[(16, 16), (32, 32), (48, 48)])
render(square, 180).convert('RGB').save('public/apple-touch-icon.png', optimize=True)
print('ok')
