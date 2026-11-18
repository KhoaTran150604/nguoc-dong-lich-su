"""Cảnh thử hoạt họa 2D – BẢN 2: nhân vật vẽ lại theo mẫu Ngô Quyền tạo bằng Google Flow (18/11/2026).

Khác bản 1 (thu_danh_nhau.py):
- Tỉ lệ người thật hơn (đầu nhỏ, ~1/6 thân), viền mực đậm, màu phẳng + 1 tông bóng.
- Ngô Quyền (chân dung MINH HỌA): mũ đồng chùm lông đỏ, giáp vảy đồng, áo đỏ viền vàng,
  đai đen, quần đen, ủng, râu dê – đứng hàng đầu, đánh tay đôi.
- Lính Việt: áo đỏ viền vàng, khăn vàng, đai đen, khiên mây. Lính Nam Hán: áo chàm, giáp vảy sắt, mũ sắt.
Nền, camera, hiệu ứng dùng lại toàn bộ bản 1.

Chạy:  python3 scripts/hoathinh/thu_danh_nhau_v2.py --nhap      (540p nháp)
       python3 scripts/hoathinh/thu_danh_nhau_v2.py            (1080p)
       thêm --khung 5.5 để xuất 1 khung hình
"""
import math
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import thu_danh_nhau as m  # noqa: E402
from thu_danh_nhau import add, capsule, circ, clamp, dirv, hx, mix, HAZE  # noqa: E402

PAL = {
    'viet': dict(tunic='#A3302A', trim='#E0B23C', pants='#2B2522', boots='#1C1614', sash='#1E1A18',
                 skin='#E2AC7E', hair='#211715', band='#E0B23C', shield='#C99A55', sline='#7A4E28',
                 blade='#E2DDCF', hilt='#C9A24A', shaft='#6B4326', collar='#F2E6CC'),
    'han': dict(tunic='#33416A', trim='#22294A', pants='#2E2A2C', boots='#1E1818', sash='#7A2E28',
                skin='#DDA77C', armor='#7C7884', aline='#46434E', helmet='#5E5A66', shield='#6A2E24',
                sline='#C9A24A', blade='#D8D6D2', hilt='#8A8070', shaft='#5A3A26', collar='#C8C0B0'),
    'hero': dict(tunic='#9E2A24', trim='#E3B53E', pants='#221C1A', boots='#1C1614', sash='#17130F',
                 skin='#E4AE80', hair='#17110F', armor='#B08A3E', aline='#5E4318', helmet='#B89140',
                 plume='#B3261E', blade='#D9C489', hilt='#8A6428', shaft='#6B4326', collar='#F2E6CC'),
}
INK2 = hx('#160E0E')
OW_ = 3.4   # viền mực đậm như mẫu
SH_ = 6.0
RW_ = 1.8


class Char2(m.Char):
    def __init__(self, *a, **kw):
        super().__init__(*a, **kw)
        self.hero = False
        self._pal('hero' if self.hero else self.team)

    def _pal(self, key):
        haze = clamp((900 - self.y) / 300) * 0.5
        self.c = {k: mix(hx(v), HAZE, haze) for k, v in PAL[key].items()}
        self.ink = mix(INK2, HAZE, haze * 0.55)

    def make_hero(self):
        self.hero = True
        self.s *= 1.08
        self._pal('hero')

    def parts(self, t):
        P = self.pose(t)
        c, team, hero = self.c, self.team, self.hero
        armored = hero or team == 'han'
        tn, sn, tf, sf = P['leg']
        L1, L2 = 56, 54
        dn = L1 * math.cos(math.radians(tn)) + L2 * math.cos(math.radians(sn))
        df = L1 * math.cos(math.radians(tf)) + L2 * math.cos(math.radians(sf))
        hip = (P['dx'], -max(dn, df))

        def leg(a, b):
            k = add(hip, dirv(a), L1)
            return k, add(k, dirv(b), L2)

        kN, aN = leg(tn, sn)
        kF, aF = leg(tf, sf)
        lam = math.radians(P['lam'])
        up = (math.sin(lam), -math.cos(lam))
        fw = (math.cos(lam), math.sin(lam))

        def T(a, b):
            return (hip[0] + a * fw[0] + b * up[0], hip[1] + a * fw[1] + b * up[1])

        neck = T(0, 84)
        tl = lam + math.radians(P['tilt'])
        head = (neck[0] + 20 * math.sin(tl), neck[1] - 20 * math.cos(tl))
        shN, shF = T(4, 76), T(-6, 76)
        eN = add(shN, dirv(P['armN'][0]), 40)
        hN = add(eN, dirv(P['armN'][1]), 38)
        eF = add(shF, dirv(P['armF'][0]), 40)
        hF = add(eF, dirv(P['armF'][1]), 38)
        wd = dirv(P['w'])
        wp = (wd[1], -wd[0])
        ops = []
        fl = t * 9 + self.phase * 7

        def body(pts, col, sh=SH_, rw=RW_, ow=OW_):
            ops.append(('p', pts, col, sh, rw, ow))

        def flat(pts, col):
            ops.append(('f', pts, col))

        def line(pts, col, w):
            ops.append(('l', pts, col, w))

        def arm(sh_, e, h, a0):
            body(capsule(sh_, e, 8.5, 7.5), c['tunic'])
            if armored:   # cổ tay giáp
                body(capsule(e, h, 7.8, 6.8), c['armor'])
                q = add(e, dirv(P['armN' if sh_ is shN else 'armF'][1]), 16)
                line([add(q, (-6, 0)), add(q, (6, 0))], c['aline'], 1.3)
            else:
                body(capsule(e, h, 7.2, 6.2), c['tunic'])
                body(capsule(add(e, dirv(P['armN' if sh_ is shN else 'armF'][1]), 26), h, 7, 6.4, 4),
                     c['trim'], 2, 1.4, 2.6)
            body(circ(h[0], h[1], 7, n=12), c['skin'], 3, 1.5, 2.6)
            if armored:   # giáp vai
                d = dirv(a0)
                body(capsule(add(sh_, d, -2), add(sh_, d, 16), 13, 10.5, 6), c['armor'], 4, 1.6, 3)
                for k in (5, 11):
                    p = add(sh_, d, k)
                    pp = (d[1], -d[0])
                    line([add(p, pp, -10), add(p, pp, 10)], c['aline'], 1.3)

        # --- vũ khí + tay xa
        if self.weapon == 'spear':
            a, b = add(hF, wd, -70), add(hF, wd, 150)
            body(capsule(a, b, 3.2, 3.2, 3), c['shaft'], 2, 1.2, 2.4)
            tip = add(b, wd, 30)
            body([add(b, wp, 6), tip, add(b, wp, -6), add(b, wd, -6)], c['blade'], 2, 1.6, 2.4)
            tipP, midP = tip, add(hF, wd, 90)
        else:  # kiếm thẳng như mẫu
            ln = 84 if hero else 74
            body([add(add(hF, wd, 12), wp, 4), add(add(hF, wd, ln - 8), wp, 3.4), add(hF, wd, ln),
                  add(add(hF, wd, ln - 8), wp, -3.4), add(add(hF, wd, 12), wp, -4)], c['blade'], 2.4, 1.8, 2.6)
            body(capsule(add(add(hF, wd, 9), wp, 10), add(add(hF, wd, 9), wp, -10), 3, 3, 3), c['hilt'], 1.6, 1, 2.2)
            body(capsule(add(hF, wd, -14), add(hF, wd, 4), 3.4, 3.4, 4), c['hilt'], 1.6, 1, 2.2)
            tipP, midP = add(hF, wd, ln - 4), add(hF, wd, 34)
        arm(shF, eF, hF, P['armF'][0])

        # --- chân: quần đen + ủng
        for k, a_, back in ((kF, aF, True), (kN, aN, False)):
            col = mix(c['pants'], m.DUSK, 0.15) if back else c['pants']
            body(capsule(hip, k, 11.5, 9.5), col, 4)
            mid = add(k, (a_[0] - k[0], a_[1] - k[1]), 0.42)
            body(capsule(k, mid, 9.5, 8.5), col, 4)
            body(capsule(mid, a_, 9, 8), c['boots'], 3, 1.4)
            body(capsule(a_, add(a_, (1, 0.12), 17), 7.5, 6.5, 4), c['boots'], 2.5, 1.4)

        # --- vạt áo dưới (đỏ / chàm) + viền
        wv = math.sin(fl) * 4
        skirt = [T(-18, 22), T(16, 22), T(25 + wv, -44), T(-27 - wv, -42)]
        body(skirt, c['tunic'], 7)
        hem = [T(25 + wv * 0.95, -36), T(25 + wv, -44), T(-27 - wv, -42), T(-26.5 - wv * 0.95, -34)]
        body(hem, c['trim'], 2.5, 1.4, 2.6)
        # thân áo
        body([T(-15, 80), T(13, 80), T(16, 20), T(-17, 20)], c['tunic'], 7)
        flat([T(-6, 82), T(8, 82), T(3, 70)], c['collar'])
        if armored:
            # vạt giáp
            body([T(-17, 20), T(16, 20), T(19, -26), T(-20, -25)], c['armor'], 5)
            for b in (8, -4, -16):
                line([T(-18, b), T(17, b)], c['aline'], 1.3)
            for a_ in (-8, 1, 10):
                line([T(a_, 18), T(a_ + 0.6 * a_ / 10, -24)], c['aline'], 1.3)
            # giáp ngực vảy
            body([T(-15, 72), T(12, 72), T(15, 22), T(-16, 22)], c['armor'], 5)
            for b in (62, 52, 42, 32):
                line([T(-15, b), T(13, b)], c['aline'], 1.3)
            for a_ in (-8, -1, 6):
                line([T(a_, 71), T(a_, 23)], c['aline'], 1.1)
        else:
            line([T(-6, 82), T(13, 40)], c['trim'], 3)   # nẹp áo vàng
        body([T(-18, 28), T(17, 28), T(17, 16), T(-18, 16)], c['sash'], 2, 1.2)

        # --- đầu
        hxp, hyp = head
        body(capsule(neck, (hxp - 2, hyp + 8), 7, 7, 4), mix(c['skin'], m.DUSK, 0.2), 2, 1, 2.4)
        if hero:   # chùm lông đỏ bay ra sau
            f1, f2 = math.sin(fl) * 4, math.sin(fl + 1.3) * 5
            body([(hxp + 2, hyp - 27), (hxp - 2, hyp - 46), (hxp - 16, hyp - 52 + f1), (hxp - 34, hyp - 44 + f1),
                  (hxp - 48, hyp - 26 + f2), (hxp - 42, hyp - 16 + f2), (hxp - 30, hyp - 26 + f1),
                  (hxp - 16, hyp - 30), (hxp - 6, hyp - 22)], c['plume'], 5, 1.8, 3)
        if team == 'viet' and not hero:   # đuôi khăn
            body([(hxp - 14, hyp - 8), (hxp - 38, hyp - 2 + math.sin(fl) * 5),
                  (hxp - 35, hyp + 5 + math.sin(fl + 1) * 5), (hxp - 13, hyp - 2)], c['band'], 2, 1.2, 2.4)
        body(circ(hxp, hyp, 14, 17), c['skin'], 5, 1.6, OW_)
        if armored:
            hc = c['helmet']
            # che gáy (vảy) phía sau
            body([(hxp - 9, hyp - 6), (hxp - 19, hyp - 4), (hxp - 22, hyp + 20), (hxp - 4, hyp + 22), (hxp - 3, hyp + 4)],
                 hc, 4, 1.4, 3)
            for b in (4, 11, 17):
                line([(hxp - 20, hyp + b), (hxp - 4, hyp + b + 1)], c['aline'], 1.2)
            body(circ(hxp - 1, hyp - 5, 17, 17, 16, math.pi * 0.96, math.pi * 2.04), hc, 4, 1.6, 3)
            body([(hxp - 18, hyp - 7), (hxp + 17, hyp - 8), (hxp + 17, hyp - 3), (hxp - 18, hyp - 2)],
                 mix(hc, m.DUSK, 0.18), 1.6, 1, 2.4)
            line([(hxp - 1, hyp - 21), (hxp - 1, hyp - 8)], c['aline'], 1.3)
            body([(hxp - 4, hyp - 21), (hxp - 1, hyp - 29), (hxp + 2, hyp - 21)], hc, 1.4, 1, 2.2)
        else:
            body(circ(hxp - 1, hyp - 3, 15.5, 16, 14, math.pi * 0.98, math.pi * 2.02), c['hair'], 3, 1.4, 2.6)
            body(circ(hxp - 9, hyp - 19, 6, n=12), c['hair'], 2, 1.2, 2.4)
            body([(hxp - 16, hyp - 10), (hxp + 15, hyp - 11), (hxp + 15, hyp - 5), (hxp - 16, hyp - 4)],
                 c['band'], 2, 1.2, 2.4)
        # mặt: lông mày cau, mắt, râu
        line([(hxp + 2, hyp - 1), (hxp + 13, hyp + 1.5)], self.ink, 2.6)
        flat(circ(hxp + 8, hyp + 4, 1.9, 2.4, 8), self.ink)
        flat(circ(hxp - 3, hyp + 5, 2.6, 3.6, 8), mix(c['skin'], m.DUSK, 0.32))   # tai
        if hero:
            line([(hxp + 8, hyp + 12), (hxp + 14.5, hyp + 11), (hxp + 13, hyp + 15)], c['hair'], 2)
            flat([(hxp + 8, hyp + 15), (hxp + 13, hyp + 15), (hxp + 9, hyp + 25)], c['hair'])
        if P['shout'] > 0.5:
            flat(circ(hxp + 11, hyp + 12, 2.8, 3.4, 10), hx('#4A1418'))
        elif not hero:
            line([(hxp + 9, hyp + 12), (hxp + 14, hyp + 11.5)], self.ink, 1.6)

        # --- tay gần + khiên
        arm(shN, eN, hN, P['armN'][0])
        shieldP = hN
        if self.weapon != 'spear' and not hero:
            sc = add(hN, (2, 0))
            if team == 'viet':
                body(circ(sc[0], sc[1], 22, 31), c['shield'], 6, 2, OW_)
                for r in (0.7, 0.42):
                    e = circ(sc[0], sc[1], 22 * r, 31 * r)
                    line(e + [e[0]], c['sline'], 1.6)
                body(circ(sc[0], sc[1], 4.5, 5.5, 10), c['sline'], 1.6, 1, 2)
            else:
                body([(sc[0] - 16, sc[1] - 33), (sc[0] + 16, sc[1] - 30), (sc[0] + 16, sc[1] + 30),
                      (sc[0] - 16, sc[1] + 33)], c['shield'], 6, 2, OW_)
                body(circ(sc[0], sc[1], 6.5, n=12), c['sline'], 1.6, 1, 2)
            shieldP = sc

        # --- xoay (ngã) + lật hướng + đặt vào cảnh (giống bản 1)
        phi = math.radians(P['phi'])
        lift = 16 * abs(math.sin(phi))
        f, s, X, Y = self.f, self.s, P['X'], self.y

        def tr(p):
            x, y = p
            x2 = x * math.cos(phi) - y * math.sin(phi)
            y2 = x * math.sin(phi) + y * math.cos(phi) - lift
            return (X + f * x2 * s, Y + y2 * s)

        out = []
        for op in ops:
            if op[0] == 'p':
                out.append(('p', [tr(q) for q in op[1]], op[2], op[3] * s, op[4] * s, op[5] * s))
            elif op[0] == 'f':
                out.append(('f', [tr(q) for q in op[1]], op[2]))
            else:
                out.append(('l', [tr(q) for q in op[1]], op[2], op[3] * s))
        meta = dict(tip=tr(tipP), mid=tr(midP), shield=tr(shieldP), feet=(X + f * P['dx'] * s, Y), P=P)
        return out, meta


# Thay nhân vật của bản 1 bằng bản 2 (chạy cả trong tiến trình con của Pool)
m.Char = Char2
m.CAST, m.PAIR_A = m.make_cast()
m.PAIR_A[0].make_hero()          # cặp đánh gần nhất: Ngô Quyền (minh họa)
m.PAIR_A[0].x, m.PAIR_A[1].x = 820, 1010   # đưa vào giữa khung lâu hơn khi máy lia
m.HITS = m.hit_events()

if __name__ == '__main__':
    if '--out' not in sys.argv:
        sys.argv += ['--out', os.path.join(m.ROOT, 'build', 'thu-hoathinh', 'v2')]
    m.main()
