"""Bản đồ hoạt họa CHI TIẾT (v2) – phong cách mặc định của kênh.

- Nền: bản đồ giấy cổ tự vẽ từ dữ liệu bờ biển Natural Earth (data/region.json) + vùng lãnh thổ tô màu
  (đa giác vẽ tay, MINH HỌA), dải phân cách sáng, sông, núi, cây, thành.
- Cờ tướng có khung chân dung: dùng ảnh trong cfg['portraits'] nếu có (ảnh tự tạo bằng Flow), nếu không
  vẽ chân dung cách điệu. Luôn ghi 'chân dung minh họa'.
- Mỗi câu chia nhiều nhịp hình (thuyền, cọc, dấu X, ấn, mũi tên...).
Quy tắc: ghi 'Bản đồ minh họa · ranh giới và vị trí gần đúng'; không đặt điểm cho Hải Môn; không vẽ biên giới hiện đại.
"""
import base64, io, json, math, os, random
import numpy as np
from PIL import Image, ImageDraw, ImageFilter
from shapely.geometry import shape, box, Polygon, MultiPolygon, Point, LineString
from shapely.ops import unary_union
import cairosvg

Image.MAX_IMAGE_PIXELS = None
COS = math.cos(math.radians(21)); LON0, LAT0, S0 = 100.0, 31.0, 240.0
def pj(lon, lat): return ((lon - LON0) * COS * S0, (LAT0 - lat) * S0)
MW, MH = pj(121.0, 8.0)

QC = (113.26, 23.13); DAI_LA = (105.85, 21.03); AI_CHAU = (105.78, 19.8); DUONG_LAM = (105.47, 21.15)
BD = (106.82, 20.86); GIAO = (105.9, 21.0)
ROUTE = [(112.6, 21.5), (111.0, 20.8), (109.4, 20.45), (108.0, 20.55), (107.3, 20.72), (106.95, 20.82)]

TERR = {  # đa giác MINH HỌA (lon, lat), sẽ cắt theo đất liền
    'nam_han': ([(104.9, 23.3), (106.0, 24.6), (108.0, 25.5), (110.5, 25.9), (112.5, 25.4), (114.6, 25.1), (116.5, 24.7), (117.4, 23.6), (117.4, 21.0), (111.0, 20.6), (109.6, 21.3), (108.1, 21.55), (106.9, 22.5), (105.9, 22.9)], (176, 74, 52)),
    'giao': ([(103.5, 22.4), (104.6, 22.85), (105.9, 22.9), (106.9, 22.5), (108.1, 21.55), (107.6, 21.0), (106.6, 20.2), (105.9, 19.4), (106.3, 18.3), (105.5, 18.05), (104.5, 19.2), (103.9, 20.4), (103.2, 21.4)], (214, 176, 70)),
    'champa': ([(105.5, 18.05), (106.6, 17.9), (108.0, 16.5), (109.5, 15.3), (109.4, 11.6), (107.6, 11.1), (106.9, 12.6), (107.2, 14.6), (106.4, 16.1), (105.4, 17.3)], (112, 132, 86)),
    'so': ([(108.8, 25.9), (110.5, 26.0), (112.5, 25.5), (114.1, 25.6), (114.3, 27.6), (113.8, 29.6), (111.0, 30.0), (109.3, 29.3), (108.6, 27.3)], (138, 120, 150)),
}
LABELS = [('NAM HÁN', (111.3, 24.0), 130), ('TĨNH HẢI', (105.0, 22.0), 100), ('(GIAO CHÂU)', (105.0, 21.55), 62),
          ('CHIÊM THÀNH', (107.6, 14.2), 90), ('SỞ', (111.5, 27.6), 110), ('BIỂN ĐÔNG', (112.5, 17.5), 110)]
RIVERS = [
    [(102.2, 23.0), (103.0, 22.6), (103.9, 22.35), (104.6, 21.9), (105.2, 21.4), (105.6, 21.12), (105.9, 20.95), (106.3, 20.6), (106.6, 20.25)],
    [(102.4, 22.4), (103.2, 21.8), (104.0, 21.2), (104.7, 20.95), (105.3, 21.2)],
    [(105.0, 22.9), (105.2, 22.2), (105.3, 21.6), (105.4, 21.3)],
    [(106.0, 21.5), (106.35, 21.12), (106.6, 20.98), (106.82, 20.86)],
    [(103.6, 21.3), (104.6, 20.6), (105.3, 20.2), (105.85, 19.75)],
    [(104.0, 19.5), (104.9, 19.0), (105.65, 18.75)],
    [(105.4, 24.2), (106.6, 23.9), (107.8, 23.5), (109.2, 23.4), (110.4, 23.5), (111.4, 23.4), (112.3, 23.1), (113.0, 22.9), (113.5, 22.4)],
    [(106.8, 22.4), (107.7, 22.7), (108.3, 22.8), (108.8, 23.1), (109.2, 23.4)],
    [(110.3, 25.4), (110.5, 24.4), (111.3, 23.5)],
    [(113.6, 25.2), (113.4, 24.3), (113.1, 23.6), (113.0, 23.0)],
    [(115.3, 24.3), (114.7, 23.6), (114.0, 23.1), (113.6, 22.9)],
    [(111.3, 25.6), (111.9, 26.4), (112.6, 27.2), (112.9, 28.2), (113.0, 29.0)],
]
DELTAS = [((106.0, 20.7), 0.75), ((113.3, 22.8), 0.55)]

def build_map(path):
    if os.path.exists(path): return Image.open(path).convert('RGB')
    root = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    reg = json.load(open(os.path.join(root, 'data/region.json')))
    view = box(LON0, 8.0, 121.0, LAT0)
    land_ll = unary_union([shape(v).intersection(view) for v in reg.values()]).buffer(0)
    def proj(g):
        ring = lambda c: [pj(x, y) for x, y in c]
        polys = [g] if g.geom_type == 'Polygon' else list(getattr(g, 'geoms', []))
        return MultiPolygon([Polygon(ring(p.exterior.coords), [ring(i.coords) for i in p.interiors]) for p in polys if p.geom_type == 'Polygon' and not p.is_empty])
    def d_of(g):
        polys = [g] if g.geom_type == 'Polygon' else list(g.geoms); out = []
        for p in polys:
            if p.is_empty: continue
            out.append('M' + ' L'.join(f'{x:.1f},{y:.1f}' for x, y in p.exterior.coords) + ' Z')
            for i in p.interiors: out.append('M' + ' L'.join(f'{x:.1f},{y:.1f}' for x, y in i.coords) + ' Z')
        return ' '.join(out)
    def texture(w, h, base, var, seed, blur=6):
        rng = np.random.default_rng(seed)
        n = rng.random((h // 8 + 1, w // 8 + 1)); im = Image.fromarray((n * 255).astype('uint8')).resize((w, h), Image.BICUBIC).filter(ImageFilter.GaussianBlur(blur))
        a = np.asarray(im).astype(float) / 255
        rgb = np.stack([np.clip(base[i] + (a - 0.5) * var, 0, 255) for i in range(3)], -1).astype('uint8')
        buf = io.BytesIO(); Image.fromarray(rgb).save(buf, 'JPEG', quality=82); return 'data:image/jpeg;base64,' + base64.b64encode(buf.getvalue()).decode()
    LP = proj(land_ll).buffer(0); tw, th = int(MW / 3), int(MH / 3)
    P = [f'<defs><clipPath id="lc"><path d="{d_of(LP)}"/></clipPath></defs>',
         f'<image href="{texture(tw, th, (66, 104, 116), 44, 1)}" x="0" y="0" width="{MW:.0f}" height="{MH:.0f}" preserveAspectRatio="none"/>']
    for i, dist in enumerate([70, 48, 28, 12]):
        ring = LP.buffer(dist).difference(LP.buffer(dist - 4))
        P.append(f'<path d="{d_of(ring)}" fill="#BFD6DA" opacity="{0.14 + 0.1 * i:.2f}"/>')
    P.append(f'<image href="{texture(tw, th, (214, 182, 128), 50, 2)}" x="0" y="0" width="{MW:.0f}" height="{MH:.0f}" preserveAspectRatio="none" clip-path="url(#lc)"/>')
    # vùng lãnh thổ minh họa + dải phân cách sáng
    for key, (pts, col) in TERR.items():
        g = Polygon(pts).buffer(0).intersection(land_ll)
        if g.is_empty: continue
        pg = proj(g).buffer(0)
        P.append(f'<path d="{d_of(pg)}" fill="rgb{col}" opacity="0.50"/>')
        P.append(f'<path d="{d_of(pg)}" fill="none" stroke="#F3E8CF" stroke-width="16" opacity="0.55" stroke-linejoin="round"/>')
        P.append(f'<path d="{d_of(pg)}" fill="none" stroke="rgb{tuple(int(c * 0.55) for c in col)}" stroke-width="4" stroke-dasharray="18 12" opacity="0.9"/>')
    # sông: viền tối + lòng sáng
    for pts in RIVERS:
        d = 'M' + ' L'.join(f'{pj(*p)[0]:.1f},{pj(*p)[1]:.1f}' for p in pts)
        P.append(f'<path d="{d}" fill="none" stroke="#3D6672" stroke-width="16" stroke-linecap="round" stroke-linejoin="round" opacity="0.8"/>')
        P.append(f'<path d="{d}" fill="none" stroke="#8DB6C2" stroke-width="9" stroke-linecap="round" stroke-linejoin="round"/>')
    P.append(f'<path d="{d_of(LP)}" fill="none" stroke="#4A2E18" stroke-width="5"/>')
    # núi + cây
    rnd = random.Random(11); inner = LP.buffer(-50)
    deltas = [Point(pj(*c)).buffer(r * S0) for c, r in DELTAS]
    rivers_buf = unary_union([LineString([pj(*p) for p in pts]).buffer(30) for pts in RIVERS])
    def ok(x, y):
        q = Point(x, y); return inner.contains(q) and not any(dd.contains(q) for dd in deltas) and not rivers_buf.contains(q)
    placed = 0
    while placed < 520:
        lon = rnd.uniform(100.5, 120.5); lat = rnd.uniform(9, 30.5); x, y = pj(lon, lat)
        if not ok(x, y): continue
        r = rnd.random(); s = rnd.uniform(0.6, 1.1)
        if r < 0.55:
            P.append(f'<g transform="translate({x:.0f} {y:.0f}) scale({s:.2f})"><polygon points="-44,22 0,-38 44,22" fill="#B0916A" stroke="#4A2E18" stroke-width="3"/><polygon points="0,-38 44,22 10,22" fill="#7E6142"/><polygon points="-12,-22 0,-38 12,-22 4,-18 -4,-20" fill="#F2E6CC"/></g>')
        else:
            for k in range(rnd.randint(1, 3)):
                dx, dy = rnd.uniform(-22, 22), rnd.uniform(-10, 10)
                P.append(f'<g transform="translate({x + dx:.0f} {y + dy:.0f}) scale({s:.2f})"><line x1="0" y1="0" x2="0" y2="16" stroke="#4A3220" stroke-width="3"/><circle cx="0" cy="-4" r="11" fill="#5E7A44" stroke="#3A4A28" stroke-width="2"/></g>')
        placed += 1
    def city(lon, lat, big=True):
        x, y = pj(lon, lat); s = 2.2 if big else 1.6
        return (f'<g transform="translate({x:.0f} {y:.0f}) scale({s})"><rect x="-26" y="-14" width="52" height="26" fill="#D8BC8A" stroke="#3A2618" stroke-width="3"/>'
                f'<rect x="-10" y="-34" width="20" height="20" fill="#C8A878" stroke="#3A2618" stroke-width="3"/><polygon points="-16,-34 0,-50 16,-34" fill="#8A3A24" stroke="#3A2618" stroke-width="3"/>'
                f'<polygon points="-30,-14 -18,-26 18,-26 30,-14" fill="#8A3A24" stroke="#3A2618" stroke-width="3"/></g>')
    P += [city(*QC), city(*DAI_LA), city(*AI_CHAU, False), city(*DUONG_LAM, False)]
    def label(t, lon, lat, size, col='#2A1A10', halo='#F2E6CC'):
        x, y = pj(lon, lat)
        return (f'<text x="{x:.0f}" y="{y:.0f}" font-family="Playfair Display" font-weight="800" font-size="{size}" text-anchor="middle" letter-spacing="6" '
                f'stroke="{halo}" stroke-width="10" stroke-linejoin="round" fill="{col}" paint-order="stroke">{t}</text>')
    for t, (lon, lat), size in LABELS:
        P.append(label(t, lon, lat, size, '#E9F1F2' if 'BIỂN' in t else '#2A1A10', '#3B5E68' if 'BIỂN' in t else '#F2E6CC'))
    for t, ll, size in [('Quảng Châu', (QC[0], QC[1] - 0.55), 66), ('Đại La', (DAI_LA[0] + 0.05, DAI_LA[1] - 0.5), 60), ('Ái Châu', (AI_CHAU[0], AI_CHAU[1] - 0.45), 54)]:
        P.append(label(t, *ll, size))
    svg = f'<svg xmlns="http://www.w3.org/2000/svg" width="{MW:.0f}" height="{MH:.0f}">{"".join(P)}</svg>'
    im = Image.open(io.BytesIO(cairosvg.svg2png(bytestring=svg.encode()))).convert('RGB')
    im.save(path); return im

# ---------- cờ tướng có chân dung ----------
def portrait_placeholder(kind, col, w, h):
    im = Image.new('RGBA', (w, h), (0, 0, 0, 0)); d = ImageDraw.Draw(im)
    d.rectangle([0, 0, w, h], fill=tuple(int(c * 0.45) for c in col) + (255,))
    for i in range(h):  # nền đỏ sơn mài chuyển sắc
        d.line([(0, i), (w, i)], fill=tuple(int(c * (0.35 + 0.35 * i / h)) for c in col) + (255,))
    gold = (226, 190, 110, 255); dark = (24, 16, 10, 255); cx = w / 2
    d.polygon([(cx - w * 0.42, h), (cx - w * 0.30, h * 0.70), (cx + w * 0.30, h * 0.70), (cx + w * 0.42, h)], fill=dark, outline=gold)  # vai áo
    d.line([(cx, h * 0.72), (cx, h)], fill=gold, width=2)
    d.ellipse([cx - w * 0.17, h * 0.34, cx + w * 0.17, h * 0.70], fill=(150, 112, 80, 255), outline=dark, width=2)  # mặt (không chi tiết)
    if kind == 'king':
        d.rectangle([cx - w * 0.22, h * 0.22, cx + w * 0.22, h * 0.36], fill=dark, outline=gold, width=2)
        d.rectangle([cx - w * 0.30, h * 0.18, cx + w * 0.30, h * 0.23], fill=gold)
        for k in range(-3, 4): d.line([(cx + k * w * 0.08, h * 0.23), (cx + k * w * 0.08, h * 0.30)], fill=gold, width=2)
    elif kind == 'prince':
        d.polygon([(cx - w * 0.2, h * 0.36), (cx - w * 0.14, h * 0.2), (cx + w * 0.14, h * 0.2), (cx + w * 0.2, h * 0.36)], fill=dark, outline=gold)
        d.ellipse([cx - 5, h * 0.14, cx + 5, h * 0.2], fill=gold)
    else:  # tướng: mũ trụ có chóp
        d.pieslice([cx - w * 0.21, h * 0.22, cx + w * 0.21, h * 0.5], 180, 360, fill=dark, outline=gold, width=2)
        d.line([(cx, h * 0.22), (cx, h * 0.08)], fill=gold, width=4); d.polygon([(cx, h * 0.04), (cx - 8, h * 0.12), (cx + 8, h * 0.12)], fill=(179, 38, 30, 255))
    return im

_BANNER_CACHE = {}
def banner_img(name, kind, col, portrait_path=None):
    key = (name, kind, col, portrait_path)
    if key in _BANNER_CACHE: return _BANNER_CACHE[key]
    W0, H0 = 300, 560; im = Image.new('RGBA', (W0, H0), (0, 0, 0, 0)); d = ImageDraw.Draw(im)
    pole = (58, 38, 22, 255); px = W0 // 2; gold = (214, 176, 90, 255); dark = (30, 20, 12, 255)
    d.line([(px, 34), (px, H0 - 8)], fill=pole, width=11); d.polygon([(px - 11, 36), (px, 2), (px + 11, 36)], fill=(205, 205, 205, 255))
    d.line([(px - 128, 58), (px + 128, 58)], fill=pole, width=9)
    for sx in (-128, 128): d.ellipse([px + sx - 9, 49, px + sx + 9, 67], fill=gold)
    fx0, fy0, fw, fh = px - 118, 64, 236, 330
    d.rectangle([fx0 - 6, fy0 - 6, fx0 + fw + 6, fy0 + fh + 6], fill=dark)
    ph = fh - 56
    if portrait_path and os.path.exists(portrait_path):
        p = Image.open(portrait_path).convert('RGBA'); tr = fw / ph
        if p.width / p.height > tr:  # ảnh ngang: cắt giữa, ưu tiên phần mặt
            nw = p.height * tr; p = p.crop(((p.width - nw) / 2, 0, (p.width + nw) / 2, p.height))
        else:
            p = p.crop((0, 0, p.width, p.width / tr))
        im.paste(p.resize((fw, ph), Image.LANCZOS), (fx0, fy0 + 56))
    else:
        im.paste(portrait_placeholder(kind, col, fw, ph), (fx0, fy0 + 56))
    d.rectangle([fx0, fy0, fx0 + fw, fy0 + 56], fill=(242, 230, 204, 255))
    d.line([(fx0, fy0 + 56), (fx0 + fw, fy0 + 56)], fill=gold, width=4)
    from render import F_TITLE  # noqa
    size = 34
    while d.textlength(name, font=F_TITLE(size)) > fw - 16 and size > 18: size -= 2
    f = F_TITLE(size); w = d.textlength(name, font=f); d.text((px - w / 2, fy0 + (56 - size * 1.2) / 2), name, font=f, fill=(40, 24, 14, 255))
    d.rectangle([fx0, fy0, fx0 + fw, fy0 + fh], outline=gold, width=6); d.rectangle([fx0 - 6, fy0 - 6, fx0 + fw + 6, fy0 + fh + 6], outline=col + (255,), width=4)
    for k in range(6): d.polygon([(fx0 + k * fw / 6, fy0 + fh + 4), (fx0 + (k + 0.5) * fw / 6, fy0 + fh + 30), (fx0 + (k + 1) * fw / 6, fy0 + fh + 4)], fill=col + (255,), outline=dark)
    d.ellipse([px - 50, H0 - 20, px + 50, H0 + 4], fill=(0, 0, 0, 90))
    _BANNER_CACHE[key] = im; return im

def register(R, ctx, work, segs, timeline):
    W, H = R.W, R.H; ease, clamp01 = R.ease, R.clamp01
    BIG = build_map(os.path.join(work, 'map_big_v2.png'))
    root = ctx.get('root', '.'); PORT = {k: os.path.join(root, v) for k, v in ctx.get('cfg', {}).get('portraits', {}).items()}
    import sys; sys.modules.setdefault('render', R)
    CAM = {'m_open': (109.3, 21.6, 0.40), 'm_giaovuong': (109.6, 22.3, 0.55), 'm_haimon': (110.6, 22.0, 0.55),
           'm_battle': (107.05, 20.92, 1.55), 'm_reveal': (109.4, 21.9, 0.48), 'm_princes': (112.6, 23.3, 0.85),
           'm_titles': (108.6, 22.2, 0.55), 'm_retreat': (109.8, 21.5, 0.52), 'm_never': (108.2, 22.4, 0.62),
           'm_irony': (106.0, 21.1, 0.85), 'm_quote': (108.8, 21.9, 0.48), 'm_rewind': (108.8, 21.5, 0.36), 'm_question': (105.9, 21.1, 0.8)}
    FIXED = tuple(ctx.get('cfg', {}).get('map_view', (109.4, 22.0, 0.44)))
    cams = [FIXED for _ in segs] if ctx.get('cfg', {}).get('camera', 'static') == 'static' else [CAM.get(s['scene'], (109.3, 21.6, 0.4)) for s in segs]
    def cam_at(idx, tl):
        prev = cams[idx - 1] if idx > 0 else cams[0]; cur = cams[idx]; u = ease(clamp01(tl / 1.3))
        lerp = lambda a, b: a + (b - a) * u
        return (lerp(prev[0], cur[0]), lerp(prev[1], cur[1]), prev[2] * (cur[2] / prev[2]) ** u)
    SH = Image.new('RGBA', (W, H), (0, 0, 0, 0)); _d = ImageDraw.Draw(SH)
    for i in range(600): _d.line([(0, i), (W, i)], fill=(14, 11, 9, int(235 * (1 - i / 600) ** 0.9)))
    for i in range(560): _d.line([(0, H - i), (W, H - i)], fill=(14, 11, 9, int(235 * (1 - i / 560) ** 0.9)))
    def view(c, drift):
        lon, lat, z = c
        bx, by = pj(lon, lat); cw, ch = W / z, H / z
        x0 = min(max(bx - cw / 2, 0), MW - cw); y0 = min(max(by - ch * 0.5, 0), MH - ch)
        im = BIG.crop((int(x0), int(y0), int(x0 + cw), int(y0 + ch))).resize((W, H), Image.BILINEAR)
        R.comp(im, SH)
        S = lambda lon_, lat_: ((pj(lon_, lat_)[0] - x0) * z, (pj(lon_, lat_)[1] - y0) * z)
        return im, S, z
    def base(idx, t):
        T = timeline[idx][0] + t; return view(cam_at(idx, t), (T % 10) / 10)
    sc_ = lambda z: 1.0  # vật trên bản đồ luôn cùng cỡ (lớn), không đổi theo camera
    def put_banner(im, x, y, name, kind, col, port=None, s=1.0, a=1.0, rot=0.0):
        b = banner_img(name, kind, col, PORT.get(port))
        if rot: b = b.rotate(rot, resample=Image.BICUBIC, expand=True, center=(b.width / 2, b.height - 8))
        bw, bh = int(b.width * 0.62 * s), int(b.height * 0.62 * s); b = b.resize((bw, bh), Image.LANCZOS)
        if a < 0.999: b = R.with_alpha(b, a)
        R.comp(im, b, (x - bw / 2, y - bh + 6 * s))
    def note(d, txt='Bản đồ minh họa · ranh giới và vị trí gần đúng · chân dung minh họa'):
        d.text((48, 1690), txt, font=R.F_REG(26), fill=R.CREAM + (180,))
    def head(d, t, txt, sub=None, y=300, size=96, col=None):
        a = int(255 * R.fade_in(t)); R.text_center(d, y, txt, R.F_TITLE(size), (col or R.GOLD2) + (a,))
        if sub: R.text_center(d, y + int(size * 1.25), sub, R.F_SEMI(42), R.CREAM + (a,))
    def dashed(d, pts, u, col, width=8, dash=26):
        L = [math.dist(pts[i], pts[i + 1]) for i in range(len(pts) - 1)]; tot = sum(L) or 1; target = tot * u; acc = 0; tip = None
        for i, l in enumerate(L):
            if acc >= target: break
            (x1, y1), (x2, y2) = pts[i], pts[i + 1]; n = max(1, int(l / dash))
            for k in range(0, n, 2):
                s0 = k / n
                if acc + s0 * l > target: break
                s1 = min((k + 1) / n, (target - acc) / l)
                d.line([(x1 + (x2 - x1) * s0, y1 + (y2 - y1) * s0), (x1 + (x2 - x1) * s1, y1 + (y2 - y1) * s1)], fill=col, width=width)
            f = min(1, (target - acc) / l); tip = (x1 + (x2 - x1) * f, y1 + (y2 - y1) * f, math.atan2(y2 - y1, x2 - x1)); acc += l
        return tip
    def arrowhead(d, tip, col, s=28):
        if not tip: return
        x, y, a = tip
        d.polygon([(x + s * math.cos(a), y + s * math.sin(a)), (x + s * 0.7 * math.cos(a + 2.5), y + s * 0.7 * math.sin(a + 2.5)), (x + s * 0.7 * math.cos(a - 2.5), y + s * 0.7 * math.sin(a - 2.5))], fill=col)
    def glow(im, cx, cy, r, col, a):
        if a <= 0.01: return
        g = Image.new('RGBA', (W, H), (0, 0, 0, 0)); ImageDraw.Draw(g).ellipse([cx - r, cy - r * 0.8, cx + r, cy + r * 0.8], fill=col + (int(130 * a),))
        R.comp(im, g.filter(ImageFilter.GaussianBlur(max(10, r / 3))))
    def junk(d, x, y, s, tilt=0, a=255, sail=(150, 60, 40)):
        def rot(px, py):
            c, sn = math.cos(math.radians(tilt)), math.sin(math.radians(tilt)); return (x + (px * c - py * sn) * s, y + (px * sn + py * c) * s)
        hull = [rot(-60, 0), rot(60, 0), rot(46, 20), rot(-50, 20)]
        d.polygon(hull, fill=(70, 44, 26, a), outline=(30, 18, 10, a))
        for mx, hh in ((-14, 70), (22, 54)):
            d.line([rot(mx, 0), rot(mx, -hh)], fill=(40, 26, 14, a), width=max(2, int(4 * s)))
            d.polygon([rot(mx, -hh + 4), rot(mx + 30, -hh + 10), rot(mx + 26, -8), rot(mx, -8)], fill=sail + (a,), outline=(40, 20, 10, a))
            for k in range(1, 4):
                yy = -hh + 4 + k * (hh - 12) / 4; d.line([rot(mx, yy), rot(mx + 28, yy + 2)], fill=(60, 30, 16, a), width=max(1, int(2 * s)))
    def boat(d, x, y, s, a=255):
        d.polygon([(x - 34 * s, y), (x + 34 * s, y), (x + 24 * s, y + 10 * s), (x - 24 * s, y + 10 * s)], fill=(40, 30, 18, a))
        for k in range(-2, 3): d.line([(x + k * 10 * s, y), (x + k * 10 * s - 8 * s, y + 18 * s)], fill=(40, 30, 18, a), width=2)
    def stake(d, x, y, s, h, a=255):
        d.polygon([(x - 5 * s, y), (x + 5 * s, y), (x + 5 * s, y - h + 14 * s), (x, y - h), (x - 5 * s, y - h + 14 * s)], fill=(88, 58, 34, a), outline=(30, 18, 10, a))
        d.polygon([(x - 5 * s, y - h + 14 * s), (x, y - h), (x + 5 * s, y - h + 14 * s)], fill=(190, 196, 200, a))
    def xmark(d, x, y, r, col, w=10):
        d.line([(x - r, y - r), (x + r, y + r)], fill=col, width=w); d.line([(x - r, y + r), (x + r, y - r)], fill=col, width=w)
    def seal(im, cx, cy, size, lines, t, col=R.RED):
        R.seal(im, t, cx, cy, size, lines, col)
    RED, GOLD = (179, 38, 30), (214, 176, 70)
    def mk(name):
        def deco(fn): R.SCENES['map_' + name] = fn; return fn
        return deco

    @mk('m_open')
    def _(im0, t, dur, ctx, seg, idx):
        im, S, z = base(idx, t)
        a = 1 - R.fade_in(t, 0.9)
        if a > 0.01:
            cover = im0.copy(); R.SCENES['chuky_hold'](cover, t, dur, ctx, seg); im = Image.blend(im, cover, a)
        d = ImageDraw.Draw(im, 'RGBA'); head(d, t - 0.3, '938', size=170, y=300); note(d); return im

    @mk('m_giaovuong')
    def _(im0, t, dur, ctx, seg, idx):
        im, S, z = base(idx, t); s = sc_(z); d = ImageDraw.Draw(im, 'RGBA')
        qx, qy = S(*QC); gx, gy = S(*GIAO)
        put_banner(im, qx - 70, qy - 10, 'Vua Nam Hán', 'king', RED, 'luu_nghiem', s, R.fade_in(t - 0.2))
        put_banner(im, qx - 230 * s, qy + 60 * s, 'Hoằng Tháo', 'prince', RED, 'hoang_thao', s * 0.85, R.fade_in(t - 1.4))
        u = ease(clamp01((t - 2.4) / 1.8)); d = ImageDraw.Draw(im, 'RGBA')
        tip = dashed(d, [(qx - 230 * s, qy + 40), ((qx + gx) / 2, min(qy, gy) - 160), (gx + 30, gy - 30)], u, R.GOLD2 + (235,), 7); arrowhead(d, tip if u < 1 else None, R.GOLD2 + (235,))
        glow(im, gx, gy, 240 * z / 0.55, (240, 225, 190), 0.45 + 0.35 * math.sin(t * 4) if u > 0.6 else 0)
        d = ImageDraw.Draw(im, 'RGBA')
        if u >= 1: R.text_center(d, int(gy - 60), '?', R.F_TITLE(120), R.GOLD2 + (int(255 * R.fade_in(t - 4.2)),))
        if t > 0.9: seal(im, 540, 470, 210, ['GIAO', 'VƯƠNG'], t - 0.9)
        d = ImageDraw.Draw(im, 'RGBA'); R.text_center(d, 610, '« vua đất Giao »', R.F_SEMI(44), R.CREAM + (int(255 * R.fade_in(t - 1.2)),))
        note(d); return im

    @mk('m_haimon')
    def _(im0, t, dur, ctx, seg, idx):
        im, S, z = base(idx, t); s = sc_(z); qx, qy = S(*QC)
        put_banner(im, qx - 70, qy - 10, 'Vua Nam Hán', 'king', RED, 'luu_nghiem', s, 1 - 0.6 * R.fade_in(t - 1.0))
        d = ImageDraw.Draw(im, 'RGBA'); a = int(255 * R.fade_in(t - 0.4)); bx, by = 90, 320
        d.rounded_rectangle([bx, by, W - bx, by + 330], radius=22, fill=(22, 18, 14, int(a * 0.88)), outline=R.GOLD + (a,), width=3)
        d.text((bx + 40, by + 26), 'HẢI MÔN', font=R.F_TITLE(80), fill=R.GOLD2 + (a,))
        d.text((bx + 40, by + 122), 'vua Nam Hán tự đóng quân tiếp ứng', font=R.F_SEMI(38), fill=R.CREAM + (a,))
        d.text((bx + 40, by + 172), 'vị trí chưa rõ · không đánh dấu trên bản đồ', font=R.F_REG(30), fill=R.COPPER + (a,))
        for k in range(5):  # trại quân trong ô
            ka = int(255 * R.fade_in(t - 0.9 - k * 0.25)); x = bx + 560 + k * 70; y = by + 290
            d.polygon([(x - 28, y), (x, y - 44), (x + 28, y)], fill=(176, 74, 52, ka), outline=(40, 20, 10, ka)); d.line([(x, y - 44), (x, y - 62)], fill=(40, 20, 10, ka), width=3)
            d.polygon([(x, y - 62), (x + 18, y - 56), (x, y - 50)], fill=RED + (ka,))
        put_banner(im, bx + 120, by + 312, 'Vua Nam Hán', 'king', RED, 'luu_nghiem', 0.7, R.fade_in(t - 1.0))
        d = ImageDraw.Draw(im, 'RGBA'); note(d); return im

    @mk('m_battle')
    def _(im0, t, dur, ctx, seg, idx):
        im, S, z = base(idx, t); s = sc_(z); d = ImageDraw.Draw(im, 'RGBA')
        pts = [S(*p) for p in ROUTE]; bx, by = S(*BD)
        # nhịp 1: đoàn thuyền tiến vào
        u = ease(clamp01((t - 0.3) / (dur * 0.38)))
        def along(f):
            L = [math.dist(pts[i], pts[i + 1]) for i in range(len(pts) - 1)]; tot = sum(L); dd = f * tot
            for i, l in enumerate(L):
                if dd <= l: q = dd / l; return (pts[i][0] + (pts[i + 1][0] - pts[i][0]) * q, pts[i][1] + (pts[i + 1][1] - pts[i][1]) * q)
                dd -= l
            return pts[-1]
        dashed(d, pts, u, R.RED + (200,), 6)
        # nhịp 2: cọc nhô lên khi triều rút (minh họa, không phải số lượng thật)
        p2 = ease(clamp01((t - dur * 0.40) / 0.9))
        for k in range(14):
            sx = bx - 150 * s + (k % 7) * 46 * s + (k // 7) * 20 * s; sy = by + 10 * s + (k // 7) * 34 * s
            stake(d, sx, sy, s, (20 + 34 * p2) * s, int(255 * min(1, p2 * 1.5)))
        if 0.05 < p2 < 1.2 and t < dur * 0.62:
            R.text_center(d, 560, 'nước triều rút ↓', R.F_SEMI(46), (190, 220, 228, int(255 * R.fade_in(t - dur * 0.40))))
        # nhịp 3: thuyền vướng cọc, nghiêng, chìm
        p3 = ease(clamp01((t - dur * 0.55) / 1.4))
        fleet = [0.93, 0.86, 0.78, 0.70, 0.62]
        for k, f in enumerate(fleet):
            fx, fy = along(u * f + (1 - u) * f * 0.2)
            if k == 0: fx, fy = fx + 10 * s, fy
            tilt = p3 * (24 + 8 * k) * (1 if k % 2 else -1); sink = p3 * 22 * s
            a = int(255 * (1 - 0.65 * p3))
            junk(d, fx, fy + sink, 0.95 * s, tilt, a)
            if p3 > 0.3:
                for r in (18, 34): d.ellipse([fx - r * s, fy + 14 * s - r * 0.4 * s, fx + r * s, fy + 14 * s + r * 0.4 * s], outline=(220, 235, 238, int(160 * (1 - p3) + 60)), width=2)
            if p3 > 0.8: xmark(d, fx, fy - 10 * s, 18 * s, R.RED + (int(255 * R.fade_in(t - dur * 0.55 - 1.1)),), 6)
        # cờ Hoằng Tháo trên thuyền đầu đổ xuống
        hx, hy = along(u * fleet[0])
        put_banner(im, hx + 10 * s, hy - 10 * s, 'Hoằng Tháo', 'prince', RED, 'hoang_thao', s * 0.8, 1 - 0.6 * p3)  # không lật/chìm theo thuyền: sử chép cách chết khác nhau
        d = ImageDraw.Draw(im, 'RGBA')
        if p3 > 0.85:
            xmark(d, hx + 30 * s, hy - 70 * s, 34 * s, R.GOLD2 + (255,), 12)
            R.text_center(d, 300, 'quá nửa chết đuối', R.F_TITLE(84), R.GOLD2 + (int(255 * R.fade_in(t - dur * 0.55 - 1.2)),))
        d.text((bx - 120 * s, by + 90 * s), 'Cửa Bạch Đằng', font=R.F_TITLE(int(34 * s)), fill=(240, 232, 210, 235), stroke_width=4, stroke_fill=(40, 60, 66))
        note(d, 'Minh họa · vị trí bãi cọc 938 chưa được khảo cổ xác định'); return im

    @mk('m_reveal')
    def _(im0, t, dur, ctx, seg, idx):
        im, S, z = base(idx, t); s = sc_(z)
        qx, qy = S(*QC); bx, by = S(*BD)
        put_banner(im, qx - 70, qy - 10, 'Vua Nam Hán', 'king', RED, 'luu_nghiem', s * 1.2, R.fade_in(t))
        rise = ease(clamp01((t - dur * 0.45) / 0.9))
        glow(im, bx, by - 60, 160, (243, 210, 122), rise)
        put_banner(im, bx, by + int(40 * (1 - rise)), 'Ngô Quyền', 'general', GOLD, 'ngo_quyen', s * 1.25, rise)
        d = ImageDraw.Draw(im, 'RGBA')
        if rise > 0.5:
            tip = dashed(d, [S(*p) for p in ROUTE[:-1]], 1.0, R.RED + (120,), 5)
            x, y = S(*ROUTE[-2]); d.line([(x - 6, y - 60), (x - 6, y + 60)], fill=R.GOLD2 + (int(255 * rise),), width=12)
        note(d); return im

    @mk('m_princes')
    def _(im0, t, dur, ctx, seg, idx):
        im, S, z = base(idx, t); R.comp(im, Image.new('RGBA', (W, H), (14, 11, 9, 140)))
        d = ImageDraw.Draw(im, 'RGBA'); a = R.fade_in(t)
        hx, hy = 540, 900
        for row, (yy, off) in enumerate(((760, 0), (1130, 95))):
            for k in range(-4, 5):
                x = hx + k * 190 + off
                if row == 0 and k == 0: continue
                fade = max(0.0, 1 - abs(x - hx) / 620)
                put_banner(im, int(x), yy, '', 'prince', (120, 90, 70), None, 0.6, R.fade_in(t - 0.1 * abs(k)) * 0.85 * fade)
        put_banner(im, hx, 760, 'Hoằng Tháo', 'prince', RED, 'hoang_thao', 0.75, R.fade_in(t - 0.6))
        d = ImageDraw.Draw(im, 'RGBA')
        if t > 1.6:
            ha = int(255 * R.fade_in(t - 1.6)); d.rounded_rectangle([hx - 92, 430, hx + 92, 770], radius=10, outline=R.GOLD2 + (ha,), width=6)
            R.text_center(d, 790, 'tước cũ: Vạn vương', R.F_TITLE(48), R.GOLD2 + (ha,))
        head(d, t, 'gần hai chục hoàng tử', 'được phong vương (theo Tân Ngũ đại sử)', y=290, size=72)
        note(d, 'Minh họa · chân dung minh họa'); return im

    @mk('m_titles')
    def _(im0, t, dur, ctx, seg, idx):
        im, S, z = base(idx, t); gx, gy = S(*GIAO); s = sc_(z)
        glow(im, gx, gy, 230 * z / 0.55, (240, 225, 190), 0.5)
        p = clamp01((t - 1.0) / 0.8)
        seal(im, 540, 470, 210, ['VẠN', 'VƯƠNG'], t, (110, 90, 70)) if p < 1 else None
        if p > 0:
            seal(im, 330, 560, 250, ['TIẾT ĐỘ', 'SỨ TĨNH HẢI'], t - 1.0); seal(im, 750, 560, 250, ['GIAO', 'VƯƠNG'], t - 1.0)
        d = ImageDraw.Draw(im, 'RGBA')
        if p >= 1:
            tl = t - 1.8; a = int(255 * R.fade_in(tl)); tip = dashed(d, [(750, 700), (gx + 40, gy - 60)], ease(clamp01(tl / 1.0)), R.GOLD2 + (a,), 6)
            arrowhead(d, tip, R.GOLD2 + (a,))
        note(d); return im

    @mk('m_retreat')
    def _(im0, t, dur, ctx, seg, idx):
        im, S, z = base(idx, t); s = sc_(z); d = ImageDraw.Draw(im, 'RGBA')
        bx, by = S(*BD); qx, qy = S(*QC)
        for k in range(3):  # xác thuyền
            junk(d, bx + (40 + 60 * k) * s, by + (10 + 12 * k) * s, 0.7 * s, 40 - 25 * k, 140)
        put_banner(im, int(bx + 40 * s), int(by), 'Hoằng Tháo', 'prince', RED, 'hoang_thao', s * 0.7, 0.45)
        d = ImageDraw.Draw(im, 'RGBA'); xmark(d, bx + 10 * s, by - 40 * s, 26 * s, R.RED + (220,), 8)
        u = ease(clamp01((t - 1.2) / (dur * 0.6)))
        back = [S(*p) for p in reversed(ROUTE)] + [S(112.8, 22.6), (qx, qy)]
        tip = dashed(d, back, u, (200, 190, 170, 220), 6); arrowhead(d, tip if u < 1 else None, (200, 190, 170, 220))
        for k, f in enumerate((0.35, 0.5)):
            if u > f:
                L = len(back) - 1; i = min(L - 1, int(f * L)); fx = back[i][0] + (back[i + 1][0] - back[i][0]) * (f * L - i); fy = back[i][1] + (back[i + 1][1] - back[i][1]) * (f * L - i)
                junk(d, fx, fy, 0.6 * s, 0, int(200 * R.fade_in(t - 1.2 - f * dur * 0.6)))
        put_banner(im, qx - 70, qy - 10, 'Vua Nam Hán', 'king', RED, 'luu_nghiem', s, 1.0)
        d = ImageDraw.Draw(im, 'RGBA'); head(d, t - 0.3, 'khóc thương', 'thu tàn quân rút về', y=300, size=88)
        note(d); return im

    @mk('m_never')
    def _(im0, t, dur, ctx, seg, idx):
        im, S, z = base(idx, t); d = ImageDraw.Draw(im, 'RGBA')
        a = int(255 * R.fade_in(t - 0.3)); x1, y1 = S(110.5, 23.6); x2, y2 = S(106.6, 21.3)
        tip = dashed(d, [(x1, y1), (x2, y2)], 1.0, R.RED + (int(a * 0.8),), 9); arrowhead(d, tip, R.RED + (int(a * 0.8),), 34)
        if t > 1.0:
            mx, my = (x1 + x2) / 2, (y1 + y2) / 2; b = int(255 * R.fade_in(t - 1.0)); xmark(d, mx, my, 60, R.GOLD2 + (b,), 14)
        head(d, t, 'không đem quân sang nữa', None, y=300, size=72); note(d); return im

    @mk('m_irony')
    def _(im0, t, dur, ctx, seg, idx):
        im, S, z = base(idx, t); gx, gy = S(*GIAO)
        glow(im, gx, gy, 300 * z / 0.85, (240, 225, 190), 0.5)
        lay = Image.new('RGBA', (W, H), (0, 0, 0, 0)); R.seal(lay, 2.0, 540, 560, 300, ['GIAO', 'VƯƠNG'])
        p = ease(clamp01((t - 0.9) / 1.0))
        if p > 0:  # ấn nứt đôi
            mask = Image.new('L', (W, H), 0); ImageDraw.Draw(mask).polygon([(540, 380), (520, 480), (565, 560), (515, 650), (545, 760), (W, 760), (W, 380)], fill=255)
            right = Image.new('RGBA', (W, H), (0, 0, 0, 0)); right.paste(lay, (0, 0), mask); left = lay.copy(); left.paste((0, 0, 0, 0), (0, 0), mask)
            lay = Image.new('RGBA', (W, H), (0, 0, 0, 0)); lay.alpha_composite(left, (-int(16 * p), int(10 * p))); lay.alpha_composite(right, (int(16 * p), int(26 * p)))
            ImageDraw.Draw(lay).line([(540, 380), (520, 480), (565, 560), (515, 650), (545, 760)], fill=R.INK + (255,), width=6)
        bx, by = S(*BD); put_banner(im, int(min(bx, W - 140)), int(by), 'Ngô Quyền', 'general', GOLD, 'ngo_quyen', sc_(z), R.fade_in(t - 1.2))
        R.comp(im, lay); d = ImageDraw.Draw(im, 'RGBA')
        R.text_center(d, 820, 'chưa từng có đất Giao', R.F_TITLE(70), R.CREAM + (int(255 * R.fade_in(t - 1.4)),))
        note(d); return im

    @mk('m_quote')
    def _(im0, t, dur, ctx, seg, idx):
        im, S, z = base(idx, t); R.comp(im, Image.new('RGBA', (W, H), (14, 11, 9, 120)))
        d = ImageDraw.Draw(im, 'RGBA'); a = R.fade_in(t)
        px0, py0, px1, py1 = 110, 330, W - 110, 1180
        page = Image.new('RGBA', (px1 - px0, py1 - py0), (232, 214, 176, int(245 * a))); pd = ImageDraw.Draw(page)
        for k in range(0, page.width, 70): pd.line([(k, 0), (k, page.height)], fill=(150, 110, 70, int(60 * a)), width=2)
        pd.rectangle([0, 0, page.width - 1, page.height - 1], outline=(120, 70, 40, int(255 * a)), width=6)
        R.comp(im, page, (px0, py0)); d = ImageDraw.Draw(im, 'RGBA')
        lines = ['« Tham đất người…', 'đất chưa lấy được,', 'đã hại chính con mình', 'và dân mình. »']
        for i, l in enumerate(lines):
            la = int(255 * R.fade_in(t - 0.5 - i * 0.7)); R.text_center(d, py0 + 110 + i * 120, l, R.F_TITLE(70), (60, 30, 18, la))
        sa = int(255 * R.fade_in(t - 3.0)); R.text_center(d, py0 + 650, '— Ngô Sĩ Liên', R.F_SEMI(46), (120, 40, 26, sa))
        R.text_center(d, py0 + 720, 'Đại Việt sử ký toàn thư', R.F_REG(36), (90, 60, 40, sa))
        seal(im, px1 - 70, py1 - 70, 130, ['NGÔ', 'SĨ LIÊN'], t - 3.0)
        return im

    @mk('m_rewind')
    def _(im0, t, dur, ctx, seg, idx):
        im, S, z = base(idx, t); p = ease(clamp01((t - 0.4) / (dur - 0.8)))
        gray = im.convert('L').convert('RGB'); im = Image.blend(im, gray, 0.6 * p); R.comp(im, Image.new('RGBA', (W, H), (70, 46, 20, int(80 * p))))
        d = ImageDraw.Draw(im, 'RGBA'); y = int(round(938 - (938 + 111) * p)); y = y if y != 0 else -1
        R.text_center(d, 300, R.year_label(y), R.F_TITLE(150), R.GOLD2 + (255,))
        R.text_center(d, 480, '◀  ~1.050 năm (theo Trần Trọng Kim)', R.F_SEMI(42), R.CREAM + (230,))
        x0, x1, yy = 140, W - 140, 600; xm = x1 - (x1 - x0) * p
        d.line([(xm, yy), (x1, yy)], fill=R.RED + (230,), width=10); d.text((x1 - 50, yy + 20), '938', font=R.F_SEMI(34), fill=R.CREAM + (220,))
        if p > 0.95: d.text((x0 - 40, yy + 20), '111 TCN', font=R.F_SEMI(34), fill=R.CREAM + (220,))
        note(d); return im

    @mk('m_question')
    def _(im0, t, dur, ctx, seg, idx):
        im, S, z = base(idx, t); gx, gy = S(*GIAO); s = sc_(z)
        glow(im, gx, gy, 260 * z / 0.8, (243, 210, 122), 0.55)
        for k, (dx, kind) in enumerate(((-230, 'general'), (0, 'king'), (230, 'general'))):
            b = banner_img('?', kind, (90, 80, 70))
            sil = Image.new('RGBA', b.size, (0, 0, 0, 0)); sil.paste((20, 16, 12, 255), (0, 0), b)
            bw, bh = int(b.width * 0.75), int(b.height * 0.75); sil = R.with_alpha(sil.resize((bw, bh)), 0.85 * R.fade_in(t - 0.4 - 0.3 * k))
            R.comp(im, sil, (gx + dx - bw / 2, gy - bh - 20))
        d = ImageDraw.Draw(im, 'RGBA'); head(d, t, 'Trước Ngô Quyền…', 'ai đã giành quyền tự chủ?', y=300, size=88)
        note(d); return im
