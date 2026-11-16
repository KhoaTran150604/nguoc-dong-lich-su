"""5 phong cách avatar cho "Song Tử Kể Sử" (cùng cặp nhân vật trong song_tu.py).

    python3 scripts/brand/avatar_5.py   → assets/brand/song-tu/5-phong-cach/*.png + bang-so-sanh.jpg
"""
import math, os, random, sys
import cairosvg
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from song_tu import twin, hand_scroll, hand_flag, gemini, map_scroll, drum_ring, INK, BR, BR2, RED, CREAM, OUT

D = os.path.join(OUT, '5-phong-cach'); os.makedirs(D, exist_ok=True)
HEAD = '<svg xmlns="http://www.w3.org/2000/svg" width="800" height="800" viewBox="0 0 800 800">'
CLIP = '<defs><clipPath id="cl"><circle cx="400" cy="400" r="{r}"/></clipPath>{extra}</defs>'
TA = dict(may='thang', not_ruoi=True); DO = dict(wink=True, may='xech', seo=True)

def pair(y=365, r=112, gap=145, tilt=4):
    return (twin(400 - gap, y, r, 'vang', 'cuoi', tilt=-tilt, **TA) +
            twin(400 + gap, y, r, 'do', 'nhe_rang', tilt=tilt, **DO))

# 1. SƠN MÀI CỔ ĐIỂN – bản đã duyệt: nền sơn mài, bản đồ, vành trống đồng
def s1():
    return (HEAD + CLIP.format(r=372, extra='<radialGradient id="bg" cx="50%" cy="45%" r="60%"><stop offset="0" stop-color="#4A3418"/><stop offset="0.7" stop-color="#22190F"/><stop offset="1" stop-color="#14110F"/></radialGradient>') +
            '<circle cx="400" cy="400" r="400" fill="#14110F"/><circle cx="400" cy="400" r="372" fill="url(#bg)"/><g clip-path="url(#cl)">' +
            map_scroll(400, 640, 300, 150) + pair() + hand_scroll(330, 600, 1.0) + hand_flag(655, 610, 1.0) + '</g>' + drum_ring(400, 386) + gemini(400, 150, 46) + '</svg>')

# 2. PHẲNG TỐI GIẢN – nền vàng đồng sáng, chỉ hai cái đầu to, đậm nét: nổi bật nhất ở cỡ nhỏ
def s2():
    o = HEAD + CLIP.format(r=400, extra='') + '<circle cx="400" cy="400" r="400" fill="#E9B949"/><g clip-path="url(#cl)">'
    o += '<circle cx="400" cy="400" r="330" fill="#F3D27A"/>'
    for i in range(16):   # tia nắng nhẹ
        a = math.radians(i * 22.5); o += f'<path d="M400,400 L{400+math.cos(a-0.08)*600},{400+math.sin(a-0.08)*600} L{400+math.cos(a+0.08)*600},{400+math.sin(a+0.08)*600} Z" fill="#FFFFFF" opacity="0.12"/>'
    o += twin(262, 400, 150, 'vang', 'cuoi', tilt=-6, **TA) + twin(538, 400, 150, 'do', 'nhe_rang', tilt=6, **DO)
    o += '</g><circle cx="400" cy="400" r="392" fill="none" stroke="#14110F" stroke-width="16"/></svg>'
    return o

# 3. ẤN TRIỆN ĐỎ – như con dấu son trên sách cổ: khung vuông bo, nền son, chữ dọc
def s3():
    o = HEAD + '<rect width="800" height="800" fill="#F2E6CC"/>'
    o += '<rect x="60" y="60" width="680" height="680" rx="40" fill="#B3261E"/><rect x="88" y="88" width="624" height="624" rx="26" fill="none" stroke="#F2E6CC" stroke-width="10"/>'
    o += '<rect x="112" y="112" width="576" height="576" rx="16" fill="none" stroke="#F2E6CC" stroke-width="3"/>'
    o += '<defs><clipPath id="cl"><rect x="112" y="112" width="576" height="576" rx="16"/></clipPath></defs><g clip-path="url(#cl)">'
    o += '<circle cx="400" cy="430" r="230" fill="#F2E6CC"/>'
    o += twin(318, 400, 100, 'vang', 'cuoi', tilt=-3, **TA) + twin(482, 400, 100, 'do', 'nhe_rang', tilt=3, **DO) + '</g>'
    for i, ch in enumerate(['SONG', 'TỬ']):
        o += f'<text x="{150 if i == 0 else 650}" y="400" font-family="Playfair Display" font-weight="800" font-size="46" fill="#F2E6CC" text-anchor="middle" transform="rotate({-90 if i == 0 else 90} {150 if i == 0 else 650} 400)" letter-spacing="6">{ch}</text>'
    rng = random.Random(2)   # vết mực loang của dấu son
    for _ in range(140):
        x, y = rng.uniform(60, 740), rng.uniform(60, 740)
        o += f'<circle cx="{x:.0f}" cy="{y:.0f}" r="{rng.uniform(1, 5):.1f}" fill="#F2E6CC" opacity="{rng.uniform(0.15, 0.5):.2f}"/>'
    return o + '</svg>'

# 4. ÂM DƯƠNG – hai anh em quay lưng trong vòng thái cực vàng/đỏ: "hai phe của mỗi trận"
def s4():
    o = HEAD + CLIP.format(r=380, extra='') + '<circle cx="400" cy="400" r="400" fill="#14110F"/>'
    o += '<g clip-path="url(#cl)"><circle cx="400" cy="400" r="380" fill="#B3261E"/>'
    o += '<path d="M400,20 A380,380 0 0 0 400,780 A190,190 0 0 0 400,400 A190,190 0 0 1 400,20 Z" fill="#D9B44A"/>'
    o += '<circle cx="400" cy="210" r="58" fill="#B3261E"/><circle cx="400" cy="590" r="58" fill="#D9B44A"/>'
    o += f'<g transform="translate(0 0)">{twin(250, 360, 104, "vang", "cuoi", tilt=-8, **TA)}</g>'
    o += f'<g transform="translate(800 0) scale(-1 1)">{twin(250, 440, 104, "do", "cuoi", tilt=-8, may="xech", seo=False)}</g></g>'
    o += '<circle cx="400" cy="400" r="384" fill="none" stroke="#C9A24A" stroke-width="10"/></svg>'
    return o

# 5. ĐÊM BẠCH ĐẰNG – điện ảnh: trăng, sông, bãi cọc, thuyền giặc cháy phía xa, hai anh em đứng trước
def s5():
    o = HEAD + CLIP.format(r=380, extra='<linearGradient id="sky" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="#0E1A2A"/><stop offset="0.6" stop-color="#2A2A3A"/><stop offset="1" stop-color="#5A3020"/></linearGradient>')
    o += '<circle cx="400" cy="400" r="400" fill="#14110F"/><g clip-path="url(#cl)"><rect width="800" height="800" fill="url(#sky)"/>'
    o += '<circle cx="560" cy="170" r="70" fill="#F3E6C0"/><circle cx="585" cy="160" r="70" fill="#22263A" opacity="0.18"/>'
    o += '<path d="M0,430 L120,360 L220,410 L330,330 L460,420 L600,350 L800,430 L800,800 L0,800 Z" fill="#1A1A22"/>'
    o += '<rect x="0" y="470" width="800" height="330" fill="#1E3A50"/>'
    for i in range(14):    # bãi cọc nhô lên
        x = 60 + i * 52; o += f'<polygon points="{x-6},560 {x+6},560 {x+6},505 {x},488 {x-6},505" fill="#2A1A10" stroke="#0A0806" stroke-width="2"/>'
    for x, s in ((150, 0.9), (680, 0.7)):   # thuyền giặc cháy phía xa
        o += f'<g transform="translate({x} 470) scale({s})"><path d="M-60,0 Q-45,22 0,22 Q45,22 70,0 Z" fill="#1A0E08"/><line x1="0" y1="0" x2="0" y2="-70" stroke="#1A0E08" stroke-width="5"/>'
        o += '<path d="M-30,-10 C-50,-40 -20,-60 -10,-100 C0,-60 30,-50 20,-10 Z" fill="#E8742A" opacity="0.9"/><path d="M-15,-10 C-25,-35 -5,-45 0,-70 C8,-45 18,-35 10,-10 Z" fill="#F3D27A"/></g>'
    o += '<rect x="0" y="560" width="800" height="240" fill="#14110F" opacity="0.55"/>'
    o += twin(270, 470, 118, 'vang', 'cuoi', tilt=-3, **TA) + twin(530, 470, 118, 'do', 'nhe_rang', tilt=3, **DO)
    o += '</g><circle cx="400" cy="400" r="384" fill="none" stroke="#C9A24A" stroke-width="10"/>' + gemini(400, 92, 34) + '</svg>'
    return o

STYLES = [('1-son-mai-co-dien', 'Sơn mài cổ điển', s1), ('2-phang-toi-gian', 'Phẳng tối giản', s2), ('3-an-trien-do', 'Ấn triện đỏ', s3),
          ('4-am-duong', 'Âm dương', s4), ('5-dem-bach-dang', 'Đêm Bạch Đằng', s5)]

if __name__ == '__main__' and '--van-vo' not in sys.argv:
    from PIL import Image, ImageDraw, ImageFont
    f = ImageFont.truetype(os.path.expanduser('~/.fonts/BeVietnamPro-SemiBold.ttf'), 30)
    sheet = Image.new('RGB', (5 * 420 + 20, 640), '#D8BE8E'); d = ImageDraw.Draw(sheet)
    for i, (fn, ten, fx) in enumerate(STYLES):
        svg = fx(); open(os.path.join(D, fn + '.svg'), 'w').write(svg)
        p = os.path.join(D, fn + '.png'); cairosvg.svg2png(bytestring=svg.encode(), write_to=p, output_width=800, output_height=800)
        im = Image.open(p).convert('RGBA'); x = 20 + i * 420
        sheet.paste(im.resize((400, 400), Image.LANCZOS), (x, 20), im.resize((400, 400), Image.LANCZOS))
        sm = im.resize((88, 88), Image.LANCZOS); sheet.paste(sm, (x + 40, 470), sm)
        tn = im.resize((40, 40), Image.LANCZOS); sheet.paste(tn, (x + 150, 494), tn)
        d.text((x + 200, 430), f'{i+1}. {ten}', fill='#2A1A10', font=f, anchor='mm'); d.text((x + 260, 514), '88px · 40px', fill='#5A3A20', font=ImageFont.truetype(os.path.expanduser('~/.fonts/BeVietnamPro-Regular.ttf'), 22), anchor='mm')
        print(fn)
    sheet.save(os.path.join(D, 'bang-so-sanh.jpg'), quality=90)

# ---------------- VĂN – VÕ: avatar nói rõ vai trò hai anh em ----------------
def book_open(cx, cy, w):
    """Quyển sử mở trên hai tay Anh Văn."""
    h = w * 0.62; o = f'<g transform="translate({cx} {cy})">'
    o += f'<path d="M0,{-h*0.42} Q{-w*0.25},{-h*0.55} {-w*0.5},{-h*0.42} L{-w*0.5},{h*0.48} Q{-w*0.25},{h*0.36} 0,{h*0.5} Z" fill="#F7EBD0" stroke="#6A4A14" stroke-width="4"/>'
    o += f'<path d="M0,{-h*0.42} Q{w*0.25},{-h*0.55} {w*0.5},{-h*0.42} L{w*0.5},{h*0.48} Q{w*0.25},{h*0.36} 0,{h*0.5} Z" fill="#F7EBD0" stroke="#6A4A14" stroke-width="4"/>'
    for k in range(5):
        y = -h * 0.28 + k * h * 0.15
        o += f'<line x1="{-w*0.42}" y1="{y}" x2="{-w*0.08}" y2="{y+4}" stroke="#8A6A3A" stroke-width="3"/><line x1="{w*0.08}" y1="{y+4}" x2="{w*0.42}" y2="{y}" stroke="#8A6A3A" stroke-width="3"/>'
    o += f'<circle cx="{-w*0.5}" cy="{h*0.15}" r="{w*0.1}" fill="#F0C8A0" stroke="#B07A50" stroke-width="3"/><circle cx="{w*0.5}" cy="{h*0.15}" r="{w*0.1}" fill="#F0C8A0" stroke="#B07A50" stroke-width="3"/>'
    return o + '</g>'

def sword_up(x, y, s):
    """Kiếm giơ cao của Em Võ (gốc ở nắm tay)."""
    return (f'<g transform="translate({x} {y}) rotate(18) scale({s})">'
            f'<polygon points="-9,-20 9,-20 7,-230 0,-252 -7,-230" fill="#DCE2E6" stroke="#3A3A3A" stroke-width="3"/><line x1="0" y1="-24" x2="0" y2="-228" stroke="#9AA2A6" stroke-width="3"/>'
            f'<rect x="-34" y="-24" width="68" height="12" rx="5" fill="{BR}" stroke="#5A3A10" stroke-width="3"/><rect x="-8" y="-12" width="16" height="40" fill="#3A2618"/>'
            f'<circle cx="0" cy="34" r="9" fill="{BR}" stroke="#5A3A10" stroke-width="3"/><circle cx="0" cy="0" r="17" fill="#F0C8A0" stroke="#B07A50" stroke-width="3"/></g>')

def shield(x, y, r):
    o = f'<g transform="translate({x} {y})"><circle r="{r}" fill="#7A1E18" stroke="{BR}" stroke-width="7"/><circle r="{r*0.72}" fill="none" stroke="{BR2}" stroke-width="3"/>'
    for i in range(8):
        a = math.radians(i * 45); o += f'<line x1="{math.cos(a)*r*0.25}" y1="{math.sin(a)*r*0.25}" x2="{math.cos(a)*r*0.68}" y2="{math.sin(a)*r*0.68}" stroke="{BR2}" stroke-width="3"/>'
    return o + f'<circle r="{r*0.22}" fill="{BR}" stroke="#5A3A10" stroke-width="3"/></g>'

def badge(x, y, chu, nen, vien):
    return (f'<g transform="translate({x} {y})"><circle r="34" fill="{nen}" stroke="{vien}" stroke-width="5"/>'
            f'<text y="11" font-family="Playfair Display" font-weight="800" font-size="{30 if len(chu) > 2 else 34}" fill="{vien}" text-anchor="middle">{chu}</text></g>')

def van_vo(chu_ten=False):
    o = HEAD + CLIP.format(r=380, extra='') + '<circle cx="400" cy="400" r="400" fill="#14110F"/><g clip-path="url(#cl)">'
    o += '<rect width="800" height="800" fill="#B3261E"/><polygon points="0,0 470,0 330,800 0,800" fill="#D9B44A"/>'
    # vân nền: bên Văn chữ + sách, bên Võ kiếm chéo
    for i in range(7):
        y = 90 + i * 100; o += f'<line x1="40" y1="{y}" x2="{300 - i*10}" y2="{y}" stroke="#F3D27A" stroke-width="6" opacity="0.35" stroke-dasharray="26 14"/>'
    for i, (x, y) in enumerate([(640, 160), (720, 330), (600, 520), (730, 640)]):
        o += f'<g transform="translate({x} {y}) rotate({30 + i*20})" opacity="0.2"><line x1="-50" y1="0" x2="50" y2="0" stroke="#F3D27A" stroke-width="8"/><line x1="0" y1="-50" x2="0" y2="50" stroke="#F3D27A" stroke-width="8"/></g>'
    # Anh Văn (trái): mở sách
    o += twin(250, 360, 108, 'vang', 'cuoi', tilt=-3, **TA) + book_open(250, 560, 230) + badge(250, 690, 'VĂN', '#F2E6CC', '#6A4A14')
    # Em Võ (phải): khiên + kiếm giơ cao
    o += sword_up(640, 520, 1.0) + twin(540, 360, 108, 'do', 'nhe_rang', tilt=4, **DO) + shield(470, 560, 72) + badge(560, 690, 'VÕ', '#14110F', '#F3D27A')
    o += '</g><circle cx="400" cy="400" r="384" fill="none" stroke="#C9A24A" stroke-width="10"/>' + gemini(400, 92, 36)
    if chu_ten:
        o += '<rect x="185" y="730" width="430" height="56" rx="28" fill="#14110F" stroke="#C9A24A" stroke-width="4"/><text x="400" y="770" font-family="Playfair Display" font-weight="800" font-size="34" fill="#F3D27A" text-anchor="middle" letter-spacing="3">SONG TỬ KỂ SỬ</text>'
    return o + '</svg>'

def render_van_vo():
    from PIL import Image, ImageDraw, ImageFont
    out = []
    for chu in (False, True):
        svg = van_vo(chu); fn = os.path.join(D, 'van-vo' + ('-co-chu' if chu else '') + '.png')
        open(fn.replace('.png', '.svg'), 'w').write(svg); cairosvg.svg2png(bytestring=svg.encode(), write_to=fn, output_width=800, output_height=800); out.append(fn)
    a, b = (Image.open(f).convert('RGBA') for f in out)
    sh = Image.new('RGB', (1960, 860), '#D8BE8E'); sh.paste(a, (20, 30), a); sh.paste(b, (860, 30), b)
    f = ImageFont.truetype(os.path.expanduser('~/.fonts/BeVietnamPro-SemiBold.ttf'), 22); d = ImageDraw.Draw(sh); y = 60
    for s in (160, 88, 40):
        t = a.resize((s, s), Image.LANCZOS); sh.paste(t, (1740 - s // 2, y), t); d.text((1700, y + s + 6), f'{s}px', fill='#2A1A10', font=f); y += s + 60
    sh.save(os.path.join(D, 'van-vo-xem-thu.jpg'), quality=90)

if __name__ == '__main__' and '--van-vo' in sys.argv:
    render_van_vo()
