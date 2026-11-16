"""Banner YouTube "Song Tử Kể Sử" 2560×1440 (vùng an toàn 1546×423 ở giữa).

    python3 scripts/brand/banner.py → assets/brand/song-tu/BANNER-YouTube-2560x1440.png (+ ảnh xem vùng an toàn)
"""
import io, math, os, sys
import cairosvg
from PIL import Image, ImageDraw
HERE = os.path.dirname(os.path.abspath(__file__)); ROOT = os.path.abspath(os.path.join(HERE, '..', '..'))
sys.path.insert(0, HERE); sys.path.insert(0, os.path.join(ROOT, 'scripts', 'video')); sys.path.insert(0, os.path.join(ROOT, 'scripts', 'hieuung'))
from song_tu import twin, gemini, INK, BR, BR2, RED, CREAM, OUT
from avatar_5 import book_open, sword_up, shield, badge, TA, DO
from bando_vung import BanDoVung
import demo as L                                   # thuyền, lính dùng chung với video
import dung as DG

W, H = 2560, 1440
SX, SY, SW, SH = (W - 1546) // 2, (H - 423) // 2, 1546, 423      # vùng an toàn

def background():
    # Bản đồ cổ (không địa danh, không vùng phe) – chỉ một phần Bắc Bộ & Hoa Nam, không phải bản đồ Việt Nam toàn cảnh
    m = BanDoVung(dict(bbox=(101.0, 16.5, 118.0, 26.0), seed=11, nui=1.3,
                       song=[[(103.6, 22.6), (104.6, 21.9), (105.3, 21.3), (105.9, 20.9), (106.5, 20.3)], [(106.2, 21.6), (106.5, 21.2), (106.85, 20.85)]]), px_per_deg=320)
    return m.view(W, H, (108.8, 21.4, 12.5)).convert('RGBA')

def overlay():
    o = [f'<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{H}">',
         '<defs><linearGradient id="v" x1="0" y1="0" x2="1" y2="0"><stop offset="0" stop-color="#14110F" stop-opacity="0.15"/>'
         '<stop offset="0.5" stop-color="#14110F" stop-opacity="0.72"/><stop offset="1" stop-color="#14110F" stop-opacity="0.15"/></linearGradient></defs>',
         f'<rect x="0" y="{SY-40}" width="{W}" height="{SH+80}" fill="url(#v)"/>',
         f'<line x1="0" y1="{SY-40}" x2="{W}" y2="{SY-40}" stroke="{BR}" stroke-width="5"/><line x1="0" y1="{SY+SH+40}" x2="{W}" y2="{SY+SH+40}" stroke="{BR}" stroke-width="5"/>']
    # rìa (chỉ TV thấy): đoàn thuyền hai phe + lính
    U = 1.25
    for j in range(5):
        o.append(L.boat(230 + j * 95, 330 + (j % 2) * 34, 0, L.TA, U))
        o.append(L.boat(2330 - j * 95, 330 + (j % 2) * 34, 180, L.DICH, U))
    for j in range(9):
        o.append(DG.soldier((150 + j * 52), 1250 + (j % 2) * 30, DG.TA, 1.3 / DG.U, phase=j))
        o.append(DG.soldier((2410 - j * 52), 1250 + (j % 2) * 30, DG.DICH, 1.3 / DG.U, phase=j, face=-1))
    # hai anh em trong vùng an toàn
    cy = SY + 175; r = 86
    o.append(f'<g transform="translate(0 0)">{twin(SX + 125, cy, r, "vang", "cuoi", tilt=-3, **TA)}{book_open(SX + 125, cy + 165, 190)}</g>')
    o.append(sword_up(SX + SW - 55, cy + 130, 0.78) + twin(SX + SW - 135, cy, r, 'do', 'nhe_rang', tilt=4, **DO) + shield(SX + SW - 190, cy + 160, 56))
    # chữ giữa
    cx = W / 2
    o.append(gemini(cx, SY + 100, 34))
    title = 'SONG TỬ KỂ SỬ'
    o.append(f'<text x="{cx}" y="{SY+250}" font-family="Playfair Display" font-weight="800" font-size="104" fill="none" stroke="{INK}" stroke-width="14" stroke-linejoin="round" text-anchor="middle" letter-spacing="6">{title}</text>')
    o.append(f'<text x="{cx}" y="{SY+250}" font-family="Playfair Display" font-weight="800" font-size="104" fill="{BR2}" text-anchor="middle" letter-spacing="6">{title}</text>')
    o.append(f'<rect x="{cx-330}" y="{SY+285}" width="660" height="62" rx="31" fill="{INK}" stroke="{BR}" stroke-width="3"/>')
    o.append(f'<text x="{cx-28}" y="{SY+327}" font-family="Be Vietnam Pro SemiBold" font-size="34" fill="{BR2}" text-anchor="end">Văn kể sử</text>'
             f'<text x="{cx}" y="{SY+327}" font-family="Be Vietnam Pro SemiBold" font-size="34" fill="{CREAM}" text-anchor="middle">–</text>'
             f'<text x="{cx+28}" y="{SY+327}" font-family="Be Vietnam Pro SemiBold" font-size="34" fill="#E8604A" text-anchor="start">Võ dẫn trận</text>')
    o.append('</svg>')
    return ''.join(o)

if __name__ == '__main__':
    bg = background()
    ov = Image.open(io.BytesIO(cairosvg.svg2png(bytestring=overlay().encode()))).convert('RGBA')
    bg.alpha_composite(ov); im = bg.convert('RGB')
    out = os.path.join(OUT, 'BANNER-YouTube-2560x1440.png'); im.save(out, optimize=True)
    # ảnh kiểm tra: khung vùng hiển thị trên các thiết bị
    chk = im.copy(); d = ImageDraw.Draw(chk)
    d.rectangle((SX, SY, SX + SW, SY + SH), outline='#00FF66', width=6)                 # mọi thiết bị
    d.rectangle((0, SY, W, SY + SH), outline='#33AAFF', width=4)                        # máy tính (rộng nhất)
    chk.resize((1280, 720)).save(os.path.join(OUT, 'banner-kiem-tra-vung-an-toan.jpg'), quality=88)
    im.crop((0, SY, W, SY + SH)).save(os.path.join(OUT, 'banner-xem-tren-may-tinh.jpg'), quality=90)
    im.crop((SX, SY, SX + SW, SY + SH)).save(os.path.join(OUT, 'banner-xem-tren-dien-thoai.jpg'), quality=90)
    print(out, os.path.getsize(out) // 1024, 'KB')
