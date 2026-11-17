"""Linh vật kênh "Song Tử Kể Sử": hai anh em sinh đôi hoạt họa (chibi), cùng style vector với video.

    python3 scripts/brand/song_tu.py            → assets/brand/song-tu/avatar-*.png (800×800)
Em VÀNG (người kể): búi tóc, cài trâm, cầm cuộn sử. Em ĐỎ (người trận): mũ trụ tua đỏ, cầm cờ.
Hàm twin() dùng lại được cho banner, thumbnail, end card.
"""
import math, os
import cairosvg

ROOT = os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', '..'))
OUT = os.path.join(ROOT, 'assets', 'brand', 'song-tu')
INK, BR, BR2, RED, CREAM = '#14110F', '#C9A24A', '#F3D27A', '#B3261E', '#F2E6CC'
SKIN, SKIN_D = '#F0C8A0', '#B07A50'

def face(cx, cy, r, mood='cuoi', wink=False, may='thang', not_ruoi=False, seo=False):
    """Mặt chibi: mắt to có điểm sáng, má hồng, miệng cười."""
    o = [f'<circle cx="{cx}" cy="{cy}" r="{r}" fill="{SKIN}" stroke="{SKIN_D}" stroke-width="3"/>',
         f'<ellipse cx="{cx-r*0.93}" cy="{cy+r*0.08}" rx="{r*0.13}" ry="{r*0.2}" fill="{SKIN}" stroke="{SKIN_D}" stroke-width="2.5"/>',
         f'<ellipse cx="{cx+r*0.93}" cy="{cy+r*0.08}" rx="{r*0.13}" ry="{r*0.2}" fill="{SKIN}" stroke="{SKIN_D}" stroke-width="2.5"/>']
    for sx in (-1, 1):
        ex, ey = cx + sx * r * 0.36, cy + r * 0.12
        if wink and sx == 1:
            o.append(f'<path d="M{ex-r*0.13},{ey} Q{ex},{ey-r*0.12} {ex+r*0.13},{ey}" stroke="{INK}" stroke-width="{r*0.06}" fill="none" stroke-linecap="round"/>')
        else:
            o.append(f'<ellipse cx="{ex}" cy="{ey}" rx="{r*0.12}" ry="{r*0.16}" fill="{INK}"/>')
            o.append(f'<circle cx="{ex+r*0.04}" cy="{ey-r*0.06}" r="{r*0.045}" fill="#FFFFFF"/><circle cx="{ex-r*0.04}" cy="{ey+r*0.05}" r="{r*0.022}" fill="#FFFFFF"/>')
        if may == 'thang':   # mày rậm, thẳng: điềm tĩnh
            o.append(f'<path d="M{ex-r*0.18},{ey-r*0.27} L{ex+r*0.18},{ey-r*0.29}" stroke="{INK}" stroke-width="{r*0.085}" stroke-linecap="round"/>')
        else:                # mày xếch: tinh nghịch, võ
            o.append(f'<path d="M{ex-sx*r*0.18},{ey-r*0.24} L{ex+sx*r*0.17},{ey-r*0.36}" stroke="{INK}" stroke-width="{r*0.085}" stroke-linecap="round"/>')
        o.append(f'<ellipse cx="{cx+sx*r*0.6}" cy="{cy+r*0.4}" rx="{r*0.11}" ry="{r*0.06}" fill="#D97A60" opacity="0.3"/>')
    if not_ruoi: o.append(f'<circle cx="{cx-r*0.5}" cy="{cy+r*0.3}" r="{r*0.035}" fill="#5A3A20"/>')
    if seo: o.append(f'<path d="M{cx+r*0.48},{cy+r*0.22} l{r*0.2},{r*0.12} M{cx+r*0.52},{cy+r*0.33} l{r*0.06},{-r*0.12} M{cx+r*0.62},{cy+r*0.38} l{r*0.06},{-r*0.12}" stroke="#A0523A" stroke-width="{r*0.03}" stroke-linecap="round"/>')
    if mood == 'nhe_rang':   # cười toe, lộ răng
        o.append(f'<path d="M{cx-r*0.26},{cy+r*0.4} Q{cx},{cy+r*0.75} {cx+r*0.26},{cy+r*0.4} Z" fill="#7A2A20" stroke="{INK}" stroke-width="2.5" stroke-linejoin="round"/>'
                 f'<path d="M{cx-r*0.22},{cy+r*0.42} L{cx+r*0.22},{cy+r*0.42} L{cx+r*0.2},{cy+r*0.5} L{cx-r*0.2},{cy+r*0.5} Z" fill="#FFFFFF"/>')
    elif mood == 'cuoi':
        o.append(f'<path d="M{cx-r*0.2},{cy+r*0.42} Q{cx},{cy+r*0.68} {cx+r*0.2},{cy+r*0.42} Z" fill="#7A2A20" stroke="{INK}" stroke-width="2.5" stroke-linejoin="round"/>'
                 f'<path d="M{cx-r*0.1},{cy+r*0.56} Q{cx},{cy+r*0.5} {cx+r*0.1},{cy+r*0.56} Q{cx},{cy+r*0.64} {cx-r*0.1},{cy+r*0.56} Z" fill="#E8826A"/>')
    else:
        o.append(f'<path d="M{cx-r*0.18},{cy+r*0.45} Q{cx},{cy+r*0.6} {cx+r*0.18},{cy+r*0.45}" stroke="{INK}" stroke-width="{r*0.05}" fill="none" stroke-linecap="round"/>')
    return ''.join(o)

def twin(cx, cy, r, ben='vang', mood='cuoi', wink=False, tilt=0, may='thang', not_ruoi=False, seo=False):
    """Một người trong cặp sinh đôi. (cx, cy) = tâm đầu, r = bán kính đầu."""
    vang = ben == 'vang'
    robe, dark, trim = ('#D9B44A', '#6A4A14', CREAM) if vang else (RED, '#4A1410', BR2)
    o = [f'<g transform="rotate({tilt} {cx} {cy + r*1.6})">']
    # thân + tay
    by = cy + r * 0.85
    o.append(f'<path d="M{cx-r*0.78},{by+r*1.25} Q{cx-r*0.82},{by+r*0.2} {cx-r*0.42},{by} L{cx+r*0.42},{by} Q{cx+r*0.82},{by+r*0.2} {cx+r*0.78},{by+r*1.25} Z" fill="{robe}" stroke="{dark}" stroke-width="4"/>')
    o.append(f'<path d="M{cx-r*0.36},{by+r*0.02} L{cx},{by+r*0.55} L{cx+r*0.36},{by+r*0.02}" fill="none" stroke="{trim}" stroke-width="{r*0.11}" stroke-linejoin="round"/>')
    o.append(f'<rect x="{cx-r*0.72}" y="{by+r*0.72}" width="{r*1.44}" height="{r*0.14}" fill="{dark}"/>')
    if not vang:   # giáp vai
        o.append(f'<path d="M{cx-r*0.86},{by+r*0.5} Q{cx-r*0.86},{by+r*0.05} {cx-r*0.42},{by} Q{cx-r*0.4},{by+r*0.35} {cx-r*0.6},{by+r*0.55} Z" fill="#7A5A24" stroke="{dark}" stroke-width="3"/>'
                 f'<path d="M{cx+r*0.86},{by+r*0.5} Q{cx+r*0.86},{by+r*0.05} {cx+r*0.42},{by} Q{cx+r*0.4},{by+r*0.35} {cx+r*0.6},{by+r*0.55} Z" fill="#7A5A24" stroke="{dark}" stroke-width="3"/>')
    o.append(face(cx, cy, r, mood, wink, may, not_ruoi, seo))
    if vang:       # thư sinh nam: tóc mai + khăn vấn đen quấn đầu, bút lông gác tai
        o.append(f'<path d="M{cx-r*1.0},{cy+r*0.25} L{cx-r*0.98},{cy-r*0.2} L{cx-r*0.8},{cy-r*0.2} L{cx-r*0.82},{cy+r*0.2} Z M{cx+r*1.0},{cy+r*0.25} L{cx+r*0.98},{cy-r*0.2} L{cx+r*0.8},{cy-r*0.2} L{cx+r*0.82},{cy+r*0.2} Z" fill="#2A1A10"/>')
        o.append(f'<path d="M{cx-r*1.06},{cy-r*0.18} Q{cx-r*1.1},{cy-r*1.12} {cx},{cy-r*1.14} Q{cx+r*1.1},{cy-r*1.12} {cx+r*1.06},{cy-r*0.18} Q{cx},{cy-r*0.48} {cx-r*1.06},{cy-r*0.18} Z" fill="#1E1612" stroke="{INK}" stroke-width="3"/>')
        for k in range(4):   # nếp khăn
            o.append(f'<path d="M{cx-r*1.0},{cy-r*(0.32+k*0.18)} Q{cx},{cy-r*(0.62+k*0.18)} {cx+r*1.0},{cy-r*(0.32+k*0.18)}" stroke="#4A3A30" stroke-width="{r*0.035}" fill="none"/>')
        o.append(f'<path d="M{cx-r*1.04},{cy-r*0.25} Q{cx},{cy-r*0.55} {cx+r*1.04},{cy-r*0.25}" stroke="{BR}" stroke-width="{r*0.06}" fill="none"/>')
        o.append(f'<g transform="rotate(-35 {cx+r*0.95} {cy-r*0.1})"><rect x="{cx+r*0.7}" y="{cy-r*0.14}" width="{r*0.6}" height="{r*0.08}" rx="{r*0.03}" fill="#8A3A24"/><path d="M{cx+r*1.3},{cy-r*0.14} l{r*0.16},{r*0.04} l{-r*0.16},{r*0.04} Z" fill="{INK}"/></g>')
    else:          # tóc mái + mũ trụ tua đỏ
        o.append(f'<path d="M{cx-r*1.0},{cy+r*0.02} Q{cx-r*0.9},{cy-r*0.55} {cx-r*0.3},{cy-r*0.48} Q{cx},{cy-r*0.3} {cx+r*0.3},{cy-r*0.48} Q{cx+r*0.9},{cy-r*0.55} {cx+r*1.0},{cy+r*0.02} Z" fill="#2A1A10"/>')
        o.append(f'<path d="M{cx-r*1.1},{cy-r*0.25} Q{cx-r*1.1},{cy-r*1.2} {cx},{cy-r*1.22} Q{cx+r*1.1},{cy-r*1.2} {cx+r*1.1},{cy-r*0.25} Q{cx},{cy-r*0.55} {cx-r*1.1},{cy-r*0.25} Z" fill="#8A6A2A" stroke="{INK}" stroke-width="4"/>')
        o.append(f'<path d="M{cx-r*0.95},{cy-r*0.5} Q{cx},{cy-r*0.85} {cx+r*0.95},{cy-r*0.5}" stroke="{BR2}" stroke-width="{r*0.07}" fill="none"/>')
        o.append(f'<circle cx="{cx}" cy="{cy-r*0.86}" r="{r*0.1}" fill="{RED}" stroke="{BR2}" stroke-width="3"/>')
        o.append(f'<path d="M{cx-r*0.08},{cy-r*1.2} L{cx},{cy-r*1.5} L{cx+r*0.08},{cy-r*1.2} Z" fill="{BR}" stroke="{INK}" stroke-width="2"/>')
        o.append(f'<path d="M{cx},{cy-r*1.45} Q{cx-r*0.45},{cy-r*1.8} {cx-r*0.5},{cy-r*1.35} Q{cx-r*0.2},{cy-r*1.55} {cx},{cy-r*1.4} Q{cx+r*0.2},{cy-r*1.55} {cx+r*0.5},{cy-r*1.35} Q{cx+r*0.45},{cy-r*1.8} {cx},{cy-r*1.45} Z" fill="{RED}" stroke="{BR2}" stroke-width="3"/>')
    o.append('</g>')
    return ''.join(o)

def hand_scroll(x, y, s):       # cuộn sử trong tay em vàng
    return (f'<g transform="translate({x} {y}) rotate(-20) scale({s})"><rect x="-38" y="-12" width="76" height="24" fill="{CREAM}" stroke="#6A4A14" stroke-width="3"/>'
            f'<rect x="-46" y="-16" width="10" height="32" rx="4" fill="#8A3A24" stroke="#3A1A10" stroke-width="2"/><rect x="36" y="-16" width="10" height="32" rx="4" fill="#8A3A24" stroke="#3A1A10" stroke-width="2"/>'
            f'<line x1="-28" y1="-3" x2="26" y2="-3" stroke="#6A4A14" stroke-width="2"/><line x1="-28" y1="5" x2="18" y2="5" stroke="#6A4A14" stroke-width="2"/>'
            f'<circle cx="-12" cy="22" r="11" fill="{SKIN}" stroke="{SKIN_D}" stroke-width="2.5"/></g>')

def hand_flag(x, y, s):         # lá cờ trong tay em đỏ
    return (f'<g transform="translate({x} {y}) scale({s})"><line x1="0" y1="40" x2="0" y2="-150" stroke="#3A2618" stroke-width="7" stroke-linecap="round"/>'
            f'<polygon points="-5,-150 0,-170 5,-150" fill="#C8CED2"/>'
            f'<path d="M4,-146 Q50,-156 82,-140 Q60,-118 82,-96 Q50,-110 4,-100 Z" fill="{BR}" stroke="#6A4A14" stroke-width="3"/>'
            f'<circle cx="0" cy="22" r="12" fill="{SKIN}" stroke="{SKIN_D}" stroke-width="2.5"/></g>')

def gemini(x, y, r):            # ký hiệu cung Song Tử ♊ trong huy hiệu đồng
    return (f'<g transform="translate({x} {y})"><circle r="{r}" fill="{INK}" stroke="{BR}" stroke-width="{r*0.1}"/><circle r="{r*0.82}" fill="none" stroke="{BR2}" stroke-width="{r*0.03}"/>'
            f'<path d="M{-r*0.5},{-r*0.48} Q0,{-r*0.3} {r*0.5},{-r*0.48} M{-r*0.5},{r*0.48} Q0,{r*0.3} {r*0.5},{r*0.48} M{-r*0.24},{-r*0.38} L{-r*0.24},{r*0.38} M{r*0.24},{-r*0.38} L{r*0.24},{r*0.38}" '
            f'stroke="{BR2}" stroke-width="{r*0.13}" fill="none" stroke-linecap="round"/></g>')

def map_scroll(cx, cy, w, h):   # tấm bản đồ cổ trải giữa hai anh em
    o = [f'<rect x="{cx-w/2}" y="{cy-h/2}" width="{w}" height="{h}" fill="#E4CC98" stroke="#6A4A14" stroke-width="4"/>',
         f'<path d="M{cx-w*0.3},{cy-h*0.35} Q{cx-w*0.1},{cy-h*0.1} {cx-w*0.18},{cy+h*0.15} Q{cx-w*0.25},{cy+h*0.35} {cx-w*0.05},{cy+h*0.42}" stroke="#5A8CA0" stroke-width="5" fill="none"/>',
         f'<path d="M{cx+w*0.1},{cy-h*0.4} Q{cx+w*0.3},{cy-h*0.2} {cx+w*0.42},{cy+h*0.05} L{cx+w*0.5},{cy+h*0.05} L{cx+w*0.5},{cy-h*0.5} Z" fill="#5A8CA0" opacity="0.8"/>']
    for dx, dy in ((-0.32, 0.05), (0.15, -0.15), (-0.05, 0.3)):
        o.append(f'<polygon points="{cx+w*dx-14},{cy+h*dy+10} {cx+w*dx},{cy+h*dy-12} {cx+w*dx+14},{cy+h*dy+10}" fill="#A88A62" stroke="#5A3A20" stroke-width="2"/>')
    for dx, dy, col in ((-0.12, -0.05, BR), (0.25, 0.25, RED)):   # hai lá cờ nhỏ hai phe
        x, y = cx + w * dx, cy + h * dy
        o.append(f'<line x1="{x}" y1="{y}" x2="{x}" y2="{y-34}" stroke="#3A2618" stroke-width="3"/><path d="M{x},{y-34} L{x+22},{y-27} L{x},{y-20} Z" fill="{col}" stroke="#3A1A10" stroke-width="1.5"/>')
    o.append(f'<path d="M{cx-w*0.15},{cy+h*0.05} Q{cx+w*0.05},{cy-h*0.25} {cx+w*0.2},{cy+h*0.1}" stroke="{RED}" stroke-width="4" stroke-dasharray="10 7" fill="none"/>')
    o.append(f'<rect x="{cx-w/2-16}" y="{cy-h/2-8}" width="18" height="{h+16}" rx="7" fill="#8A3A24" stroke="#3A1A10" stroke-width="3"/>'
             f'<rect x="{cx+w/2-2}" y="{cy-h/2-8}" width="18" height="{h+16}" rx="7" fill="#8A3A24" stroke="#3A1A10" stroke-width="3"/>')
    return ''.join(o)

def drum_ring(c, r):            # vành trống đồng + chim Lạc bay ngược chiều kim đồng hồ
    o = [f'<circle cx="{c}" cy="{c}" r="{r}" fill="none" stroke="{BR}" stroke-width="10"/>', f'<circle cx="{c}" cy="{c}" r="{r-28}" fill="none" stroke="{BR}" stroke-width="3"/>']
    for i in range(60):
        a = math.radians(i * 6); o.append(f'<line x1="{c+math.cos(a)*(r-6)}" y1="{c+math.sin(a)*(r-6)}" x2="{c+math.cos(a)*(r-22)}" y2="{c+math.sin(a)*(r-22)}" stroke="{BR}" stroke-width="2" opacity="0.6"/>')
    for i in range(8):
        a = i * 45 + 22.5; x, y = c + math.cos(math.radians(a)) * (r - 14), c + math.sin(math.radians(a)) * (r - 14)
        o.append(f'<path d="M-14,0 Q0,-10 14,0 Q0,-4 -14,0 Z M-2,0 L-8,-12 L4,-2 Z" fill="{BR2}" transform="translate({x:.1f} {y:.1f}) rotate({a - 90:.1f})"/>')
    return ''.join(o)

def avatar(size=800, text=False):
    c = size / 2; k = size / 800
    o = [f'<svg xmlns="http://www.w3.org/2000/svg" width="{size}" height="{size}" viewBox="0 0 800 800">',
         '<defs><radialGradient id="bg" cx="50%" cy="45%" r="60%"><stop offset="0" stop-color="#4A3418"/><stop offset="0.7" stop-color="#22190F"/><stop offset="1" stop-color="#14110F"/></radialGradient>'
         '<clipPath id="cl"><circle cx="400" cy="400" r="372"/></clipPath></defs>',
         '<circle cx="400" cy="400" r="400" fill="#14110F"/><circle cx="400" cy="400" r="372" fill="url(#bg)"/>',
         '<g clip-path="url(#cl)">',
         map_scroll(400, 640, 300, 150),
         twin(255, 365, 112, "vang", "cuoi", tilt=-4, may="thang", not_ruoi=True), hand_scroll(330, 600, 1.0),
         twin(545, 365, 112, "do", "nhe_rang", wink=True, tilt=4, may="xech", seo=True), hand_flag(655, 610, 1.0),
         '</g>', drum_ring(400, 386), gemini(400, 150, 46)]
    if text:
        o.append('<path id="arc" d="M150,560 A260,260 0 0 0 650,560" fill="none"/>')
        o.append(f'<rect x="170" y="690" width="460" height="64" rx="32" fill="{INK}" stroke="{BR}" stroke-width="4"/>'
                 f'<text x="400" y="735" font-family="Playfair Display" font-weight="800" font-size="40" fill="{BR2}" text-anchor="middle" letter-spacing="3">SONG TỬ KỂ SỬ</text>')
    o.append('</svg>')
    return ''.join(o)

if __name__ == '__main__':
    os.makedirs(OUT, exist_ok=True)
    for text in (False, True):
        svg = avatar(800, text); name = 'avatar-co-chu' if text else 'avatar'
        open(os.path.join(OUT, name + '.svg'), 'w').write(svg)
        cairosvg.svg2png(bytestring=svg.encode(), write_to=os.path.join(OUT, name + '.png'), output_width=800, output_height=800)
        print(name)
