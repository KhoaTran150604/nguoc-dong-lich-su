"""Bản đồ VÙNG theo style kênh (giấy cổ, núi gạch bóng, cây, sóng) – dùng chung cho cả series.

Đường bờ lấy từ dữ liệu thật (data/region.json, Natural Earth) nhưng KHÔNG vẽ biên giới hiện đại.
Lãnh thổ các phe là vùng tô màu MINH HỌA, truyền vào qua cấu hình từng tập.

Dùng:
    cfg = dict(bbox=(101, 16, 118.5, 26.5), seed=3,
               vung=[dict(poly=[(lon,lat),...], mau='#D9B44A', ten='TĨNH HẢI QUÂN', o=(lon,lat), co=40)],
               song=[[(lon,lat),...], ...],
               diadanh=[dict(ten='Đại La', o=(105.85,21.03), loai='thanh'|'kinh'|'cham'|'chu', co=30)],
               bien=[dict(ten='BIỂN', o=(lon,lat), co=60)])
    m = BanDoVung(cfg, px_per_deg=300)          # vẽ nền 1 lần, cache PNG theo cấu hình
    img = m.view(W, H, cam=(lon, lat, rong_do))  # khung hình theo camera (tâm, bề rộng tính bằng độ kinh)
    x, y = m.to_screen(lon, lat, W, H, cam)      # đặt cờ, mũi tên lên đúng chỗ
"""
import hashlib, io, json, math, os, random
import numpy as np
import cairosvg
from PIL import Image, ImageFilter
from shapely.geometry import Point, Polygon, box, shape
from shapely.ops import unary_union

Image.MAX_IMAGE_PIXELS = None
ROOT = os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', '..'))
CACHE = os.path.join(ROOT, 'assets', 'bando', '_cache')
INK, BRONZE = '#2A1A10', '#C9A24A'
LAND, MUD, SEA = '#D8BE8E', '#A8916A', '#3F7088'
COS = math.cos(math.radians(21))

def _texture(w, h, seed):
    rng = np.random.default_rng(seed)
    n = rng.random((h // 8 + 1, w // 8 + 1))
    a = np.asarray(Image.fromarray((n * 255).astype('uint8')).resize((w, h), Image.BICUBIC).filter(ImageFilter.GaussianBlur(6))).astype(float) / 255
    fine = rng.random((h, w)) * 0.25
    return np.clip(128 + ((a - 0.5) * 0.9 + (fine - 0.12) * 0.4) * 70, 0, 255).astype('uint8')

class BanDoVung:
    def __init__(self, cfg, px_per_deg=300):
        self.cfg, self.S = cfg, px_per_deg
        self.lon0, self.lat0, self.lon1, self.lat1 = cfg['bbox']
        self.w = int((self.lon1 - self.lon0) * COS * self.S); self.h = int((self.lat1 - self.lat0) * self.S)
        key = hashlib.sha1((json.dumps(cfg, sort_keys=True, default=str) + str(px_per_deg) + open(__file__).read()).encode()).hexdigest()[:12]
        os.makedirs(CACHE, exist_ok=True); path = os.path.join(CACHE, f'vung-{key}.png')
        if not os.path.exists(path): self._build(path)
        self.img = Image.open(path).convert('RGB')

    def pj(self, lon, lat): return ((lon - self.lon0) * COS * self.S, (self.lat1 - lat) * self.S)

    def _d(self, g):
        polys = [g] if g.geom_type == 'Polygon' else [p for p in getattr(g, 'geoms', []) if p.geom_type == 'Polygon']
        out = []
        for p in polys:
            if p.is_empty: continue
            out.append('M' + ' L'.join(f'{x:.1f},{y:.1f}' for x, y in (self.pj(*c) for c in p.exterior.coords)) + ' Z')
            for r in p.interiors: out.append('M' + ' L'.join(f'{x:.1f},{y:.1f}' for x, y in (self.pj(*c) for c in r.coords)) + ' Z')
        return ' '.join(out)

    def _build(self, path):
        cfg, S = self.cfg, self.S; k = S / 300          # kích thước ký hiệu theo độ phân giải nền
        reg = json.load(open(os.path.join(ROOT, 'data', 'region.json')))
        view = box(self.lon0 - 1, self.lat0 - 1, self.lon1 + 1, self.lat1 + 1)
        land = unary_union([shape(v).buffer(0) for v in reg.values()]).intersection(view)
        land = land.simplify(0.01)
        rng = random.Random(cfg.get('seed', 3))
        o = [f'<svg xmlns="http://www.w3.org/2000/svg" width="{self.w}" height="{self.h}">', f'<rect width="{self.w}" height="{self.h}" fill="{SEA}"/>']
        for i, dist in enumerate([0.22, 0.14, 0.07]):   # vòng sóng ven bờ
            ring = land.buffer(dist).difference(land.buffer(dist - 0.02))
            o.append(f'<path d="{self._d(ring)}" fill="#C4DCE2" opacity="{0.22 + 0.12*i:.2f}"/>')
        o.append(f'<path d="{self._d(land.buffer(0.03))}" fill="{MUD}"/>')
        o.append(f'<path d="{self._d(land)}" fill="{LAND}"/>')
        for v in cfg.get('vung', []):                  # lãnh thổ minh họa
            g = Polygon(v['poly']).intersection(land)
            o.append(f'<path d="{self._d(g)}" fill="{v["mau"]}" opacity="{v.get("dam", 0.32)}"/>')
            o.append(f'<path d="{self._d(g)}" fill="none" stroke="{v["mau"]}" stroke-width="{4*k:.1f}" stroke-dasharray="{14*k:.0f} {8*k:.0f}" opacity="0.8"/>')
        o.append(f'<path d="{self._d(land)}" fill="none" stroke="#5A3A20" stroke-width="{3.2*k:.1f}"/>')
        for line in cfg.get('song', []):
            pts = ' '.join(f'{x:.1f},{y:.1f}' for x, y in (self.pj(*p) for p in line))
            o.append(f'<polyline points="{pts}" fill="none" stroke="#5F8EA0" stroke-width="{6*k:.1f}" stroke-linecap="round" stroke-linejoin="round"/>')
        # sóng biển
        for _ in range(int((self.lon1 - self.lon0) * (self.lat1 - self.lat0) * 1.6)):
            lon, lat = rng.uniform(self.lon0, self.lon1), rng.uniform(self.lat0, self.lat1)
            if land.buffer(0.25).contains(Point(lon, lat)): continue
            x, y = self.pj(lon, lat); s = 9 * k
            o.append(f'<path d="M{x:.0f},{y:.0f} q{s:.1f},{-s:.1f} {2*s:.1f},0 q{s:.1f},{s:.1f} {2*s:.1f},0" fill="none" stroke="#D6E6EA" stroke-width="{2*k:.1f}" opacity="0.5"/>')
        # núi + cây trong đất liền (tránh chỗ có chữ)
        keep = [Point(*d['o']).buffer(0.35) for d in cfg.get('diadanh', [])] + [Point(*v['o']).buffer(0.9) for v in cfg.get('vung', []) if 'o' in v]
        avoid = unary_union(keep) if keep else Point(0, 0).buffer(0.001)
        inner = land.buffer(-0.12)
        hills = cfg.get('nui', 1.0)
        for _ in range(int((self.lon1 - self.lon0) * (self.lat1 - self.lat0) * 2.4 * hills)):
            lon, lat = rng.uniform(self.lon0, self.lon1), rng.uniform(self.lat0, self.lat1); pt = Point(lon, lat)
            if not inner.contains(pt) or avoid.contains(pt): continue
            x, y = self.pj(lon, lat)
            if rng.random() < 0.55:
                s = rng.uniform(0.7, 1.3) * 1.6 * k
                o.append(f'<g transform="translate({x:.0f} {y:.0f}) scale({s:.2f})"><path d="M-22,10 Q-12,-14 0,-20 Q12,-14 22,10 Z" fill="#B49870" stroke="#5A3A20" stroke-width="1.6"/>'
                         f'<path d="M0,-20 Q12,-14 22,10 L6,10 Q8,-4 0,-20 Z" fill="#8E7350"/>' + ''.join(f'<line x1="{4+j*5}" y1="{-12+j*6}" x2="{9+j*5}" y2="{-4+j*6}" stroke="#5A3A20" stroke-width="0.9"/>' for j in range(3)) + '</g>')
            else:
                s = rng.uniform(0.8, 1.2) * 1.8 * k
                o.append(f'<g transform="translate({x:.0f} {y:.0f}) scale({s:.2f})"><line x1="0" y1="0" x2="0" y2="6" stroke="#4A3220" stroke-width="1.6"/><circle cy="-3" r="5.5" fill="#6B8250" stroke="#3E4E2E" stroke-width="1"/></g>')
        # chữ: tên vùng, biển, địa danh
        def txt(lon, lat, t, size, col=INK, ls=3, w='800', fam='Playfair Display'):
            x, y = self.pj(lon, lat)
            return (f'<text x="{x:.0f}" y="{y:.0f}" font-family="{fam}" font-weight="{w}" font-size="{size*k:.0f}" fill="none" stroke="#F2E6CC" stroke-width="{size*k*0.14:.1f}" stroke-linejoin="round" text-anchor="middle" letter-spacing="{ls*k:.0f}" opacity="0.85">{t}</text>'
                    f'<text x="{x:.0f}" y="{y:.0f}" font-family="{fam}" font-weight="{w}" font-size="{size*k:.0f}" fill="{col}" text-anchor="middle" letter-spacing="{ls*k:.0f}">{t}</text>')
        for v in cfg.get('vung', []):
            if v.get('ten'): o.append(txt(*v['o'], v['ten'], v.get('co', 54), v.get('mau_chu', INK), 6))
        for b in cfg.get('bien', []):
            x, y = self.pj(*b['o']); s = b.get('co', 60) * k
            o.append(f'<text x="{x:.0f}" y="{y:.0f}" font-family="Playfair Display" font-weight="800" font-size="{s:.0f}" fill="#E8EEF0" text-anchor="middle" letter-spacing="{10*k:.0f}">{b["ten"]}</text>')
        for d in cfg.get('diadanh', []):
            x, y = self.pj(*d['o']); s = d.get('co', 46); loai = d.get('loai', 'cham'); lx, ly = d.get('lech', (0, 0))
            if loai in ('thanh', 'kinh'):
                g = 1.5 * k * (1.25 if loai == 'kinh' else 1)
                o.append(f'<g transform="translate({x:.0f} {y:.0f}) scale({g:.2f})"><rect x="-22" y="-18" width="44" height="26" fill="#C8A878" stroke="#3A2618" stroke-width="3"/>'
                         f'<polygon points="-26,-18 0,-38 26,-18" fill="#8A3A24" stroke="#3A2618" stroke-width="3"/>' + ('<rect x="-6" y="-8" width="12" height="16" fill="#3A2618"/>' if loai == 'kinh' else '') + '</g>')
                o.append(txt(d['o'][0] + lx, d['o'][1] - 0.3 + ly, d['ten'], s))
            elif loai == 'cham':
                o.append(f'<circle cx="{x:.0f}" cy="{y:.0f}" r="{7*k:.1f}" fill="{INK}" stroke="#F2E6CC" stroke-width="{2*k:.1f}"/>')
                o.append(txt(d['o'][0] + lx, d['o'][1] - 0.25 + ly, d['ten'], s, ls=1))
            else:
                o.append(txt(d['o'][0] + lx, d['o'][1] + ly, d['ten'], s, d.get('mau', '#1E3A44'), 2))
        o.append('</svg>')
        png = cairosvg.svg2png(bytestring=''.join(o).encode())
        im = Image.open(io.BytesIO(png)).convert('RGB')
        tex = _texture(self.w, self.h, cfg.get('seed', 3))
        arr = np.asarray(im).astype(float) * (0.86 + 0.28 * tex[..., None] / 255)
        Image.fromarray(np.clip(arr, 0, 255).astype('uint8')).save(path)

    # ---- camera ----
    def _box(self, W, H, cam):
        lon, lat, wdeg = cam; cx, cy = self.pj(lon, lat)
        vw = wdeg * COS * self.S; vh = vw * H / W
        return cx - vw / 2, cy - vh / 2, vw, vh

    def view(self, W, H, cam):
        x, y, vw, vh = self._box(W, H, cam)
        x = max(0, min(self.w - vw, x)); y = max(0, min(self.h - vh, y))
        return self.img.crop((int(x), int(y), int(x + vw), int(y + vh))).resize((W, H), Image.LANCZOS)

    def to_screen(self, lon, lat, W, H, cam):
        x, y, vw, vh = self._box(W, H, cam)
        x = max(0, min(self.w - vw, x)); y = max(0, min(self.h - vh, y))
        px, py = self.pj(lon, lat)
        return (px - x) * W / vw, (py - y) * H / vh

def lerp_cam(a, b, u):
    """Lia/zoom mượt giữa hai camera (zoom theo hàm mũ cho đều mắt)."""
    return (a[0] + (b[0] - a[0]) * u, a[1] + (b[1] - a[1]) * u, a[2] * (b[2] / a[2]) ** u)
