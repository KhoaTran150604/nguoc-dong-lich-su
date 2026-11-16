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

if __name__ == '__main__':
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
