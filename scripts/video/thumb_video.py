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
AV = os.path.join(ROOT, 'assets', 'brand', 'song-tu', 'AVATAR-YouTube-800x800.png')

# Mỗi phần: cảnh + thời điểm (tỉ lệ trong cảnh) + vùng cắt 4K (x0, y0, k = thu nhỏ) + điểm đầu mũi tên (đoàn quân) + điểm X (mục tiêu), tọa độ 4K
CFG = {
    ('e2', 1): dict(canh='s41', f=0.95, x0=1080, y0=60, k=0.735, tu=(1470, 840), x=(2380, 1152),
                    dong=('MỘT HÀNG CỌC GỖ', 'ĐÁNH CHÌM CẢ HẠM ĐỘI?')),
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

def head(l1, l2, y=90):          # dải mực: chữ kem, dòng 2 vàng đồng, gạch đỏ sơn mài
    return (f'<rect x="0" y="0" width="{W}" height="{y+330}" fill="{MUC}" opacity="0.82"/>'
            + T(540, y + 120, l1, 96, KEM) + T(540, y + 240, l2, 64, DONG2)
            + f'<rect x="190" y="{y+268}" width="700" height="8" rx="4" fill="{DO}"/>')

def foot(phan, nhan):
    av = 'data:image/png;base64,' + base64.b64encode(open(AV, 'rb').read()).decode()
    return (f'<rect x="0" y="{H-190}" width="{W}" height="190" fill="{MUC}" opacity="0.85"/>'
            f'<rect x="60" y="{H-138}" width="190" height="64" rx="8" fill="{DO}"/>' + T(155, H - 94, phan, 36, KEM, fam='Be Vietnam Pro', w='700')
            + T(280, H - 90, nhan, 56, DONG2, anchor='start')
            + f'<defs><clipPath id="a"><circle cx="{W-120}" cy="{H-95}" r="62"/></clipPath></defs><image href="{av}" x="{W-182}" y="{H-157}" width="124" height="124" clip-path="url(#a)"/>'
            f'<circle cx="{W-120}" cy="{H-95}" r="62" fill="none" stroke="{DONG}" stroke-width="4"/>')

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

def make(tap, n, phan, nhan, out):
    c = CFG[(tap, n)]; im = render_4k(tap, c['canh'], c['f']).convert('RGB')
    k, X0, Y0, ZT = c['k'], c['x0'], c['y0'], 400
    zone = im.crop((X0, Y0, X0 + int(W / k), Y0 + int((H - ZT) / k))).resize((W, H - ZT), Image.LANCZOS)
    b = Image.new('RGBA', (W, H), (20, 17, 15, 255)); b.paste(zone, (0, ZT))
    P = lambda x, y: ((x - X0) * k, ZT + (y - Y0) * k)
    fx, fy = P(*c['tu']); sx, sy = P(*c['x'])
    b.alpha_composite(svg(head(*c['dong']) + xmark(sx, sy) + arrow(fx + 40, fy - 10, sx - 80, sy - 55) + foot(phan, nhan)))
    b.convert('RGB').save(out, quality=94); return out

if __name__ == '__main__':
    tap, n, out = sys.argv[1], int(sys.argv[2]), sys.argv[3]
    print(make(tap, n, f'PHẦN {n}', 'BẠCH ĐẰNG 938', out))
