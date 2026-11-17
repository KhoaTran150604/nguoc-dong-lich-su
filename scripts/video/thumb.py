"""Thumbnail Short/video 1080×1920 vẽ trực tiếp ở độ phân giải gốc (không phóng to khung video).

    python3 scripts/video/thumb.py e2 1        → build/short/e2-p1/THUMB-E2-P1.jpg
Khung: cảnh "anh hùng" (cọc, thuyền, cờ chân dung...) + chữ hook rất lớn (vàng, viền đen, từ khóa trong ô đỏ)
+ nhãn PHẦN n · tên trận + avatar kênh. Mỗi phần chọn cảnh trong THUMBS.
"""
import base64, io, math, os, random, sys
import cairosvg
from PIL import Image, ImageFilter
import numpy as np
HERE = os.path.dirname(os.path.abspath(__file__)); ROOT = os.path.abspath(os.path.join(HERE, '..', '..'))
sys.path.insert(0, HERE); sys.path.insert(0, os.path.join(ROOT, 'scripts', 'hieuung'))
import nhanvat as NV
W, H = 1080, 1920
MUC, DONG, DONG2, KEM, DO = '#14110F', '#C9A24A', '#F3D27A', '#F2E6CC', '#B3261E'
AVATAR = os.path.join(ROOT, 'assets', 'brand', 'song-tu', 'AVATAR-YouTube-800x800.png')

DEFS = ('<defs>'
        '<linearGradient id="vang" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="#FFF1B0"/><stop offset="0.55" stop-color="#F3C94A"/><stop offset="1" stop-color="#C98A1E"/></linearGradient>'
        '<linearGradient id="go" x1="0" y1="0" x2="1" y2="0"><stop offset="0" stop-color="#3A2212"/><stop offset="0.35" stop-color="#7A4E2A"/><stop offset="0.6" stop-color="#8E5E34"/><stop offset="1" stop-color="#2E1A0E"/></linearGradient>'
        '<linearGradient id="sat" x1="0" y1="0" x2="1" y2="0"><stop offset="0" stop-color="#4A5258"/><stop offset="0.45" stop-color="#D8E0E4"/><stop offset="0.7" stop-color="#9AA4AA"/><stop offset="1" stop-color="#3A4046"/></linearGradient>'
        '<linearGradient id="troi" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="#1A1420"/><stop offset="0.35" stop-color="#5A2A28"/><stop offset="0.6" stop-color="#C2582C"/><stop offset="0.75" stop-color="#F0A040"/></linearGradient>'
        '<linearGradient id="nuoc" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="#3E6E86"/><stop offset="1" stop-color="#0E2230"/></linearGradient>'
        '<linearGradient id="buom" x1="0" y1="0" x2="1" y2="0"><stop offset="0" stop-color="#7A1A14"/><stop offset="0.5" stop-color="#C23A2A"/><stop offset="1" stop-color="#6A1410"/></linearGradient>'
        '<radialGradient id="vin" cx="50%" cy="45%" r="75%"><stop offset="0.55" stop-color="#000" stop-opacity="0"/><stop offset="1" stop-color="#000" stop-opacity="0.75"/></radialGradient>'
        '<radialGradient id="lua" cx="50%" cy="50%" r="50%"><stop offset="0" stop-color="#FFE9A0" stop-opacity="0.95"/><stop offset="0.4" stop-color="#F08A2A" stop-opacity="0.6"/><stop offset="1" stop-color="#C0301A" stop-opacity="0"/></radialGradient>'
        '</defs>')

# ---------------- cảnh nền ----------------
def sky_sea(horizon=900, sun=(780, 760), em=False):
    rng = random.Random(4); o = [f'<rect width="{W}" height="{H}" fill="url(#troi)"/>',
                                 f'<circle cx="{sun[0]}" cy="{sun[1]}" r="120" fill="#FFD27A" opacity="0.85"/><circle cx="{sun[0]}" cy="{sun[1]}" r="220" fill="#FFB050" opacity="0.18"/>']
    for k, (y, col, op) in enumerate([(horizon - 60, '#3A2030', 0.9), (horizon - 25, '#24161E', 1)]):   # núi xa
        pts = [(0, horizon)] + [(x, y - rng.uniform(20, 120) * (1 - k * 0.4)) for x in range(0, W + 120, 120)] + [(W, horizon)]
        o.append(f'<polygon points="{" ".join(f"{x:.0f},{yy:.0f}" for x, yy in pts)}" fill="{col}" opacity="{op}"/>')
    o.append(f'<rect x="0" y="{horizon}" width="{W}" height="{H-horizon}" fill="url(#nuoc)"/>')
    for i in range(25 if em else 70):         # vệt sáng mặt nước
        y = horizon + 10 + (i ** 1.35) * 1.6; w = rng.uniform(30, 160) * (1 + i / 40)
        o.append(f'<rect x="{sun[0] - w/2 + rng.uniform(-60, 60):.0f}" y="{y:.0f}" width="{w:.0f}" height="{2 + i/25:.1f}" fill="#FFC870" opacity="{max(0.05, 0.5 - i/150):.2f}"/>')
    for i in range(12 if em else 50):         # sóng
        x, y = rng.uniform(0, W), rng.uniform(horizon + 40, H)
        s = 10 + (y - horizon) / 30
        o.append(f'<path d="M{x:.0f},{y:.0f} q{s},{-s*0.6} {2*s},0 q{s},{s*0.6} {2*s},0" fill="none" stroke="#9CC4D4" stroke-width="{1.5 + (y-horizon)/400:.1f}" opacity="0.35"/>')
    return ''.join(o)

def map_bg(cam, cfg=None):
    """Nền bản đồ cổ độ phân giải cao (bbox nhỏ, nhiều điểm ảnh/độ)."""
    from bando_vung import BanDoVung
    cfg = cfg or dict(bbox=(103.0, 18.6, 108.6, 23.4), seed=21, nui=1.0,
                      song=[[(103.6, 22.6), (104.6, 21.9), (105.3, 21.3), (105.9, 20.9), (106.5, 20.3)], [(106.2, 21.6), (106.5, 21.2), (106.85, 20.85)]])
    m = BanDoVung(cfg, px_per_deg=760)
    return m.view(W, H, cam)

# ---------------- vật thể chi tiết ----------------
def stake(x, y_bot, h, w, tilt=0, water=None):
    """Cọc gỗ kiểu hoạt hình (cel-shading): thân gỗ tròn hơi cong, có vỏ, mấu cành; đầu vót lởm chởm
    nhiều mặt + chóp sắt (sử chép cọc "đầu bịt sắt"); water = y mặt nước (gợn nước quanh cọc)."""
    rng = random.Random(int(x * 7 + h)); top = y_bot - h; L = '#2A170B'; sw = max(5, w * 0.07)
    neck = top + w * 0.7; bend = rng.uniform(-0.06, 0.06) * w
    wb, wt = w * 0.56, w * 0.5                 # nửa bề rộng chân / cổ (thân hơi thon)
    body = (f'M{x-wb},{y_bot+w} C{x-wb-bend},{(y_bot+neck)/2+40} {x-wt+bend},{(y_bot+neck)/2-60} {x-wt},{neck} '
            f'L{x+wt},{neck} C{x+wt+bend},{(y_bot+neck)/2-60} {x+wb-bend},{(y_bot+neck)/2+40} {x+wb},{y_bot+w} Z')
    o = [f'<g transform="rotate({tilt} {x} {y_bot})" stroke-linejoin="round" stroke-linecap="round">',
         f'<path d="{body}" fill="#8E5527" stroke="{L}" stroke-width="{sw}"/>',
         f'<path d="M{x+w*0.2},{neck+sw} C{x+w*0.24},{(y_bot+neck)/2} {x+w*0.26},{y_bot} {x+w*0.28},{y_bot+w} L{x+wb-sw},{y_bot+w} '
         f'C{x+wb-bend-sw},{(y_bot+neck)/2+40} {x+wt+bend-sw},{(y_bot+neck)/2-60} {x+wt-sw},{neck+sw} Z" fill="#673A18"/>',   # mảng tối
         f'<path d="M{x-w*0.3},{neck+w*0.5} L{x-w*0.33},{neck+(y_bot-neck)*0.75}" stroke="#B87A42" stroke-width="{w*0.09:.1f}"/>']  # vệt sáng
    for k in range(4):                         # mảng vỏ cây: nét dọc ngắn lệch nhau
        yy = neck + (y_bot - neck) * rng.uniform(0.15, 0.85); xx = x + rng.uniform(-w * 0.25, w * 0.15); ll = rng.uniform(40, 90)
        o.append(f'<path d="M{xx:.0f},{yy:.0f} q{rng.uniform(-6,6):.0f},{ll/2:.0f} 0,{ll:.0f}" fill="none" stroke="#4A2810" stroke-width="{sw*0.55:.1f}"/>')
    side = rng.choice((-1, 1)); by = neck + (y_bot - neck) * 0.45      # mấu cành chặt
    o.append(f'<path d="M{x+side*wt*0.9},{by} l{side*w*0.28},{-w*0.14} l{side*w*0.04},{w*0.2} l{-side*w*0.3},{w*0.12} Z" fill="#8E5527" stroke="{L}" stroke-width="{sw*0.8}"/>')
    o.append(f'<ellipse cx="{x+side*(wt*0.9+w*0.31)}" cy="{by-w*0.03}" rx="{w*0.05}" ry="{w*0.1}" fill="#E0A964" stroke="{L}" stroke-width="{sw*0.6}"/>')
    tip = top - w * 0.5                         # đầu vót: các mặt vát cao thấp không đều
    j = [rng.uniform(-0.12, 0.12) * w for _ in range(3)]
    o.append(f'<polygon points="{x-wt},{neck} {x-wt*0.55},{neck-w*0.25+j[0]} {x-wt*0.1},{neck-w*0.08+j[1]} {x+wt*0.45},{neck-w*0.3+j[2]} {x+wt},{neck} '
             f'{x+w*0.2},{top} {x-w*0.2},{top}" fill="#D9A062" stroke="{L}" stroke-width="{sw}"/>')
    o.append(f'<polygon points="{x+wt*0.45},{neck-w*0.3+j[2]} {x+wt-sw/2},{neck} {x+w*0.2},{top} {x+w*0.05},{top}" fill="#AE7038"/>')
    o.append(f'<path d="M{x-wt*0.1},{neck-w*0.08+j[1]} L{x-w*0.05},{top}" stroke="#AE7038" stroke-width="{sw*0.6}"/>')
    o.append(f'<rect x="{x-w*0.25}" y="{top-w*0.02}" width="{w*0.5}" height="{w*0.14}" rx="{w*0.04}" fill="#4E565C" stroke="{L}" stroke-width="{sw*0.8}"/>')  # đai sắt
    o.append(f'<polygon points="{x-w*0.2},{top} {x+w*0.2},{top} {x},{tip}" fill="#6E787E" stroke="{L}" stroke-width="{sw}"/>')  # chóp sắt
    o.append(f'<polygon points="{x-w*0.11},{top-w*0.04} {x-w*0.02},{top-w*0.04} {x},{tip+w*0.14}" fill="#C4CDD2"/>')
    o.append('</g>')
    if water is not None:
        for k in range(2):
            o.append(f'<ellipse cx="{x}" cy="{water+k*14}" rx="{w*(0.85+k*0.55):.0f}" ry="{w*(0.16+k*0.07):.0f}" fill="none" stroke="#E8F4F8" stroke-width="{7-k*2}" opacity="{0.85-k*0.3:.2f}"/>')
    return ''.join(o)

def bai_coc(y0, y1, n_rows=5, seed=3, w0=26, w1=70, water_col='#2E5E78', skip=None, thua=4.0, cao=(2.8, 3.8)):
    """Bãi cọc nhiều cây nhỏ, xa nhỏ gần to (phối cảnh); hàng xa vẽ trước. skip(x, y) -> True để chừa chỗ."""
    rng = random.Random(seed); o = []
    for r in range(n_rows):
        u = r / max(1, n_rows - 1); y = y0 + (y1 - y0) * u ** 1.3; w = w0 + (w1 - w0) * u
        gap = w * thua * rng.uniform(0.9, 1.1); x = rng.uniform(-w, gap * 0.6)
        while x < W + w:
            yy = y + rng.uniform(-w * 0.25, w * 0.25); ww = w * rng.uniform(0.85, 1.12)
            if not (skip and skip(x, yy)):
                o.append(stake(x, yy, ww * rng.uniform(*cao), ww, rng.uniform(-7, 7)))
                o.append(f'<ellipse cx="{x:.0f}" cy="{yy+ww*0.1:.0f}" rx="{ww*0.75:.0f}" ry="{ww*0.2:.0f}" fill="{water_col}"/>'
                         f'<ellipse cx="{x:.0f}" cy="{yy+ww*0.08:.0f}" rx="{ww*0.85:.0f}" ry="{ww*0.2:.0f}" fill="none" stroke="#E8F4F8" stroke-width="{max(2,ww*0.06):.1f}" opacity="0.8"/>')
            x += gap * rng.uniform(0.8, 1.2)
    return ''.join(o)

def junk(x, y, s=1.0, tilt=0, broken=False, flip=False):
    """Chiến thuyền Nam Hán chi tiết: thân ván, buồm cánh dơi có nan, cờ."""
    f = -1 if flip else 1
    o = [f'<g transform="translate({x} {y}) rotate({tilt}) scale({f*s} {s})">',
         '<path d="M-260,-10 Q-250,60 -170,80 L190,80 Q250,60 290,-40 L240,-20 L-220,-10 Z" fill="#5A361C" stroke="#1E120A" stroke-width="6"/>',
         '<path d="M-250,10 L270,-10" stroke="#3A2212" stroke-width="5"/><path d="M-240,35 L255,22" stroke="#3A2212" stroke-width="5"/><path d="M-215,58 L225,50" stroke="#3A2212" stroke-width="5"/>',
         '<rect x="-230" y="-40" width="420" height="30" fill="#7A4A26" stroke="#1E120A" stroke-width="4"/>']
    for mx, mh, sw in ((-90, 330, 150), (90, 270, 120)):
        o.append(f'<line x1="{mx}" y1="-30" x2="{mx}" y2="{-30-mh}" stroke="#2A160A" stroke-width="9"/>')
        o.append(f'<path d="M{mx+6},{-30-mh+10} Q{mx+sw*0.8},{-30-mh} {mx+sw},{-30-mh*0.55} L{mx+sw*0.95},-50 L{mx+6},-50 Z" fill="url(#buom)" stroke="#3A0A06" stroke-width="5"/>')
        for k in range(1, 6):
            yy = -30 - mh + 10 + k * (mh - 60) / 6
            o.append(f'<line x1="{mx+6}" y1="{yy:.0f}" x2="{mx+sw*0.97:.0f}" y2="{yy+6:.0f}" stroke="#3A0A06" stroke-width="3"/>')
        o.append(f'<path d="M{mx},{-30-mh} l40,8 l-40,12 Z" fill="{DO}" stroke="#1E120A" stroke-width="2"/>')
    if broken:
        o.append('<path d="M20,80 L40,20 L10,-10 L60,-20" stroke="#0A0604" stroke-width="7" fill="none"/>')
        for k in range(6):
            o.append(f'<rect x="{-120+k*60}" y="{95+(k%2)*18}" width="44" height="10" fill="#6A4428" transform="rotate({k*23} {-100+k*60} 100)"/>')
    o.append('</g>')
    return ''.join(o)

def splash(x, y, r):
    rng = random.Random(int(x)); o = []
    for k in range(14):
        a = math.radians(-160 + k * 10 + rng.uniform(-4, 4)); l = r * rng.uniform(0.6, 1.2)
        o.append(f'<path d="M{x},{y} Q{x+math.cos(a)*l*0.5},{y+math.sin(a)*l*0.9} {x+math.cos(a)*l},{y+math.sin(a)*l*0.6}" stroke="#E8F4F8" stroke-width="{rng.uniform(3,7):.1f}" fill="none" opacity="0.8"/>')
    return ''.join(o) + f'<ellipse cx="{x}" cy="{y}" rx="{r}" ry="{r*0.18}" fill="#E8F4F8" opacity="0.55"/>'

def portrait_flag(ma, side, x, y, s, ten=None, tilt=0, grey=0.0):
    from demo import banner
    return banner(x, y, ten or NV.NHANVAT[ma].get('ten', ma.upper()), side, s, img=NV.data_uri(ma), tilt=tilt, grey=grey)

def glow(x, y, r, col='#FFD27A', op=0.45): return f'<circle cx="{x}" cy="{y}" r="{r}" fill="{col}" opacity="{op}"/>'

# ---------------- chữ ----------------
def headline(lines, y0=170, size=118):
    """lines: [(chữ, 'vang'|'do')] – dòng 'do' đặt trong ô đỏ chữ trắng."""
    o = []; y = y0
    for t, kieu in lines:
        if kieu == 'do':
            w = min(W - 70, len(t) * size * 0.62 + 80)
            o.append(f'<rect x="{(W-w)/2:.0f}" y="{y - size*0.9:.0f}" width="{w:.0f}" height="{size*1.18:.0f}" rx="18" fill="{DO}" stroke="#14110F" stroke-width="8" transform="rotate(-2 {W/2} {y})"/>')
            o.append(f'<text x="{W/2}" y="{y:.0f}" font-family="Playfair Display" font-weight="800" font-size="{size}" fill="#FFFFFF" text-anchor="middle" transform="rotate(-2 {W/2} {y})">{t}</text>')
        else:
            o.append(f'<text x="{W/2}" y="{y:.0f}" font-family="Playfair Display" font-weight="800" font-size="{size}" fill="none" stroke="#0A0806" stroke-width="22" stroke-linejoin="round" text-anchor="middle">{t}</text>')
            o.append(f'<text x="{W/2}" y="{y:.0f}" font-family="Playfair Display" font-weight="800" font-size="{size}" fill="url(#vang)" text-anchor="middle">{t}</text>')
        y += size * 1.22
    return ''.join(o)

def footer(phan, nhan):
    av = 'data:image/png;base64,' + base64.b64encode(open(AVATAR, 'rb').read()).decode()
    return (f'<rect x="0" y="{H-300}" width="{W}" height="300" fill="#0A0806" opacity="0.55"/>'
            f'<rect x="60" y="{H-245}" width="300" height="96" rx="48" fill="{DO}" stroke="{DONG2}" stroke-width="6"/>'
            f'<text x="210" y="{H-180}" font-family="Be Vietnam Pro SemiBold" font-size="54" fill="#FFFFFF" text-anchor="middle">{phan}</text>'
            f'<text x="63" y="{H-77}" font-family="Playfair Display" font-weight="800" font-size="68" fill="#0A0806">{nhan}</text>'
            f'<text x="60" y="{H-80}" font-family="Playfair Display" font-weight="800" font-size="68" fill="{DONG2}">{nhan}</text>'
            f'<defs><clipPath id="av"><circle cx="{W-150}" cy="{H-160}" r="105"/></clipPath></defs>'
            f'<circle cx="{W-150}" cy="{H-160}" r="112" fill="{DONG}"/><image href="{av}" x="{W-255}" y="{H-265}" width="210" height="210" clip-path="url(#av)"/>')

# ---------------- cảnh từng phần ----------------
TA, DICH, GIAN = ('#D9B44A', '#5A3A10'), ('#A8382A', '#4A1410'), ('#4A4440', '#1E1A16')

def canh_coc():        # P1: bãi cọc nhỏ dày đặc, một chiến thuyền mắc giữa bãi cọc, đoàn thuyền giặc phía sau
    bg = sky_sea(960, (300, 840), em=True) + junk(820, 985, 0.22, -2, flip=True) + junk(960, 990, 0.18, 1, flip=True)
    hole = lambda x, y: 300 < x < 820 and 1150 < y < 1330
    o = [bai_coc(1010, 1110, 2, seed=5, w0=16, w1=24), junk(560, 1250, 0.95, 10, broken=True), splash(600, 1300, 200),
         bai_coc(1500, 1800, 3, seed=8, w0=46, w1=74, thua=4.5)]
    return ''.join(o), bg

def canh_phan_boi():   # P2: Dương Đình Nghệ ngã xuống, Kiều Công Tiễn đứng sau
    o = [glow(330, 1180, 230, '#B3261E', 0.22), portrait_flag('duong-dinh-nghe', TA, 330, 1560, 1.55, tilt=-24, grey=0.5),
         glow(780, 1100, 230, '#000000', 0.3), portrait_flag('kieu-cong-tien', GIAN, 780, 1520, 1.75)]
    return ''.join(o), map_bg((105.8, 20.9, 2.4))

def canh_loi_can():    # P3: Tiêu Ích can, Lưu Cung không nghe, đoàn thuyền ra khơi
    o = [sky_sea(1250, (540, 1100)), glow(300, 1000, 330, '#F3D27A', 0.18), portrait_flag('tieu-ich', DICH, 300, 1380, 1.45),
         portrait_flag('luu-cung', DICH, 790, 1330, 1.25, tilt=6), junk(560, 1560, 0.5, 2, flip=True), junk(860, 1600, 0.42, -3, flip=True)]
    return ''.join(o), None

def canh_chuan_bi():   # P4: bãi cọc ngầm dưới làn nước, Ngô Quyền ở trên, giặc nhỏ ở chân trời
    bg = sky_sea(1000, (820, 900), em=True) + junk(860, 1005, 0.16, 0, flip=True) + junk(950, 1000, 0.13, 0, flip=True)
    o = [bai_coc(1300, 1780, 3, seed=11, w0=36, w1=66, water_col='#2E6E8E', thua=4.5)]
    o.append(f'<rect x="0" y="1150" width="{W}" height="{H-1150}" fill="#2E6E8E" opacity="0.55"/>')
    o.append(f'<path d="M0,1150 Q270,1135 540,1150 T1080,1150" stroke="#DCEBF0" stroke-width="5" fill="none" opacity="0.8"/>')
    o.append(glow(540, 760, 250, '#F3D27A', 0.22)); o.append(portrait_flag('ngo-quyen', TA, 540, 1050, 1.25))
    return ''.join(o), bg

def canh_nuoc_rut():   # P5: nước rút lộ cả bãi cọc trên bùn, chiến thuyền mắc cọc nghiêng
    bg = sky_sea(900, (760, 780), em=True)
    hole = lambda x, y: 230 < x < 880 and 1180 < y < 1400
    o = [f'<rect x="0" y="1060" width="{W}" height="{H-1060}" fill="#6A5A40" opacity="0.6"/>',
         bai_coc(1090, 1180, 2, seed=21, w0=18, w1=26, water_col='#5A4C36'),
         junk(560, 1250, 1.0, -15, broken=True),
         bai_coc(1520, 1800, 3, seed=23, w0=48, w1=76, water_col='#5A4C36', thua=4.5)]
    return ''.join(o), bg

def canh_xung_vuong():  # P6: Ngô Quyền xưng vương, đóng đô Cổ Loa
    rays = ''.join(f'<polygon points="540,1000 {540+math.cos(math.radians(a-4))*1400:.0f},{1000+math.sin(math.radians(a-4))*1400:.0f} {540+math.cos(math.radians(a+4))*1400:.0f},{1000+math.sin(math.radians(a+4))*1400:.0f}" fill="#F3D27A" opacity="0.12"/>' for a in range(0, 360, 20))
    o = [rays, glow(540, 1000, 420, '#F3D27A', 0.3), portrait_flag('ngo-quyen', TA, 540, 1600, 1.9)]
    return ''.join(o), map_bg((105.9, 21.1, 2.0))

THUMBS = {('e2', 1): (canh_coc, [('MỘT HÀNG', 'vang'), ('CỌC GỖ', 'vang'), ('ĐÁNH CHÌM', 'vang'), ('CẢ HẠM ĐỘI?', 'do')]),
          ('e2', 2): (canh_phan_boi, [('THẮNG GIẶC', 'vang'), ('NGOÀI…', 'vang'), ('CHẾT VÌ', 'vang'), ('NGƯỜI TRONG', 'do')]),
          ('e2', 3): (canh_loi_can, [('MỘT LỜI CAN', 'vang'), ('BỊ BỎ', 'vang'), ('NGOÀI TAI', 'do')]),
          ('e2', 4): (canh_chuan_bi, [('GIẶC CÒN', 'vang'), ('TRÊN BIỂN,', 'vang'), ('NGÔ QUYỀN ĐÃ…', 'do')]),
          ('e2', 5): (canh_nuoc_rut, [('CHỈ TRONG', 'vang'), ('CHỐC LÁT,', 'vang'), ('NƯỚC RÚT…', 'do')]),
          ('e2', 6): (canh_xung_vuong, [('SAU', 'vang'), ('BẠCH ĐẰNG,', 'vang'), ('NGÔ QUYỀN', 'vang'), ('LÀM GÌ?', 'do')])}

def make(tap, n, phan, nhan, out):
    import subprocess, thumb_video as TV
    if (tap, n) in TV.CFG:      # mẫu mới (duyệt 17/11): khung chính video vẽ 4K + mũi tên/X – chạy tiến trình riêng
        subprocess.run([sys.executable, TV.__file__, tap, str(n), out], check=True, cwd=ROOT); return out
    fn, lines = THUMBS[(tap, n)]
    body, bg = fn()
    if isinstance(bg, str):   # nền vẽ bằng SVG → làm mờ nhẹ như xóa phông, tiền cảnh giữ sắc nét
        bg = Image.open(io.BytesIO(cairosvg.svg2png(bytestring=f'<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{H}">{DEFS}{bg}</svg>'.encode()))).convert('RGBA').filter(ImageFilter.GaussianBlur(5))
        base = bg
    else:
        base = (bg.convert('RGBA') if bg is not None else Image.new('RGBA', (W, H), (20, 17, 15, 255)))
    if bg is not None and base is not bg:   # nền bản đồ tối lại để nổi chữ và nhân vật
        base = Image.blend(base, Image.new('RGBA', (W, H), (12, 9, 6, 255)), 0.35)
    size = 118 if len(lines) <= 3 else 108
    svg = (f'<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{H}">{DEFS}{body}'
           f'<rect width="{W}" height="{H}" fill="url(#vin)"/>'
           f'<rect x="0" y="0" width="{W}" height="{len(lines)*size*1.22+170}" fill="#0A0806" opacity="0.35"/>'
           + headline(lines, 190, size) + footer(phan, nhan) + '</svg>')
    ov = Image.open(io.BytesIO(cairosvg.svg2png(bytestring=svg.encode()))).convert('RGBA')
    base.alpha_composite(ov)
    arr = np.asarray(base.convert('RGB')).astype(np.float32)          # hạt giấy nhẹ cho chất "tranh"
    noise = np.random.default_rng(n).normal(0, 4, arr.shape[:2])[..., None]
    Image.fromarray(np.clip(arr + noise, 0, 255).astype('uint8')).save(out, quality=94)
    return out

if __name__ == '__main__':
    tap, n = sys.argv[1], int(sys.argv[2])
    od = os.path.join(ROOT, 'build', 'short', f'{tap}-p{n}'); os.makedirs(od, exist_ok=True)
    print(make(tap, n, f'PHẦN {n}', 'BẠCH ĐẰNG 938', os.path.join(od, f'THUMB-{tap.upper()}-P{n}.jpg')))
