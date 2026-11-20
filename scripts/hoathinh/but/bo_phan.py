"""THƯ VIỆN BỘ PHẬN – mỗi hàm vẽ một bộ phận lên Buc theo Khung + spec (dict) của nhân vật.

Mọi số đo theo R (bán kính đầu). Nguồn sáng: TRÊN-TRÁI → bóng phẳng nằm dưới-phải.
Mặt quay 3/4 sang PHẢI: mắt/miệng lệch phải, tai trái to (lộ), tai phải nhỏ (khuất).

Thêm bộ phận mới: viết hàm `ten(b, k, S)` theo cùng mẫu, đăng ký trong `nhan_vat.py` (LOP).
"""
import math

from but import (Hinh, cong, da_giac, elip, gop, hop, mau_diem, net_thuon, sang, thanh,  # noqa: F401
                 toi, tron)

SANG = (-1, -1)      # hướng nguồn sáng (đơn vị) – chỉ để nhớ: bóng dịch (+dx, +dy)


def _pts(k, pts):
    return [k.H(*p[:2]) + ((0,) if len(p) > 2 else ()) for p in pts]


def _pts_b(k, pts):
    return [k.B(*p[:2]) + ((0,) if len(p) > 2 else ()) for p in pts]


def _dai(pts_tren, dy):
    """Dải bề dày dy (px) nằm dưới đường pts_tren."""
    q = mau_diem(pts_tren, 60)
    return da_giac(q + [(x, y + dy) for x, y in q[::-1]])


# ═══════════════════════════ ĐẦU ═══════════════════════════
def tai(b, k, S):
    """Tai người: trái to (lộ), phải nhỏ (khuất sau má). Nét gờ tai mảnh thuôn."""
    T = S.get('tai', {})
    da = S['mau'].get('tai', S['mau']['da'])
    long_ = S['mau'].get('tai_trong') or toi(da, 0.07)
    kt = T.get('trong', 0.55)
    for s, (dx, dy, rx, ry, rot) in ((-1, T.get('trai', (-0.97, 0.10, 0.20, 0.25, 12))),
                                    (1, T.get('phai', (0.98, 0.08, 0.13, 0.20, -10)))):
        x, y = k.H(dx, dy)
        h = elip(x, y, k.r(rx), k.r(ry), rot)
        b.khoi(h, da)
        with b.cat(h):
            b.to(elip(x - s * k.r(rx) * 0.1, y + k.r(ry) * 0.05, k.r(rx) * kt, k.r(ry) * (kt + 0.05), rot), long_)
        b.net([(x - s * k.r(rx) * 0.05, y - k.r(ry) * 0.55), (x + s * k.r(rx) * 0.35, y - k.r(ry) * 0.2),
               (x + s * k.r(rx) * 0.25, y + k.r(ry) * 0.35), (x - s * k.r(rx) * 0.1, y + k.r(ry) * 0.5)], 'ct')


def _gai(k, G):
    """Chỏm lông gai: G = [(góc°, dài R, nửa rộng gốc °, nghiêng đỉnh °), …] (0° phải, −90° đỉnh)."""
    out = Hinh()
    for g, dai, rong, ng in G:
        def P(rr, deg):
            a = math.radians(deg)
            return k.H(rr * math.cos(a), rr * math.sin(a))
        out = out + cong([P(0.84, g - rong), P(1.0 + dai * 0.40, g - rong * 0.45 + ng * 0.4),
                          P(1.0 + dai, g + ng) + (0,),
                          P(1.0 + dai * 0.30, g + rong * 0.55 + ng * 0.3), P(0.84, g + rong)])
    return out


def dau_da(b, k, S):
    """Khối đầu (màu da, hoặc màu lông `mau.dau`) + chỏm lông gai `gai` + bóng trăng khuyết dưới-phải."""
    h = k.dau()
    if S.get('gai'):
        h = h + _gai(k, S['gai'])
    c = S['mau'].get('dau', S['mau']['da'])
    b.khoi(h, c)
    with b.cat(h):
        b.bong(h, toi(c, 0.08 if 'dau' in S['mau'] else 0.06), k.r(0.09), k.r(0.09))
        if S.get('gai'):
            sx, sy = k.H(-0.30, -0.70)
            vs = elip(sx, sy, k.r(0.40), k.r(0.12), -30)
            b.to(vs - vs.dich(k.r(0.04), k.r(0.07)), sang(c, 0.10))
    for seg in S.get('long_net', []):
        b.net(_pts(k, seg), 'ct', toi(c, 0.22))
    return h


def mat_na(b, k, S):
    """Mặt nạ da (khỉ): 2 thùy quanh mắt + cằm/mõm, mũi lông `mai` chĩa xuống giữa trán, cắt trong đầu."""
    N = S['mat_na']
    c = S['mau']['da']
    h = gop(*[tron(*k.H(dx, dy), k.r(r)) for dx, dy, r in N['thuy']])
    cx, cy, rx, ry = N['cam']
    h = h + elip(*k.H(cx, cy), k.r(rx), k.r(ry))
    if N.get('mai'):
        h = h - cong(_pts(k, N['mai']))
    h = h & k.dau()
    b.khoi(h, c, 'trong', dang=False)
    with b.cat(h):
        b.bong(h, toi(c, 0.06), k.r(0.08), k.r(0.08))
    return h


def _bup(k, goc, r, d=1.0):
    """Các búp tròn (tóc xoăn / râu rậm) quanh vành đầu: goc = list độ (0° = phải, 90° = dưới,
    −90° = đỉnh), r = bán kính búp (R), d = khoảng cách tâm búp tới tâm đầu (R)."""
    out = Hinh()
    for i, g in enumerate(goc):
        a = math.radians(g)
        rr = r[i] if isinstance(r, (list, tuple)) else r
        out = out + tron(k.hx + d * k.R * math.cos(a), k.hy + d * k.R * math.sin(a), k.r(rr))
    return out


def toc_chom(b, k, S):
    """Mảng tóc chụp đỉnh đầu, chân tóc theo S['toc']['chan'] (điểm R, trái→phải).
    `bup` (góc, độ): búp tóc xoăn thò ra ngoài vành đầu → tóc nhận ra được từ bóng dáng.
    Không có bup thì tóc nở đều `no` R. Có bóng, vệt sáng, sợi tóc."""
    T = S['toc']
    c = S['mau']['toc']
    no = k.r(T.get('no', 0.05))
    chan = _pts(k, T['chan'])
    vung = cong(chan + [k.H(1.8, -0.2, )[:2] + (0,), k.H(1.8, -2.0)[:2] + (0,),
                        k.H(-1.8, -2.0)[:2] + (0,), k.H(-1.8, -0.2)[:2] + (0,)])
    if T.get('bup'):
        hair = (k.dau() + _bup(k, T['bup'], T.get('bup_r', 0.18), T.get('bup_d', 0.95))) & vung
    else:
        hair = k.dau().phong(no) & vung
    b.khoi(hair, c)
    with b.cat(hair):
        b.bong(hair, toi(c, 0.10), k.r(0.10), k.r(0.12))
        sx, sy = k.H(-0.35, -0.72)
        vs = elip(sx, sy, k.r(0.42), k.r(0.13), -28)
        b.to(vs - vs.dich(k.r(0.04), k.r(0.07)), sang(c, 0.10))
    for seg in T.get('soi', []):
        b.net(_pts(k, seg), 'ct', toi(c, 0.22))
    return hair


def vong_tran(b, k, S):
    """Vòng kim loại ôm trán, chạy theo chân tóc (bám mặt cầu đầu), có hoa văn mây ở chính diện."""
    V = S['vong_tran']
    c = S['mau']['vang']
    tren = _pts(k, V['duong'])
    q = mau_diem(tren, 60)
    dy = k.r(V.get('day', 0.14))
    strip = da_giac(q + [(x, y + dy * (0.75 + 0.25 * math.sin(math.pi * i / 59))) for i, (x, y) in enumerate(q)][::-1])
    band = strip & k.dau().phong(k.r(V.get('no', 0.0)))
    b.khoi(band, c)
    with b.cat(band):
        b.bong(band, toi(c, 0.14), 0, k.r(0.05))
    if V.get('nut'):                                          # nút vòng khuyên (kim cô Ngộ Không)
        for dx, dy, rn in V['nut']:
            x, y = k.H(dx, dy)
            vong = tron(x, y, k.r(rn)) - tron(x, y, k.r(rn * 0.48))
            b.khoi(vong, c, 'ct', dang=True)
            with b.cat(vong):
                b.bong(vong, toi(c, 0.16), k.r(0.03), k.r(0.03))
            b.to(tron(x, y, k.r(rn * 0.48)), toi(c, 0.45))
            b.to(tron(x - k.r(rn * 0.1), y - k.r(rn * 0.1), k.r(rn * 0.16)), sang(c, 0.12))
        return band
    ox, oy = V.get('hoa_van', (0.26, -0.33))
    x, y = k.H(ox, oy)
    r = k.r(0.085)
    b.khoi(elip(x, y, r * 1.25, r), c, 'ct', dang=False)
    for s in (-1, 1):                                         # 2 xoắn mây đối xứng
        sp = [(x + s * (r * 0.15 + r * 0.55 * (1 - i / 14)) * math.cos(i * 0.5) * 0.9,
               y - r * 0.55 * (1 - i / 14) * math.sin(i * 0.5) * 0.9) for i in range(15)]
        b.net(sp, k.r(0.022), toi(c, 0.30))
    return band


def rau_quai_non(b, k, S):
    """Râu quai nón ôm hàm + chòm cằm nhọn. Mép trên râu theo S['rau']['mep'] (điểm R trái→phải)."""
    Rr = S['rau']
    c = S['mau'].get('rau', S['mau']['toc'])
    mep = _pts(k, Rr['mep'])
    vung = cong(mep + [k.H(1.6, 0.0)[:2] + (0,), k.H(1.6, 2.0)[:2] + (0,),
                       k.H(-1.6, 2.0)[:2] + (0,), k.H(-1.6, 0.0)[:2] + (0,)])
    beard = k.dau().phong(k.r(Rr.get('no', 0.07)))
    if Rr.get('bup'):                                         # búp râu xoăn phình ra ngoài vành hàm
        beard = beard + _bup(k, Rr['bup'], Rr.get('bup_r', 0.14), Rr.get('bup_d', 1.0))
    beard = beard & vung
    if Rr.get('mep_bup'):                                     # búp lông dọc mép trên (má) – râu, không phải khăn
        q = mau_diem(Rr['mep'], 60)
        for t in Rr['mep_bup']:
            x, y = q[round(t * (len(q) - 1))]
            beard = beard + (tron(*k.H(x, y + 0.05), k.r(Rr.get('mep_bup_r', 0.11))) & k.dau().phong(k.r(0.05)))
    cx, cy = Rr.get('chom', (0.16, 1.02))
    dai = Rr.get('chom_dai', 0.26)
    chom = cong(_pts(k, [(cx - 0.32, cy - 0.22), (cx - 0.14, cy + dai * 0.45), (cx + 0.04, cy + dai, 0),
                         (cx + 0.18, cy + dai * 0.40), (cx + 0.34, cy - 0.22)]))
    beard = beard + chom
    b.khoi(beard, c)
    with b.cat(beard):
        b.bong(beard, toi(c, 0.10), k.r(0.10), k.r(0.10))
    for seg in Rr.get('soi', []):
        b.net(_pts(k, seg), 'ct', toi(c, 0.22))
    if Rr.get('ria'):                                         # ria mép 2 vạt cong xuống
        x0, y0 = Rr['ria']
        for s, L in ((-1, 0.26), (1, 0.20)):
            pts = _pts(k, [(x0, y0), (x0 + s * L * 0.55, y0 + 0.02), (x0 + s * L, y0 + 0.10)])
            vat = net_thuon(pts, k.r(0.07), k.r(0.085), k.r(0.01))
            b.khoi(vat, c, 'ct', dang=False)
    return beard


# ═══════════════════════════ MẶT ═══════════════════════════
MAY = {   # lông mày theo biểu cảm: (độ vòm, nghiêng đầu trong (+ hạ xuống), độ cao)
    'hien': (0.050, 0.00, -0.22),
    'vui': (0.080, -0.02, -0.25),
    'quyet': (0.010, 0.17, -0.18),
    'ngac': (0.110, -0.03, -0.37),
    'buon': (0.020, -0.15, -0.24),
}


def mat(b, k, S):
    """Mắt (đen bầu dục + 2 đốm sáng) · lông mày (nét thuôn) · má hồng · miệng – theo biểu cảm."""
    M = S['mat']
    ink = b.muc
    bc = M.get('bieu_cam', 'hien')
    da = S['mau']['da']
    rx, ry = k.r(M.get('rx', 0.13)), k.r(M.get('ry', 0.16))
    # má hồng (dưới cùng)
    ma = M.get('mau_ma') or sang(_tron_mau(da, '#E0645A', 0.55), 0.02)
    for i, (dx, dy) in enumerate(M['vt']):
        x, y = k.H(dx, dy)
        b.to(elip(x + (0.02 if i else -0.02) * k.R, y + k.r(0.22), k.r(0.12) * (0.85 if i else 1), k.r(0.07)), ma)
    for i, (dx, dy) in enumerate(M['vt']):
        x, y = k.H(dx, dy)
        f = 0.88 if i == 1 else 1.0                        # mắt phía xa hẹp hơn (3/4)
        if M.get('mo', 1.0) < 0.2 or bc == 'cuoi_nham':    # nhắm / cười híp: cung ∩
            b.net([(x - rx * f, y + ry * 0.15), (x, y - ry * 0.45), (x + rx * f, y + ry * 0.15)], k.r(0.05), thuon=True)
        else:
            mo = M.get('mo', 1.0) * (1.2 if bc == 'ngac' else 1.0)
            eye = elip(x, y, rx * f, ry * mo)
            b.to(eye, ink)
            b.to(elip(x - rx * 0.28 * f, y - ry * 0.38 * mo, rx * 0.36, ry * 0.30 * mo), '#FFFFFF')
            b.to(tron(x + rx * 0.35 * f, y + ry * 0.42 * mo, rx * 0.15), '#FFFFFF')
            if bc == 'buon':                               # mí trên trĩu xuống phía ngoài
                ngoai = -1 if i == 0 else 1                # đuôi mắt: trái với mắt trái, phải với mắt phải
                mi = da_giac([(x - rx * 1.4, y - ry * 1.5), (x + rx * 1.4, y - ry * 1.5),
                              (x + rx * 1.4, y - ry * (0.05 if ngoai > 0 else 0.62)),
                              (x - rx * 1.4, y - ry * (0.62 if ngoai > 0 else 0.05))])
                b.to(mi & eye.phong(2), da)
        # lông mày
        vom, ng, cao = MAY.get(bc if bc in MAY else 'hien', MAY['hien'])
        vom, ng, cao = M.get('may_vom', vom), M.get('may_nghieng', ng), M.get('may_cao', cao)
        s = -1 if i == 0 else 1                              # đầu TRONG của mày trái nằm bên phải
        w = k.r(M.get('may_rong', 0.36)) * f
        y0 = y + k.r(cao)
        pts = [(x - w / 2, y0), (x, y0 - k.r(vom)), (x + w / 2, y0)]
        if s < 0:   # mày trái: đầu trong = bên phải
            pts[2] = (pts[2][0], pts[2][1] + k.r(ng))
        else:       # mày phải: đầu trong = bên trái
            pts[0] = (pts[0][0], pts[0][1] + k.r(ng))
        mc = M.get('mau_may', ink)
        b.to(net_thuon(pts, k.r(0.035), k.r(M.get('may_day', 0.075)), k.r(0.03)), mc)
    if M.get('mui'):                                          # 2 lỗ mũi nhỏ (khỉ)
        x, y = k.H(*M['mui'])
        for s in (-1, 1):
            b.to(elip(x + s * k.r(0.045), y, k.r(0.022), k.r(0.03), s * 20), ink)
    mieng(b, k, S)


def _tron_mau(a, c, t):
    ra, ga, ba = (int(a.lstrip('#')[i:i + 2], 16) for i in (0, 2, 4))
    rc, gc, bc_ = (int(c.lstrip('#')[i:i + 2], 16) for i in (0, 2, 4))
    return '#%02X%02X%02X' % (round(ra + (rc - ra) * t), round(ga + (gc - ga) * t), round(ba + (bc_ - ba) * t))


def mieng(b, k, S):
    M = S['mat']
    kieu = M.get('mieng', 'cuoi')
    if not kieu:
        return
    x, y = k.H(*M.get('mieng_vt', (0.24, 0.40)))
    w = k.r(M.get('mieng_rong', 0.20))
    if kieu == 'cuoi':
        b.to(net_thuon([(x - w / 2, y - k.r(0.01)), (x, y + k.r(0.055)), (x + w / 2, y - k.r(0.02))],
                       k.r(0.012), k.r(0.04), k.r(0.012)), b.muc)
    elif kieu in ('cuoi_mo', 'noi', 'cuoi_to'):
        if kieu == 'cuoi_to':
            w = w * 1.2
        h = k.r({'cuoi_mo': 0.11, 'noi': 0.08, 'cuoi_to': 0.17}[kieu])
        mo = cong([(x - w / 2, y - k.r(0.02), 0), (x + w / 2, y - k.r(0.03), 0),
                   (x + w * 0.25, y + h * 0.8), (x - w * 0.2, y + h * 0.85)])
        b.khoi(mo, '#6E2A22', 'ct', dang=False)
        with b.cat(mo):
            b.to(elip(x + w * 0.05, y + h * 0.95, w * 0.32, h * 0.45), '#E07A6E')
    elif kieu == 'buon':
        b.to(net_thuon([(x - w * 0.4, y + k.r(0.04)), (x, y - k.r(0.015)), (x + w * 0.4, y + k.r(0.035))],
                       k.r(0.012), k.r(0.036), k.r(0.012)), b.muc)
    elif kieu == 'mim':
        b.to(net_thuon([(x - w * 0.38, y + k.r(0.01)), (x, y + k.r(0.02)), (x + w * 0.38, y)],
                       k.r(0.02), k.r(0.05), k.r(0.02)), b.muc)
    elif kieu == 'o':
        b.khoi(elip(x, y + k.r(0.04), w * 0.26, k.r(0.08)), '#6E2A22', 'ct', dang=False)
    else:   # thang
        b.net([(x - w * 0.35, y), (x + w * 0.35, y)], k.r(0.035))


# ═══════════════════════════ THÂN & ÁO ═══════════════════════════
def ao_giao_linh(b, k, S):
    """Áo GIAO LĨNH (cổ chéo, vạt trái người mặc đè vạt phải – 'y' khi nhìn thẳng): thân màu áo,
    bóng phải + bóng cổ, áo trong tam giác, 2 vạt cổ, đai lưng ôm cong + nơ, gấu tuỳ chọn, nếp áo."""
    A = S['ao']
    m = S['mau']
    body = k.than()
    c = m['ao']
    b.khoi(body, c)
    R = k.R
    with b.cat(body):
        if A.get('vay'):                                       # váy (da hổ) dưới thắt lưng + sọc
            vy = k.top + k.r(A['vay'])
            b.to(hop(k.bx - 3 * R, vy, k.bx + 3 * R, k.bot + R), m['vay'])
            for dx, dy, L in A.get('vay_soc', []):
                x, y = k.B(dx, dy)
                b.to(net_thuon([(x, y), (x + k.r(0.03), y + k.r(L * 0.5)), (x + k.r(0.01), y + k.r(L))],
                               k.r(0.012), k.r(0.055), k.r(0.012)), m.get('soc', toi(m['vay'], 0.25)))
        if A.get('gau_rang'):                                  # gấu răng cưa
            gy, n, sau = A['gau_rang']
            x0, x1 = k.bx - 1.3 * R, k.bx + 1.3 * R
            rang = [(x0 + (x1 - x0) * i / (2 * n), k.top + k.r(gy + (sau if i % 2 else 0))) for i in range(2 * n + 1)]
            b.to(da_giac(rang + [(x1, k.bot + R), (x0, k.bot + R)]), m['gau'])
            for p0, p1 in zip(rang, rang[1:]):
                b.net([p0, p1], 'trong', thuon=False)
        if A.get('gau'):                                       # dải gấu khác màu
            gy = k.top + k.r(A['gau'])
            b.to(hop(k.bx - 3 * R, gy, k.bx + 3 * R, k.bot + R), m.get('gau', toi(c, 0.2)))
            b.net([(k.bx - 2 * R, gy), (k.bx + 2 * R, gy)], 'trong', thuon=False)
        b.bong(body, toi(c, 0.09), k.r(0.24), 0)                 # bóng cạnh phải
        b.to(elip(k.hx + k.r(0.15), k.top - k.r(0.02), k.r(0.80), k.r(0.24)), toi(c, 0.13))   # bóng đầu đổ xuống
        # áo trong (tam giác giữa 2 vạt)
        V = k.B(*A.get('v', (0.22, 0.46)))
        b.khoi(da_giac([k.B(-0.10, -0.05), k.B(0.64, -0.05), V]), m.get('ao_trong', '#F2E8D2'), 'ct', dang=False)
        cv = m.get('co', '#EFE4CC')
        dc = k.r(A.get('co_day', 0.13))
        # vạt dưới (vạt phải người mặc): từ vai trái nhìn → điểm V
        duoi = net_thuon([k.B(-0.10, -0.08), k.B(0.05, 0.20), V], dc, dc, dc * 0.6, dau_tron=False)
        b.khoi(duoi, cv, 'ct', dang=False)
        # vạt trên (đè): từ vai phải nhìn → chéo xuống trái tới đai lưng
        tren = net_thuon([k.B(0.66, -0.08), k.B(0.30, 0.40), k.B(-0.20, A.get('dai', (1.20, 1.40))[0] + 0.05)],
                         dc, dc * 1.05, dc, dau_tron=False)
        b.do_bong(tren, toi(c, 0.16), -k.r(0.05), k.r(0.05))       # bóng mép vạt đổ lên thân
        b.khoi(tren, cv, 'ct', dang=False)
        b.net([k.B(0.58, 0.02), k.B(0.26, 0.42), k.B(-0.14, 1.10)], k.r(0.018), toi(cv, 0.12))  # chỉ viền vạt
        # nếp áo
        for seg in A.get('nep', [[(-0.42, 1.55), (-0.39, 1.82)], [(0.30, 1.58), (0.34, 1.84)]]):
            b.net(_pts_b(k, seg), 'ct', toi(c, 0.20))
        # đai lưng cong ôm thân
        if A.get('dai'):
            d0, d1 = A['dai']
            sag = k.r(0.06)
            tren_d = [(k.bx - 2 * R, k.top + k.r(d0)), (k.bx, k.top + k.r(d0) + sag), (k.bx + 2 * R, k.top + k.r(d0))]
            dai = _dai(tren_d, k.r(d1 - d0))
            cd = m.get('dai', '#EFE4CC')
            b.khoi(dai, cd, 'trong', dang=False)
            b.bong(dai, toi(cd, 0.12), 0, k.r(0.05))
    if A.get('dai'):                                          # nơ thắt lưng (đè ra ngoài thân)
        d0, d1 = A['dai']
        cd = m.get('dai', '#EFE4CC')
        x, y = k.B(A.get('no_x', 0.12), (d0 + d1) / 2 + 0.04)
        for s in (-1, 1):                                     # 2 dải buông
            dt = net_thuon([(x + s * k.r(0.03), y), (x + s * k.r(0.10), y + k.r(0.30)), (x + s * k.r(0.08), y + k.r(0.48))],
                           k.r(0.08), k.r(0.10), k.r(0.11), dau_tron=False)
            b.khoi(dt, cd, 'ct', dang=False)
        for s in (-1, 1):                                     # 2 tai nơ
            tn = cong([(x, y - k.r(0.02)), (x + s * k.r(0.20), y - k.r(0.12)), (x + s * k.r(0.24), y + k.r(0.05)),
                       (x + s * k.r(0.06), y + k.r(0.05))])
            b.khoi(tn, cd, 'ct', dang=False)
            b.to(tn - tn.dich(-s * k.r(0.04), -k.r(0.03)), toi(cd, 0.12))
        b.khoi(elip(x, y, k.r(0.07), k.r(0.075)), m.get('no', toi(cd, 0.10)), 'ct', dang=False)
    b.dang.append(body)
    return body


def chuoi_so(b, k, S):
    """Chuỗi sọ nhỏ 'dễ thương' quanh cổ (Sa Tăng). Vẽ từ hai đầu vào giữa → sọ giữa nằm trước."""
    C = S['chuoi_so']
    c = S['mau'].get('so', '#EFE6D2')
    r = k.r(C.get('r', 0.10))
    pts = mau_diem(_pts_b(k, C['duong']), C.get('so', 9) * 8)
    n = C.get('so', 9)
    vt = [pts[round(i * (len(pts) - 1) / (n - 1))] for i in range(n)]
    giua = vt[n // 2][0]
    b.net([(x, y - r * 0.1) for x, y in mau_diem(_pts_b(k, C['duong']), 40)], k.r(0.035),
          S['mau'].get('day_so', '#4A2A1E'), thuon=False)
    for x, y in sorted(vt, key=lambda p: -abs(p[0] - giua)):
        so = tron(x, y - r * 0.12, r) + hop(x - r * 0.60, y + r * 0.30, x + r * 0.60, y + r * 0.92, r * 0.32)
        b.khoi(so, c, 'ct', dang=True)
        with b.cat(so):
            b.bong(so, toi(c, 0.12), r * 0.25, r * 0.22)
        for s in (-1, 1):
            b.to(elip(x + s * r * 0.38, y + r * 0.02, r * 0.24, r * 0.28), b.muc)
        b.to(da_giac([(x, y + r * 0.30), (x - r * 0.10, y + r * 0.48), (x + r * 0.10, y + r * 0.48)]), b.muc)
        for s in (-0.22, 0.22):
            b.net([(x + s * r, y + r * 0.62), (x + s * r, y + r * 0.86)], r * 0.10, thuon=False)


def duoi_xoan(b, k, S):
    """Đuôi xoắn (khỉ…): dải thuôn w0→w1 từ gốc sau thân ra vòng xoắn. Toạ độ thân (k.B).
    D: root, c (tâm xoắn), a0 (độ bắt đầu), turns, r0→r1 (bán kính, R), w0→w1 (bề dày, R)."""
    D = S['duoi']
    c = S['mau'].get('dau', S['mau']['da'])
    R = k.R
    cx, cy = k.B(*D['c'])
    rx, ry = k.B(*D['root'])
    a0 = math.radians(D['a0'])
    sx, sy = cx + D['r0'] * R * math.cos(a0), cy + D['r0'] * R * math.sin(a0)
    tam = [(rx + (sx - rx) * i / 4, ry + (sy - ry) * i / 4) for i in range(4)]
    for i in range(41):
        t = i / 40
        a = a0 + D['turns'] * 2 * math.pi * t
        r = (D['r0'] * (1 - t) + D['r1'] * t) * R
        tam.append((cx + r * math.cos(a), cy + r * math.sin(a)))
    w0, w1 = k.r(D['w0']), k.r(D['w1'])
    h = net_thuon(tam, w0, (w0 + w1) / 2, w1, n=200)
    b.khoi(h, c)
    with b.cat(h):
        b.bong(h, toi(c, 0.10), k.r(0.05), k.r(0.05))
    b.net(tam[int(len(tam) * 0.45):-2], k.r(D['w1'] * 0.35), sang(c, 0.12))
    return h


# ═══════════════════════════ TAY & VŨ KHÍ ═══════════════════════════
def ban_tay(b, k, S):
    """MỘT bàn tay tròn, vẽ đè lên cán vũ khí; nét ngón cái gợi đang nắm."""
    x, y, r = k.tay()
    da = S['mau'].get('tay', S['mau']['da'])
    h = tron(x, y, r)
    b.khoi(h, da)
    with b.cat(h):
        b.bong(h, toi(da, 0.07), r * 0.20, r * 0.20)
    b.net([(x - r * 0.15, y - r * 0.62), (x + r * 0.35, y - r * 0.42), (x + r * 0.48, y - r * 0.02)], 'ct')
    return h


def _khung_truc(k):
    top, bot, (ux, uy) = k.truc_vu_khi()
    nx, ny = -uy, ux                         # pháp tuyến (sang phải khi trục thẳng đứng)

    def P(s, w=0.0):                          # điểm: s (R) từ đỉnh xuống, lệch w (R) theo pháp tuyến
        x, y = k.tren_truc(s)
        return (x + nx * w * k.R, y + ny * w * k.R)
    L = math.hypot(bot[0] - top[0], bot[1] - top[1]) / k.R
    return P, L


def vu_khi(b, k, S):
    kieu = S['vu_khi']['kieu']
    return VU_KHI_KIEU[kieu](b, k, S)


def gay_nhu_y(b, k, S):
    """Như Ý Kim Cô Bổng (Ngộ Không): thân đỏ dài suốt trục chuẩn, hai đầu bịt vàng có vạch đen."""
    V, m = S['vu_khi'], S['mau']
    P0, L = _khung_truc(k)
    h0 = V.get('ha', 0.0)

    def P(sv, wv=0.0):
        return P0(sv + h0, wv)
    L = L - h0
    w = V.get('day', 0.115)
    can, vang = m.get('can', '#B9413A'), m.get('vang', '#F3C232')
    g = thanh(P(0), P(L), k.r(w), bo=False)
    b.khoi(g, can)
    with b.cat(g):
        b.bong(g, toi(can, 0.12), k.r(0.08), 0)
    dv = V.get('dau', 0.44)
    for s0, s1 in ((0, dv), (L - dv, L)):
        bit = thanh(P(s0), P(s1), k.r(w + 0.012), bo=False)
        b.khoi(bit, vang)
        with b.cat(bit):
            b.bong(bit, toi(vang, 0.14), k.r(0.08), 0)
            mid = (s0 + s1) / 2
            b.to(thanh(P(mid - 0.018), P(mid + 0.018), k.r(w + 0.05), bo=False), b.muc)


def nguyet_san(b, k, S):
    """Hàng Yêu Bảo Trượng / nguyệt nha sản (Sa Tăng): mũi giáo + lưỡi liềm trăng ngửa + khâu vàng + cán.
    Cả đầu vũ khí nằm gọn dưới ĐỈNH chuẩn (luật cầm thấp)."""
    V, m = S['vu_khi'], S['mau']
    P0, L = _khung_truc(k)
    h0 = V.get('ha', 0.06)                                    # hạ cả cụm cho đỉnh (kể cả viền) nằm dưới chuẩn

    def P(s, w=0.0):
        return P0(s + h0, w)
    L = L - h0
    bac, vang = m.get('bac', '#D5DBE1'), m.get('vang', '#D9A93A')
    gold_can = m.get('can', vang)
    # cán (chạy suốt từ chân mũi giáo xuống chuôi)
    can = thanh(P(0.30), P(L - 0.05), k.r(V.get('can_day', 0.085)), bo=True)
    b.khoi(can, gold_can)
    with b.cat(can):
        b.bong(can, toi(gold_can, 0.12), k.r(0.06), 0)
    # lưỡi liềm trăng ngửa: tròn ngoài − tròn trong dịch lên theo trục
    sl = V.get('liem_s', 0.64)
    cx, cy = P(sl)
    rr = k.r(V.get('liem_r', 0.46))
    ux, uy = (P(0)[0] - P(1)[0]) / k.R, (P(0)[1] - P(1)[1]) / k.R
    rx_, ry_ = rr * V.get('liem_det', 1.40), rr * 0.92
    goc = math.degrees(math.atan2(ux, -uy))
    dd = V.get('liem_day', 0.22) * k.R - ry_ * 0.05
    liem = elip(cx, cy, rx_, ry_, goc) - elip(cx + ux * dd, cy + uy * dd, rx_ * 0.93, ry_ * 0.95, goc)
    b.khoi(liem, bac)
    with b.cat(liem):
        b.bong(liem, toi(bac, 0.14), k.r(0.05), k.r(0.05))
        b.to(liem - liem.dich(k.r(0.025), k.r(0.04)), sang(bac, 0.08))
    # mũi giáo (lá) trên đỉnh
    mui = cong([P(0.0) + (0,), P(0.22, 0.17), P(0.48, 0.10), P(0.62, 0.0) + (0,), P(0.48, -0.10), P(0.22, -0.17)])
    b.khoi(mui, bac)
    with b.cat(mui):
        b.to(da_giac([P(0.0), P(0.62), P(0.62, 0.3), P(0.0, 0.3)]), toi(bac, 0.10))
    b.khoi(thanh(P(0.58), P(0.72), k.r(0.11), bo=False), vang)   # khâu dưới mũi giáo (trụ đều)
    # khâu vàng nối lưỡi – cán
    kh = thanh(P(sl + 0.28), P(sl + 0.46), k.r(0.13), bo=False)
    b.khoi(kh, vang)
    with b.cat(kh):
        b.bong(kh, toi(vang, 0.15), k.r(0.05), 0)
    b.khoi(tron(*P(L - 0.05), k.r(0.10)), vang)               # chuôi tròn cuối cán


VU_KHI_KIEU = dict(gay=gay_nhu_y, nguyet_san=nguyet_san)
