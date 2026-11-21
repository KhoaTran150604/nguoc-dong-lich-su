"""BÚT – lõi bộ vẽ vector cho nhân vật chibi (thư viện skia, tự vẽ 100% bằng code).

Khác bộ cũ `chibi/ve.py` (Pillow, đa giác + nét đều):
- HÌNH là đường cong Bezier thật (`cong`, `duong`), cộng/trừ/giao khối được (`+ - &`) → tạo hình
  phức tạp (lưỡi liềm = tròn − tròn, tóc = đầu ∩ vùng trên chân tóc) mà không phải tự tính giao điểm.
- NÉT 3 CẤP (luật vẽ đẹp số 1): viền NGOÀI (bóng dáng cả nhân vật) dày nhất, viền TRONG (ranh
  giới bộ phận) vừa, nét CHI TIẾT mảnh và THUÔN hai đầu. Viền ngoài được tự tính = hợp mọi khối
  đã đăng ký, vẽ một lần ở cuối (`chot_vien`).
- BÓNG PHẲNG mép cứng (cel shading) tự tính từ chính khối: `bong()` = khối − khối dịch về phía
  sáng. Màu bóng tự sinh (`toi`) – tối hơn + lệch sắc về tím; sáng (`sang`) lệch về vàng.
  KHÔNG gradient / blur / glow (luật kênh).

Toạ độ đều ở cỡ 1× (px của khung ảnh); `Buc(scale=2)` để xuất ảnh lớn gấp đôi, nét vẫn sắc.
"""
import colorsys
import math
from contextlib import contextmanager

import skia

MUC = '#0A0807'   # mực viền mặc định


# ───────────────────────────── MÀU ─────────────────────────────
def _rgb(h):
    h = h.lstrip('#')
    return int(h[0:2], 16), int(h[2:4], 16), int(h[4:6], 16)


def mau(h, a=255):
    """'#RRGGBB' → màu skia."""
    r, g, b = _rgb(h)
    return skia.ColorSetARGB(a, r, g, b)


def _hex(r, g, b):
    return '#%02X%02X%02X' % tuple(max(0, min(255, round(v * 255))) for v in (r, g, b))


def _doi(h, dl, ds, huong_sac, dh):
    r, g, b = (v / 255 for v in _rgb(h))
    hh, l, s = colorsys.rgb_to_hls(r, g, b)
    d = (huong_sac - hh + 0.5) % 1.0 - 0.5          # đường ngắn nhất trên vòng màu
    hh = (hh + max(-dh, min(dh, d))) % 1.0
    l = max(0.0, min(1.0, l + dl))
    s = max(0.0, min(1.0, s + ds))
    return _hex(*colorsys.hls_to_rgb(hh, l, s))


def toi(h, k=0.12):
    """Màu BÓNG của h: tối hơn k, đậm sắc hơn chút, lệch sắc về tím (như hoạ sĩ tô bóng)."""
    return _doi(h, -k, k * 0.12, 0.75, 0.015 + k * 0.08)


def sang(h, k=0.10):
    """Màu VỆT SÁNG của h: sáng hơn k, lệch sắc về vàng ấm."""
    return _doi(h, k, -k * 0.2, 0.14, 0.02)


# ───────────────────────────── HÌNH ─────────────────────────────
class Hinh:
    """Một khối (skia.Path kín). Phép: a + b (hợp), a - b (trừ), a & b (giao)."""

    def __init__(self, path=None):
        self.p = path if path is not None else skia.Path()

    def _op(self, o, op):
        try:
            return Hinh(skia.Op(self.p, o.p, op))
        except Exception:                      # skia hiếm khi trả lỗi với đường suy biến → giữ nguyên
            return Hinh(skia.Path(self.p))

    def __add__(self, o):
        return self._op(o, skia.PathOp.kUnion_PathOp)

    def __sub__(self, o):
        return self._op(o, skia.PathOp.kDifference_PathOp)

    def __and__(self, o):
        return self._op(o, skia.PathOp.kIntersect_PathOp)

    def bien(self, m):
        q = skia.Path(self.p)
        q.transform(m)
        return Hinh(q)

    def dich(self, dx, dy):
        return self.bien(skia.Matrix.Translate(dx, dy))

    def xoay(self, deg, cx, cy):
        m = skia.Matrix()
        m.setRotate(deg, cx, cy)
        return self.bien(m)

    def co(self, sx, sy=None, cx=0.0, cy=0.0):
        m = skia.Matrix()
        m.setScale(sx, sx if sy is None else sy, cx, cy)
        return self.bien(m)

    def phong(self, d):
        """Nở khối ra đều d px (d<0: co vào)."""
        if d == 0:
            return Hinh(skia.Path(self.p))
        pt = skia.Paint(Style=skia.Paint.kStroke_Style, StrokeWidth=abs(d) * 2,
                        StrokeJoin=skia.Paint.kRound_Join)
        vien = skia.Path()
        pt.getFillPath(self.p, vien)
        return self + Hinh(vien) if d > 0 else self - Hinh(vien)

    @property
    def khung(self):
        r = self.p.getBounds()
        return r.left(), r.top(), r.right(), r.bottom()

    def rong(self):
        return self.p.isEmpty()


def gop(*hs):
    """Hợp nhiều khối."""
    out = Hinh()
    for h in hs:
        if h is not None:
            out = out + h
    return out


# ── khối cơ bản ──
def tron(cx, cy, r):
    p = skia.Path()
    p.addCircle(cx, cy, r)
    return Hinh(p)


def elip(cx, cy, rx, ry, rot=0.0):
    p = skia.Path()
    p.addOval(skia.Rect.MakeLTRB(cx - rx, cy - ry, cx + rx, cy + ry))
    h = Hinh(p)
    return h.xoay(rot, cx, cy) if rot else h


def hop(x0, y0, x1, y1, r=0.0):
    p = skia.Path()
    p.addRRect(skia.RRect.MakeRectXY(skia.Rect.MakeLTRB(x0, y0, x1, y1), r, r))
    return Hinh(p)


def da_giac(pts):
    p = skia.Path()
    p.addPoly([skia.Point(x, y) for x, y in ((q[0], q[1]) for q in pts)], True)
    return Hinh(p)


def thanh(p0, p1, nua, bo=True):
    """Thanh thẳng từ p0→p1, nửa bề ngang `nua`; bo=True: hai đầu tròn."""
    dx, dy = p1[0] - p0[0], p1[1] - p0[1]
    L = math.hypot(dx, dy) or 1.0
    nx, ny = -dy / L * nua, dx / L * nua
    h = da_giac([(p0[0] + nx, p0[1] + ny), (p1[0] + nx, p1[1] + ny),
                 (p1[0] - nx, p1[1] - ny), (p0[0] - nx, p0[1] - ny)])
    if bo:
        h = h + tron(*p0, nua) + tron(*p1, nua)
    return h


# ── đường cong mượt qua các điểm (Catmull-Rom → Bezier bậc 3) ──
def _xy(q):
    return (q[0], q[1])


def _nhon(q):
    return len(q) > 2 and q[2] == 0      # điểm (x, y, 0) = GÓC NHỌN (không làm mượt tại đó)


def _doan(pts, kin, cang):
    n = len(pts)
    out = []
    for i in (range(n) if kin else range(n - 1)):
        a = pts[(i - 1) % n] if kin else pts[max(i - 1, 0)]
        b, c = pts[i], pts[(i + 1) % n]
        d = pts[(i + 2) % n] if kin else pts[min(i + 2, n - 1)]
        t1 = 0 if _nhon(b) else cang
        t2 = 0 if _nhon(c) else cang
        (ax, ay), (bx, by), (cx, cy), (dx, dy) = _xy(a), _xy(b), _xy(c), _xy(d)
        c1 = (bx + (cx - ax) / 6 * t1, by + (cy - ay) / 6 * t1)
        c2 = (cx - (dx - bx) / 6 * t2, cy - (dy - by) / 6 * t2)
        out.append(((bx, by), c1, c2, (cx, cy)))
    return out


def cong(pts, cang=1.0):
    """Khối KÍN mượt đi qua mọi điểm. Điểm (x, y, 0) giữ góc nhọn. cang<1: căng hơn, >1: phồng."""
    p = skia.Path()
    seg = _doan(pts, True, cang)
    p.moveTo(*seg[0][0])
    for _, c1, c2, e in seg:
        p.cubicTo(*c1, *c2, *e)
    p.close()
    return Hinh(p)


def duong(pts, cang=1.0):
    """Đường HỞ mượt (skia.Path) qua các điểm – dùng cho nét."""
    p = skia.Path()
    p.moveTo(*_xy(pts[0]))
    if len(pts) == 2:
        p.lineTo(*_xy(pts[1]))
        return p
    for _, c1, c2, e in _doan(pts, False, cang):
        p.cubicTo(*c1, *c2, *e)
    return p


def mau_diem(pts, n=60, kin=False, cang=1.0):
    """Lấy n điểm đều tham số trên đường mượt qua pts."""
    if len(pts) == 2:
        (x0, y0), (x1, y1) = _xy(pts[0]), _xy(pts[1])
        return [(x0 + (x1 - x0) * i / (n - 1), y0 + (y1 - y0) * i / (n - 1)) for i in range(n)]
    seg = _doan(pts, kin, cang)
    out = []
    per = max(2, n // len(seg))
    for j, (b, c1, c2, e) in enumerate(seg):
        for i in range(per + (1 if j == len(seg) - 1 else 0)):
            t = i / per
            u = 1 - t
            out.append((u ** 3 * b[0] + 3 * u * u * t * c1[0] + 3 * u * t * t * c2[0] + t ** 3 * e[0],
                        u ** 3 * b[1] + 3 * u * u * t * c1[1] + 3 * u * t * t * c2[1] + t ** 3 * e[1]))
    return out


def net_thuon(pts, w0, wm, w1=None, n=80, cang=1.0, dau_tron=True):
    """Nét THUÔN: bề dày w0 (đầu) → wm (giữa) → w1 (cuối) – như nét bút lông. Trả Hinh để tô."""
    w1 = w0 if w1 is None else w1
    q = mau_diem(pts, n, cang=cang)
    m = len(q)
    L, R = [], []
    for i, (x, y) in enumerate(q):
        a, b = q[max(i - 1, 0)], q[min(i + 1, m - 1)]
        dx, dy = b[0] - a[0], b[1] - a[1]
        ln = math.hypot(dx, dy) or 1.0
        t = i / (m - 1)
        s = math.sin(math.pi * min(t, 1 - t))           # 0 ở hai đầu, 1 ở giữa (mượt)
        w = (w0 if t < 0.5 else w1) * (1 - s) + wm * s
        nx, ny = -dy / ln * w / 2, dx / ln * w / 2
        L.append((x + nx, y + ny))
        R.append((x - nx, y - ny))
    h = da_giac(L + R[::-1])
    if dau_tron:
        if w0 > 0.6:
            h = h + tron(*q[0], w0 / 2)
        if w1 > 0.6:
            h = h + tron(*q[-1], w1 / 2)
    return h


# ───────────────────────────── BỨC VẼ ─────────────────────────────
class Buc:
    """Khung ảnh. D = bộ bề dày nét 3 cấp (px ở cỡ 1×): ngoai / trong / ct (chi tiết)."""

    def __init__(self, w, h, nen='#F6F3EC', muc=MUC, D=None, scale=1.0):
        self.w, self.h, self.scale = w, h, scale
        self.muc = muc
        self.D = D or dict(ngoai=9.0, trong=5.0, ct=3.6)
        self.sf = skia.Surface(int(w * scale), int(h * scale))
        self.c = self.sf.getCanvas()
        self.c.scale(scale, scale)
        if nen:
            self.c.clear(mau(nen))
        else:
            self.c.clear(skia.ColorTRANSPARENT)
        self.dang = []            # khối thuộc bóng dáng ngoài (để chốt viền ngoài)
        self.lo = []              # lỗ rỗng (lòng vòng trượng…) – khoét trắng trong ảnh bóng dáng
        self.dang_phu = []        # chi tiết mảnh (răng cào…) chỉ góp vào phép thử bóng dáng, không ăn viền ngoài dày

    # ── tô / kẻ ──
    def to(self, h, m, a=255):
        self.c.drawPath(h.p, skia.Paint(AntiAlias=True, Color=mau(m, a)))

    def ke(self, h_or_path, day, m=None):
        p = h_or_path.p if isinstance(h_or_path, Hinh) else h_or_path
        self.c.drawPath(p, skia.Paint(AntiAlias=True, Color=mau(m or self.muc), Style=skia.Paint.kStroke_Style,
                                      StrokeWidth=day, StrokeCap=skia.Paint.kRound_Cap,
                                      StrokeJoin=skia.Paint.kRound_Join))

    def khoi(self, h, m, vien='trong', dang=True):
        """Tô khối + viền cấp `vien` ('ngoai'/'trong'/'ct'/số px/None). dang=True: góp vào bóng dáng."""
        self.to(h, m)
        if vien:
            self.ke(h, self.D[vien] if isinstance(vien, str) else vien)
        if dang:
            self.dang.append(h)

    def net(self, pts, day='ct', m=None, thuon=True, cang=1.0):
        """Nét chi tiết (lông mày, nếp áo, sợi tóc). thuon=True: hai đầu nhọn dần."""
        w = self.D[day] if isinstance(day, str) else day
        if thuon:
            self.to(net_thuon(pts, w * 0.25, w * 1.15, cang=cang), m or self.muc)
        else:
            self.ke(duong(pts, cang), w, m)

    # ── bóng / sáng phẳng ──
    def bong(self, h, m, dx, dy, trong=None):
        """Mảng bóng mép cứng = h − h dịch (−dx, −dy): bóng nằm phía (dx, dy) so với nguồn sáng.
        trong: chỉ giữ phần bóng nằm trong khối này (vd bóng đầu đổ lên thân)."""
        s = h - h.dich(-dx, -dy)
        if trong is not None:
            s = s & trong
        self.to(s, m)
        return s

    def do_bong(self, h, m, dx, dy, trong=None):
        """Bóng ĐỔ của khối h lên nền phía dưới nó = h dịch (dx, dy) − h (vẽ TRƯỚC khi vẽ h)."""
        s = h.dich(dx, dy) - h
        if trong is not None:
            s = s & trong
        self.to(s, m)
        return s

    def vet_sang(self, h, m, dx, dy, co=None):
        """Vệt sáng mép cứng ở phía nguồn sáng = h − h dịch (dx, dy); co: thu gọn theo vùng."""
        s = h - h.dich(dx, dy)
        if co is not None:
            s = s & co
        self.to(s, m)
        return s

    @contextmanager
    def cat(self, h):
        """Chỉ vẽ bên trong khối h (vd hoạ tiết áo nằm trong thân)."""
        self.c.save()
        self.c.clipPath(h.p, skia.ClipOp.kIntersect, True)
        try:
            yield
        finally:
            self.c.restore()

    # ── chốt ──
    def chot_vien(self, them=None):
        """Viền NGOÀI dày = đường bao hợp mọi khối đã đăng ký (vẽ đè cuối cùng)."""
        u = gop(*(self.dang + (them or [])))
        self.ke(u, self.D['ngoai'])
        return u

    def luu(self, path):
        self.sf.makeImageSnapshot().save(path, skia.kPNG)
        return path
