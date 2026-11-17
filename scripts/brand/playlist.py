"""Ảnh bìa playlist "Ngược Dòng Sử Việt" 1280×720 (vẽ ở 2560×1440 rồi thu nhỏ).

    python3 scripts/brand/playlist.py → assets/brand/song-tu/PLAYLIST-NguocDongSuViet-1280x720.jpg (+ ảnh xem thử cỡ nhỏ)
Bố cục: nền bản đồ cổ (cùng banner) · Văn trái, Võ phải · tiêu đề lớn · trục thời gian mũi tên chỉ ngược về Văn Lang.
"""
import io, os, sys
import cairosvg
from PIL import Image
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
from song_tu import twin, gemini, INK, BR, BR2, RED, CREAM, OUT
from avatar_5 import book_open, sword_up, shield, TA, DO
from banner import background, W, H

MOC = ['Văn Lang', 'Bắc thuộc', 'Ngô', 'Lý', 'Trần', 'Lê', 'Tây Sơn', 'Nguyễn', '1976']

def overlay():
    o = [f'<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{H}">',
         '<defs><radialGradient id="v" cx="0.5" cy="0.48" r="0.75"><stop offset="0" stop-color="#14110F" stop-opacity="0.82"/>'
         '<stop offset="0.6" stop-color="#14110F" stop-opacity="0.62"/><stop offset="1" stop-color="#14110F" stop-opacity="0.35"/></radialGradient></defs>',
         f'<rect width="{W}" height="{H}" fill="url(#v)"/>',
         f'<rect x="28" y="28" width="{W-56}" height="{H-56}" fill="none" stroke="{BR}" stroke-width="8"/>',
         f'<rect x="48" y="48" width="{W-96}" height="{H-96}" fill="none" stroke="{BR}" stroke-width="3" opacity="0.7"/>']
    cx = W / 2
    # nhãn kênh
    o.append(gemini(cx - 300, 205, 46))
    o.append(f'<text x="{cx-232}" y="226" font-family="Be Vietnam Pro SemiBold" font-size="58" fill="{BR2}" letter-spacing="10">SONG TỬ KỂ SỬ</text>')
    # tiêu đề hai dòng
    for y, t in ((500, 'NGƯỢC DÒNG'), (750, 'SỬ VIỆT')):
        for extra in (f'fill="none" stroke="{INK}" stroke-width="26" stroke-linejoin="round"', f'fill="{BR2}"'):
            o.append(f'<text x="{cx}" y="{y}" font-family="Playfair Display" font-weight="800" font-size="205" text-anchor="middle" letter-spacing="4" {extra}>{t}</text>')
    o.append(f'<text x="{cx}" y="880" font-family="Be Vietnam Pro SemiBold" font-size="62" fill="{CREAM}" text-anchor="middle">Kể lùi từ hiện tại về thời dựng nước</text>')
    # trục thời gian: mũi tên chỉ sang trái (ngược dòng)
    x0, x1, ty = 330, W - 330, 1110
    o.append(f'<line x1="{x0+40}" y1="{ty}" x2="{x1}" y2="{ty}" stroke="{BR}" stroke-width="12" stroke-linecap="round"/>')
    o.append(f'<polygon points="{x0-30},{ty} {x0+60},{ty-48} {x0+60},{ty+48}" fill="{RED}" stroke="{BR2}" stroke-width="5" stroke-linejoin="round"/>')
    n = len(MOC); step = (x1 - x0 - 110) / (n - 1)
    for i, m in enumerate(MOC):
        x = x0 + 110 + i * step
        hi = i in (0, n - 1)
        o.append(f'<circle cx="{x}" cy="{ty}" r="{22 if hi else 15}" fill="{RED if i == 0 else INK}" stroke="{BR2}" stroke-width="6"/>')
        y = ty + 95 if i % 2 == 0 else ty - 50
        o.append(f'<text x="{x}" y="{y}" font-family="Be Vietnam Pro SemiBold" font-size="{56 if hi else 46}" fill="{BR2 if hi else CREAM}" text-anchor="middle">{m}</text>')
    # hai anh em
    cy, r = 500, 128
    o.append(twin(240, cy, r, 'vang', 'cuoi', tilt=-4, **TA) + book_open(240, cy + 245, 280))
    o.append(sword_up(W - 130, cy + 195, 1.1) + twin(W - 245, cy, r, 'do', 'nhe_rang', tilt=4, **DO) + shield(W - 330, cy + 235, 80))
    o.append('</svg>')
    return ''.join(o)

if __name__ == '__main__':
    bg = background()
    ov = Image.open(io.BytesIO(cairosvg.svg2png(bytestring=overlay().encode()))).convert('RGBA')
    bg.alpha_composite(ov); im = bg.convert('RGB').resize((1280, 720), Image.LANCZOS)
    out = os.path.join(OUT, 'PLAYLIST-NguocDongSuViet-1280x720.jpg'); im.save(out, quality=92)
    # xem thử ở cỡ hiển thị trong danh sách playlist (~ 320 và 160 px)
    sh = Image.new('RGB', (520, 200), '#0F0F0F')
    sh.paste(im.resize((320, 180), Image.LANCZOS), (10, 10)); sh.paste(im.resize((160, 90), Image.LANCZOS), (350, 10))
    sh.save(os.path.join(OUT, 'playlist-xem-thu-nho.jpg'), quality=90)
    print(out, os.path.getsize(out) // 1024, 'KB')
