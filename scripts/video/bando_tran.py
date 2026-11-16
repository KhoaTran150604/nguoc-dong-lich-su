"""Bản đồ trận cửa sông Bạch Đằng (MINH HỌA, không theo tỉ lệ thật) – khung 16:9.

Nền vẽ một lần ở 2 trạng thái nước (lên / rút) rồi trộn theo mức triều, nên mỗi khung hình
chỉ phải vẽ lớp thuyền, cọc, cờ. Toạ độ theo khung chuẩn 960×540, nhân U cho độ phân giải thật.
"""
import io, math, random
import numpy as np
import cairosvg
from PIL import Image, ImageFilter

INK, BRONZE, BRONZE2, RED, CREAM = '#2A1A10', '#C9A24A', '#F3D27A', '#B3261E', '#F2E6CC'
LAND, LAND2, MUD, SEA_HI, SEA_LO = '#D8BE8E', '#CBAE7C', '#A8916A', '#3F7088', '#5A8CA0'

# Luồng sông chính (thượng nguồn trái → cửa biển phải) và nhánh phụ
RIVER = [(-30, 132), (60, 140), (150, 168), (240, 190), (330, 206), (420, 232), (500, 258),
         (565, 280), (625, 296), (690, 308), (800, 326), (900, 340)]
TRIBS = [[(285, -20), (300, 60), (318, 130), (330, 205)],
         [(-20, 330), (90, 300), (190, 268), (280, 238), (360, 218)],
         [(120, -20), (130, 50), (150, 120), (165, 165)]]
SEA = 'M655,-10 C612,70 668,150 646,232 C636,268 640,300 652,318 C676,372 690,430 612,550 L970,550 L970,-10 Z'
ISLANDS = [(712, 205, 26), (745, 255, 16), (700, 400, 22), (790, 160, 14), (835, 300, 30),
           (880, 420, 20), (760, 470, 18), (905, 210, 12), (668, 330, 8), (690, 270, 7)]

def _pts(p, U): return ' '.join(f'{x*U:.1f},{y*U:.1f}' for x, y in p)

def _texture(w, h, seed):
    rng = np.random.default_rng(seed)
    n = rng.random((h // 6 + 1, w // 6 + 1))
    a = np.asarray(Image.fromarray((n * 255).astype('uint8')).resize((w, h), Image.BICUBIC).filter(ImageFilter.GaussianBlur(5))).astype(float) / 255
    fine = rng.random((h, w)) * 0.25
    v = (a - 0.5) * 0.9 + (fine - 0.12) * 0.4
    return Image.fromarray(np.clip(128 + v * 70, 0, 255).astype('uint8'))

def _hill(x, y, s, U, rng):
    s *= U; o = (f'<g transform="translate({x*U:.1f} {y*U:.1f}) scale({s:.2f})">'
                 f'<path d="M-22,10 Q-12,-14 0,-20 Q12,-14 22,10 Z" fill="#B49870" stroke="#5A3A20" stroke-width="1.6"/>'
                 f'<path d="M0,-20 Q12,-14 22,10 L6,10 Q8,-4 0,-20 Z" fill="#8E7350"/>')
    for k in range(3):   # nét gạch bóng kiểu bản đồ cổ
        o += f'<line x1="{4+k*5}" y1="{-12+k*6}" x2="{9+k*5}" y2="{-4+k*6}" stroke="#5A3A20" stroke-width="0.9"/>'
    return o + '</g>'

def _tree(x, y, s, U):
    s *= U
    return (f'<g transform="translate({x*U:.1f} {y*U:.1f}) scale({s:.2f})"><line x1="0" y1="0" x2="0" y2="6" stroke="#4A3220" stroke-width="1.6"/>'
            f'<circle cy="-3" r="5.5" fill="#6B8250" stroke="#3E4E2E" stroke-width="1"/></g>')

def _field(x, y, U, rot):
    o = f'<g transform="translate({x*U:.1f} {y*U:.1f}) rotate({rot}) scale({U:.2f})">'
    for i in range(3):
        for j in range(2):
            o += f'<rect x="{i*11}" y="{j*8}" width="10" height="7" fill="#C9B47A" stroke="#8C7444" stroke-width="0.7"/>'
            o += f'<line x1="{i*11+2}" y1="{j*8+3.5}" x2="{i*11+8}" y2="{j*8+3.5}" stroke="#7E8E4A" stroke-width="0.7"/>'
    return o + '</g>'

def _waves(U, rng):
    o = []
    for _ in range(70):
        x, y = rng.uniform(660, 950), rng.uniform(10, 530)
        o.append(f'<path d="M{x*U:.1f},{y*U:.1f} q{3*U:.1f},{-3*U:.1f} {6*U:.1f},0 q{3*U:.1f},{3*U:.1f} {6*U:.1f},0" fill="none" stroke="#D6E6EA" stroke-width="{0.9*U:.1f}" opacity="0.55"/>')
    return ''.join(o)

def _compass(x, y, U):
    r = 26 * U; o = f'<g transform="translate({x*U:.1f} {y*U:.1f})">'
    o += f'<circle r="{r:.1f}" fill="none" stroke="{BRONZE}" stroke-width="{1.5*U:.1f}"/><circle r="{r*0.8:.1f}" fill="none" stroke="{BRONZE}" stroke-width="{0.8*U:.1f}"/>'
    for a, l in [(0, 1), (90, 0.6), (180, 0.6), (270, 0.6)]:
        o += f'<polygon points="0,{-r*l:.1f} {4*U:.1f},0 0,{4*U:.1f} {-4*U:.1f},0" fill="{BRONZE2 if a == 0 else BRONZE}" transform="rotate({a})"/>'
    return o + f'<text y="{-r-5*U:.1f}" font-family="Playfair Display" font-weight="800" font-size="{11*U:.0f}" fill="{BRONZE2}" text-anchor="middle">B</text></g>'

def bg_svg(W, H, U, tide):
    """tide 1 = nước lên, 0 = nước rút."""
    rng = random.Random(11)
    o = [f'<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{H}">', f'<rect width="{W}" height="{H}" fill="{LAND}"/>']
    # đồng bằng phía nam: ruộng
    for _ in range(26):
        x, y = rng.uniform(20, 560), rng.uniform(300, 520)
        o.append(_field(x, y, U, rng.choice([-8, -4, 0, 5, 9])))
    # bãi bồi + nước: sông chính, nhánh phụ
    mud_w, river_w = 40, (38 if tide > 0.5 else 15)
    trib_w = 8 if tide > 0.5 else 4
    for p in TRIBS:
        o.append(f'<polyline points="{_pts(p, U)}" fill="none" stroke="{MUD}" stroke-width="{11*U:.1f}" stroke-linecap="round" stroke-linejoin="round"/>')
    o.append(f'<polyline points="{_pts(RIVER, U)}" fill="none" stroke="{MUD}" stroke-width="{mud_w*U:.1f}" stroke-linecap="round" stroke-linejoin="round"/>')
    # biển: bãi bùn ven bờ khi nước rút
    o.append(f'<path d="{SEA}" fill="{MUD}" transform="scale({U:.3f})"/>')
    sea_c = SEA_HI if tide > 0.5 else SEA_LO
    o.append(f'<path d="{SEA}" fill="{sea_c}" transform="translate({(0 if tide > 0.5 else 14)*U:.1f} 0) scale({U:.3f})"/>')
    for p in TRIBS:
        o.append(f'<polyline points="{_pts(p, U)}" fill="none" stroke="{sea_c}" stroke-width="{trib_w*U:.1f}" stroke-linecap="round" stroke-linejoin="round"/>')
    o.append(f'<polyline points="{_pts(RIVER, U)}" fill="none" stroke="{sea_c}" stroke-width="{river_w*U:.1f}" stroke-linecap="round" stroke-linejoin="round"/>')
    for k in range(3):   # vệt sóng ven bờ
        o.append(f'<path d="{SEA}" fill="none" stroke="#C4DCE2" stroke-width="{0.9:.1f}" opacity="{0.55-0.15*k:.2f}" transform="translate({(10+9*k+(0 if tide > 0.5 else 14))*U:.1f} 0) scale({U:.3f})"/>')
    o.append(_waves(U, rng))
    # đảo đá ngoài cửa biển
    for x, y, r in ISLANDS:
        o.append(f'<ellipse cx="{x*U:.1f}" cy="{y*U:.1f}" rx="{r*1.4*U:.1f}" ry="{r*0.8*U:.1f}" fill="{MUD}" opacity="{0.0 if tide > 0.5 else 0.8}"/>')
        o.append(f'<path d="M{(x-r)*U:.1f},{y*U:.1f} Q{(x-r*0.6)*U:.1f},{(y-r*1.1)*U:.1f} {x*U:.1f},{(y-r*0.9)*U:.1f} Q{(x+r*0.7)*U:.1f},{(y-r*1.2)*U:.1f} {(x+r)*U:.1f},{y*U:.1f} Z" fill="#9A8A60" stroke="#4A3A22" stroke-width="{1.2*U:.1f}"/>')
        o.append(f'<circle cx="{(x-r*0.2)*U:.1f}" cy="{(y-r*0.7)*U:.1f}" r="{r*0.28*U:.1f}" fill="#6B8250"/>')
    # đồi núi bờ bắc, cây
    for _ in range(38):
        x, y = rng.uniform(10, 620), rng.uniform(10, 120)
        if y < 0.18 * x - 10 + 110 or True:
            o.append(_hill(x, y, rng.uniform(0.7, 1.3), U, rng))
    for _ in range(60):
        x, y = rng.uniform(10, 640), rng.uniform(150, 530)
        ry = 132 + (x / 900) * 200
        if abs(y - ry) > 40: o.append(_tree(x, y, rng.uniform(0.7, 1.1), U))
    # chữ
    t = lambda x, y, s, txt, c=INK, rot=0, ls=2: (f'<text x="{x*U:.0f}" y="{y*U:.0f}" font-family="Playfair Display" font-weight="800" font-size="{s*U:.0f}" fill="{c}" text-anchor="middle" letter-spacing="{ls}" transform="rotate({rot} {x*U:.0f} {y*U:.0f})">{txt}</text>')
    o.append(t(250, 172, 17, 'Sông Bạch Đằng', '#1E3A44', 13, 1))
    o.append(t(800, 100, 22, 'BIỂN', '#E8EEF0', 0, 6))
    o.append(t(612, 334, 12, 'cửa biển', '#1E3A44', 0, 1))
    o.append(_compass(905, 62, U))
    # khung viền bản đồ cổ + nhãn
    o.append(f'<rect x="{6*U:.1f}" y="{6*U:.1f}" width="{W-12*U:.1f}" height="{H-12*U:.1f}" fill="none" stroke="{INK}" stroke-width="{2.5*U:.1f}"/>')
    o.append(f'<rect x="{11*U:.1f}" y="{11*U:.1f}" width="{W-22*U:.1f}" height="{H-22*U:.1f}" fill="none" stroke="{BRONZE}" stroke-width="{1*U:.1f}"/>')
    o.append(f'<rect x="{20*U:.1f}" y="{H-44*U:.1f}" width="{238*U:.1f}" height="{26*U:.1f}" fill="{CREAM}" stroke="{INK}" stroke-width="{1.2*U:.1f}" opacity="0.92"/>')
    o.append(f'<text x="{139*U:.1f}" y="{H-26*U:.1f}" font-family="Be Vietnam Pro SemiBold" font-size="{11.5*U:.0f}" fill="{INK}" text-anchor="middle">Cửa sông Bạch Đằng · bản đồ minh họa</text>')
    o.append('</svg>')
    return ''.join(o)

_cache = {}
def background(W, H, U, tide):
    """Ảnh nền RGBA đã trộn theo mức triều (0–1), có vân giấy."""
    if (W, 'hi') not in _cache:
        tex = _texture(W, H, 5)
        for k, tv in (('hi', 1), ('lo', 0)):
            im = Image.open(io.BytesIO(cairosvg.svg2png(bytestring=bg_svg(W, H, U, tv).encode()))).convert('RGB')
            arr = np.asarray(im).astype(float) * (0.86 + 0.28 * np.asarray(tex)[..., None] / 255)
            _cache[(W, k)] = Image.fromarray(np.clip(arr, 0, 255).astype('uint8')).convert('RGBA')
    tide = max(0.0, min(1.0, tide))
    return Image.blend(_cache[(W, 'lo')], _cache[(W, 'hi')], tide)
