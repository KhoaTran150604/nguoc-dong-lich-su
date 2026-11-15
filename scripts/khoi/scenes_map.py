"""Phong cách 'bản đồ hoạt họa' cho render.py (--style map).

Nền là bản đồ cổ giấy dó (minh họa). Camera lia và zoom theo từng câu, kèm cờ, mũi tên, nhãn.
Quy tắc: luôn ghi 'minh họa, ranh giới và vị trí gần đúng'; không vẽ đường biên giới hiện đại sắc nét;
không đặt điểm cho địa danh chưa rõ vị trí (Hải Môn).
"""
import base64, io, json, math, os, random
import numpy as np
from PIL import Image, ImageDraw, ImageFilter
from shapely.geometry import shape, box, Polygon, MultiPolygon, Point
from shapely.ops import unary_union
import cairosvg

Image.MAX_IMAGE_PIXELS = None
COS = math.cos(math.radians(21)); LON0, LAT0, S0 = 96.0, 38.0, 160.0
def pj(lon, lat): return ((lon - LON0) * COS * S0, (LAT0 - lat) * S0)
MW, MH = pj(124.0, 5.0)

# Vị trí minh họa (lon, lat)
QC = (113.26, 23.13)      # Quảng Châu – nơi Nam Hán đóng đô (E2b-B18)
DAI_LA = (105.85, 21.03)
DUONG_LAM = (105.47, 21.15)
BD = (106.82, 20.86)      # cửa Bạch Đằng (minh họa, cửa sông xưa nằm sâu hơn – E2-F42)
GIAO = (105.9, 21.0)
ROUTE = [(112.4, 21.3), (110.6, 20.6), (109.0, 20.4), (107.7, 20.6), (107.1, 20.78), BD]

def build_map(path):
    if os.path.exists(path): return Image.open(path).convert('RGB')
    root = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    reg = json.load(open(os.path.join(root, 'data/region.json')))
    view = box(LON0, 5.0, 124.0, LAT0)
    def proj(g):
        ring = lambda c: [pj(x, y) for x, y in c]
        polys = [g] if g.geom_type == 'Polygon' else list(g.geoms)
        return MultiPolygon([Polygon(ring(p.exterior.coords), [ring(i.coords) for i in p.interiors]) for p in polys if not p.is_empty])
    land = unary_union([shape(v).intersection(view) for v in reg.values()])
    LP = proj(land).buffer(0)
    def d_of(g):
        polys = [g] if g.geom_type == 'Polygon' else list(g.geoms); out = []
        for p in polys:
            if p.is_empty: continue
            out.append('M' + ' L'.join(f'{x:.1f},{y:.1f}' for x, y in p.exterior.coords) + ' Z')
            for i in p.interiors: out.append('M' + ' L'.join(f'{x:.1f},{y:.1f}' for x, y in i.coords) + ' Z')
        return ' '.join(out)
    def texture(w, h, base, var, seed):
        rng = np.random.default_rng(seed)
        n = rng.random((h // 8 + 1, w // 8 + 1)); im = Image.fromarray((n * 255).astype('uint8')).resize((w, h), Image.BICUBIC).filter(ImageFilter.GaussianBlur(6))
        a = np.asarray(im).astype(float) / 255
        rgb = np.stack([np.clip(base[i] + (a - 0.5) * var, 0, 255) for i in range(3)], -1).astype('uint8')
        buf = io.BytesIO(); Image.fromarray(rgb).save(buf, 'JPEG', quality=80); return 'data:image/jpeg;base64,' + base64.b64encode(buf.getvalue()).decode()
    tw, th = int(MW / 2), int(MH / 2)
    P = [f'<defs><clipPath id="lc"><path d="{d_of(LP)}"/></clipPath></defs>',
         f'<image href="{texture(tw, th, (70, 98, 108), 50, 1)}" x="0" y="0" width="{MW:.0f}" height="{MH:.0f}" preserveAspectRatio="none"/>']
    for i, dist in enumerate([40, 25, 12]):
        ring = LP.buffer(dist).difference(LP.buffer(dist - 3))
        P.append(f'<path d="{d_of(ring)}" fill="#A9C4C9" opacity="{0.18 + 0.12 * i:.2f}"/>')
    P.append(f'<image href="{texture(tw, th, (205, 178, 132), 55, 2)}" x="0" y="0" width="{MW:.0f}" height="{MH:.0f}" preserveAspectRatio="none" clip-path="url(#lc)"/>')
    P.append(f'<path d="{d_of(LP)}" fill="none" stroke="#5A3A20" stroke-width="4"/>')
    # sông (minh họa): sông Hồng, sông Bạch Đằng, sông Châu Giang
    for pts in [[(103.6, 22.6), (104.6, 21.9), (105.3, 21.3), (105.9, 20.9), (106.5, 20.3)], [(106.3, 21.15), (106.6, 20.98), BD],
                [(110.3, 23.5), (111.6, 23.3), (112.6, 23.1), (113.4, 22.8)]]:
        P.append('<path d="M' + ' L'.join(f'{pj(*p)[0]:.1f},{pj(*p)[1]:.1f}' for p in pts) + '" fill="none" stroke="#5F8C9A" stroke-width="7" stroke-linecap="round" stroke-linejoin="round"/>')
    rnd = random.Random(7); inner = LP.buffer(-40); cnt = 0
    while cnt < 150:
        lon = rnd.uniform(100, 120); lat = rnd.uniform(14, 30.5); x, y = pj(lon, lat)
        if inner.contains(Point(x, y)):
            s = rnd.uniform(0.4, 0.7)
            P.append(f'<g transform="translate({x:.0f} {y:.0f}) scale({s:.2f})"><polygon points="-40,20 0,-34 40,20" fill="#A88A62" stroke="#5A3A20" stroke-width="3"/><polygon points="0,-34 40,20 8,20" fill="#7A5E40"/></g>'); cnt += 1
    svg = f'<svg xmlns="http://www.w3.org/2000/svg" width="{MW:.0f}" height="{MH:.0f}">{"".join(P)}</svg>'
    im = Image.open(io.BytesIO(cairosvg.svg2png(bytestring=svg.encode()))).convert('RGB')
    # tông mực: tối lại một chút cho hợp nhận diện kênh
    arr = np.asarray(im).astype(float); arr = arr * 0.82 + np.array([20, 17, 15]) * 0.18
    im = Image.fromarray(arr.clip(0, 255).astype('uint8')); im.save(path); return im

def register(R, ctx, work, segs, timeline):
    W, H = R.W, R.H
    BIG = build_map(os.path.join(work, 'map_big.png'))
    ease, clamp01 = R.ease, R.clamp01
    # camera theo từng câu: (lon, lat, zoom)  zoom = px khung / px bản đồ
    WIDE = (109.6, 22.2, 0.52); FAR = (109.0, 22.5, 0.36)
    CAM = {'chuky_hold': WIDE, 'giao_vuong': (109.6, 22.3, 0.6), 'hai_mon': (110.2, 22.0, 0.58), 'bach_dang': (107.6, 20.9, 1.15),
           'doi_dau': (109.4, 22.0, 0.55), 'lui': FAR, 'so1050': FAR, 'van_xuan': (105.9, 21.0, 0.95), 'thanh_62': (106.2, 20.8, 0.8),
           'phung_hung': (105.6, 21.1, 1.25), 'ran_vo': (111.0, 25.0, 0.5)}
    cams = [CAM.get(s['scene'], WIDE) for s in segs]
    def cam_at(idx, tl):
        prev = cams[idx - 1] if idx > 0 else WIDE; cur = cams[idx]; u = ease(clamp01(tl / 1.4))
        lerp = lambda a, b: a + (b - a) * u
        return (lerp(prev[0], cur[0]), lerp(prev[1], cur[1]), prev[2] * (cur[2] / prev[2]) ** u)
    SH = Image.new('RGBA', (W, H), (0, 0, 0, 0)); _d = ImageDraw.Draw(SH, 'RGBA')
    for i in range(640): _d.line([(0, i), (W, i)], fill=(14, 11, 9, int(235 * (1 - i / 640) ** 0.8)))
    for i in range(560): _d.line([(0, H - i), (W, H - i)], fill=(14, 11, 9, int(230 * (1 - i / 560) ** 0.8)))
    def view(c, drift):
        lon, lat, z = c; z *= 1 + 0.015 * drift
        bx, by = pj(lon, lat); cw, ch = W / z, H / z
        x0, y0 = bx - cw / 2, by - ch * 0.48
        im = BIG.crop((int(x0), int(y0), int(x0 + cw), int(y0 + ch))).resize((W, H), Image.BILINEAR)
        R.comp(im, SH)
        S = lambda lon_, lat_: ((pj(lon_, lat_)[0] - x0) * z, (pj(lon_, lat_)[1] - y0) * z)
        return im, S, z
    def minh_hoa(d):
        d.text((48, 1700), 'Bản đồ minh họa · ranh giới và vị trí gần đúng', font=R.F_REG(28), fill=R.CREAM + (170,))
    def flag(d, x, y, col, name, a=1.0, sc=1.0):
        A = int(255 * a); h = 120 * sc
        d.line([(x, y), (x, y - h)], fill=(40, 26, 16, A), width=int(6 * sc))
        d.polygon([(x, y - h), (x + 70 * sc, y - h + 18 * sc), (x, y - h + 40 * sc)], fill=col + (A,))
        d.ellipse([x - 10, y - 5, x + 10, y + 5], fill=(0, 0, 0, int(A * 0.4)))
        f = R.F_TITLE(int(40 * sc)); w = d.textlength(name, font=f)
        d.rounded_rectangle([x - w / 2 - 14, y + 12, x + w / 2 + 14, y + 12 + 54 * sc], radius=10, fill=(20, 17, 15, int(A * 0.8)))
        d.text((x - w / 2, y + 14), name, font=f, fill=R.CREAM + (A,))
    def region_glow(im, S, z, col, a, r_deg=1.3, center=GIAO):
        cx, cy = S(*center); r = r_deg * S0 * z
        g = Image.new('RGBA', (W, H), (0, 0, 0, 0)); ImageDraw.Draw(g).ellipse([cx - r, cy - r * 0.8, cx + r, cy + r * 0.8], fill=col + (int(110 * a),))
        R.comp(im, g.filter(ImageFilter.GaussianBlur(40)))
    def headline(d, t, txt, sub=None, y=330):
        a = int(255 * R.fade_in(t)); R.text_center(d, y, txt, R.F_TITLE(96), R.GOLD2 + (a,))
        if sub: R.text_center(d, y + 120, sub, R.F_SEMI(44), R.CREAM + (a,))
    def dashed(d, pts, u, col, width=8, dash=26):
        L = [math.dist(pts[i], pts[i + 1]) for i in range(len(pts) - 1)]; tot = sum(L); target = tot * u; acc = 0
        for i, l in enumerate(L):
            if acc >= target: break
            (x1, y1), (x2, y2) = pts[i], pts[i + 1]; n = max(1, int(l / dash))
            for k in range(0, n, 2):
                s0 = k / n; s1 = min((k + 1) / n, 1)
                if acc + s0 * l > target: break
                s1 = min(s1, (target - acc) / l)
                d.line([(x1 + (x2 - x1) * s0, y1 + (y2 - y1) * s0), (x1 + (x2 - x1) * s1, y1 + (y2 - y1) * s1)], fill=col, width=width)
            acc += l
        return pts[-1] if u >= 1 else None
    def base(idx, tl):
        T = timeline[idx][0] + tl
        return view(cam_at(idx, tl), (T % 10) / 10)

    def mk(name):
        def deco(fn): R.SCENES['map_' + name] = fn; return fn
        return deco

    @mk('chuky_hold')
    def _(im0, t, dur, ctx, seg, idx):
        im, S, z = base(idx, t); d = ImageDraw.Draw(im, 'RGBA')
        a = int(255 * (1 - R.fade_in(t, 0.8)))
        # chuyển từ màn chữ ký sang bản đồ
        if a > 0:
            cover = im0.copy(); R.SCENES['chuky_hold'](cover, t, dur, ctx, seg); im = Image.blend(im, cover, a / 255)
            d = ImageDraw.Draw(im, 'RGBA')
        R.text_center(d, 330, '938', R.F_TITLE(150), R.GOLD2 + (int(255 * R.fade_in(t - 0.3)),))
        x, y = S(*QC); d.text((x - 90, y - 30), 'NAM HÁN', font=R.F_TITLE(48), fill=(120, 30, 22, 230))
        x, y = S(*GIAO); d.text((x - 120, y - 140), 'GIAO CHÂU', font=R.F_TITLE(44), fill=(70, 46, 20, 230))
        minh_hoa(d); return im

    @mk('giao_vuong')
    def _(im0, t, dur, ctx, seg, idx):
        im, S, z = base(idx, t); u = ease(clamp01((t - 0.6) / 2.0))
        region_glow(im, S, z, (230, 220, 200), 0.6 + 0.4 * math.sin(t * 3))
        d = ImageDraw.Draw(im, 'RGBA'); flag(d, *S(*QC), R.RED, 'Quảng Châu')
        q = S(*QC); g = S(*GIAO)
        dashed(d, [q, ((q[0] + g[0]) / 2, min(q[1], g[1]) - 120), g], u, R.GOLD2 + (230,), 7)
        if u > 0.95:
            R.text_center(d, int(g[1] - 30), '?', R.F_TITLE(110), R.GOLD2 + (int(255 * R.fade_in(t - 2.6)),))
        R.seal(im, t, 540, 520, 230, ['GIAO', 'VƯƠNG'])
        d = ImageDraw.Draw(im, 'RGBA')
        R.text_center(d, 660, '« vua đất Giao »', R.F_SEMI(46), R.CREAM + (int(255 * R.fade_in(t - 0.5)),))
        minh_hoa(d); return im

    @mk('hai_mon')
    def _(im0, t, dur, ctx, seg, idx):
        im, S, z = base(idx, t); d = ImageDraw.Draw(im, 'RGBA'); flag(d, *S(*QC), R.RED, 'Quảng Châu')
        a = int(255 * R.fade_in(t - 0.3)); bx, by = 110, 390
        d.rounded_rectangle([bx, by, W - bx, by + 250], radius=22, fill=(20, 17, 15, int(a * 0.85)), outline=R.GOLD + (a,), width=3)
        d.polygon([(bx + 60, by + 70), (bx + 120, by + 88), (bx + 60, by + 108)], fill=R.RED + (a,)); d.line([(bx + 60, by + 60), (bx + 60, by + 190)], fill=R.CREAM + (a,), width=5)
        d.text((bx + 110, by + 40), 'HẢI MÔN', font=R.F_TITLE(84), fill=R.GOLD2 + (a,))
        d.text((bx + 110, by + 140), 'vua Nam Hán đóng quân tiếp ứng', font=R.F_SEMI(38), fill=R.CREAM + (a,))
        d.text((bx + 110, by + 190), '(vị trí chưa rõ – không đánh dấu trên bản đồ)', font=R.F_REG(30), fill=R.COPPER + (a,))
        minh_hoa(d); return im

    @mk('bach_dang')
    def _(im0, t, dur, ctx, seg, idx):
        im, S, z = base(idx, t); d = ImageDraw.Draw(im, 'RGBA')
        u = ease(clamp01((t - 0.8) / (dur * 0.55)))
        pts = [S(*p) for p in ROUTE]; dashed(d, pts, u, R.RED + (235,), 9)
        if u > 0:  # mũi tên tại đầu đoạn
            k = min(len(pts) - 1, max(1, int(u * (len(pts) - 1)) + 1)); (x1, y1), (x2, y2) = pts[k - 1], pts[k]
            f = u * (len(pts) - 1) - (k - 1); hx, hy = x1 + (x2 - x1) * min(f, 1), y1 + (y2 - y1) * min(f, 1)
            ang = math.atan2(y2 - y1, x2 - x1)
            d.polygon([(hx + 26 * math.cos(ang), hy + 26 * math.sin(ang)), (hx + 16 * math.cos(ang + 2.4), hy + 16 * math.sin(ang + 2.4)), (hx + 16 * math.cos(ang - 2.4), hy + 16 * math.sin(ang - 2.4))], fill=R.RED + (255,))
        x, y = S(*BD); d.text((x - 150, y + 40), 'Cửa Bạch Đằng', font=R.F_TITLE(40), fill=(30, 52, 60, 240))
        if u > 0.98:
            a = int(255 * R.fade_in(t - 0.8 - dur * 0.55)); r = 40
            d.line([(x - r, y - r), (x + r, y + r)], fill=R.GOLD2 + (a,), width=12); d.line([(x - r, y + r), (x + r, y - r)], fill=R.GOLD2 + (a,), width=12)
            R.text_center(d, 360, 'quá nửa chết đuối', R.F_TITLE(84), R.GOLD2 + (a,))
        minh_hoa(d); return im

    @mk('doi_dau')
    def _(im0, t, dur, ctx, seg, idx):
        im, S, z = base(idx, t); d = ImageDraw.Draw(im, 'RGBA')
        flag(d, *S(*QC), R.RED, 'NAM HÁN', 1.0, 1.2)
        flag(d, *S(*BD), R.GOLD2, 'NGÔ QUYỀN', R.fade_in(t - dur * 0.45), 1.2)
        pts = [S(*p) for p in ROUTE]; dashed(d, pts[:-1], 1.0, R.RED + (150,), 6)
        if t > dur * 0.45:
            x, y = S(*ROUTE[-2]); a = int(255 * R.fade_in(t - dur * 0.45))
            d.line([(x - 10, y - 70), (x - 10, y + 70)], fill=R.GOLD2 + (a,), width=12)
        minh_hoa(d); return im

    @mk('lui')
    def _(im0, t, dur, ctx, seg, idx):
        im, S, z = base(idx, t)
        p = ease(clamp01((t - 0.3) / (dur - 0.6)))
        sep = Image.new('RGBA', (W, H), (60, 40, 20, int(90 * p))); R.comp(im, sep)
        d = ImageDraw.Draw(im, 'RGBA'); y = int(round(938 - (938 + 111) * p)); y = y if y != 0 else -1
        R.text_center(d, 330, R.year_label(y), R.F_TITLE(150), R.GOLD2 + (255,))
        R.text_center(d, 510, '◀  ngược dòng thời gian', R.F_MED(40), R.CREAM + (220,))
        minh_hoa(d); return im

    @mk('so1050')
    def _(im0, t, dur, ctx, seg, idx):
        im, S, z = base(idx, t); R.comp(im, Image.new('RGBA', (W, H), (60, 40, 20, 90)))
        region_glow(im, S, z, R.RED, 0.9, 1.6)
        d = ImageDraw.Draw(im, 'RGBA'); a = int(255 * R.fade_in(t))
        n = int(1050 * ease(clamp01((t - 0.3) / 1.2)))
        R.text_center(d, 300, f'~{n:,}'.replace(',', '.') + ' năm', R.F_TITLE(120), R.GOLD2 + (a,))
        R.text_center(d, 450, 'bị phương Bắc đô hộ', R.F_SEMI(46), R.CREAM + (a,))
        R.text_center(d, 515, '(theo cách tính của Trần Trọng Kim)', R.F_REG(34), R.COPPER + (a,))
        minh_hoa(d); return im

    @mk('van_xuan')
    def _(im0, t, dur, ctx, seg, idx):
        im, S, z = base(idx, t); region_glow(im, S, z, R.GOLD2, R.fade_in(t - 0.5), 1.0)
        d = ImageDraw.Draw(im, 'RGBA'); a = int(255 * R.fade_in(t - 0.5))
        x, y = S(*GIAO); R.text_center(d, int(y - 60), 'VẠN XUÂN', R.F_TITLE(80), (90, 50, 14, a))
        R.text_center(d, 330, '544', R.F_TITLE(140), R.GOLD2 + (a,)); R.text_center(d, 490, 'Lý Bí xưng đế, đặt tên nước', R.F_SEMI(44), R.CREAM + (a,))
        minh_hoa(d); return im

    @mk('thanh_62')
    def _(im0, t, dur, ctx, seg, idx):
        im, S, z = base(idx, t); sw = ease(clamp01((t - dur * 0.55) / 1.2))
        region_glow(im, S, z, R.GOLD2, 1 - sw, 1.0); region_glow(im, S, z, R.RED, sw, 1.2)
        d = ImageDraw.Draw(im, 'RGBA')
        a1 = int(255 * clamp01(1 - 2 * sw)); a2 = int(255 * clamp01(2 * sw - 1))
        R.text_center(d, 320, '62 năm tự chủ', R.F_TITLE(96), R.GOLD2 + (max(a1, 0),))
        R.text_center(d, 440, 'Lý Nam Đế · Triệu Việt Vương · Hậu Lý', R.F_SEMI(38), R.CREAM + (max(a1, 0),))
        R.text_center(d, 320, 'Thuộc Tùy, Đường', R.F_TITLE(96), R.GOLD2 + (a2,))
        R.text_center(d, 440, 'hơn 300 năm (theo cách tính của Toàn thư)', R.F_SEMI(38), R.CREAM + (a2,))
        minh_hoa(d); return im

    @mk('phung_hung')
    def _(im0, t, dur, ctx, seg, idx):
        im, S, z = base(idx, t); d = ImageDraw.Draw(im, 'RGBA'); x, y = S(*DUONG_LAM)
        for k in range(3):
            r = 30 + ((t * 60 + k * 50) % 150); d.ellipse([x - r, y - r, x + r, y + r], outline=R.GOLD2 + (int(200 * (1 - r / 180)),), width=5)
        flag(d, x, y, R.GOLD2, 'Đường Lâm', R.fade_in(t - 0.4))
        a = int(255 * R.fade_in(t - 0.2)); R.text_center(d, 320, '791', R.F_TITLE(140), R.GOLD2 + (a,))
        R.text_center(d, 480, 'Phùng Hưng dấy binh vây phủ thành', R.F_SEMI(44), R.CREAM + (a,))
        minh_hoa(d); return im

    @mk('ran_vo')
    def _(im0, t, dur, ctx, seg, idx):
        im, S, z = base(idx, t); d = ImageDraw.Draw(im, 'RGBA'); p = ease(clamp01((t - 0.8) / 2.2))
        cracks = [[(103.5, 29.5), (106.5, 27.2), (108.2, 28.4), (111.0, 26.4), (113.8, 27.6), (117.0, 25.6)],
                  [(108.2, 28.4), (109.0, 30.2)], [(111.0, 26.4), (110.2, 24.6)], [(113.8, 27.6), (115.8, 29.6)]]
        for c in cracks: dashed(d, [S(*q) for q in c], p, R.RED + (235,), 7, dash=400)
        a = int(255 * R.fade_in(t)); R.text_center(d, 320, 'THẾ KỶ X', R.F_TITLE(120), R.GOLD2 + (a,))
        R.text_center(d, 470, 'phương Bắc rạn vỡ', R.F_SEMI(48), R.CREAM + (a,))
        minh_hoa(d); return im
