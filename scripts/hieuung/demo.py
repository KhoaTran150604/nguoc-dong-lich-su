"""Demo thư viện hiệu ứng H1–H12 (bản nháp 16:9, chất lượng thấp).

Cách chạy (từ thư mục làm việc có map_big.png do bandoco/build.py tạo ra):
    python3 demo.py [--final] [H1 H3 ...]
Mỗi hiệu ứng là một clip riêng trong clips/, có cache theo nội dung: chỉ render lại khi
code hoặc tham số thay đổi. Cuối cùng nối lại bằng concat (-c copy).
"""
import hashlib, io, math, os, subprocess, sys
import cairosvg
from PIL import Image

Image.MAX_IMAGE_PIXELS = None
FINAL = '--final' in sys.argv
W, H, FPS = (1920, 1080, 30) if FINAL else (960, 540, 15)
DUR = 3.6
COS = math.cos(math.radians(21)); LON0, LAT0, S0 = 102.0, 26.5, 260.0
def pj(lon, lat): return ((lon - LON0) * COS * S0, (LAT0 - lat) * S0)
def ease(x): x = max(0, min(1, x)); return x * x * (3 - 2 * x)
def seg(t, a, b): return ease((t - a) / (b - a))
def lerp(a, b, u): return a + (b - a) * u

# ---- Màu nhận diện ----
MUC, DONG, DONG2, DO, KEM = '#14110F', '#C9A24A', '#F3D27A', '#B3261E', '#F2E6CC'
TA = ('#D9B44A', '#5A3A10')      # phe ta: vàng đồng
DICH = ('#A8382A', '#4A1410')    # phe địch: đỏ

BIG = Image.open('map_big.png').convert('RGB')
CAM = (106.45, 21.0, 900.0)      # tâm lon, lat, bề rộng khung (đơn vị bản đồ)

def base_frame(cam=CAM):
    cx, cy = pj(cam[0], cam[1]); vw = cam[2]; vh = vw * H / W
    box = (int(cx - vw / 2), int(cy - vh / 2), int(cx + vw / 2), int(cy + vh / 2))
    return BIG.crop(box).resize((W, H), Image.LANCZOS)

K = W / CAM[2]                    # px màn hình / đơn vị bản đồ
U = W / 960                       # hệ số theo độ phân giải
def sc(lon, lat, cam=CAM):
    bx, by = pj(lon, lat); cx, cy = pj(cam[0], cam[1])
    return W / 2 + (bx - cx) * K, H / 2 + (by - cy) * K

def path_at(pts, u):
    if u <= 0: return pts[0]
    L = [math.dist(pts[i], pts[i + 1]) for i in range(len(pts) - 1)]; d = u * sum(L)
    for i, l in enumerate(L):
        if d <= l: f = d / l; return (lerp(pts[i][0], pts[i + 1][0], f), lerp(pts[i][1], pts[i + 1][1], f))
        d -= l
    return pts[-1]

# ---- Thư viện ký hiệu ----
def banner(x, y, name, side, s=0.42, tilt=0, op=1.0, grey=0.0, outline=0.0, img=None):
    """Cờ tướng. img = data URI chân dung (scripts/video/nhanvat.py); không có thì vẽ hình bóng người."""
    col, dark = side
    if grey > 0:
        g = lambda c: '#%02x%02x%02x' % tuple(int(lerp(int(c[i:i+2], 16), 0x80, grey)) for i in (1, 3, 5))
        col, dark = g(col), g(dark)
    s *= U
    o = [f'<g transform="translate({x:.1f} {y:.1f}) rotate({tilt:.1f}) scale({s:.3f})" opacity="{op:.2f}">',
         '<ellipse cx="0" cy="4" rx="34" ry="10" fill="#000" opacity="0.35"/>',
         '<line x1="0" y1="0" x2="0" y2="-300" stroke="#3A2618" stroke-width="8"/><polygon points="-9,-300 0,-326 9,-300" fill="#C8C8C8"/>',
         '<line x1="-78" y1="-268" x2="78" y2="-268" stroke="#3A2618" stroke-width="7"/>',
         f'<rect x="-70" y="-266" width="140" height="190" fill="{col}" stroke="{dark}" stroke-width="5"/>',
         f'<rect x="-70" y="-266" width="140" height="40" fill="{KEM}" stroke="{dark}" stroke-width="4"/>',
         f'<text x="0" y="-238" font-family="Be Vietnam Pro SemiBold" font-size="{min(22, 200/max(1,len(name))):.1f}" fill="#2A1A10" text-anchor="middle">{name}</text>',
         (f'<svg x="-64" y="-224" width="128" height="144" viewBox="0 0 90 100" preserveAspectRatio="xMidYMid slice"><image href="{img}" width="90" height="100" preserveAspectRatio="xMidYMid slice"/></svg>'
          f'<rect x="-64" y="-224" width="128" height="144" fill="#808080" opacity="{0.75*grey:.2f}"/><rect x="-64" y="-224" width="128" height="144" fill="none" stroke="{dark}" stroke-width="3"/>'
          if img else
          f'<g transform="translate(0 -150)"><circle cx="0" cy="0" r="34" fill="{dark}"/><path d="M-40,-4 Q0,-62 40,-4 L32,-2 Q0,-46 -32,-2 Z" fill="{dark}"/><rect x="-46" y="34" width="92" height="36" rx="12" fill="{dark}"/></g>'),
         f'<polygon points="-70,-76 70,-76 0,-56" fill="{col}" stroke="{dark}" stroke-width="4"/>']
    if outline > 0:
        o.append(f'<rect x="-80" y="-276" width="160" height="230" fill="none" stroke="{DONG2}" stroke-width="10" opacity="{outline:.2f}"/>')
    o.append('</g>'); return ''.join(o)

def trail(pts, u, col, dash=True):
    n = 40; pp = [sc(*path_at(pts, u * i / n)) for i in range(n + 1)]
    da = f'stroke-dasharray="{8*U:.0f} {7*U:.0f}"' if dash else ''
    return f'<polyline points="{" ".join(f"{x:.1f},{y:.1f}" for x, y in pp)}" fill="none" stroke="{col}" stroke-width="{4*U:.1f}" {da} stroke-linecap="round" opacity="0.9"/>'

def boat(x, y, ang, side, s=1.0):
    """Thuyền gỗ nhìn ngang, buồm cánh dơi; ang chỉ để biết hướng (trái/phải) và độ nghiêng nhỏ."""
    col, dark = side; s *= U
    flip = -1 if math.cos(math.radians(ang)) < 0 else 1
    tilt = ang if abs(ang) < 45 else 0
    battens = ''.join(f'<line x1="4" y1="{yy}" x2="{24 + (yy+44)*0.05:.1f}" y2="{yy+1}" stroke="{dark}" stroke-width="1.2"/>' for yy in (-36, -28, -20, -12))
    return (f'<g transform="translate({x:.1f} {y:.1f}) rotate({tilt:.1f}) scale({flip*s:.2f} {s:.2f})">'
            f'<path d="M-40,-6 Q-36,8 -26,12 L28,12 Q38,8 46,-10 L40,-4 L-30,-2 Z" fill="#6A4428" stroke="#2A1A10" stroke-width="2"/>'
            f'<line x1="-30" y1="3" x2="38" y2="3" stroke="#3A2618" stroke-width="1.5"/>'
            f'<line x1="2" y1="-2" x2="2" y2="-48" stroke="#2A1A10" stroke-width="2.5"/>'
            f'<path d="M4,-46 Q18,-48 26,-42 L28,-6 L4,-6 Z" fill="{col}" stroke="{dark}" stroke-width="1.8"/>{battens}'
            f'<line x1="-20" y1="-2" x2="-20" y2="-30" stroke="#2A1A10" stroke-width="2"/>'
            f'<path d="M-18,-28 L-6,-25 L-6,-6 L-18,-6 Z" fill="{col}" stroke="{dark}" stroke-width="1.5"/>'
            f'<polygon points="2,-48 2,-56 12,-52" fill="{DO}"/></g>')

def sword(ang, s):
    """Kiếm dựng đứng, gốc ở chuôi (0,0); xoay quanh chuôi."""
    return (f'<g transform="rotate({ang:.1f}) scale({s:.2f})">'
            f'<polygon points="-5,-14 5,-14 4,-120 0,-132 -4,-120" fill="#D8DDE0" stroke="#3A3A3A" stroke-width="1.5"/>'
            f'<line x1="0" y1="-16" x2="0" y2="-118" stroke="#9AA2A6" stroke-width="1.5"/>'
            f'<rect x="-18" y="-16" width="36" height="7" rx="3" fill="{DONG}" stroke="#5A3A10" stroke-width="1.5"/>'
            f'<rect x="-4" y="-9" width="8" height="24" fill="#3A2618"/><circle cx="0" cy="18" r="5" fill="{DONG}" stroke="#5A3A10" stroke-width="1.5"/></g>')

def city(x, y, s=1.0):
    s *= U
    return (f'<g transform="translate({x:.1f} {y:.1f}) scale({s:.2f})"><rect x="-22" y="-18" width="44" height="26" fill="#C8A878" stroke="#3A2618" stroke-width="3"/>'
            f'<polygon points="-26,-18 0,-38 26,-18" fill="#8A3A24" stroke="#3A2618" stroke-width="3"/></g>')

def mountain(x, y, s=1.0):
    s *= U
    return (f'<g transform="translate({x:.0f} {y:.0f}) scale({s:.2f})"><polygon points="-40,20 0,-34 40,20" fill="#A88A62" stroke="#5A3A20" stroke-width="3"/>'
            f'<polygon points="0,-34 40,20 8,20" fill="#7A5E40"/><polygon points="-10,-20 0,-34 10,-20 4,-16 -4,-18" fill="{KEM}"/></g>')

def tree(x, y, s=1.0):
    s *= U
    return f'<g transform="translate({x:.0f} {y:.0f}) scale({s:.2f})"><line x1="0" y1="0" x2="0" y2="16" stroke="#4A3220" stroke-width="4"/><circle cx="0" cy="-4" r="13" fill="#5E7A44" stroke="#3A4A2A" stroke-width="2"/></g>'

def flame(x, y, s, t, seed):
    f = 1 + 0.18 * math.sin(t * 14 + seed * 2.3); s *= U
    return (f'<g transform="translate({x:.1f} {y:.1f}) scale({s:.2f} {s*f:.2f})">'
            f'<path d="M0,0 C-14,-6 -12,-22 0,-40 C12,-22 14,-6 0,0 Z" fill="#D2541E" opacity="0.92"/>'
            f'<path d="M0,0 C-7,-4 -6,-14 0,-26 C6,-14 7,-4 0,0 Z" fill="{DONG2}"/></g>')

def burst(x, y, u):
    """H3 – dấu va chạm đỏ sơn mài + vòng sóng đồng."""
    o = []
    for k in range(3):
        r = (u * 3 - k)
        if 0 < r < 1.6:
            o.append(f'<circle cx="{x:.1f}" cy="{y:.1f}" r="{(20 + 70*r)*U:.1f}" fill="none" stroke="{DONG}" stroke-width="{(6 - 3*r)*U:.1f}" opacity="{max(0, 1 - r/1.6):.2f}"/>')
    pulse = 1 + 0.15 * math.sin(u * math.pi * 6)
    star = ' '.join(f'{x + math.cos(a)*rr*U*pulse:.1f},{y + math.sin(a)*rr*U*pulse:.1f}'
                    for i in range(16) for a, rr in [(i * math.pi / 8, 34 if i % 2 == 0 else 14)])
    o.append(f'<polygon points="{star}" fill="{DO}" stroke="{MUC}" stroke-width="{2*U:.1f}"/>')
    return ''.join(o)

def xmark(x, y, u):
    a = min(1, u * 2); b = max(0, min(1, u * 2 - 1)); r = 60 * U
    o = f'<line x1="{x-r:.1f}" y1="{y-r:.1f}" x2="{x-r+2*r*a:.1f}" y2="{y-r+2*r*a:.1f}" stroke="{DO}" stroke-width="{16*U:.1f}" stroke-linecap="round"/>'
    if b > 0: o += f'<line x1="{x+r:.1f}" y1="{y-r:.1f}" x2="{x+r-2*r*b:.1f}" y2="{y-r+2*r*b:.1f}" stroke="{DO}" stroke-width="{16*U:.1f}" stroke-linecap="round"/>'
    return o

# ---- Địa điểm (minh họa) ----
DAILA = (105.85, 21.03); BD = (106.82, 20.86)
LAND_PATH = [DAILA, (106.15, 21.05), (106.45, 21.0), (106.68, 20.92)]
SEA_PATH = [(108.2, 20.45), (107.6, 20.6), (107.15, 20.72), BD]

# ---- 12 hiệu ứng: hàm trả về SVG lớp phủ tại thời điểm t ----
def H1(t):
    u = seg(t, 0.4, 3.0); x, y = sc(*path_at(LAND_PATH, u))
    return banner(x, y, 'NGÔ QUYỀN', TA)

def H2(t):
    u = seg(t, 0.3, 3.2); o = []
    for i, lag in enumerate([0.0, 0.07, 0.13]):
        p = path_at(SEA_PATH, max(0, u - lag)); x, y = sc(*p)
        x += (0, 18, -14)[i] * U; y += (0, 26, -24)[i] * U
        for k in range(3):   # gợn sóng sau đuôi thuyền (thuyền đi sang trái → sóng bên phải)
            r = (t * 1.5 + k / 3) % 1
            o.append(f'<path d="M{x + (40 + 30*r)*U:.1f},{y + (10 - 8*r)*U:.1f} q{6*U:.1f},{4*U:.1f} {12*U:.1f},0" fill="none" stroke="#E8F0F2" stroke-width="{2*U:.1f}" opacity="{0.8*(1-r):.2f}"/>')
        o.append(boat(x, y, 170, DICH, 0.9))
    return ''.join(o)

def H3(t):
    """Giao chiến: hai cờ áp sát, hai kiếm chém vào nhau, lửa bùng phía dưới."""
    u = seg(t, 0.2, 1.2); ax, ay = sc(lerp(106.0, 106.25, u), 21.0); bx, by = sc(lerp(106.9, 106.65, u), 21.0)
    o = [banner(ax, ay, 'NGÔ QUYỀN', TA), banner(bx, by, 'HOẰNG THÁO', DICH)]
    if t > 1.0:
        cx, cy = (ax + bx) / 2, ay - 20 * U
        g = seg(t, 1.0, 1.5); f = min(1, (t - 1.0) / 0.5)
        for i in range(7):   # lửa
            fx = cx + (i - 3) * 13 * U; sz = (1.3 - abs(i - 3) * 0.16) * f
            o.append(flame(fx, cy + 6 * U, sz, t, i))
        hit = t - 1.5
        shake = 4 * math.sin(t * 40) * max(0, 1 - hit * 2) if hit > 0 else 0
        o.append(f'<g transform="translate({cx:.1f} {cy:.1f})">')
        o.append(f'<g transform="translate({-26*U:.1f} 0)">{sword(lerp(-75, 32, g) + shake, 1.1*U)}</g>')
        o.append(f'<g transform="translate({26*U:.1f} 0)">{sword(lerp(75, -32, g) - shake, 1.1*U)}</g>')
        if 0 < hit < 0.6:   # tia lóe lúc chạm kiếm
            a = 1 - hit / 0.6
            o.append(f'<circle cx="0" cy="{-90*U:.1f}" r="{(12 + 36*hit)*U:.1f}" fill="{DONG2}" opacity="{0.85*a:.2f}"/>')
        o.append('</g>')
    return ''.join(o)

def H4(t):
    x, y = sc(*DAILA); u = seg(t, 1.2, 3.0); r = 150 * U * u
    o = [f'<defs><clipPath id="c"><circle cx="{x:.1f}" cy="{y:.1f}" r="{r:.1f}"/></clipPath></defs>',
         f'<circle cx="{x:.1f}" cy="{y:.1f}" r="{150*U:.1f}" fill="{DICH[0]}" opacity="0.35"/>',
         f'<circle cx="{x:.1f}" cy="{y:.1f}" r="{150*U:.1f}" fill="{TA[0]}" opacity="0.6" clip-path="url(#c)"/>',
         city(x, y, 1.4)]
    d = seg(t, 0.3, 1.1); bounce = math.sin(min(1, max(0, (t - 1.1) / 0.4)) * math.pi) * 8 * U
    o.append(banner(x + 6*U, y - 30*U - (1 - d) * 160*U - bounce, 'NGÔ QUYỀN', TA, 0.36, op=d))
    return ''.join(o)

def H5(t):
    x, y = sc(106.6, 20.95)
    o = banner(x, y, 'HOẰNG THÁO', DICH, op=1 - 0.4*seg(t, 1.2, 2.0))
    if t > 0.8: o += xmark(x, y - 75*U, (t - 0.8) / 1.2)
    return o

def H6(t):
    path = [(106.45, 21.0), (106.75, 20.92), (107.1, 20.78)]
    u = seg(t, 0.6, 3.2); x, y = sc(*path_at(path, u))
    return banner(x, y, 'HOẰNG THÁO', DICH, tilt=-18*seg(t, 0.2, 0.7), op=1 - 0.85*seg(t, 1.8, 3.4))

def H7(t):
    """Phục binh: cờ nhỏ lấp ló sau núi rừng, rồi cờ tướng hiện ra."""
    cx, cy = sc(106.3, 21.15); o = []
    for j, (dx, dy) in enumerate([(-100, -20), (-60, -45), (-15, -40), (25, -30), (65, -42), (110, -18), (-80, 20), (90, 15)]):
        a = seg(t, 0.3 + j * 0.12, 0.7 + j * 0.12); sway = 3 * math.sin(t * 5 + j)
        if a > 0:
            px, py = cx + dx * U, cy + dy * U
            o.append(f'<g opacity="{a:.2f}" transform="translate({px:.1f} {py + (1-a)*12*U:.1f})">'
                     f'<line x1="0" y1="0" x2="0" y2="{-34*U:.1f}" stroke="#3A2618" stroke-width="{2*U:.1f}"/>'
                     f'<path d="M0,{-34*U:.1f} L{(18+sway)*U:.1f},{-28*U:.1f} L0,{-20*U:.1f} Z" fill="{TA[0]}" stroke="{TA[1]}" stroke-width="{1.2*U:.1f}"/></g>')
    for dx, dy, k in [(-90, 10, 'm'), (-40, -25, 'm'), (30, 5, 'm'), (85, -15, 'm'), (-70, 50, 't'), (-20, 40, 't'), (20, 55, 't'), (60, 45, 't'), (105, 35, 't')]:
        o.append(mountain(cx + dx*U, cy + dy*U, 0.9) if k == 'm' else tree(cx + dx*U, cy + dy*U))
    a = seg(t, 1.4, 2.2); flash = math.sin(min(1, max(0, (t - 2.2) / 0.6)) * math.pi)
    o.append(banner(cx, cy + 40*U, 'PHỤC BINH', TA, op=a, outline=flash))
    return ''.join(o)

def H8(t):
    x, y = sc(106.6, 20.95); fall = seg(t, 0.8, 1.8)
    return banner(x, y, 'TƯỚNG ĐỊCH', DICH, tilt=80 * fall, grey=seg(t, 1.6, 2.6))

def H9(t):
    o = []; pts = [(106.95, 20.78), (107.05, 20.83), (107.0, 20.72), (107.12, 20.75), (106.9, 20.7)]
    for i, p in enumerate(pts):
        x, y = sc(*p); o.append(boat(x, y, 170, DICH, 1.2))
        a = seg(t, 0.4 + i * 0.45, 0.9 + i * 0.45)
        if a > 0: o.append(f'<g opacity="{a:.2f}">' + flame(x - 4*U, y - 4*U, 0.9 * a, t, i) + flame(x + 10*U, y - 2*U, 0.6 * a, t, i + 5) + '</g>')
    return ''.join(o)

def H10(t):
    """Thủy triều – khung sa bàn mặt cắt nhỏ trên bản đồ."""
    lv = seg(t, 0.2, 1.4) - seg(t, 2.0, 3.2)   # 0 → 1 → 0
    x0, y0, w, h = 560*U, 80*U, 360*U, 250*U; bed = y0 + h - 40*U
    o = [f'<rect x="{x0:.0f}" y="{y0:.0f}" width="{w:.0f}" height="{h:.0f}" fill="{KEM}" stroke="{DONG}" stroke-width="{4*U:.1f}" rx="{8*U:.0f}"/>',
         f'<rect x="{x0:.0f}" y="{bed:.0f}" width="{w:.0f}" height="{40*U:.0f}" fill="#8A6A44"/>']
    wl = bed - lerp(60, 170, lv) * U
    o.append(f'<rect x="{x0:.0f}" y="{wl:.1f}" width="{w:.0f}" height="{bed-wl:.1f}" fill="#3A7CA5" opacity="0.75"/>')
    for i in range(6):
        sx = x0 + (60 + i * 48) * U
        o.append(f'<polygon points="{sx-7*U:.1f},{bed+10*U:.1f} {sx+7*U:.1f},{bed+10*U:.1f} {sx+7*U:.1f},{bed-90*U:.1f} {sx:.1f},{bed-110*U:.1f} {sx-7*U:.1f},{bed-90*U:.1f}" fill="#6A4428" stroke="#2A1A10" stroke-width="{1.5*U:.1f}"/>')
        o.append(f'<polygon points="{sx-7*U:.1f},{bed-90*U:.1f} {sx:.1f},{bed-110*U:.1f} {sx+7*U:.1f},{bed-90*U:.1f}" fill="#C8CED2"/>')
    o.append(boat(x0 + w/2, min(wl, bed - 110*U) - 2*U, 0 if t < 2.6 else -12, DICH, 1.6))   # nước rút: thuyền mắc cọc
    o.append(f'<text x="{x0+w/2:.0f}" y="{y0+26*U:.0f}" font-family="Be Vietnam Pro SemiBold" font-size="{18*U:.0f}" fill="{MUC}" text-anchor="middle">{"NƯỚC LÊN · CỌC CHÌM" if t < 2.0 else "NƯỚC RÚT · THUYỀN MẮC CỌC"}</text>')
    o.append(f'<rect x="{x0:.0f}" y="{wl:.1f}" width="{w:.0f}" height="{bed-wl:.1f}" fill="#3A7CA5" opacity="0.35"/>')
    return ''.join(o)

def H11(t):
    yr = int(round(lerp(1976, 938, seg(t, 0.2, 3.0)))); cx, cy = W/2, H/2
    rot = -360 * seg(t, 0.2, 3.0)    # ngược chiều kim đồng hồ
    ticks = ''.join(f'<line x1="0" y1="{-120*U:.1f}" x2="0" y2="{-104*U:.1f}" stroke="{DONG}" stroke-width="{3*U:.1f}" transform="rotate({i*15})"/>' for i in range(24))
    birds = ''.join(f'<path d="M{-10*U:.1f},0 Q0,{-8*U:.1f} {10*U:.1f},0 Q0,{-3*U:.1f} {-10*U:.1f},0 Z" fill="{DONG2}" transform="rotate({i*60}) translate(0 {-140*U:.1f}) rotate(-90)"/>' for i in range(6))
    return (f'<rect width="{W}" height="{H}" fill="{MUC}" opacity="0.55"/>'
            f'<g transform="translate({cx} {cy})"><circle r="{150*U:.1f}" fill="{MUC}" opacity="0.85" stroke="{DONG}" stroke-width="{4*U:.1f}"/>'
            f'<g transform="rotate({rot:.1f})">{ticks}{birds}</g>'
            f'<text y="{22*U:.1f}" font-family="Playfair Display" font-weight="800" font-size="{68*U:.0f}" fill="{DONG2}" text-anchor="middle">{yr}</text></g>')

def H12(t):
    a = seg(t, 0.2, 0.8); x0, y0, w = W - 470*U, 330*U, 440*U
    return (f'<g opacity="{a:.2f}"><rect x="{x0:.0f}" y="{y0:.0f}" width="{w:.0f}" height="{150*U:.0f}" fill="{MUC}" opacity="0.9" stroke="{DONG}" stroke-width="{3*U:.1f}" rx="{8*U:.0f}"/>'
            f'<text x="{x0+18*U:.0f}" y="{y0+44*U:.0f}" font-family="Playfair Display" font-weight="800" font-size="{40*U:.0f}" fill="{DONG}">“</text>'
            f'<text x="{x0+44*U:.0f}" y="{y0+42*U:.0f}" font-family="Be Vietnam Pro" font-size="{19*U:.0f}" fill="{KEM}">(Khung mẫu – chỉ minh họa vị trí)</text>'
            f'<text x="{x0+44*U:.0f}" y="{y0+70*U:.0f}" font-family="Be Vietnam Pro" font-size="{19*U:.0f}" fill="{KEM}">Lời người xưa được sử chép lại</text>'
            f'<text x="{x0+44*U:.0f}" y="{y0+98*U:.0f}" font-family="Be Vietnam Pro" font-size="{19*U:.0f}" fill="{KEM}">sẽ đặt ở đây, tối đa 3 dòng.</text>'
            f'<text x="{x0+w-18*U:.0f}" y="{y0+134*U:.0f}" font-family="Be Vietnam Pro" font-size="{15*U:.0f}" fill="{DONG}" text-anchor="end">— Nguồn: tên sách, quyển</text></g>')

EFFECTS = [('H1', 'Hành quân bộ', H1), ('H2', 'Hành quân thủy', H2), ('H3', 'Giao chiến', H3),
           ('H4', 'Chiếm thành', H4), ('H5', 'Thắng trận', H5), ('H6', 'Thua / rút chạy', H6),
           ('H7', 'Phục binh', H7), ('H8', 'Tướng tử trận', H8), ('H9', 'Hỏa công', H9),
           ('H10', 'Thủy triều', H10), ('H11', 'Thời gian trôi', H11), ('H12', 'Trích lời người xưa', H12)]

def chrome(code, name):
    return (f'<rect x="{16*U:.0f}" y="{16*U:.0f}" width="{290*U:.0f}" height="{44*U:.0f}" rx="{6*U:.0f}" fill="{MUC}" opacity="0.88" stroke="{DONG}" stroke-width="{2*U:.1f}"/>'
            f'<text x="{30*U:.0f}" y="{46*U:.0f}" font-family="Be Vietnam Pro SemiBold" font-size="{22*U:.0f}" fill="{DONG2}">{code} · {name}</text>'
            f'<text x="{W/2:.0f}" y="{H-14*U:.0f}" font-family="Be Vietnam Pro" font-size="{14*U:.0f}" fill="{KEM}" text-anchor="middle" opacity="0.85">Bản đồ minh họa, ranh giới và vị trí gần đúng · BẢN NHÁP</text>')

def render(code, name, fn):
    src = open(__file__, 'rb').read()
    key = hashlib.sha1(src + f'{code}{W}{FPS}'.encode()).hexdigest()[:10]
    os.makedirs('clips', exist_ok=True)
    out = f'clips/{code}-{W}-{key}.mp4'
    if os.path.exists(out): print(code, 'cache'); return out
    base = base_frame().convert('RGBA')
    p = subprocess.Popen(['ffmpeg', '-y', '-loglevel', 'error', '-f', 'rawvideo', '-pix_fmt', 'rgb24', '-s', f'{W}x{H}',
                          '-r', str(FPS), '-i', '-', '-c:v', 'libx264', '-pix_fmt', 'yuv420p',
                          '-preset', 'veryfast' if FINAL else 'ultrafast', '-crf', '20' if FINAL else '26', out], stdin=subprocess.PIPE)
    for i in range(int(DUR * FPS)):
        t = i / FPS
        svg = f'<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{H}">{fn(t)}{chrome(code, name)}</svg>'
        ov = Image.open(io.BytesIO(cairosvg.svg2png(bytestring=svg.encode()))).convert('RGBA')
        fr = base.copy(); fr.alpha_composite(ov)
        fa = min(1, t / 0.25, (DUR - t) / 0.25)      # mờ vào/ra
        if fa < 1: fr = Image.blend(Image.new('RGBA', (W, H), (20, 17, 15, 255)), fr, fa)
        p.stdin.write(fr.convert('RGB').tobytes())
    p.stdin.close(); p.wait(); print(code, 'ok'); return out

if __name__ == '__main__':
    pick = [a for a in sys.argv[1:] if not a.startswith('--')]
    files = [render(c, n, f) for c, n, f in EFFECTS if not pick or c in pick]
    open('list.txt', 'w').write(''.join(f"file '{f}'\n" for f in files))
    name = 'demo-hieuung-final.mp4' if FINAL else 'demo-hieuung-nhap.mp4'
    subprocess.run(['ffmpeg', '-y', '-loglevel', 'error', '-f', 'concat', '-safe', '0', '-i', 'list.txt', '-c', 'copy', name], check=True)
    print('->', name)
