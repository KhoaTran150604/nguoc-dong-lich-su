# -*- coding: utf-8 -*-
"""Sinh HTML storyboard (khung hình + thoại) từ storyboard_phapbao.T → output/_prev/storyboard.html"""
import html
import os
import sys

sys.stdout.reconfigure(encoding='utf-8')
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
ROOT = os.path.dirname(os.path.dirname(os.path.dirname(HERE)))
import storyboard_phapbao as SB

OUTDIR = os.path.join(ROOT, 'du-an', 'tay-du-ky', 'output', '_prev')

HEAD = """<meta name="claude:viewport-fit-sides" content="cover">
<title>Storyboard Pháp Bảo</title>
<link rel="stylesheet" href="https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&family=Space+Grotesk:wght@600;700&display=swap">
<style>
:root{--bg:#f4f1ea;--fg:#262019;--muted:#6f685c;--card:#fffdf8;--line:#e4ddd0;--accent:#b33224;--gold:#9a7416;--chip:#efe9dc;--fh:"Space Grotesk",sans-serif;--fb:"Inter",sans-serif}
@media (prefers-color-scheme:dark){:root:not([data-theme="light"]){--bg:#171410;--fg:#ece6db;--muted:#a69b89;--card:#211d17;--line:#342e25;--accent:#e2604e;--gold:#d6ab45;--chip:#2a251e;color-scheme:dark}}
:root[data-theme="dark"]{--bg:#171410;--fg:#ece6db;--muted:#a69b89;--card:#211d17;--line:#342e25;--accent:#e2604e;--gold:#d6ab45;--chip:#2a251e;color-scheme:dark}
*{box-sizing:border-box}body{margin:0;background:var(--bg);color:var(--fg);font-family:var(--fb);line-height:1.55}
.wrap{max-width:900px;margin:0 auto;padding-left:max(16px,env(safe-area-inset-left,0px));padding-right:max(16px,env(safe-area-inset-right,0px))}
header{padding-block:34px 14px}h1{font-family:var(--fh);font-size:clamp(1.7rem,5vw,2.5rem);margin:.2em 0}
.eyebrow{font-size:.72rem;letter-spacing:.14em;text-transform:uppercase;color:var(--muted);font-weight:600}
.lead{color:var(--muted)}.status{display:inline-flex;gap:.4em;align-items:center;background:var(--chip);border:1px solid var(--line);border-radius:999px;padding:.3em .8em;font-size:.82rem;font-weight:600;margin-top:10px}
.dot{width:.6em;height:.6em;border-radius:50%;background:var(--gold)}
.scene{background:var(--card);border:1px solid var(--line);border-radius:14px;overflow:hidden;margin:16px 0}
.scene img{display:block;width:100%;max-width:100%}
.meta{display:flex;gap:10px;align-items:center;padding:12px 16px 0}
.act{font-family:var(--fh);font-weight:700;background:var(--accent);color:#fff;padding:.2em .6em;border-radius:7px;font-size:.84rem}
.act.fx{background:var(--gold)}.scene.demo{border:1px dashed var(--gold)}
.tc{color:var(--muted);font-size:.82rem;font-family:var(--fh)}
.loi{padding:10px 16px 16px;margin:0;font-size:.95rem}
footer{padding-block:24px 48px;color:var(--muted);font-size:.84rem}
</style>
"""


def main():
    os.makedirs(OUTDIR, exist_ok=True)
    parts = [HEAD, '<div class="wrap">',
             '<header><div class="eyebrow">西遊 · Storyboard nháp · chưa render video</div>',
             '<h1>Storyboard — Top 15 Pháp Bảo</h1>',
             '<p class="lead">%d khung hình tĩnh + lời thoại, đúng mạch kịch bản (đã chấm 91/92). '
             'Mỗi pháp bảo có thêm khung <b>⚡ minh họa sức mạnh</b> (gạch vàng). '
             'Duyệt bố cục &amp; mạch kể trước khi làm video.</p>'
             '<span class="status"><span class="dot"></span>NHÁP — chờ bạn duyệt</span></header>' % len(SB.T)]
    for act, tc, sid, scn, loi in SB.T:
        parts.append(
            '<article class="scene"><div class="meta"><span class="act">%s</span><span class="tc">%s</span></div>'
            '<img src="sb/%s.jpg" alt="%s"><p class="loi">%s</p></article>'
            % (html.escape(act), html.escape(tc), sid, html.escape(act), html.escape(loi)))
        if sid in SB.DEMOS:
            parts.append(
                '<article class="scene demo"><div class="meta"><span class="act fx">⚡ SỨC MẠNH</span></div>'
                '<img src="sb/%sd.jpg" alt="minh hoa suc manh"><p class="loi">%s</p></article>'
                % (sid, html.escape(SB.DEMOS[sid][1])))
    parts.append('<footer>Storyboard video dài "Top 15 Pháp Bảo Tây Du" · nhân vật + nền + pháp bảo vẽ bằng Bộ Bút · '
                 'lời thoại theo kịch bản v2 · chưa render video.</footer></div>')
    out = os.path.join(OUTDIR, 'storyboard.html')
    open(out, 'w', encoding='utf-8').write('\n'.join(parts))
    print('xong:', out)


if __name__ == '__main__':
    main()
