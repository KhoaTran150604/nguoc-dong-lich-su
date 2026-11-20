"""Bộ máy dựng video dùng chung cho cả series Ngược Dòng Sử Việt.

Mỗi tập là một module trong scripts/video/tap/ (vd tap/e2.py) khai báo:
    SCENES = {'s01': ham(tl, d) -> svg, ...}   # hàm vẽ lớp phủ, gọi bg_*() để chọn nền
    SFX(code, d) -> [(giây_trong_cảnh, tên_âm, độ_lớn, độ_dài|None)]   # tuỳ chọn
    TAIL = 3.0                                  # giữ cảnh cuối thêm (giây)

Chạy (từ gốc repo):
    python3 scripts/video/dung.py e2 docs/videos/E2-loi-doc.txt --stills [s05,s12]   # ảnh tĩnh duyệt khung
    python3 scripts/video/dung.py e2 docs/videos/E2-loi-doc.txt assets/e2/E2-GiaHuy   # nháp 540p30
    python3 scripts/video/dung.py e2 ... assets/e2/E2-GiaHuy --final --fps60          # bản cuối 1080p60
Lời đọc: mỗi dòng một câu; "# sNN" gán cảnh; "# lặng N" giữ cảnh trước thêm N giây;
"# lặng N sNN" chèn cảnh lặng riêng. Mốc câu lấy từ <giọng>.json (skill giong-doc).
Đầu ra ở build/<tập>/ (clip từng cảnh có cache → sửa cảnh nào render lại cảnh đó).
"""
import hashlib, importlib, io, json, math, os, re, subprocess, sys
import numpy as np
HERE = os.path.dirname(os.path.abspath(__file__)); ROOT = os.path.abspath(os.path.join(HERE, '..', '..'))
sys.path.insert(0, os.path.join(HERE, '..', 'hieuung')); sys.path.insert(0, HERE)
import tuongthich                   # máy không có cairo/ffmpeg hệ thống -> dùng resvg-py / imageio-ffmpeg
import demo as L                    # thư viện hiệu ứng H1–H12 đã duyệt (banner, boat, sword, flame, ...)
import nhanvat as NV
import amthanh as AT
import cairosvg
import anhsang as AS                # lớp ánh sáng dùng chung (--anhsang[=ngay|chieu|dem])
from PIL import Image
_as = next((a for a in sys.argv if a.startswith('--anhsang')), None)
ANH_SANG = (_as.split('=', 1)[1] if _as and '=' in _as else 'ngay') if _as else None

W, H, FPS, U = L.W, L.H, L.FPS, L.U
TA, DICH, DONG, DONG2, KEM, MUC, DO = L.TA, L.DICH, L.DONG, L.DONG2, L.KEM, L.MUC, L.DO
seg, lerp, ease = L.seg, L.lerp, L.ease
GIAN = ('#4A4440', '#1E1A16')        # phe phản (Kiều Công Tiễn...): xám

# ---------------- Nền ----------------
STATE = {}
def bg_tran(bando, tide):            # bản đồ trận (bando_tran) theo mức nước
    STATE['bg'] = ('tran', bando, tide); return ''
def bg_vung(bando, cam):             # bản đồ vùng (bando_vung) theo camera
    STATE['bg'] = ('vung', bando, cam); return ''
def bg_den():                        # nền mực tối (thẻ tiêu đề, sa bàn)
    STATE['bg'] = ('den',); return ''
def bg_anh(path):                    # nền là một ảnh có sẵn (banner, thumbnail...)
    STATE['bg'] = ('anh', path); return ''
def dim(a):                          # làm tối nền (cho khung trích, chân dung lớn)
    return f'<rect width="{W}" height="{H}" fill="{MUC}" opacity="{a:.2f}"/>'

def _bg_image():
    b = STATE.get('bg', ('den',))
    if b[0] == 'tran':
        lit = ANH_SANG or getattr(EP, 'ANH_SANG', None)
        return (b[1].background(W, H, U, b[2], lit=lit) if lit else b[1].background(W, H, U, b[2])).copy()
    if b[0] == 'vung': return b[1].view(W, H, b[2]).convert('RGBA')
    if b[0] == 'anh':
        if b[1] not in STATE_C: STATE_C[b[1]] = Image.open(b[1]).convert('RGBA').resize((W, H), Image.LANCZOS)
        return STATE_C[b[1]].copy()
    return Image.new('RGBA', (W, H), (20, 17, 15, 255))

# ---------------- Ký hiệu dùng chung ----------------
def flag(ma, side, x, y, s=0.3, ten=None, **kw):
    """Cờ chân dung. ma = mã nhân vật (scripts/video/nhanvat.py)."""
    return L.banner(x, y, ten or NV.NHANVAT[ma].get('ten', ma.upper()), side, s, img=NV.data_uri(ma), **kw)

def small_flags(cx, cy, n, side, t, r=60, seed=1, appear=(0.2, 1.6)):
    """H7: nhiều cờ nhỏ lấp ló (binh lính, trăm quan...)."""
    import random; rng = random.Random(seed); o = []
    for j in range(n):
        dx, dy = rng.uniform(-r, r), rng.uniform(-r * 0.6, r * 0.6)
        a = seg(t, appear[0] + j * (appear[1] - appear[0]) / n, appear[0] + j * (appear[1] - appear[0]) / n + 0.4)
        if a <= 0: continue
        sw = 3 * math.sin(t * 5 + j); px, py = cx + dx * U, cy + dy * U + (1 - a) * 10 * U
        o.append(f'<g opacity="{a:.2f}" transform="translate({px:.1f} {py:.1f})"><line x1="0" y1="0" x2="0" y2="{-26*U:.1f}" stroke="#3A2618" stroke-width="{1.6*U:.1f}"/>'
                 f'<path d="M0,{-26*U:.1f} L{(14+sw)*U:.1f},{-21*U:.1f} L0,{-16*U:.1f} Z" fill="{side[0]}" stroke="{side[1]}" stroke-width="{U:.1f}"/></g>')
    return ''.join(o)

def soldier(x, y, side, s=1.0, t=0.0, phase=0.0, face=1):
    """Hình lính (thay cờ nhỏ): phe ta áo vàng, nón, khiên mây, giáo; phe địch áo đỏ, mũ trụ tua đỏ, kích.
    (x, y) = chân lính; s = cỡ (1 ≈ cao 64 đơn vị khung 960); face = 1 nhìn phải, -1 nhìn trái."""
    ta = side is TA or side == TA
    col, dark = (('#D9B44A', '#5A3A10') if ta else ('#A8382A', '#3A0E0A'))
    bob = math.sin(t * 6 + phase) * 1.0
    o = [f'<g transform="translate({x:.1f} {y + bob*U*s:.1f}) scale({face*s*U:.3f} {s*U:.3f})">',
         '<ellipse cx="0" cy="1" rx="11" ry="3" fill="#000" opacity="0.28"/>',
         '<rect x="-5" y="-15" width="4" height="15" rx="1.5" fill="#3A2618"/><rect x="1" y="-15" width="4" height="15" rx="1.5" fill="#3A2618"/>',
         f'<path d="M-9,-14 L9,-14 L7,-37 L-7,-37 Z" fill="{col}" stroke="{dark}" stroke-width="1.4"/>',
         f'<rect x="-8" y="-25" width="16" height="3" fill="{dark}"/>']
    if not ta:   # giáp vảy
        o.append(''.join(f'<path d="M{xx},{yy} q2,2 4,0" stroke="{dark}" stroke-width="0.8" fill="none"/>' for yy in (-34, -30) for xx in (-6, -2, 2)))
    o.append('<circle cx="0" cy="-43" r="6.5" fill="#E2B98C" stroke="#5A3A20" stroke-width="0.9"/>')
    o.append('<circle cx="2.2" cy="-43.5" r="0.9" fill="#1E120A"/>')
    if ta:
        o.append('<polygon points="-12,-45 0,-56 12,-45" fill="#B08A3A" stroke="#3A2618" stroke-width="1.2"/>')
        o.append('<line x1="11" y1="5" x2="11" y2="-66" stroke="#4A3220" stroke-width="2"/><polygon points="8.5,-64 11,-74 13.5,-64" fill="#C8CED2" stroke="#3A3A3A" stroke-width="0.6"/>')
        o.append('<line x1="7" y1="-31" x2="11" y2="-36" stroke="#E2B98C" stroke-width="3" stroke-linecap="round"/>')
        o.append('<circle cx="-9" cy="-27" r="7.5" fill="#8A6A30" stroke="#C9A24A" stroke-width="1.6"/><circle cx="-9" cy="-27" r="2" fill="#C9A24A"/>')
    else:
        o.append(f'<path d="M-7.5,-44 Q-7,-53 0,-54 Q7,-53 7.5,-44 Z" fill="#5A2A1A" stroke="#1E120A" stroke-width="1"/><path d="M0,-54 Q-4,-60 -6,-57 Q-2,-58 0,-55 Q2,-58 6,-57 Q4,-60 0,-54 Z" fill="#B3261E"/>')
        o.append('<line x1="11" y1="5" x2="11" y2="-66" stroke="#4A3220" stroke-width="2"/><path d="M11,-66 L11,-74 M11,-68 Q17,-70 15,-62 Q13,-66 11,-64" stroke="#3A3A3A" stroke-width="1.2" fill="#C8CED2"/>')
        o.append('<line x1="7" y1="-31" x2="11" y2="-36" stroke="#E2B98C" stroke-width="3" stroke-linecap="round"/>')
    o.append('</g>'); return ''.join(o)

def soldiers(cx, cy, n, side, t, r=60, seed=1, appear=(0.2, 1.6), s=0.55, face=1, ok=None):
    """H7 (bản mới): một toán lính hiện dần quanh (cx, cy). Dùng cho quân đông, phục binh."""
    import random; rng = random.Random(seed); pts = []
    tries = 0
    while len(pts) < n and tries < n * 30:                      # ok(x, y) = điểm hợp lệ (vd đất liền)
        dx, dy = rng.uniform(-r, r), rng.uniform(-r * 0.55, r * 0.55); tries += 1
        if ok is None or ok(cx + dx * U, cy + dy * U): pts.append((dx, dy, len(pts)))
    o = []
    for dx, dy, j in sorted(pts, key=lambda p: p[1]):            # vẽ từ xa đến gần
        a = seg(t, appear[0] + j * (appear[1] - appear[0]) / n, appear[0] + j * (appear[1] - appear[0]) / n + 0.4)
        if a <= 0: continue
        o.append(f'<g opacity="{a:.2f}">' + soldier(cx + dx * U, cy + dy * U + (1 - a) * 8 * U, side, s, t, j * 0.7, face) + '</g>')
    return ''.join(o)

def clash(x, y, tl, s=0.45):
    """H3: hai kiếm chém vào nhau + lửa."""
    if tl < 0: return ''
    g = seg(tl, 0.0, 0.5); f = min(1, tl / 0.5); hit = tl - 0.5; o = []
    for i in range(5): o.append(L.flame(x + (i - 2) * 6 * U * s / 0.45, y + 3 * U, (0.5 - abs(i - 2) * 0.09) * f * s / 0.45, tl, i))
    sh = 4 * math.sin(tl * 40) * max(0, 1 - hit * 2) if hit > 0 else 0
    o.append(f'<g transform="translate({x:.1f} {y:.1f})"><g transform="translate({-12*U*s/0.45:.1f} 0)">{L.sword(lerp(-75, 32, g)+sh, s*U)}</g>'
             f'<g transform="translate({12*U*s/0.45:.1f} 0)">{L.sword(lerp(75, -32, g)-sh, s*U)}</g>')
    if 0 < hit < 0.6: o.append(f'<circle cx="0" cy="{-38*U*s/0.45:.1f}" r="{(5+18*hit)*U*s/0.45:.1f}" fill="{DONG2}" opacity="{0.85*(1-hit/0.6):.2f}"/>')
    return ''.join(o) + '</g>'

def xmark(x, y, u, r=40): return L.xmark(x, y, u) if r == 60 else _xm(x, y, u, r)
def _xm(x, y, u, r):
    a = min(1, u * 2); b = max(0, min(1, u * 2 - 1)); r *= U
    o = f'<line x1="{x-r:.1f}" y1="{y-r:.1f}" x2="{x-r+2*r*a:.1f}" y2="{y-r+2*r*a:.1f}" stroke="{DO}" stroke-width="{11*U:.1f}" stroke-linecap="round"/>'
    if b > 0: o += f'<line x1="{x+r:.1f}" y1="{y-r:.1f}" x2="{x+r-2*r*b:.1f}" y2="{y-r+2*r*b:.1f}" stroke="{DO}" stroke-width="{11*U:.1f}" stroke-linecap="round"/>'
    return o

def glow(x, y, t, r=50, col=DONG2):
    """Vòng sáng nhấp nhô quanh một điểm (gây chú ý)."""
    k = (t * 0.8) % 1
    return (f'<circle cx="{x:.1f}" cy="{y:.1f}" r="{(r*0.5+r*k)*U:.1f}" fill="none" stroke="{col}" stroke-width="{3*U:.1f}" opacity="{0.8*(1-k):.2f}"/>'
            f'<circle cx="{x:.1f}" cy="{y:.1f}" r="{r*0.35*U:.1f}" fill="{col}" opacity="0.25"/>')

def tint(x, y, u, r, col, op=0.35):
    """H4: vùng màu loang dần từ một điểm."""
    return f'<circle cx="{x:.1f}" cy="{y:.1f}" r="{r*U*ease(u):.1f}" fill="{col}" opacity="{op:.2f}"/>'

def link(x1, y1, x2, y2, u=1.0, col=DONG2, broken=0.0):
    """Đường nối quan hệ (con rể, chủ tướng...); broken>0 thì đứt gãy, chuyển đỏ."""
    xm, ym = lerp(x1, x2, u), lerp(y1, y2, u)
    if broken <= 0:
        return f'<line x1="{x1:.1f}" y1="{y1:.1f}" x2="{xm:.1f}" y2="{ym:.1f}" stroke="{col}" stroke-width="{4*U:.1f}" stroke-dasharray="{10*U:.0f} {7*U:.0f}"/>'
    gap = 0.12 * broken; mx, my = (x1 + x2) / 2, (y1 + y2) / 2
    return (f'<line x1="{x1:.1f}" y1="{y1:.1f}" x2="{lerp(x1, x2, 0.5-gap):.1f}" y2="{lerp(y1, y2, 0.5-gap) + 12*U*broken:.1f}" stroke="{DO}" stroke-width="{4*U:.1f}"/>'
            f'<line x1="{lerp(x1, x2, 0.5+gap):.1f}" y1="{lerp(y1, y2, 0.5+gap) - 12*U*broken:.1f}" x2="{x2:.1f}" y2="{y2:.1f}" stroke="{DO}" stroke-width="{4*U:.1f}"/>')

def _wrap(text, n):
    words, lines, cur = text.split(), [], ''
    for w_ in words:
        if len(cur) + len(w_) + 1 > n and cur: lines.append(cur); cur = w_
        else: cur = (cur + ' ' + w_).strip()
    return lines + ([cur] if cur else [])

def quote(text, nguon, a=1.0, ma=None, side=TA, ten=None):
    """H12: khung trích lời người xưa (CHỈ lời sử chép), có ghi nguồn; tuỳ chọn chân dung bên trái."""
    lines = _wrap(text, 40); lh = 34 * U; w = 640 * U; x0 = (W - w) / 2 + (90 * U if ma else 0); h = (len(lines) * 34 + 110) * U; y0 = (H - h) / 2
    o = [f'<g opacity="{a:.2f}">', dim(0.45),
         f'<rect x="{x0:.0f}" y="{y0:.0f}" width="{w:.0f}" height="{h:.0f}" rx="{10*U:.0f}" fill="{MUC}" opacity="0.93" stroke="{DONG}" stroke-width="{3*U:.1f}"/>',
         f'<text x="{x0+22*U:.0f}" y="{y0+64*U:.0f}" font-family="Playfair Display" font-weight="800" font-size="{64*U:.0f}" fill="{DONG}">“</text>']
    for i, ln in enumerate(lines):
        o.append(f'<text x="{x0+62*U:.0f}" y="{y0+(56+i*34)*U:.0f}" font-family="Be Vietnam Pro" font-size="{22*U:.0f}" fill="{KEM}">{ln}</text>')
    o.append(f'<text x="{x0+w-24*U:.0f}" y="{y0+h-26*U:.0f}" font-family="Be Vietnam Pro" font-size="{16*U:.0f}" fill="{DONG}" text-anchor="end">— {nguon}</text>')
    if ma: o.append(flag(ma, side, x0 - 100 * U, y0 + h * 0.5 + 150 * U, 0.85, ten=ten))
    o.append('</g>'); return ''.join(o)

def clock(year, t, rot_u):
    """H11: vòng trống đồng quay NGƯỢC chiều kim đồng hồ, năm chạy."""
    cx, cy, r = W / 2, H / 2, 150 * U
    ticks = ''.join(f'<line x1="0" y1="{-r*0.8:.1f}" x2="0" y2="{-r*0.69:.1f}" stroke="{DONG}" stroke-width="{3*U:.1f}" transform="rotate({i*15})"/>' for i in range(24))
    birds = ''.join(f'<path d="M{-10*U:.1f},0 Q0,{-8*U:.1f} {10*U:.1f},0 Q0,{-3*U:.1f} {-10*U:.1f},0 Z" fill="{DONG2}" transform="rotate({i*60}) translate(0 {-r*0.93:.1f}) rotate(-90)"/>' for i in range(6))
    return (f'<g transform="translate({cx:.0f} {cy:.0f})"><circle r="{r:.1f}" fill="{MUC}" opacity="0.88" stroke="{DONG}" stroke-width="{4*U:.1f}"/>'
            f'<g transform="rotate({-360*rot_u:.1f})">{ticks}{birds}</g>'
            f'<text y="{24*U:.1f}" font-family="Playfair Display" font-weight="800" font-size="{72*U:.0f}" fill="{DONG2}" text-anchor="middle">{year}</text></g>')

def logo_card(a=1.0, sub=None):
    """Thẻ tên kênh / end card (logo trống đồng)."""
    p = os.path.join(ROOT, 'assets', 'brand', 'Avatar-NguocDongSuViet-800x800.png')
    if '_logo' not in STATE_C:
        import base64; STATE_C['_logo'] = 'data:image/png;base64,' + base64.b64encode(open(p, 'rb').read()).decode()
    s = 300 * U
    o = [f'<g opacity="{a:.2f}">', dim(0.75), f'<defs><clipPath id="lg"><circle cx="{W/2:.0f}" cy="{H*0.40:.0f}" r="{s*0.47:.0f}"/></clipPath></defs>',
         f'<image href="{STATE_C["_logo"]}" x="{(W-s)/2:.0f}" y="{H*0.40-s/2:.0f}" width="{s:.0f}" height="{s:.0f}" clip-path="url(#lg)"/>',
         f'<text x="{W/2:.0f}" y="{H*0.40+s/2+60*U:.0f}" font-family="Playfair Display" font-weight="800" font-size="{46*U:.0f}" fill="{DONG2}" text-anchor="middle" letter-spacing="{4*U:.0f}">NGƯỢC DÒNG SỬ VIỆT</text>']
    if sub: o.append(f'<text x="{W/2:.0f}" y="{H*0.40+s/2+110*U:.0f}" font-family="Be Vietnam Pro SemiBold" font-size="{28*U:.0f}" fill="{KEM}" text-anchor="middle">{sub}</text>')
    o.append('</g>'); return ''.join(o)
STATE_C = {}

def _uri(path):
    if path not in STATE_C:
        import base64; STATE_C[path] = 'data:image/png;base64,' + base64.b64encode(open(path, 'rb').read()).decode()
    return STATE_C[path]

def subscribe_card(t, avatar):
    """Màn hình kết: avatar kênh + thanh Thích · Không thích · ĐĂNG KÝ · Chuông; nút Thích và Đăng ký nhấp nháy."""
    cx = W / 2; pop = ease(min(1, t / 0.5)); sl = ease(min(1, max(0, (t - 0.3) / 0.5)))
    s = 230 * U * (0.6 + 0.4 * pop); ay = H * 0.33
    o = [f'<rect width="{W}" height="{H}" fill="{MUC}"/>',
         f'<defs><clipPath id="av"><circle cx="{cx:.0f}" cy="{ay:.0f}" r="{s/2:.0f}"/></clipPath></defs>',
         f'<image href="{_uri(avatar)}" x="{cx-s/2:.0f}" y="{ay-s/2:.0f}" width="{s:.0f}" height="{s:.0f}" clip-path="url(#av)" opacity="{pop:.2f}"/>']
    bw, bh = 560 * U, 104 * U; bx = cx - bw / 2; by = H * 0.6 + (1 - sl) * 60 * U
    o.append(f'<g opacity="{sl:.2f}"><rect x="{bx:.0f}" y="{by:.0f}" width="{bw:.0f}" height="{bh:.0f}" rx="{30*U:.0f}" fill="{KEM}" stroke="{DONG}" stroke-width="{4*U:.1f}"/>')
    def pulse(t0): return max(0, math.sin(max(0, t - t0) * 2 * math.pi * 1.2)) if t > t0 else 0
    pl, ps = pulse(1.0), pulse(1.6); ic = by + bh / 2
    # Thích
    lx = bx + 80 * U; lk = 1 + 0.22 * pl; lcol = '#2F7BEA' if t > 1.0 else '#3A3A3A'
    o.append(f'<g transform="translate({lx:.0f} {ic:.0f}) scale({U*lk:.3f})"><circle r="40" fill="#2F7BEA" opacity="{0.25*pl:.2f}"/>'
             f'<rect x="-22" y="-4" width="11" height="26" rx="3" fill="{lcol}"/><path d="M-8,-4 L2,-24 Q6,-32 12,-26 Q14,-20 10,-8 L22,-8 Q28,-7 26,0 L22,18 Q20,22 15,22 L-8,22 Z" fill="{lcol}"/></g>')
    # Không thích
    dx = bx + 175 * U
    o.append(f'<g transform="translate({dx:.0f} {ic:.0f}) scale({U:.3f}) rotate(180)"><rect x="-22" y="-4" width="11" height="26" rx="3" fill="#3A3A3A"/><path d="M-8,-4 L2,-24 Q6,-32 12,-26 Q14,-20 10,-8 L22,-8 Q28,-7 26,0 L22,18 Q20,22 15,22 L-8,22 Z" fill="#3A3A3A"/></g>')
    # ĐĂNG KÝ (nhấp nháy, đổi sang đỏ khi "bấm")
    sx = bx + 345 * U; sk = 1 + 0.12 * ps; on = t > 1.6
    o.append(f'<g transform="translate({sx:.0f} {ic:.0f}) scale({sk:.3f})"><rect x="{-115*U:.0f}" y="{-30*U:.0f}" width="{230*U:.0f}" height="{60*U:.0f}" rx="{30*U:.0f}" fill="{"#CC1F1A" if on else MUC}"/>'
             f'<rect x="{-100*U:.0f}" y="{-14*U:.0f}" width="{40*U:.0f}" height="{28*U:.0f}" rx="{8*U:.0f}" fill="#FFFFFF"/><polygon points="{-86*U:.0f},{-8*U:.0f} {-86*U:.0f},{8*U:.0f} {-71*U:.0f},0" fill="{"#CC1F1A" if on else MUC}"/>'
             f'<text x="{26*U:.0f}" y="{9*U:.0f}" font-family="Be Vietnam Pro SemiBold" font-size="{25*U:.0f}" fill="#FFFFFF" text-anchor="middle">{"ĐÃ ĐĂNG KÝ" if t > 3.2 else "ĐĂNG KÝ"}</text>'
             f'<rect x="{-122*U:.0f}" y="{-37*U:.0f}" width="{244*U:.0f}" height="{74*U:.0f}" rx="{37*U:.0f}" fill="none" stroke="#CC1F1A" stroke-width="{4*U:.1f}" opacity="{0.8*ps:.2f}"/></g>')
    # Chuông (lắc nhẹ sau khi đăng ký)
    bxl = bx + bw - 62 * U; wob = 18 * math.sin(t * 18) * max(0, 1 - abs(t - 3.6) * 2) if t > 3.2 else 0
    o.append(f'<g transform="translate({bxl:.0f} {ic:.0f}) rotate({wob:.1f} 0 {-26*U:.0f}) scale({U:.3f})"><path d="M-18,12 Q-18,-20 0,-22 Q18,-20 18,12 L24,18 L-24,18 Z" fill="#2A2A2A"/><circle cy="24" r="6" fill="#2A2A2A"/><rect x="-3" y="-30" width="6" height="8" rx="2" fill="#2A2A2A"/></g>')
    o.append('</g>')
    return ''.join(o)

def saban(level, stakes_up=1.0, boats=(), x0=None, y0=None, w=None, h=None, show_stakes=True):
    """Sa bàn mặt cắt cửa sông (minh họa). level 1 = nước lên, 0 = nước rút; stakes_up 0–1 = cọc đang được cắm."""
    x0 = 140 * U if x0 is None else x0; y0 = 70 * U if y0 is None else y0; w = 680 * U if w is None else w; h = 400 * U if h is None else h
    k = h / (400 * U); bed = y0 + h - 60 * U * k
    o = [f'<rect x="{x0:.0f}" y="{y0:.0f}" width="{w:.0f}" height="{h:.0f}" fill="{KEM}" stroke="{DONG}" stroke-width="{4*U:.1f}" rx="{10*U:.0f}"/>',
         f'<rect x="{x0:.0f}" y="{bed:.0f}" width="{w:.0f}" height="{60*U*k:.0f}" fill="#8A6A44"/>']
    wl = bed - lerp(90, 270, level) * U * k
    o.append(f'<rect x="{x0:.0f}" y="{wl:.1f}" width="{w:.0f}" height="{bed-wl:.1f}" fill="#3A7CA5" opacity="0.8"/>')
    top = bed - 190 * U * k; n = max(3, int(w / (62 * U * k)) - 1)
    if show_stakes:
        for i in range(n):
            sx = x0 + (w - (n - 1) * 62 * U * k) / 2 + i * 62 * U * k
            up = max(0, min(1, stakes_up * n * 0.9 - i * 0.8)); dy = (1 - up) * -260 * U * k
            if up <= 0: continue
            tt = top + dy if stakes_up < 1 else top
            o.append(f'<g opacity="{min(1, up*2):.2f}"><polygon points="{sx-10*U*k:.1f},{bed+14*U*k+dy:.1f} {sx+10*U*k:.1f},{bed+14*U*k+dy:.1f} {sx+10*U*k:.1f},{tt+24*U*k:.1f} {sx:.1f},{tt:.1f} {sx-10*U*k:.1f},{tt+24*U*k:.1f}" fill="#6A4428" stroke="#1E120A" stroke-width="{2*U:.1f}"/>'
                     f'<polygon points="{sx-10*U*k:.1f},{tt+24*U*k:.1f} {sx:.1f},{tt:.1f} {sx+10*U*k:.1f},{tt+24*U*k:.1f}" fill="#C8CED2"/></g>')
    for bx, side, tilt in boats:
        X = x0 + w * bx; by = min(wl, top + 6 * U * k) - 2 * U
        o.append(f'<g transform="rotate({tilt:.1f} {X:.1f} {by:.1f})">{L.boat(X, by, 0 if side is TA else 180, side, 2.0 * k)}</g>')
    o.append(f'<rect x="{x0:.0f}" y="{wl:.1f}" width="{w:.0f}" height="{bed-wl:.1f}" fill="#2F6E96" opacity="0.55"/>')
    return ''.join(o)

# ---------------- Đọc lời đọc + mốc thời gian ----------------
def read_script(path):
    out, scene, pause = [], None, (0.0, None)
    for raw in open(path, encoding='utf-8'):
        t = raw.strip()
        m = re.match(r'#\s*(s\d\d)\b', t); p = re.match(r'#\s*lặng\s*([\d.]+)\s*(s\d\d)?', t)
        if m: scene = m.group(1)
        elif p: pause = (float(p.group(1)), p.group(2))
        elif t and not t.startswith('#'): out.append((scene, t, pause)); pause = (0.0, None)
    return out

def timeline(items, meta=None, tail=0.8):
    if meta: base = [(x['start'], x['end']) for x in meta['lines']]
    else:
        base, t = [], 0.3
        for _, txt, _ in items:
            d = len(txt.split()) * 0.36 + 0.3; base.append((t, t + d)); t += d + 0.35
    shift, res, pauses = 0.0, [], []
    for (a, b), (_, _, (p, sc)) in zip(base, items):
        if p: pauses.append((a + shift, p, sc)); shift += p
        res.append((a + shift, b + shift))
    end = (meta['duration'] if meta else base[-1][1] + 0.3) + shift + tail
    return res, pauses, end

def plan_scenes(items, times, pauses, end):
    seq = []
    for (sc, _, _), (a, _) in zip(items, times):
        if not seq or seq[-1][0] != sc: seq.append([sc, max(0.0, a - 0.15)])
    for t0, p, sc in pauses:
        if not sc: continue
        k = next(i for i, s in enumerate(seq) if s[1] >= t0 - 0.2)
        seq.insert(k, [sc, t0 - (0.3 if k == 0 else 0)]); seq[k + 1][1] = t0 + p - 0.15
    seq[0][1] = 0.0
    return [(sc, a, (seq[i + 1][1] if i + 1 < len(seq) else end)) for i, (sc, a) in enumerate(seq)]

# ---------------- Render ----------------
EP = None
def frame(code, tl, d):
    STATE.clear()
    svg = f'<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{H}">{EP.SCENES[code](tl, d)}</svg>'
    ov = Image.open(io.BytesIO(cairosvg.svg2png(bytestring=svg.encode()))).convert('RGBA')
    fr = _bg_image()
    as_name = ANH_SANG or getattr(EP, 'ANH_SANG', None)
    if as_name: fr = AS.ap_dung(fr, ov, as_name, U).convert('RGBA')
    else: fr.alpha_composite(ov)
    fade = getattr(EP, 'FADE', {}).get(code)
    if fade:
        fa = min(1, tl / fade[0] if fade[0] else 1, (d - tl) / fade[1] if fade[1] else 1)
        if fa < 1: fr = Image.blend(Image.new('RGBA', (W, H), (20, 17, 15, 255)), fr, max(0, fa))
    return fr.convert('RGB')

def render_scene(job):
    code, a, b, out = job; d = b - a; tmp = out + '.tmp.mp4'
    p = subprocess.Popen(['ffmpeg', '-y', '-loglevel', 'error', '-f', 'rawvideo', '-pix_fmt', 'rgb24', '-s', f'{W}x{H}', '-r', str(FPS), '-i', '-',
                          '-c:v', 'libx264', '-pix_fmt', 'yuv420p', '-preset', 'veryfast' if L.FINAL else 'ultrafast', '-crf', '18' if L.FINAL else '26',
                          '-threads', '1', tmp], stdin=subprocess.PIPE)
    prev_svg, prev = None, None
    for i in range(round(d * FPS)):              # số khung chỉ theo độ dài cảnh → clip cache dùng lại được khi cảnh bị dời
        tl = i / FPS
        STATE.clear(); svg = EP.SCENES[code](tl, d); key = (svg, repr(STATE.get('bg')))
        if key == prev_svg and not getattr(EP, 'FADE', {}).get(code):   # khung tĩnh → dùng lại
            p.stdin.write(prev); continue
        prev = frame(code, tl, d).tobytes(); prev_svg = key; p.stdin.write(prev)
    p.stdin.close(); p.wait(); os.replace(tmp, out)
    return f'{code} ok {d:.1f}s'

def main():
    global EP
    args = [a for a in sys.argv[1:] if not a.startswith('--')]
    sys.modules['dung'] = sys.modules[__name__]          # để tap/*.py dùng chung trạng thái với bộ máy
    EP = importlib.import_module('tap.' + args[0])
    items = read_script(args[1]); tail = getattr(EP, 'TAIL', 0.8)
    out_dir = os.path.join(ROOT, 'build', args[0]); os.makedirs(out_dir, exist_ok=True)
    stills = next((a for a in sys.argv if a.startswith('--stills')), None)
    if stills:
        times, pauses, end = timeline(items, tail=tail)
        pick = stills.split('=', 1)[1].split(',') if '=' in stills else None
        sd = os.path.join(out_dir, 'stills'); os.makedirs(sd, exist_ok=True)
        for code, a, b in plan_scenes(items, times, pauses, end):
            if pick and code not in pick: continue
            frame(code, (b - a) * 0.7, b - a).save(os.path.join(sd, f'{code}.png')); print(code, f'{b-a:.1f}s')
        print(f'Tổng ước {end/60:.1f} phút'); return
    voice = args[2]; meta = json.load(open(voice + '.json'))
    assert len(meta['lines']) == len(items), f'Số câu trong {voice}.json ({len(meta["lines"])}) khác file lời đọc ({len(items)}) – tạo lại giọng'
    times, pauses, end = timeline(items, meta, tail)
    plan = plan_scenes(items, times, pauses, end)
    # Cache theo NỘI DUNG từng cảnh: thư viện dùng chung + phần chung của file tập + hàm của riêng cảnh đó + độ dài cảnh.
    # Không tính giờ bắt đầu → dời/cắt câu không làm render lại cảnh có hình y nguyên; sửa 1 cảnh chỉ render cảnh đó.
    import inspect
    as_name = ANH_SANG or getattr(EP, 'ANH_SANG', None)
    shared = b''.join(open(f, 'rb').read() for f in (__file__, L.__file__, NV.__file__) + tuple(getattr(EP, 'DEPS', ())))
    if as_name: shared += open(AS.__file__, 'rb').read() + as_name.encode()
    ep_src = open(EP.__file__, encoding='utf-8').read(); fn_src = {}
    for c, f in EP.SCENES.items():
        try: fn_src[c] = inspect.getsource(f)
        except (OSError, TypeError): fn_src[c] = c
    ep_common = ep_src
    for t in fn_src.values(): ep_common = ep_common.replace(t, '')
    ep_common = ep_common.split('# ---------------- SHORT')[0]     # phần cấu hình Short không ảnh hưởng hình video dài
    def scene_key(c, d): return hashlib.sha1(shared + ep_common.encode() + fn_src[c].encode() + f'{c}{d:.2f}{W}{FPS}'.encode()).hexdigest()[:12]
    cd = os.path.join(out_dir, 'clips'); os.makedirs(cd, exist_ok=True)
    jobs = [(c, a, b, os.path.join(cd, f'{c}-{W}p{FPS}-{scene_key(c, b - a)}.mp4')) for c, a, b in plan]
    todo = [j for j in jobs if not os.path.exists(j[3])]
    print(f'{len(jobs)} cảnh · {len(jobs)-len(todo)} dùng lại cache · render {len(todo)} · {W}x{H} {FPS}fps · dài {end/60:.1f} phút', flush=True)
    import multiprocessing as mp           # 'fork' để tiến trình con giữ EP (Mac mặc định 'spawn')
    with mp.get_context('fork').Pool(min(4, os.cpu_count())) as pool:
        import time; t0 = time.time(); tot = sum(j[2] - j[1] for j in todo) or 1; done = 0.0; n = 0
        prog = os.path.join(out_dir, 'tien-do.txt')
        for msg in pool.imap_unordered(render_scene, sorted(todo, key=lambda j: -(j[2] - j[1]))):
            n += 1; done += float(msg.split()[-1][:-1]); f = done / tot; el = time.time() - t0
            eta = el / f * (1 - f) if f > 0 else 0
            bar = '█' * int(f * 20) + '░' * (20 - int(f * 20))
            line = f'Render {bar} {f*100:3.0f}%  ({n}/{len(todo)} cảnh)  đã {el/60:.1f} phút · còn ~{eta/60:.1f} phút  [{msg}]'
            print(line, flush=True); open(prog, 'w').write(line + '\n')
    lst = os.path.join(out_dir, 'list.txt'); open(lst, 'w').write(''.join(f"file '{j[3]}'\n" for j in jobs))
    hinh = os.path.join(out_dir, 'hinh.mp4')
    subprocess.run(['ffmpeg', '-y', '-loglevel', 'error', '-f', 'concat', '-safe', '0', '-i', lst, '-c', 'copy', hinh], check=True)
    v = AT.load_audio(voice + '.mp3'); segs, prev = [], 0
    for k, (t0, p, _) in enumerate(pauses):
        orig = t0 - sum(pp for _, pp, _ in pauses[:k]); cut = int(orig * AT.SR)
        segs += [v[prev:cut], np.zeros(int(p * AT.SR))]; prev = cut
    segs.append(v[prev:]); vo = np.concatenate(segs)
    sfx = getattr(EP, 'SFX', lambda c, d: [])
    events = [(a + t, nm, g, dd) for c, a, b in plan for t, nm, g, dd in sfx(c, b - a)]
    wav = os.path.join(out_dir, 'tieng.wav'); AT.write_wav(AT.mix(vo, events, end), wav)
    name = os.path.join(out_dir, f'{args[0].upper()}-' + (f'1080p{FPS}' if L.FINAL else 'nhap') + '.mp4')
    subprocess.run(['ffmpeg', '-y', '-loglevel', 'error', '-i', hinh, '-i', wav, '-map', '0:v', '-map', '1:a', '-c:v', 'copy',
                    '-c:a', 'aac', '-b:a', '192k', '-shortest', '-movflags', '+faststart', name], check=True)
    print('->', name, f'{end/60:.1f} phút')

if __name__ == '__main__':
    main()
