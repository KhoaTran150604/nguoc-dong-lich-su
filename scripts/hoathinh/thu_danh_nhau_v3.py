"""Cảnh thử hoạt họa 2D – BẢN 3: Ngô Quyền là "rối giấy" cắt từ ẢNH Google Flow (18/11/2026).

Ảnh nguồn: assets/portraits/ngo-quyen-flow-tpose.png (tư thế chữ T, chân dung MINH HỌA tạo bằng Flow).
Code tách nền kem, cắt thân / cánh tay / cẳng tay / kiếm, gắn khớp vai–khuỷu rồi xoay theo tư thế.
Các lính khác, nền, camera, hiệu ứng: dùng lại bản 2 (thu_danh_nhau_v2.py).

Chạy:  python3 scripts/hoathinh/thu_danh_nhau_v3.py --nhap | (bỏ trống = 1080p) | --khung 3.0
"""
import math
import os
import sys
import inspect

import numpy as np
from PIL import Image, ImageDraw, ImageFilter

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import thu_danh_nhau_v2 as v2  # noqa: E402  (đã thay nhân vật bản 2 vào bản 1)
m = v2.m
from thu_danh_nhau import clamp, ease  # noqa: E402

SRC = os.path.join(m.ROOT, 'assets', 'portraits', 'ngo-quyen-flow-tpose.png')
CROP = (14, 14, 1706, 976)          # bỏ khung đen bo góc của ảnh chụp
FEET = (865, 935)                   # giữa hai gót ủng (toạ độ ảnh đã cắt)
HEIGHT_WORLD = 400                 # chiều cao nhân vật trong cảnh (đơn vị thế giới 1080p)
IMG_H = 895                         # chiều cao nhân vật trong ảnh (chóp lông → đế ủng)
PAD = 520

# khớp (toạ độ ảnh đã cắt)
SH_L, EL_L = (725, 325), (624, 338)       # tay bên trái màn hình (tay phải của nhân vật)
SH_R, EL_R, HAND_R = (962, 322), (1068, 330), (1186, 322)
ARM_L = [(380, 240), (700, 240), (762, 300), (762, 396), (380, 396)]
ARM_R = [(938, 300), (975, 238), (1320, 238), (1320, 402), (938, 402)]
SWORD_BOX = (330, 790, 735, 945)
GRIP, SWORD_TIP = (662, 843), (352, 916)
CAP_R = 62


def _load():
    im = Image.open(SRC).convert('RGB').crop(CROP)
    ImageDraw.Draw(im).rectangle((1540, 790, 1660, 910), fill=(243, 228, 192))   # dấu ✦ góc ảnh
    w = im.copy()
    for p in [(10, 10), (w.width - 10, 10), (10, w.height - 10), (w.width - 10, w.height - 10), (800, 940)]:
        ImageDraw.floodfill(w, p, (255, 0, 255), thresh=60)
    a = np.asarray(w)
    alpha = ~((a[..., 0] == 255) & (a[..., 1] == 0) & (a[..., 2] == 255))
    alpha[:, :300] = False
    alpha[:, 1350:] = False
    al = Image.fromarray(alpha.astype(np.uint8) * 255).filter(ImageFilter.MinFilter(3))   # bỏ viền kem
    rgba = im.convert('RGBA')
    rgba.putalpha(al)
    return rgba


def _cut(rgba, poly=None, box=None, minus=()):
    msk = Image.new('L', rgba.size, 0)
    d = ImageDraw.Draw(msk)
    if poly:
        d.polygon(poly, fill=255)
    elif box:
        d.rectangle(box, fill=255)
    else:
        d.rectangle((0, 0) + rgba.size, fill=255)
    for p in minus:
        d.polygon(p, fill=0) if isinstance(p, list) else d.rectangle(p, fill=0)
    out = Image.new('RGBA', rgba.size, (0, 0, 0, 0))
    a = np.minimum(np.asarray(rgba.getchannel('A')), np.asarray(msk))
    out.paste(rgba, (0, 0))
    out.putalpha(Image.fromarray(a))
    return out


def _pad(im):
    c = Image.new('RGBA', (im.width + 2 * PAD, im.height + 2 * PAD), (0, 0, 0, 0))
    c.paste(im, (PAD, PAD))
    return c


R = {}


def rig():
    if R:
        return R
    rgba = _load()
    elbow_cut_L = [(380, 240), (EL_L[0], 240), (EL_L[0], 396), (380, 396)]
    elbow_cut_R = [(EL_R[0], 238), (1320, 238), (1320, 402), (EL_R[0], 402)]
    torso = _cut(rgba, minus=(ARM_L, ARM_R, SWORD_BOX))
    # "nắp vai": giữ lại phần vai gốc quanh khớp (phía trong người) để khi tay xoay không hở
    for sh, side in ((SH_L, 1), (SH_R, -1)):
        cap = Image.new('L', rgba.size, 0)
        d = ImageDraw.Draw(cap)
        d.ellipse((sh[0] - CAP_R, sh[1] - CAP_R, sh[0] + CAP_R, sh[1] + CAP_R), fill=255)
        if side == 1:
            d.rectangle((0, 0, sh[0] - 22, rgba.height), fill=0)
        else:
            d.rectangle((sh[0] + 22, 0, rgba.width, rgba.height), fill=0)
        a = np.minimum(np.asarray(rgba.getchannel('A')), np.asarray(cap))
        piece = rgba.copy()
        piece.putalpha(Image.fromarray(a))
        base = Image.new('RGBA', rgba.size, (0, 0, 0, 0))
        base.alpha_composite(piece)
        base.alpha_composite(torso)
        torso = base
    R['torso'] = _pad(torso)
    R['upL'] = _pad(_cut(rgba, ARM_L, minus=(elbow_cut_L,)))
    R['foL'] = _pad(_cut(rgba, elbow_cut_L))
    R['upR'] = _pad(_cut(rgba, ARM_R, minus=(elbow_cut_R,)))
    R['foR'] = _pad(_cut(rgba, elbow_cut_R))
    R['sword'] = _pad(_cut(rgba, box=SWORD_BOX))
    R['ang_sw'] = math.degrees(math.atan2(SWORD_TIP[1] - GRIP[1], SWORD_TIP[0] - GRIP[0]))
    R['len_sw'] = math.hypot(SWORD_TIP[0] - GRIP[0], SWORD_TIP[1] - GRIP[1])
    return R


def P_(p):
    return (p[0] + PAD, p[1] + PAD)


def rot_about(im, piv, deg, to=None):
    """Xoay ảnh quanh điểm piv (deg>0 = theo chiều kim đồng hồ trên màn hình), dời piv tới 'to'."""
    to = to or piv
    return im.rotate(-deg, resample=Image.BICUBIC, center=piv, translate=(to[0] - piv[0], to[1] - piv[1]))


def rp(p, piv, deg):
    r = math.radians(deg)
    x, y = p[0] - piv[0], p[1] - piv[1]
    return (piv[0] + x * math.cos(r) - y * math.sin(r), piv[1] + x * math.sin(r) + y * math.cos(r))


# tư thế: aL/aR = góc vai (0 = dang ngang, + = hạ xuống), bL/bR = gập khuỷu thêm, c = góc kiếm so với cẳng tay
GUARD = dict(aL=72, bL=8, aR=58, bR=-62, c=-100, dx=0, dy=0, lean=0)
WIND = dict(aL=60, bL=20, aR=-62, bR=-40, c=-80, dx=-10, dy=0, lean=-4)
SLASH = dict(aL=50, bL=10, aR=22, bR=0, c=-8, dx=22, dy=6, lean=5)
BLOCK = dict(aL=70, bL=10, aR=-8, bR=-80, c=-95, dx=-14, dy=0, lean=-3)
ATK3 = [(0.0, GUARD), (0.30, WIND), (0.40, SLASH), (0.58, SLASH), (1.0, GUARD)]
DEF3 = [(0.0, GUARD), (0.28, BLOCK), (0.42, dict(BLOCK, dx=-24, lean=-6)), (0.62, BLOCK), (1.0, GUARD)]


def keyed(u, keys):
    for (u0, a), (u1, b) in zip(keys, keys[1:]):
        if u0 <= u <= u1:
            t = ease((u - u0) / (u1 - u0))
            return {k: a[k] + (b[k] - a[k]) * t for k in a}
    return dict(keys[-1][1])


class Puppet(v2.Char2):
    """Ngô Quyền rối giấy. Giữ nhịp đánh của bản 1 (role 'left'), vẽ bằng ảnh thay cho đa giác."""
    _cache = {}

    def pose3(self, t):
        n = math.floor(t / self.period + self.phase)
        u = (t / self.period + self.phase) - n
        atk = n % 2 == 0
        Q = keyed(u, ATK3 if atk else DEF3)
        Q['dy'] += 2.5 * math.sin(t * 3.1)          # thở
        return Q, atk, u

    def build(self, t):
        key = round(t, 4)
        if key in self._cache:
            return self._cache[key]
        r = rig()
        Q, atk, u = self.pose3(t)
        cv = r['torso'].copy()
        # tay trái màn hình: hướng ra ngoài là -x  → góc dương (hạ xuống) = ngược chiều kim đồng hồ
        sL, eL = P_(SH_L), P_(EL_L)
        eL2 = rp(eL, sL, -Q['aL'])
        cv.alpha_composite(rot_about(r['foL'], eL, -(Q['aL'] + Q['bL']), eL2))
        cv.alpha_composite(rot_about(r['upL'], sL, -Q['aL']))
        # tay phải màn hình (cầm kiếm)
        sR, eR, hR = P_(SH_R), P_(EL_R), P_(HAND_R)
        eR2 = rp(eR, sR, Q['aR'])
        fa = Q['aR'] + Q['bR']
        hR2 = rp(hR, eR, fa)
        hR2 = (hR2[0] + eR2[0] - eR[0], hR2[1] + eR2[1] - eR[1])
        sw_deg = fa + Q['c'] - r['ang_sw']      # hướng lưỡi kiếm (0 = chĩa ra ngoài theo cẳng tay)
        cv.alpha_composite(rot_about(r['sword'], P_(GRIP), sw_deg, hR2))
        cv.alpha_composite(rot_about(r['upR'], sR, Q['aR']))
        cv.alpha_composite(rot_about(r['foR'], eR, fa, eR2))
        tipd = math.radians(fa + Q['c'])
        tip = (hR2[0] + r['len_sw'] * math.cos(tipd), hR2[1] + r['len_sw'] * math.sin(tipd))
        mid = (hR2[0] + 0.45 * r['len_sw'] * math.cos(tipd), hR2[1] + 0.45 * r['len_sw'] * math.sin(tipd))
        if Q['lean']:
            fp = P_(FEET)
            cv = rot_about(cv, fp, Q['lean'])
            tip, mid = rp(tip, fp, Q['lean']), rp(mid, fp, Q['lean'])
        res = (cv, Q, atk, u, tip, mid)
        if len(self._cache) > 64:
            self._cache.clear()
        self._cache[key] = res
        return res

    def parts(self, t):
        cv, Q, atk, u, tip, mid = self.build(t)
        K = m.G.get('K', 1.0)
        sc = HEIGHT_WORLD / IMG_H                   # ảnh → thế giới
        X = self.x + Q['dx']
        Y = self.y + Q['dy']
        fp = P_(FEET)

        def W(p):
            return (X + (p[0] - fp[0]) * sc, Y + (p[1] - fp[1]) * sc)

        bb = cv.getbbox()
        piece = cv.crop(bb)
        size = (max(1, int(piece.width * sc * K)), max(1, int(piece.height * sc * K)))
        piece = piece.resize(size, Image.LANCZOS)
        # hòa ánh chiều tà
        a = np.asarray(piece).astype(np.float32)
        a[..., :3] *= np.array([1.0, 0.9, 0.8])
        piece = Image.fromarray(np.clip(a, 0, 255).astype(np.uint8), 'RGBA')
        x0, y0 = W((bb[0], bb[1]))
        P = dict(_atk=atk, _u=u, X=X)
        meta = dict(tip=W(tip), mid=W(mid), shield=W(mid), feet=(X, self.y), P=P)
        return [('img', piece, x0, y0)], meta


# --- vá render của bản 1 để vẽ được mảnh ảnh ('img')
_src = inspect.getsource(m.render)
_old = "            elif op[0] == 'f':\n                ImageDraw.Draw(cv).polygon"
assert _old in _src
_src = _src.replace(_old, "            elif op[0] == 'img':\n"
                          "                cv.paste(op[1], (int(round((op[2] - cx_) * K)), int(round(op[3] * K))), op[1])\n"
                    + _old)
exec(compile(_src, m.__file__, 'exec'), m.__dict__)

# --- thay Ngô Quyền bản 2 bằng rối giấy
_old_hero = m.PAIR_A[0]
hero = Puppet(_old_hero.x, _old_hero.y, 'viet', 1, role='left', period=_old_hero.period, phase=_old_hero.phase)
hero.x = 790
m.CAST[m.CAST.index(_old_hero)] = hero
m.PAIR_A = (hero, m.PAIR_A[1])
m.PAIR_A[1].x = 1000
m.HITS = m.hit_events()

if __name__ == '__main__':
    if '--out' not in sys.argv:
        sys.argv += ['--out', os.path.join(m.ROOT, 'build', 'thu-hoathinh', 'v3')]
    m.main()
