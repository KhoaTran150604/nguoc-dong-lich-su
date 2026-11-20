"""Thumbnail Short 1080×1920 lấy từ CHÍNH cảnh trong video dài, vẽ lại ở 4K cho nét (phong cách mộc mạc của kênh),
thêm mũi tên / dấu X chỉ vào chi tiết chính. Duyệt mẫu 17/11/2026 (E2 phần 1).

    python3 scripts/video/thumb_video.py e2 1 <out.jpg>
Chạy tiến trình riêng vì phải dựng bộ máy ở độ phân giải 3840×2160 (thumb.py tự gọi khi phần đó có trong CFG).
"""
import base64, io, json, math, os, sys, importlib
HERE = os.path.dirname(os.path.abspath(__file__)); ROOT = os.path.abspath(os.path.join(HERE, '..', '..'))
sys.path.insert(0, HERE); sys.path.insert(0, os.path.join(ROOT, 'scripts', 'hieuung'))
import cairosvg
from PIL import Image

W, H = 1080, 1920
MUC, DONG, DONG2, KEM, DO = '#14110F', '#C9A24A', '#F3D27A', '#F2E6CC', '#B3261E'
HEAD_Y, FOOT_DY = 140, 30     # chữ tiêu đề hạ xuống (trước 90) và dải chân hạ xuống (trước 0) – tránh nút/chữ của YouTube Shorts che (người dùng góp ý 17/11)
AV = os.path.join(ROOT, 'assets', 'brand', 'song-tu', 'AVATAR-YouTube-800x800.png')

# Mỗi phần: cảnh + thời điểm (tỉ lệ trong cảnh) + vùng cắt 4K (x0, y0, k = thu nhỏ) + điểm đầu mũi tên (đoàn quân) + điểm X (mục tiêu), tọa độ 4K
CFG = {
    ('e2', 1): dict(canh='s41', f=0.95, x0=1080, y0=60, k=0.735, tu=(1470, 840), x=(2380, 1152),
                    dong=('MỘT HÀNG CỌC GỖ', 'ĐÁNH CHÌM CẢ HẠM ĐỘI?')),
    # P2–P6 (17/11/2026): a0/a1 = điểm đầu/cuối mũi tên (4K, tuỳ chọn); mark = 'x' (mặc định) hoặc 'ring' (khoanh tròn, không phải thất bại)
    ('e2', 2): dict(canh='s16', f=0.6, x0=1250, y0=60, k=0.735, tu=(2160, 560), x=(1800, 770), a0=(2150, 520), a1=(1890, 700),
                    dong=('THẮNG GIẶC NGOÀI,', 'CHẾT VÌ NGƯỜI TRONG')),
    ('e2', 3): dict(canh='s28', f=0.9, x0=980, y0=60, k=0.735, tu=(2208, 1260), x=(1290, 1290), a0=(2120, 1230), a1=(1390, 1240),
                    dong=('MỘT LỜI CAN', 'BỊ BỎ NGOÀI TAI')),
    ('e2', 4): dict(canh='s34', f=0.4, x0=1190, y0=60, k=0.735, tu=(1400, 700), x=(1920, 1250), a0=(1420, 640), a1=(1800, 1080), mark='ring',
                    dong=('GIẶC CÒN TRÊN BIỂN,', 'NGÔ QUYỀN ĐÃ…')),
    ('e2', 5): dict(canh='s43', f=0.7, x0=1080, y0=60, k=0.735, tu=(1446, 800), x=(2200, 1080),
                    dong=('CHỈ TRONG CHỐC LÁT,', 'NƯỚC RÚT…')),
    ('e2', 6): dict(canh='s49', f=0.95, x0=1250, y0=60, k=0.735, tu=(2583, 968), x=(1906, 830), a0=(2560, 930), a1=(2030, 840), mark='ring',
                    dong=('SAU BẠCH ĐẰNG,', 'NGÔ QUYỀN LÀM GÌ?')),
}

def render_4k(tap, canh, f):
    import demo as L
    L.W, L.H, L.U = 3840, 2160, 4.0
    import dung as D
    sys.modules['dung'] = D
    EP = importlib.import_module('tap.' + tap); D.EP = EP
    c = EP.SHORTS[1] if hasattr(EP, 'SHORTS') and 1 in EP.SHORTS else {}
    loi = c.get('loi_doc', f'docs/videos/{tap.upper()}-loi-doc.txt'); gi = c.get('giong')
    items = D.read_script(os.path.join(ROOT, loi)); meta = json.load(open(os.path.join(ROOT, gi + '.json')))
    t, p, e = D.timeline(items, meta, getattr(EP, 'TAIL', 0.8))
    a, b = next((a, b) for cc, a, b in D.plan_scenes(items, t, p, e) if cc == canh)
    return D.frame(canh, (b - a) * f, b - a)

def svg(s):
    return Image.open(io.BytesIO(cairosvg.svg2png(bytestring=f'<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{H}">{s}</svg>'.encode()))).convert('RGBA')
def T(x, y, t, size, fill, anchor='middle', fam='Playfair Display', w='800'):
    return f'<text x="{x}" y="{y}" text-anchor="{anchor}" font-family="{fam}" font-weight="{w}" font-size="{size}" fill="{fill}">{t}</text>'

def head(l1, l2, y=None):
    y = HEAD_Y if y is None else y          # dải mực: chữ kem, dòng 2 vàng đồng, gạch đỏ sơn mài
    return (f'<rect x="0" y="0" width="{W}" height="{y+330}" fill="{MUC}" opacity="0.82"/>'
            + T(540, y + 120, l1, min(96, int(96 * 15 / max(15, len(l1)))), KEM) + T(540, y + 240, l2, min(64, int(64 * 20 / max(20, len(l2)))), DONG2)
            + f'<rect x="190" y="{y+268}" width="700" height="8" rx="4" fill="{DO}"/>')

def foot(phan, nhan):
    H2 = H + FOOT_DY
    av = 'data:image/png;base64,' + base64.b64encode(open(AV, 'rb').read()).decode()
    return (f'<rect x="0" y="{H2-190}" width="{W}" height="{190-FOOT_DY}" fill="{MUC}" opacity="0.85"/>'
            f'<rect x="60" y="{H2-138}" width="190" height="64" rx="8" fill="{DO}"/>' + T(155, H2 - 94, phan, 36, KEM, fam='Be Vietnam Pro', w='700')
            + T(280, H2 - 90, nhan, 56, DONG2, anchor='start')
            + f'<defs><clipPath id="a"><circle cx="{W-120}" cy="{H2-95}" r="62"/></clipPath></defs><image href="{av}" x="{W-182}" y="{H2-157}" width="124" height="124" clip-path="url(#a)"/>'
            f'<circle cx="{W-120}" cy="{H2-95}" r="62" fill="none" stroke="{DONG}" stroke-width="4"/>')

def arrow(ax0, ay0, ax1, ay1):    # mũi tên nét đứt đỏ sơn mài, viền mực, cong nhẹ
    mx, my = (ax0 + ax1) / 2 + 60, (ay0 + ay1) / 2 - 120
    o = (f'<path d="M{ax0},{ay0} Q{mx},{my} {ax1},{ay1}" fill="none" stroke="{MUC}" stroke-width="26" stroke-linecap="round"/>'
         f'<path d="M{ax0},{ay0} Q{mx},{my} {ax1},{ay1}" fill="none" stroke="{DO}" stroke-width="15" stroke-linecap="round" stroke-dasharray="34 18"/>')
    ang = math.atan2(ay1 - my, ax1 - mx); L = 56
    pts = [(ax1 + math.cos(ang) * 30, ay1 + math.sin(ang) * 30), (ax1 + math.cos(ang + 2.5) * L, ay1 + math.sin(ang + 2.5) * L),
           (ax1 + math.cos(ang - 2.5) * L, ay1 + math.sin(ang - 2.5) * L)]
    return o + f'<polygon points="{" ".join(f"{x:.0f},{y:.0f}" for x, y in pts)}" fill="{DO}" stroke="{MUC}" stroke-width="7" stroke-linejoin="round"/>'

def xmark(sx, sy, r=60):
    ring = f'<circle cx="{sx}" cy="{sy}" r="{r+40}" fill="none" stroke="{DONG2}" stroke-width="5" stroke-dasharray="12 10" opacity="0.9"/>'
    return ring + ''.join(f'<path d="M{sx-r},{sy-r} L{sx+r},{sy+r} M{sx+r},{sy-r} L{sx-r},{sy+r}" stroke="{c}" stroke-width="{w}" stroke-linecap="round"/>'
                          for c, w in ((MUC, 30), (DO, 17)))

def ring(sx, sy, r=80):        # khoanh tròn (dùng khi chi tiết không phải 'thất bại')
    return (f'<circle cx="{sx}" cy="{sy}" r="{r+34}" fill="none" stroke="{DONG2}" stroke-width="5" stroke-dasharray="12 10" opacity="0.9"/>'
            + ''.join(f'<circle cx="{sx}" cy="{sy}" r="{r}" fill="none" stroke="{c}" stroke-width="{w}"/>' for c, w in ((MUC, 22), (DO, 12))))

# Bố cục v2 (17/11/2026, người dùng chốt cho thống nhất với video): trên cùng là dải "BẠCH ĐẰNG 938 · PHẦN n" GIỐNG dải trong video,
# câu hook nằm trong hộp ở giữa/dưới khung (HOOK_Y, cfg 'hook_y' để đổi riêng), phần còn lại là nền cảnh – không còn dải chân.
LAYOUT, BAND_H, HOOK_Y = 'v2', 294, 1530   # v2: KHÔNG vẽ mũi tên (người dùng: rối mắt), chỉ giữ dấu X / vòng tròn

def band_v2(phan, nhan):
    def tx(t, size, col, y, sw):
        return (f'<text x="540" y="{y}" font-family="Playfair Display" font-weight="800" font-size="{size}" fill="none" stroke="{MUC}" stroke-width="{sw}" stroke-linejoin="round" text-anchor="middle" letter-spacing="2">{t}</text>'
                + f'<text x="540" y="{y}" font-family="Playfair Display" font-weight="800" font-size="{size}" fill="{col}" text-anchor="middle" letter-spacing="2">{t}</text>')
    return (f'<rect x="0" y="0" width="{W}" height="{BAND_H}" fill="{MUC}" opacity="0.9"/>' + tx(nhan, 84, DONG2, 180, 11)
            + f'<rect x="{W/2-105}" y="206" width="210" height="58" rx="29" fill="{DO}" stroke="{DONG2}" stroke-width="4"/>'
            + f'<text x="{W/2}" y="247" font-family="Be Vietnam Pro SemiBold" font-size="34" fill="#FFFFFF" text-anchor="middle">{phan}</text>')

def hook_v2(l1, l2, cy):
    s1 = min(84, int(84 * 15 / max(15, len(l1)))); s2 = min(60, int(60 * 20 / max(20, len(l2))))
    return (f'<rect x="40" y="{cy-150}" width="{W-80}" height="300" rx="22" fill="{MUC}" opacity="0.86" stroke="{DONG}" stroke-width="4"/>'
            + T(540, cy - 30, l1, s1, KEM) + T(540, cy + 70, l2, s2, DONG2)
            + f'<rect x="190" y="{cy+100}" width="700" height="8" rx="4" fill="{DO}"/>')

def make(tap, n, phan, nhan, out):
    c = CFG[(tap, n)]; im = render_4k(tap, c['canh'], c['f']).convert('RGB')
    v2 = LAYOUT == 'v2'
    k, X0, Y0, ZT = c['k'], c['x0'], c['y0'], (BAND_H if v2 else HEAD_Y + 330)
    if v2: k = max(k, (H - ZT) / (2160 - Y0) + 0.002)          # vùng cảnh cao hơn → phóng nhẹ để không vượt khung 4K
    zone = im.crop((X0, Y0, X0 + int(W / k), Y0 + int((H - ZT) / k))).resize((W, H - ZT), Image.LANCZOS)
    b = Image.new('RGBA', (W, H), (20, 17, 15, 255)); b.paste(zone, (0, ZT))
    P = lambda x, y: ((x - X0) * k, ZT + (y - Y0) * k)
    fx, fy = P(*c['tu']); sx, sy = P(*c['x'])
    if 'a0' in c: (ax0, ay0), (ax1, ay1) = P(*c['a0']), P(*c['a1'])
    else: ax0, ay0, ax1, ay1 = fx + 40, fy - 10, sx - 80, sy - 55
    mk = ring(sx, sy) if c.get('mark') == 'ring' else xmark(sx, sy)
    if v2: b.alpha_composite(svg(mk + hook_v2(*c['dong'], c.get('hook_y', HOOK_Y)) + band_v2(phan, nhan)))
    else: b.alpha_composite(svg(head(*c['dong']) + mk + arrow(ax0, ay0, ax1, ay1) + foot(phan, nhan)))
    b.convert('RGB').save(out, quality=94); return out

if __name__ == '__main__':
    tap, n, out = sys.argv[1], int(sys.argv[2]), sys.argv[3]
    print(make(tap, n, f'PHẦN {n}', 'BẠCH ĐẰNG 938', out))
