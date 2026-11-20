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
    if T.get('kieu') == 'heo':
        return _tai_heo(b, k, S)
    if T.get('kieu') == 'nhon':
        return _tai_nhon(b, k, S)
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


def _tai_heo(b, k, S):
    """Tai heo quạt cụp (Bát Giới): gốc giấu sau đầu/mũ, vành trên phồng, chóp rủ xuống, lòng hồng đậm.
    T.trai/phai = dict(goc=(dx, dy), dinh=(dx, dy), rong=R). Tai phải (xa) vẽ trước, nhỏ hơn."""
    T = S['tai']
    da = S['mau'].get('tai', S['mau']['da'])
    long_ = S['mau'].get('tai_trong') or toi(da, 0.10)
    for ten, sg in (('phai', -1), ('trai', 1)):
        E = T[ten]
        g, t = k.H(*E['goc']), k.H(*E['dinh'])
        L = math.hypot(t[0] - g[0], t[1] - g[1])
        ux, uy = (t[0] - g[0]) / L, (t[1] - g[1]) / L
        nx, ny = -uy * sg, ux * sg                              # pháp tuyến hướng LÊN (vành trên)
        w = k.r(E['rong'])

        def Q(a, c):
            return (g[0] + ux * L * a + nx * w * c, g[1] + uy * L * a + ny * w * c)
        h = cong([Q(0, 0.5), Q(0.48, 0.60), Q(0.84, 0.40), Q(1.0, 0.04), Q(0.86, -0.28), Q(0.48, -0.42), Q(0, -0.5)])
        b.khoi(h, da)
        with b.cat(h):
            b.to(cong([Q(0.20, 0.30), Q(0.52, 0.40), Q(0.80, 0.24), Q(0.88, 0.0), Q(0.70, -0.20), Q(0.34, -0.24)]),
                 long_)
            b.bong(h, toi(da, 0.08), k.r(0.07), k.r(0.07))
        b.net([Q(0.30, 0.44), Q(0.60, 0.48), Q(0.84, 0.30)], 'ct', S['mau'].get('gan', toi(da, 0.18)))  # gờ vành tai


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
    if T.get('gai'):                                           # chỏm tóc gai dựng (yêu quái)
        hair = hair + _gai(k, T['gai'])
    for pts, (w0, wm, w1) in T.get('loc', []):                 # lọn tóc ôm mặt buông trước vai (nhân vật nữ)
        hair = hair + net_thuon(_pts(k, pts), k.r(w0), k.r(wm), k.r(w1))
    b.khoi(hair, c)
    with b.cat(hair):
        bx_, by_ = T.get('bong', (0.10, 0.12))
        b.bong(hair, toi(c, 0.10), k.r(bx_), k.r(by_))
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
        if M.get('ma_vt'):                                     # má đặt riêng (vd mõm heo chiếm giữa mặt)
            x, y = k.H(*M['ma_vt'][i])
            y -= k.r(0.22)
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
            if M.get('mi_xech') and bc in M['mi_xech']:   # mí trên phẳng, xếch lên ở đuôi ngoài (mắt híp tinh nghịch)
                ngoai = -1 if i == 0 else 1
                sau = M['mi_xech'][bc]
                y_in, y_out = y - ry * mo * (1 - sau * 1.6), y - ry * mo * (1 - sau * 0.6)
                xa, xb = x - rx * f * 1.4, x + rx * f * 1.4
                ya, yb = (y_out, y_in) if ngoai < 0 else (y_in, y_out)
                mi = da_giac([(xa, y - ry * 2), (xb, y - ry * 2), (xb, yb), (xa, ya)])
                b.to(mi & eye.phong(2), da)
                b.to(net_thuon([(xa + rx * f * 0.45, ya + (yb - ya) * 0.16), (xb - rx * f * 0.45, ya + (yb - ya) * 0.84)],
                               k.r(0.03), k.r(0.045), k.r(0.03)) & eye.phong(k.r(0.03)), ink)
            if M.get('mi'):                                # lông mi cong ở đuôi mắt (nhân vật nữ)
                ng = -1 if i == 0 else 1
                b.to(net_thuon([(x + ng * rx * f * 0.70, y - ry * mo * 0.62), (x + ng * rx * f * 1.15, y - ry * mo * 0.80),
                                (x + ng * rx * f * 1.40, y - ry * mo * 1.10)], k.r(0.035), k.r(0.040), k.r(0.008)), ink)
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
    if M.get('mom'):
        mom_heo(b, k, S)
    mieng(b, k, S)
    if M.get('nanh'):
        _nanh(b, k, S)


def mom_heo(b, k, S):
    """Mõm heo bầu dục giữa mặt (Bát Giới) + 2 lỗ mũi dọc, bóng dưới-phải, đốm sáng trên-trái."""
    Mo = S['mat']['mom']
    x, y = k.H(*Mo['vt'])
    rx, ry = k.r(Mo['rx']), k.r(Mo['ry'])
    c = S['mau'].get('mom', toi(S['mau']['da'], 0.06))
    h = elip(x, y, rx, ry, Mo.get('xoay', 0))
    b.khoi(h, c, 'trong', dang=False)
    with b.cat(h):
        b.bong(h, toi(c, 0.08), k.r(0.05), k.r(0.05))
    lm = S['mau'].get('lo_mui', toi(c, 0.40))
    for i, sx in enumerate((-1, 1)):
        f = 1.0 if i == 0 else 0.88
        b.to(elip(x + sx * rx * 0.34, y + ry * 0.04, rx * 0.11 * f, ry * 0.36 * f), lm)


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
        if A.get('mo'):                                        # áo phanh ngực – lộ bụng (Bát Giới)
            _bung(b, k, S)
        else:
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
        if A.get('ca_sa'):                                     # cà sa khoác ĐÈ lên áo (sau cổ áo, trước đai)
            _ca_sa(b, k, S, body)
        # nếp áo
        for seg in A.get('nep', [[(-0.42, 1.55), (-0.39, 1.82)], [(0.30, 1.58), (0.34, 1.84)]]):
            b.net(_pts_b(k, seg), 'ct', A.get('nep_mau') or toi(c, 0.20))
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


def _bung(b, k, S):
    """Bụng tròn lộ giữa 2 vạt áo phanh: A.mo = điểm mép mở (toạ độ thân, vòng kín), A.ron = rốn."""
    A, m = S['ao'], S['mau']
    da = m.get('bung', m['da'])
    body = k.than()
    belly = cong(_pts_b(k, A['mo']))
    loi = A.get('bung_loi', False)                             # bụng phệ phình RA NGOÀI thân (rìa bóng dáng)
    if not loi:
        belly = belly & body
    else:                                                      # chỉ phình ở eo/bụng, không nhú lên trên vai
        belly = belly & (body + hop(k.bx - 3 * k.R, k.top + k.r(0.45), k.bx + 3 * k.R, k.bot + k.R))
    vat = m.get('vat', sang(m['ao'], 0.10))                    # viền vạt áo sáng hơn thân (đọc được trên nền tối)
    b.to(belly.phong(k.r(A.get('vat_day', 0.07))) & body, vat)
    b.khoi(belly, da, 'trong', dang=loi)
    with b.cat(belly):
        b.bong(belly, toi(da, 0.07), k.r(0.12), k.r(0.10))
        b.to(elip(k.hx + k.r(0.15), k.top - k.r(0.02), k.r(0.80), k.r(0.26)), toi(da, 0.10))   # bóng đầu đổ xuống
    if A.get('ron'):
        x, y = k.B(*A['ron'])
        cr = m.get('ron', toi(da, 0.30))
        b.net([(x - k.r(0.09), y - k.r(0.05)), (x, y), (x + k.r(0.09), y - k.r(0.05))], 'ct', cr)
        b.to(elip(x, y + k.r(0.06), k.r(0.032), k.r(0.04)), cr)
    for seg in A.get('nep_bung', []):
        b.net(_pts_b(k, seg), 'ct', toi(da, 0.18))


def khan_co(b, k, S):
    """Khăn quàng cổ thắt nút (Bát Giới): dải ôm cổ + 2 vạt tam giác buông + nút tròn."""
    K_ = S['khan']
    c = S['mau'].get('khan', S['mau']['vang'])
    d = k.r(K_.get('day', 0.14))
    dai = net_thuon(_pts_b(k, K_['duong']), d, d, d, dau_tron=False) & k.than()
    b.khoi(dai, c, 'trong', dang=False)
    with b.cat(dai):
        b.bong(dai, toi(c, 0.14), 0, k.r(0.05))
    nx, ny, nr = K_['nut']
    x, y = k.B(nx, ny)
    for vat in K_.get('vat', []):
        v = cong([(x, y)] + [k.B(*q) + (0,) for q in vat])
        b.khoi(v, c, 'ct', dang=False)
        with b.cat(v):
            b.bong(v, toi(c, 0.14), k.r(0.05), k.r(0.04))
    b.khoi(tron(x, y, k.r(nr)), S['mau'].get('no') or toi(c, 0.10), 'ct', dang=False)
    b.to(tron(x - k.r(nr * 0.3), y - k.r(nr * 0.3), k.r(nr * 0.28)), sang(c, 0.10))


def mu_tron(b, k, S):
    """Mũ tròn chụp đỉnh (Bát Giới): chỏm phồng hơn đầu, vành vàng ôm trán, hoa mây vàng chính diện."""
    Mu = S['mu']
    c, v, da = S['mau']['mu'], S['mau'].get('vanh_mu', S['mau']['vang']), S['mau']['da']
    no = k.r(Mu.get('no', 0.05))
    vanh = _pts(k, Mu['vanh'])                                  # mép trên dải vành = mép dưới chỏm
    tren = cong(vanh + [k.H(1.9, -0.2) + (0,), k.H(1.9, -2.2) + (0,), k.H(-1.9, -2.2) + (0,), k.H(-1.9, -0.2) + (0,)])
    dx, dy = Mu.get('dinh', (0.02, -0.52))
    rx, ry = Mu.get('chom', (0.96, 0.64))
    chom = (k.dau().phong(no) + elip(*k.H(dx, dy), k.r(rx), k.r(ry))) & tren
    q = mau_diem(vanh, 60)
    dv = k.r(Mu.get('day', 0.12))
    strip = da_giac(q + [(x, y + dv) for x, y in q][::-1])
    band = strip & k.dau().phong(no + k.r(0.01))
    b.do_bong(band, toi(da, 0.10), 0, k.r(0.07), trong=k.dau())   # bóng vành đổ lên trán
    b.khoi(chom, c)
    with b.cat(chom):
        b.bong(chom, toi(c, 0.12), k.r(0.10), k.r(0.10))
        if Mu.get('vet_sang'):                                 # mặc định không (luật 4: vải không có vệt sáng)
            sx, sy = k.H(-0.40, -0.86)
            vs = elip(sx, sy, k.r(0.40), k.r(0.12), -32)
            b.to(vs - vs.dich(k.r(0.04), k.r(0.07)), sang(c, 0.16))
    b.khoi(band, v)
    with b.cat(band):
        b.bong(band, toi(v, 0.14), 0, k.r(0.04))
    if Mu.get('may'):                                           # hoa mây vàng chính diện
        x, y, r = Mu['may']
        x, y = k.H(x, y)
        r = k.r(r)
        may = (tron(x, y - r * 0.18, r * 0.55) + tron(x - r * 0.55, y + r * 0.10, r * 0.42) +
               tron(x + r * 0.55, y + r * 0.10, r * 0.42) + hop(x - r * 0.95, y + r * 0.05, x + r * 0.95, y + r * 0.50, r * 0.22))
        b.khoi(may, v, 'ct', dang=False)
        with b.cat(may):
            b.bong(may, toi(v, 0.14), r * 0.12, r * 0.12)
        for sx_ in (-1, 0, 1):                                   # 3 xoắn mây
            cx_, cy_ = x + sx_ * r * 0.55, y + (0.12 if sx_ else -0.14) * r
            rr = r * (0.22 if sx_ else 0.28)
            sp = [(cx_ + rr * (1 - i / 16) * math.cos(i * 0.55 + 2.2), cy_ + rr * (1 - i / 16) * math.sin(i * 0.55 + 2.2))
                  for i in range(15)]
            b.net(sp, k.r(0.020), toi(v, 0.35))
    return chom + band


def day_mu(b, k, S):
    """Dải buông của mũ (Tì Lư) – lớp SAU CÙNG (sau tai, thân, đầu): chỉ lộ phần thò ra cạnh đầu, buông xuống vai.
    Mu.day_bang = [(dx, dy, dài, rộng), …] (R)."""
    Mu, m = S['mu'], S['mau']
    if not Mu.get('day_bang'):
        return
    do, kem = m.get('mu', '#D23B2B'), m.get('day_mu', '#EAD08A')
    for dx, dy, L, w in Mu.get('day_bang', []):
        x, y = k.H(dx, dy)
        L, w = k.r(L), k.r(w)
        lech = w * 0.27 * (1 if dx > 0 else -1)                   # đuôi loe + lệch ra ngoài như vải
        bang = cong([(x - w / 2, y, 0), (x + w / 2, y, 0), (x + lech + w * 0.64, y + L, 0), (x + lech, y + L - w * 0.40, 0),
                     (x + lech - w * 0.64, y + L, 0)])
        b.khoi(bang, kem)
        b.net([(x, y + w * 0.5), (x + lech * 0.5, y + L * 0.6), (x + lech, y + L - w * 0.75)], k.r(0.026), m.get('chi_mu', do), thuon=False)


def mu_ti_lu(b, k, S):
    """Mũ Tì Lư (Đường Tăng): vành vàng lõi đỏ ôm trán + 5 cánh sen nhọn đỏ viền vàng (cánh giữa cao nhất,
    vẽ từ ngoài vào trước) + 2 dải buông kem hai bên mặt xuống vai.
    Mu.canh = [(dx, nửa rộng, cao), …] (R); Mu.truoc = dx cánh chính diện; Mu.day_bang = [(dx, dy, dài, rộng), …]."""
    Mu, m = S['mu'], S['mau']
    do, vang, kem = m.get('mu', '#D23B2B'), m['vang'], m.get('day_mu', '#EAD08A')
    da = m['da']
    vanh = _pts(k, Mu['vanh'])
    q = mau_diem(vanh, 80)

    def y_at(x):
        return min(q, key=lambda p_: abs(p_[0] - x))[1]
    # cánh sen
    front = Mu.get('truoc', 0.20)
    for dx, hw, h in sorted(Mu['canh'], key=lambda c_: -abs(c_[0] - front)):
        x = k.hx + dx * k.R
        y0 = y_at(x) + k.r(0.06)
        hw, h = k.r(hw), k.r(h)
        canh = cong([(x - hw, y0, 0), (x - hw * 0.98, y0 - h * 0.40), (x - hw * 0.52, y0 - h * 0.80), (x, y0 - h, 0),
                     (x + hw * 0.52, y0 - h * 0.80), (x + hw * 0.98, y0 - h * 0.40), (x + hw, y0, 0)])
        b.khoi(canh, vang)
        long_ = canh.phong(-k.r(Mu.get('vien_canh', 0.065)))
        b.to(long_, do)
        with b.cat(long_):
            b.bong(long_, toi(do, 0.12), hw * 0.45, 0)
        b.ke(long_, b.D['ct'])
        if Mu.get('nu', 0.05):
            b.khoi(tron(x, y0 - h, k.r(Mu.get('nu', 0.05))), vang, 'ct')
    # vành
    no = k.r(Mu.get('no', 0.07))
    dv = k.r(Mu.get('day', 0.17))
    band = da_giac(q + [(x, y + dv) for x, y in q][::-1]) & k.dau().phong(no)
    b.do_bong(band, toi(da, 0.10), 0, k.r(0.07), trong=k.dau())
    b.khoi(band, vang)
    loi = da_giac([(x, y + dv * 0.28) for x, y in q] + [(x, y + dv * 0.72) for x, y in q][::-1]) & band
    b.to(loi, do)
    b.ke(loi, b.D['trong'])
    return band


def mu(b, k, S):
    """Mũ theo kiểu: 'tron' (Bát Giới) · 'ti_lu' (Đường Tăng)."""
    return {'tron': mu_tron, 'ti_lu': mu_ti_lu}[S['mu'].get('kieu', 'tron')](b, k, S)


def _ca_sa(b, k, S, body):
    """Cà sa đỏ khoác chéo (Đường Tăng): mảng đỏ dưới đường chéo `cheo`, lưới ô gạch vàng so le, viền vàng mép chéo."""
    C, m = S['ao']['ca_sa'], S['mau']
    do, luoi = m.get('ca_sa', '#B5362A'), m.get('luoi', m['vang'])
    (x0, y0), (x1, y1) = C['cheo']
    yb = C.get('duoi', 1.88)
    reg = da_giac([k.B(x0, y0), k.B(x1, y1), k.B(x1, yb), k.B(x0, yb)]) & body
    b.khoi(reg, do, 'trong', dang=False)
    o, og, nl = C.get('o', 0.22), C.get('gach', 0.45), k.r(C.get('net', 0.025))

    def luoi_(mau_):
        y, i = min(y0, y1) + o * 0.5, 0
        while y < yb - 0.02:
            b.net([k.B(x0, y), k.B(x1, y)], nl, mau_, thuon=False)
            x = x0 + (og * 0.5 if i % 2 else 0)
            while x < x1:
                b.net([k.B(x, y), k.B(x, min(y + o, yb))], nl, mau_, thuon=False)
                x += og
            y, i = y + o, i + 1
    with b.cat(reg):
        luoi_(luoi)
    sh = (reg - reg.dich(-k.r(0.24), 0)) & reg                 # bóng phải: phủ đỏ tối + lưới tối
    b.to(sh, toi(do, 0.10))
    with b.cat(sh):
        luoi_(toi(luoi, 0.14))
    vien = thanh(k.B(x0, y0), k.B(x1, y1), k.r(C.get('vien', 0.055)), bo=False) & body
    b.khoi(vien, luoi, 'ct', dang=False)


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


def cao_chin_rang(b, k, S):
    """Cửu xỉ đinh ba (Bát Giới): thanh ngang vuông góc trục + 9 răng chĩa xuống, 2 khâu vàng, cán bạc.
    Hạ cả cụm (`ha`) để đầu thanh ngang (bên trái nhô cao do nghiêng 8.7°) vẫn dưới ĐỈNH chuẩn."""
    V, m = S['vu_khi'], S['mau']
    P0, L = _khung_truc(k)
    w0, w1 = V.get('tu', -0.52), V.get('den', 0.72)
    th = V.get('thanh', 0.15)
    h0 = V.get('ha', (abs(w0) + 0.08) * math.sin(math.radians(8.7)) + 0.05)

    def P(sv, wv=0.0):
        return P0(sv + h0, wv)
    L = L - h0
    bac, can_c, vang = m.get('bac', '#E0E0E2'), m.get('can', '#C2C5CC'), m.get('vang', '#D3A85B')
    n, rd, rw = V.get('so_rang', 9), V.get('rang_dai', 0.34), V.get('rang_rong', 0.095)
    can = thanh(P(th + rd + 0.07), P(L - 0.05), k.r(V.get('can_day', 0.085)), bo=True)   # cán bắt đầu dưới răng
    b.khoi(can, can_c)
    with b.cat(can):
        b.bong(can, toi(can_c, 0.12), k.r(0.06), 0)
    hw = rw / 2
    rang = gop(*[cong([P(th * 0.5, w - hw) + (0,), P(th * 0.5, w + hw) + (0,), P(th + rd * 0.62, w + hw * 0.95),
                       P(th + rd, w) + (0,), P(th + rd * 0.62, w - hw * 0.95)])            # răng thuôn nhọn
                 for w in (w0 + (w1 - w0) * i / (n - 1) for i in range(n))])
    bar = thanh(P(th / 2, w0 - 0.04), P(th / 2, w1 + 0.04), k.r(th / 2), bo=True)
    # răng mảnh: viền 'trong' riêng, KHÔNG góp vào viền ngoài dày (viền 9px sẽ nuốt răng 11px thành vạch đen)
    b.khoi(rang, bac, 'trong', dang=False)
    with b.cat(rang):
        b.bong(rang, toi(bac, 0.14), k.r(0.035), 0)
    b.dang_phu.append(rang)
    b.khoi(bar, bac)
    with b.cat(bar):
        b.bong(bar, toi(bac, 0.14), 0, k.r(0.05))
        b.to(bar - bar.dich(0, k.r(0.035)), sang(bac, 0.10))
    for wa, wb in ((w0 - 0.07, w0 + 0.05), (w1 - 0.05, w1 + 0.07)):   # khâu vàng hai đầu thanh
        dk = thanh(P(th / 2, wa), P(th / 2, wb), k.r(th / 2 + 0.015), bo=False)
        b.khoi(dk, vang, 'ct')
        with b.cat(dk):
            b.bong(dk, toi(vang, 0.15), 0, k.r(0.04))
    for s0, s1 in V.get('khau', ((th + rd + 0.04, th + rd + 0.18), (th + rd + 0.30, th + rd + 0.38))):
        kh = thanh(P(s0), P(s1), k.r(0.12), bo=False)
        b.khoi(kh, vang)
        with b.cat(kh):
            b.bong(kh, toi(vang, 0.15), k.r(0.05), 0)
    b.khoi(tron(*P(L - 0.05), k.r(0.10)), vang)                # chuôi tròn cuối cán


def tich_truong(b, k, S):
    """Tích trượng (Đường Tăng): mũi nhọn vàng trên đỉnh, vòng lớn rỗng + 2 khoen nhỏ hai bên, khâu vàng, cán gỗ nâu.
    Vòng chỉ góp ĐĨA NGOÀI vào bóng dáng (viền ngoài dày không ăn vào lòng vòng)."""
    V, m = S['vu_khi'], S['mau']
    P0, L = _khung_truc(k)
    h0 = V.get('ha', 0.04)

    def P(sv, wv=0.0):
        return P0(sv + h0, wv)
    L = L - h0
    vang, can_c = m.get('vang', '#E6B23C'), m.get('can', '#9A7328')
    sv, rv = V.get('vong_s', 0.58), V.get('vong_r', 0.33)
    ri = rv * V.get('vong_trong', 0.58)
    can = thanh(P(sv + rv + 0.06), P(L - 0.04), k.r(V.get('can_day', 0.075)), bo=True)
    b.khoi(can, can_c)
    with b.cat(can):
        b.bong(can, toi(can_c, 0.12), k.r(0.05), 0)
        b.net([P(sv + rv + 0.35, -0.02), P(L - 0.45, -0.025)], k.r(0.016), toi(can_c, 0.28), thuon=False)  # vân gỗ
    mui = cong([P(0) + (0,), P(0.14, 0.075), P(sv - rv + 0.04, 0.085) + (0,), P(sv - rv + 0.04, -0.085) + (0,),
                P(0.14, -0.075)])
    b.khoi(mui, vang)
    with b.cat(mui):
        b.bong(mui, toi(vang, 0.14), k.r(0.04), 0)
    cx, cy = P(sv)
    vong = tron(cx, cy, k.r(rv)) - tron(cx, cy, k.r(ri))
    b.khoi(vong, vang, 'trong', dang=False)
    with b.cat(vong):
        b.bong(vong, toi(vang, 0.14), k.r(0.05), k.r(0.05))
        b.to(vong - vong.dich(k.r(0.025), k.r(0.04)), sang(vang, 0.12))
    b.dang.append(tron(cx, cy, k.r(rv)))
    b.lo.append(tron(cx, cy, k.r(ri)))                          # lỗ vòng giữ rỗng trong ảnh bóng dáng
    for w in (-1, 1):                                          # 2 khoen treo vào vòng (4h, 8h)
        x, y = P(sv + V.get('khoen_s', 0.14), w * V.get('khoen_w', 0.30))
        r = k.r(V.get('khoen_r', 0.105))
        khoen = tron(x, y, r) - tron(x, y, r * V.get('khoen_lo', 0.52))
        b.khoi(khoen, vang, 'ct', dang=False)
        b.lo.append(tron(x, y, r * V.get('khoen_lo', 0.52)))
        with b.cat(khoen):
            b.bong(khoen, toi(vang, 0.14), r * 0.25, r * 0.25)
        b.dang.append(tron(x, y, r))
    kh = thanh(P(sv + rv - 0.04), P(sv + rv + 0.14), k.r(0.105), bo=False)
    b.khoi(kh, vang)
    with b.cat(kh):
        b.bong(kh, toi(vang, 0.15), k.r(0.04), 0)
    b.khoi(tron(*P(L - 0.04), k.r(0.09)), vang)               # chuôi tròn


VU_KHI_KIEU = dict(gay=gay_nhu_y, nguyet_san=nguyet_san, cao=cao_chin_rang, tich_truong=tich_truong)


# ═══════════════════════════ NGỰA (Bạch Long Mã) ═══════════════════════════
# Dùng với KhungNgua (khung.py). Lông trắng: bóng phẳng màu `mau.bong` (xám-xanh nhạt) thay vì toi().
def _bong_long(S):
    return S['mau'].get('bong') or toi(S['mau']['da'], 0.10)


def _xoan(b, k, x, y, r, c, quay=1, w=0.022):
    """Nét xoắn mây nhỏ (bờm, đuôi, hoạ tiết) tâm (x, y) px, bán kính r px."""
    sp = [(x + quay * r * (1 - i / 16) * math.cos(i * 0.55 + 2.2), y + r * (1 - i / 16) * math.sin(i * 0.55 + 2.2))
          for i in range(15)]
    b.net(sp, k.r(w), c)


def _cum_may(k, bup):
    """Cụm búp mây (bờm, đuôi): bup = [(dx, dy, r), …] theo R so với tâm đầu."""
    return gop(*[tron(*k.H(dx, dy), k.r(r)) for dx, dy, r in bup])


def _ve_cum_may(b, k, S, bup, xoan=(), dang=True):
    c = S['mau']['bom']
    h = _cum_may(k, bup)
    b.khoi(h, c, 'trong', dang=dang)
    with b.cat(h):
        b.bong(h, toi(c, 0.10), k.r(0.08), k.r(0.08))
    for dx, dy, r, q in xoan:
        x, y = k.H(dx, dy)
        _xoan(b, k, x, y, k.r(r), toi(c, 0.30), q)
    return h


def duoi_ngua(b, k, S):
    """Đuôi bông mây (lớp sau cùng, bám mông trái)."""
    D = S['duoi_ngua']
    if D.get('bup'):
        return _ve_cum_may(b, k, S, D['bup'], D.get('xoan', ()))
    c = S['mau']['bom']
    w0, wm, w1 = (k.r(v) for v in D.get('day', (0.34, 0.44, 0.10)))
    h = net_thuon(_pts(k, D['duong']), w0, wm, w1)
    b.khoi(h, c, 'trong')
    with b.cat(h):
        b.bong(h, toi(c, 0.10), k.r(0.09), k.r(0.06))
    for seg in D.get('soi', []):
        b.net(_pts(k, seg), 'ct', toi(c, 0.30))
    if D.get('cuon'):                                            # lọn cuộn mây ở chóp đuôi (cùng "ngôn ngữ mây" với bờm)
        h = h + _ve_cum_may(b, k, S, D['cuon'], D.get('xoan', ()))
    return h


def chan_ngua(b, k, S, xa):
    """2 chân phía xa (xa=True, tô màu bóng, nhấc nhẹ) hoặc 2 chân phía gần. Vẽ TRƯỚC thân (thân đè mép trên)."""
    m = S['mau']
    c = _bong_long(S) if xa else m['da']
    cm = m.get('mong_xa' if xa else 'mong', toi(c, 0.12))
    for x in (k.N['chan_xa'] if xa else k.N['chan_gan']):
        chan, mong = k.chan(x, xa)
        b.khoi(chan, c)
        with b.cat(chan):
            if not xa:
                b.bong(chan, _bong_long(S), k.r(0.12), 0)
            else:
                b.vet_sang(chan, m['da'], k.r(0.09), 0)
            b.to(mong, cm)
            b.ke(mong, b.D['ct'])
            b.bong(mong, toi(cm, 0.10), k.r(0.08), 0)


def chan_xa(b, k, S):
    chan_ngua(b, k, S, True)


def chan_gan(b, k, S):
    chan_ngua(b, k, S, False)


def than_ngua(b, k, S):
    """Thân bầu dục nằm ngang + bóng phẳng dưới-phải + bóng đầu đổ lên ngực."""
    c = S['mau']['da']
    h = k.than()
    b.khoi(h, c)
    with b.cat(h):
        b.bong(h, _bong_long(S), k.r(0.20), k.r(0.18))
        b.to(elip(*k.H(0.10, 0.92), k.r(0.95), k.r(0.30)), _bong_long(S))       # bóng đầu đổ xuống ngực
    return h


def yen_ngua(b, k, S):
    """Yên: dây đai vàng vòng bụng (trong thân) + tấm yên xanh đen viền vàng gồ nhẹ trên lưng."""
    Y, m = S['yen'], S['mau']
    vang, c = m['vang'], m['yen']
    body = k.than()
    dw = k.r(Y.get('dai_rong', 0.17))
    dai = net_thuon(_pts(k, Y['dai']), dw, dw, dw, dau_tron=False) & body
    b.khoi(dai, vang, 'trong', dang=False)
    with b.cat(dai):
        b.bong(dai, toi(vang, 0.14), k.r(0.05), 0)
    tam = cong(_pts(k, Y['tam']))
    b.do_bong(tam, toi(_bong_long(S), 0.04), k.r(0.04), k.r(0.07), trong=body)
    b.khoi(tam, vang, 'trong')                                    # viền vàng = tấm yên vàng, lõi xanh co vào
    long_ = tam.phong(-k.r(Y.get('vien', 0.08)))
    b.to(long_, c)
    with b.cat(long_):
        b.bong(long_, toi(c, 0.08), k.r(0.10), k.r(0.10))
    b.ke(long_, b.D['ct'])
    return tam


def _hoa_may(b, k, x, y, r, c):
    """Hoa mây vàng nhỏ (như trên mũ Bát Giới) tâm (x, y) px, cỡ r px."""
    may = (tron(x, y - r * 0.18, r * 0.55) + tron(x - r * 0.55, y + r * 0.10, r * 0.42) +
           tron(x + r * 0.55, y + r * 0.10, r * 0.42) + hop(x - r * 0.95, y + r * 0.05, x + r * 0.95, y + r * 0.50, r * 0.22))
    b.khoi(may, c, 'ct', dang=False)
    for sx_ in (-1, 0, 1):
        cx_, cy_ = x + sx_ * r * 0.55, y + (0.12 if sx_ else -0.14) * r
        _xoan(b, k, cx_, cy_, r * (0.22 if sx_ else 0.28), toi(c, 0.35), 1, 0.016)


def khan_ngua(b, k, S):
    """Khăn quàng ngực xanh đen dưới đầu: dải cong + nút thắt + 2 vạt buông + hoa mây vàng (vẽ trước đầu)."""
    K_, m = S['khan_ngua'], S['mau']
    c = m['khan']
    d = k.r(K_.get('day', 0.30))
    dai = net_thuon(_pts(k, K_['duong']), d * 0.8, d, d * 0.7, dau_tron=True)
    nx, ny, nr = K_['nut']
    x, y = k.H(nx, ny)
    vats = [cong([(x, y)] + [k.H(*q) for q in v]) for v in K_.get('vat', [])]   # tà khăn bầu (không góc nhọn)
    for v in vats:                                               # tà khăn: viền trong, không ăn viền ngoài dày
        b.khoi(v, c, 'trong', dang=False)
        b.dang_phu.append(v)
        with b.cat(v):
            b.bong(v, toi(c, 0.08), k.r(0.05), k.r(0.04))
    if K_.get('vat_nguc'):                                       # vạt tam giác buông trước ngực (sau dải)
        vn = cong(_pts(k, K_['vat_nguc']))
        b.khoi(vn, c)
        with b.cat(vn):
            b.bong(vn, toi(c, 0.08), k.r(0.08), k.r(0.04))
    b.khoi(dai, c)
    with b.cat(dai):
        b.bong(dai, toi(c, 0.08), 0, k.r(0.07))
    b.khoi(elip(x, y, k.r(nr * 1.15), k.r(nr)), toi(c, 0.04), 'trong')
    b.to(elip(x - k.r(nr * 0.38), y - k.r(nr * 0.38), k.r(nr * 0.36), k.r(nr * 0.24), -30), sang(c, 0.22))  # tách nút khỏi màu mực
    if K_.get('may'):
        mx, my, mr = K_['may']
        _hoa_may(b, k, *k.H(mx, my), k.r(mr), m['vang'])
    return dai


def bom_sau(b, k, S):
    """Bờm phía sau gáy (vẽ TRƯỚC đầu): búp mây buông dọc gáy trái xuống lưng – che chỗ đầu nối thân."""
    B_ = S['bom']
    c = S['mau']['bom']
    for loc in B_.get('loc', []):                                # lọn bờm dài buông qua vai (vẽ sau búp)
        pts, (w0, wm, w1) = loc
        h = net_thuon(_pts(k, pts), k.r(w0), k.r(wm), k.r(w1))
        b.khoi(h, c, 'trong')
        with b.cat(h):
            b.bong(h, toi(c, 0.10), k.r(0.07), k.r(0.05))
    return _ve_cum_may(b, k, S, B_['sau'], B_.get('xoan_sau', ()))


def tai_ngua(b, k, S):
    """Tai ngựa nhọn hình lá (sau đầu): lòng hồng; tai xa nhỏ hơn. tai_ngua = [dict(goc, dinh, rong), …] xa→gần."""
    m = S['mau']
    c, long_ = m['da'], m.get('tai_trong', '#F4AFC0')
    for E in S['tai_ngua']:
        g, t = k.H(*E['goc']), k.H(*E['dinh'])
        L = math.hypot(t[0] - g[0], t[1] - g[1])
        ux, uy = (t[0] - g[0]) / L, (t[1] - g[1]) / L
        nx, ny = -uy, ux
        w = k.r(E['rong'])

        def Q(a, s):
            return (g[0] + ux * L * a + nx * w * s, g[1] + uy * L * a + ny * w * s)
        h = cong([Q(0, -0.5), Q(0.45, -0.52), Q(1.0, 0.0) + (0,), Q(0.45, 0.52), Q(0, 0.5)])
        b.khoi(h, c)
        with b.cat(h):
            b.to(cong([Q(0.12, -0.26), Q(0.50, -0.26), Q(0.86, 0.0) + (0,), Q(0.50, 0.26), Q(0.12, 0.26)]), long_)
            b.bong(h, _bong_long(S), k.r(0.07), k.r(0.04))


def dau_ngua(b, k, S):
    """Khối đầu + mõm liền (lông trắng) + bóng trăng khuyết dưới-phải."""
    c = S['mau']['da']
    h = k.dau_mom()
    b.khoi(h, c)
    with b.cat(h):
        b.bong(h, _bong_long(S), k.r(0.10), k.r(0.10))
    mx, my, rx, ry = k.N['mom']
    tu, den = S.get('mom_vien', (125, 215))                    # nét trong mép trái mõm (ranh mõm – má)
    b.net([k.H(mx + rx * math.cos(math.radians(a)), my + ry * math.sin(math.radians(a))) for a in range(tu, den + 1, 10)],
          'trong')
    return h


def bom_tren(b, k, S):
    """Bờm trước trán (chỏm mây) – đè lên đỉnh đầu, giữa hai tai."""
    B_ = S['bom']
    return _ve_cum_may(b, k, S, B_['tren'], B_.get('xoan_tren', ()))


def sung_rong(b, k, S):
    """2 sừng rồng vàng ngắn, mỗi sừng 1 nhánh. sung = [dict(goc, dinh, nhanh, day), …] xa→gần."""
    c = S['mau']['vang']
    for E in S['sung']:
        g, t, n = k.H(*E['goc']), k.H(*E['dinh']), E['nhanh']
        d = k.r(E.get('day', 0.15))
        m_ = ((g[0] + t[0]) / 2 + k.r(E.get('cong', 0.04)), (g[1] + t[1]) / 2)
        than = net_thuon([g, m_, t], d, d * 0.92, d * 0.62)
        p0 = (g[0] + (t[0] - g[0]) * 0.50, g[1] + (t[1] - g[1]) * 0.50)
        nh = net_thuon([p0, k.H(*n)], d * 0.75, d * 0.62, d * 0.50)
        h = than + nh
        b.khoi(h, c)
        with b.cat(h):
            b.bong(h, toi(c, 0.14), k.r(0.05), 0)


def cuong_ngua(b, k, S):
    """Dây cương vàng mảnh: vòng mũi ôm mõm + dây má lên sau tai + khoen tròn; 2 lỗ mũi chấm."""
    C = S['cuong']
    c = S['mau']['vang']
    mx, my, rx, ry = k.N['mom']
    s = C.get('s', 0.90)
    d = k.r(C.get('day', 0.075))
    vong = [k.H(mx + rx * s * math.cos(math.radians(a)), my + ry * s * math.sin(math.radians(a)))
            for a in range(C.get('tu', 196), C.get('den', 336), 10)]
    mui = net_thuon(vong, d, d, d, dau_tron=True)
    ma = net_thuon(_pts(k, C['ma']), d, d, d)
    for h in (ma, mui):
        b.khoi(h, c, 'ct', dang=False)
    x, y = vong[0]
    b.khoi(tron(x, y, k.r(0.07)), c, 'ct', dang=False)
    b.to(tron(x, y, k.r(0.028)), toi(c, 0.40))
    for i, (dx, dy) in enumerate(C.get('lo_mui', [])):
        f = 1.0 if i == 0 else 0.86
        b.to(elip(*k.H(dx, dy), k.r(0.032) * f, k.r(0.062) * f, C.get('mui_xoay', 28)), b.muc)


# ═══════════════════════════ NHÂN VẬT NỮ (Bạch Cốt Tinh, Nữ Vương…) ═══════════════════════════
def toc_dai(b, k, S):
    """Tóc dài buông SAU đầu và thân (lớp đầu tiên): khối tóc = đầu nở + mảng buông theo `duong`
    (điểm R theo tâm đầu, vòng kín). Thân vẽ sau đè giữa → chỉ lộ hai bên vai/lưng."""
    T = S['toc_dai']
    c = S['mau']['toc']
    h = k.dau().phong(k.r(T.get('no', 0.07))) + cong(_pts(k, T['duong']))
    b.khoi(h, c)
    with b.cat(h):
        b.bong(h, toi(c, 0.10), k.r(0.16), k.r(0.06))
    for seg in T.get('soi', []):
        b.net(_pts(k, seg), 'ct', toi(c, 0.22))
    return h


def tram_xuong(b, k, S):
    """Trâm xương nhỏ cài tóc (Bạch Cốt Tinh) + nơ ruy băng tuỳ chọn. tram = dict(vt, goc, dai, r, no=(dx, dy, cỡ))."""
    T, m = S['tram'], S['mau']
    x, y = k.H(*T['vt'])
    L, r = k.r(T.get('dai', 0.42)), k.r(T.get('r', 0.07))
    g = math.radians(T.get('goc', -35))
    ux, uy = math.cos(g), math.sin(g)
    nx, ny = -uy, ux
    p0, p1 = (x - ux * L / 2, y - uy * L / 2), (x + ux * L / 2, y + uy * L / 2)
    xg = m.get('xuong', '#EFE8DA')
    bone = thanh(p0, p1, r * 0.55)
    for px, py in (p0, p1):
        bone = bone + tron(px + nx * r * 0.62, py + ny * r * 0.62, r) + tron(px - nx * r * 0.62, py - ny * r * 0.62, r)
    if T.get('no'):                                              # nơ ruy băng (sau trâm)
        bx, by, s = T['no']
        bx, by = k.H(bx, by)
        s = k.r(s)
        cn = m.get('no_toc', m.get('co', '#9C7CC8'))
        for d in (-1, 1):
            vong = cong([(bx, by), (bx + d * s * 1.05, by - s * 0.62), (bx + d * s * 1.15, by + s * 0.30)])
            b.khoi(vong, cn, 'trong')
            with b.cat(vong):
                b.bong(vong, toi(cn, 0.10), s * 0.18, s * 0.18)
        for d in (-1, 1):
            b.khoi(net_thuon([(bx, by), (bx + d * s * 0.35, by + s * 0.70), (bx + d * s * 0.55, by + s * 1.15)],
                             s * 0.36, s * 0.40, s * 0.30, dau_tron=False), cn, 'ct', dang=False)
        b.khoi(tron(bx, by, s * 0.30), toi(cn, 0.06), 'ct')
    b.khoi(bone, xg, 'trong')
    with b.cat(bone):
        b.bong(bone, toi(xg, 0.10), r * 0.30, r * 0.30)


def _so_nho(b, k, cx, cy, r, c):
    """Sọ nhỏ dễ thương (tròn + hàm bo) – mắt chấm, mũi tam giác, 2 vạch răng."""
    so = tron(cx, cy - r * 0.20, r * 0.92) + hop(cx - r * 0.56, cy + r * 0.36, cx + r * 0.56, cy + r * 1.08, r * 0.28)
    b.khoi(so, c, 'trong')
    with b.cat(so):
        b.bong(so, toi(c, 0.12), r * 0.25, r * 0.22)
    for s in (-1, 1):
        b.to(elip(cx + s * r * 0.38, cy + r * 0.02, r * 0.24, r * 0.28), b.muc)
        b.to(tron(cx + s * r * 0.38 - r * 0.07, cy - r * 0.06, r * 0.07), '#FFFFFF')
    b.to(da_giac([(cx, cy + r * 0.30), (cx - r * 0.10, cy + r * 0.48), (cx + r * 0.10, cy + r * 0.48)]), b.muc)
    for s in (-0.22, 0.22):
        b.net([(cx + s * r, cy + r * 0.62), (cx + s * r, cy + r * 0.86)], r * 0.10, thuon=False)
    return so


def gay_xuong(b, k, S):
    """Gậy xương (Bạch Cốt Tinh): cán xương trắng ngà, đốt khớp 2 núm ở chuôi, khâu ruy băng tím,
    sọ nhỏ dễ thương trên đỉnh. Theo trục chuẩn – đỉnh sọ dưới ĐỈNH chuẩn."""
    V, m = S['vu_khi'], S['mau']
    P0, L = _khung_truc(k)
    h0 = V.get('ha', 0.04)

    def P(s, w=0.0):
        return P0(s + h0, w)
    L = L - h0
    xg = m.get('xuong', '#EFE8DA')
    rs = V.get('so_r', 0.24)
    can = thanh(P(rs * 1.6), P(L - 0.12), k.r(V.get('day', 0.07)), bo=True)
    b.khoi(can, xg)
    with b.cat(can):
        b.bong(can, toi(xg, 0.10), k.r(0.05), 0)
    for w in (-0.075, 0.075):                                    # đầu khớp xương cuối chuôi
        b.khoi(tron(*P(L - 0.08, w), k.r(0.085)), xg)
    cn = m.get('no_gay', m.get('co', '#8E6BB8'))
    for s0 in V.get('dot', (rs * 2.2 + 0.30,)):                 # nơ ruy băng tím buộc cán, 2 đuôi bay sang phải
        bx, by = P(s0)
        s = k.r(V.get('no_co', 0.13))
        for pts in ([(bx, by), (bx + s * 1.2, by + s * 0.9), (bx + s * 2.6, by + s * 1.0)],
                    [(bx, by), (bx + s * 0.9, by + s * 1.6), (bx + s * 2.1, by + s * 2.4)]):
            duoi = net_thuon(pts, s * 0.55, s * 0.62, s * 0.40, dau_tron=False)
            b.khoi(duoi, cn, 'trong', dang=False)                 # mảnh: không ăn viền ngoài dày
            b.dang_phu.append(duoi)
        for d in (-1, 1):
            vong = cong([(bx, by), (bx + d * s * 1.05, by - s * 0.62), (bx + d * s * 1.15, by + s * 0.30)])
            b.khoi(vong, cn, 'trong', dang=False)
            b.dang_phu.append(vong)
            with b.cat(vong):
                b.bong(vong, toi(cn, 0.10), s * 0.18, s * 0.18)
        b.khoi(tron(bx, by, s * 0.32), toi(cn, 0.06), 'ct')
    cx, cy = P(rs * 1.12)
    _so_nho(b, k, cx, cy, k.r(rs), xg)


VU_KHI_KIEU['gay_xuong'] = gay_xuong


def mien_phuong(b, k, S):
    """Mũ phượng / miện vàng (Nữ Vương): vành vàng ôm chân tóc + các cánh nhọn đứng nạm ngọc đỏ +
    tua vàng rủ hai bên (hạt đỏ) + chấm hoa điền đỏ giữa trán.
    mien = dict(vanh=[điểm R], day, canh=[(dx, nửa rộng, cao)], tua=[(dx, dy, dài)], hoa_dien=(dx, dy))."""
    M_, m = S['mien'], S['mau']
    vang, ngoc = m['vang'], m.get('ngoc', '#D23B3B')
    q = mau_diem(_pts(k, M_['vanh']), 80)

    def y_at(x):
        return min(q, key=lambda p_: abs(p_[0] - x))[1]
    for dx, dy, L in M_.get('tua', []):                          # tua rủ (sau cùng của miện)
        x, y = k.H(dx, dy)
        b.net([(x, y), (x + k.r(0.01), y + k.r(L))], k.r(0.035), toi(vang, 0.10), thuon=False)
        hr = k.r(M_.get('hat', 0.055))
        hat = tron(x + k.r(0.01), y + k.r(L) + hr * 0.9, hr)
        b.khoi(hat, ngoc, 'ct', dang=False)
    front = M_.get('truoc', 0.30)
    for dx, hw, h in sorted(M_.get('canh', []), key=lambda c_: -abs(c_[0] - front)):
        x = k.hx + dx * k.R
        y0 = y_at(x) + k.r(0.04)
        hw, h = k.r(hw), k.r(h)
        canh = cong([(x - hw, y0, 0), (x - hw * 0.90, y0 - h * 0.45), (x - hw * 0.40, y0 - h * 0.82), (x, y0 - h, 0),
                     (x + hw * 0.40, y0 - h * 0.82), (x + hw * 0.90, y0 - h * 0.45), (x + hw, y0, 0)])
        b.khoi(canh, vang)
        with b.cat(canh):
            b.bong(canh, toi(vang, 0.14), hw * 0.45, 0)
        b.khoi(tron(x, y0 - h * 0.42, min(hw * 0.42, k.r(0.08))), ngoc, 'ct')
    dv = k.r(M_.get('day', 0.13))
    band = da_giac(q + [(x, y + dv) for x, y in q][::-1]) & k.dau().phong(k.r(M_.get('no', 0.09)))
    b.khoi(band, vang)
    with b.cat(band):
        b.bong(band, toi(vang, 0.14), 0, k.r(0.04))
    for dx in M_.get('ngoc_vanh', []):                          # ngọc đỏ nhỏ trên vành
        x = k.hx + dx * k.R
        b.khoi(tron(x, y_at(x) + dv * 0.5, k.r(0.045)), ngoc, 'ct', dang=False)
    if M_.get('hoa_dien'):                                       # chấm hoa điền đỏ giữa trán
        x, y = k.H(*M_['hoa_dien'])
        r = k.r(0.05)
        b.to(cong([(x, y - r * 1.5, 0), (x + r * 0.8, y), (x, y + r * 1.5, 0), (x - r * 0.8, y)]), ngoc)
    return band


def quat_tron(b, k, S):
    """Quạt lụa tròn (Nữ Vương): mặt quạt tròn kem viền vàng + hoa đỏ 5 cánh, cán vàng, tua đỏ ở chuôi.
    Mặt quạt đặt ở ĐỈNH trục chuẩn (cầm thấp)."""
    V, m = S['vu_khi'], S['mau']
    P0, L = _khung_truc(k)
    h0 = V.get('ha', 0.03)

    def P(s, w=0.0):
        return P0(s + h0, w)
    L = L - h0
    vang = m.get('vang', '#E2B13C')
    rq = V.get('quat_r', 0.40)
    can = thanh(P(rq * 1.6), P(L - 0.10), k.r(V.get('day', 0.06)), bo=True)
    b.khoi(can, m.get('can', vang))
    with b.cat(can):
        b.bong(can, toi(m.get('can', vang), 0.12), k.r(0.04), 0)
    b.khoi(tron(*P(L - 0.10), k.r(0.07)), vang, 'ct')            # chuôi tròn
    x, y = P(rq * 2 + 0.10, 0.10)                                # tua đỏ rủ dưới mặt quạt, lệch phải cán
    Lt = V.get('tua', 0.42)
    tua = net_thuon([(x, y), (x + k.r(0.05), y + k.r(Lt * 0.48)), (x + k.r(0.09), y + k.r(Lt))], k.r(0.06), k.r(0.08), k.r(0.13),
                    dau_tron=False)
    b.khoi(tua, m.get('tua', '#C8333F'), 'ct', dang=False)
    b.dang_phu.append(tua)
    b.khoi(tron(x, y, k.r(0.055)), vang, 'ct', dang=False)
    cx, cy = P(rq)
    r = k.r(rq)
    det = V.get('det', 1.0)                                      # >1: mặt quạt bầu dục ngang
    rx_ = r * det
    mat = elip(cx, cy, rx_, r)
    b.khoi(mat, vang)                                            # viền vàng = đĩa vàng, lòng kem co vào
    long_ = elip(cx, cy, rx_ - k.r(0.055), r - k.r(0.055))
    kem = m.get('lua', '#F7EEDC')
    b.to(long_, kem)
    with b.cat(long_):
        b.bong(long_, toi(kem, 0.08), k.r(0.08), k.r(0.08))
        n = V.get('nan', 0)                                      # nan quạt toả từ cuống
        for i in range(n):
            a = math.radians(-160 + 140 * i / max(n - 1, 1))
            b.net([(cx, cy + r * 0.92), (cx + rx_ * math.cos(a), cy + r * math.sin(a))], k.r(0.022),
                  m.get('can', vang), thuon=False)
    b.ke(long_, b.D['ct'])
    do = m.get('hoa', '#D9485A')                                 # hoa 5 cánh
    rh = r * 0.30
    hoa = gop(*[tron(cx + rh * math.cos(math.radians(a)), cy + rh * math.sin(math.radians(a)), rh * 0.62)
                for a in range(-90, 270, 72)])
    b.khoi(hoa, do, 'ct', dang=False)
    with b.cat(hoa):
        b.bong(hoa, toi(do, 0.12), rh * 0.25, rh * 0.25)
    b.khoi(tron(cx, cy, rh * 0.40), vang, 'ct', dang=False)
    b.khoi(thanh(P(rq * 2 - 0.05), P(rq * 2 + 0.12), k.r(0.085), bo=False), vang, 'ct')   # khâu nối cán


VU_KHI_KIEU['quat_tron'] = quat_tron


# ═══════════════════════════ YÊU QUÁI (tiểu yêu) ═══════════════════════════
def _tai_nhon(b, k, S):
    """Tai nhọn vểnh (yêu quái): lá nhọn từ gốc (giấu sau đầu) tới chóp, lòng tai sẫm hơn.
    T.trai/phai = dict(goc=(dx, dy), dinh=(dx, dy), rong=R)."""
    T = S['tai']
    da = S['mau'].get('tai', S['mau']['da'])
    long_ = S['mau'].get('tai_trong') or toi(da, 0.10)
    for ten, sg in (('phai', -1), ('trai', 1)):
        E = T[ten]
        g, t = k.H(*E['goc']), k.H(*E['dinh'])
        L = math.hypot(t[0] - g[0], t[1] - g[1])
        ux, uy = (t[0] - g[0]) / L, (t[1] - g[1]) / L
        nx, ny = -uy * sg, ux * sg                              # pháp tuyến hướng LÊN (vành trên)
        w = k.r(E['rong'])

        def Q(a, c):
            return (g[0] + ux * L * a + nx * w * c, g[1] + uy * L * a + ny * w * c)
        h = cong([Q(0, 0.5), Q(0.45, 0.50), Q(0.80, 0.24), Q(1.0, 0.0) + (0,), Q(0.74, -0.24), Q(0.36, -0.44), Q(0, -0.5)])
        b.khoi(h, da)
        with b.cat(h):
            b.to(cong([Q(0.12, 0.26), Q(0.46, 0.28), Q(0.80, 0.08) + (0,), Q(0.44, -0.20), Q(0.12, -0.24)]), long_)
            b.bong(h, toi(da, 0.08), k.r(0.06), k.r(0.06))
        b.net([Q(0.28, 0.40), Q(0.60, 0.34), Q(0.86, 0.14)], 'ct', toi(da, 0.25))


def sung_yeu(b, k, S):
    """Sừng nhỏ hình nón cong (yêu quái), mọc từ chân tóc: sung_yeu = [dict(goc, dinh, day, cong, gio), …].
    Vẽ SAU tóc nên gốc sừng nằm trên mảng tóc. `gio` = số gờ ngang trên sừng."""
    c = S['mau'].get('sung', '#F1E4C6')
    for E in S['sung_yeu']:
        g, t = k.H(*E['goc']), k.H(*E['dinh'])
        L = math.hypot(t[0] - g[0], t[1] - g[1])
        ux, uy = (t[0] - g[0]) / L, (t[1] - g[1]) / L
        nx, ny = -uy, ux
        d = k.r(E.get('day', 0.20)) / 2
        cg = k.r(E.get('cong', 0.05))

        def Q(a, w):                                             # a dọc sừng 0→1, w ngang (px), cong lệch theo a²
            return (g[0] + ux * L * a + nx * (w + cg * a * a), g[1] + uy * L * a + ny * (w + cg * a * a))
        h = cong([Q(0, -d), Q(0.45, -d * 0.72), Q(0.80, -d * 0.36), Q(1.0, 0) + (0,), Q(0.80, d * 0.30),
                  Q(0.45, d * 0.66), Q(0, d)])
        b.khoi(h, c)
        with b.cat(h):
            b.bong(h, toi(c, 0.12), k.r(0.05), k.r(0.02))
            for i in range(E.get('gio', 2)):
                a = 0.22 + 0.22 * i
                b.net([Q(a, -d * (1 - a * 0.8)), Q(a + 0.04, 0), Q(a, d * (1 - a * 0.8))], k.r(0.022), toi(c, 0.24))


def _nanh(b, k, S):
    """Răng nanh trắng nhỏ thò xuống từ mép miệng (yêu quái): mat.nanh = (dx so với tâm miệng, cỡ) theo R."""
    M = S['mat']
    kieu = M.get('mieng', 'cuoi')
    if not kieu or kieu == 'o':
        return
    x, y = k.H(*M.get('mieng_vt', (0.24, 0.40)))
    dx, s = M['nanh']
    x0 = x + k.r(dx)
    s = k.r(s)
    y0 = y + k.r({'cuoi': 0.035, 'buon': 0.0, 'mim': 0.012, 'thang': 0.0}.get(kieu, -0.02))
    h = cong([(x0 - s * 0.55, y0 - s * 0.15, 0), (x0 + s * 0.55, y0 - s * 0.15, 0), (x0 + s * 0.12, y0 + s * 0.85),
              (x0, y0 + s * 1.05, 0), (x0 - s * 0.20, y0 + s * 0.80)])
    b.khoi(h, '#FFFFFF', 'ct', dang=False)


def huy_hieu(b, k, S):
    """Huy hiệu tròn trước ngực áo lính, chữ 卒 (Tốt – lính quèn) viết bằng nét mực.
    huy_hieu = dict(vt=(dx, dy) toạ độ thân, r=R)."""
    Hh, m = S['huy_hieu'], S['mau']
    cx, cy = k.B(*Hh['vt'])
    r = k.r(Hh.get('r', 0.27))
    vien = m.get('vien_huy', '#D24B3C')
    b.khoi(tron(cx, cy, r), vien, 'trong', dang=False)
    long_ = tron(cx, cy, r * 0.80)
    nen = m.get('huy', '#F1E4C6')
    b.to(long_, nen)
    with b.cat(long_):
        b.bong(long_, toi(nen, 0.08), r * 0.10, r * 0.12)
    b.ke(long_, b.D['ct'] * 0.8)
    u = r * 0.58
    nets = [  # 卒: chấm · ngang · 2 chữ 人 · thập 十
        [(0.00, -0.98), (0.10, -0.80)],
        [(-0.62, -0.66), (0.66, -0.68)],
        [(-0.22, -0.52), (-0.52, -0.12)], [(-0.34, -0.34), (-0.12, -0.16)],
        [(0.36, -0.52), (0.06, -0.12)], [(0.24, -0.34), (0.50, -0.14)],
        [(-0.86, 0.14), (0.88, 0.12)],
        [(0.01, -0.06), (0.01, 1.00)],
    ]
    for seg in nets:
        b.net([(cx + u * px, cy + u * py) for px, py in seg], k.r(0.034), b.muc, thuon=False)


def giao_tua(b, k, S):
    """Giáo lính (tiểu yêu): mũi lá bạc có gân, khâu, chùm TUA ĐỎ dưới mũi, cán gỗ. Theo trục chuẩn."""
    V, m = S['vu_khi'], S['mau']
    P0, L = _khung_truc(k)
    h0 = V.get('ha', 0.04)

    def P(s, w=0.0):
        return P0(s + h0, w)
    L = L - h0
    bac, go = m.get('bac', '#D5DBE1'), m.get('can', '#9A6B3F')
    do = m.get('tua', '#D24B3C')
    can = thanh(P(0.50), P(L - 0.05), k.r(V.get('day', 0.065)), bo=True)
    b.khoi(can, go)
    with b.cat(can):
        b.bong(can, toi(go, 0.12), k.r(0.04), 0)
    lm = V.get('mui', 0.56)                                       # chiều dài mũi giáo
    mui = cong([P(0.0) + (0,), P(lm * 0.36, 0.14), P(lm * 0.78, 0.09), P(lm, 0.0) + (0,), P(lm * 0.78, -0.09),
                P(lm * 0.36, -0.14)])
    b.khoi(mui, bac)
    with b.cat(mui):
        b.to(da_giac([P(0.0), P(lm), P(lm, 0.3), P(0.0, 0.3)]), toi(bac, 0.10))
    b.net([P(lm * 0.12), P(lm * 0.86)], k.r(0.022), toi(bac, 0.30))
    st = lm - 0.02                                                # tua đỏ: chùm loe xuống, 3 chóp
    td, tr = V.get('tua_dai', 0.46), V.get('tua_rong', 1.0)
    tua = cong([P(st, -0.07), P(st + td * 0.30, -0.20 * tr), P(st + td * 0.70, -0.24 * tr), P(st + td, -0.20 * tr) + (0,),
                P(st + td * 0.80, -0.08 * tr), P(st + td * 1.06, 0.02) + (0,), P(st + td * 0.82, 0.10 * tr),
                P(st + td * 0.96, 0.24 * tr) + (0,), P(st + td * 0.62, 0.24 * tr), P(st + td * 0.28, 0.18 * tr), P(st, 0.07)])
    b.khoi(tua, do)
    with b.cat(tua):
        b.bong(tua, toi(do, 0.12), k.r(0.06), 0)
    for w0, w1 in ((-0.08, -0.14), (0.0, -0.02), (0.08, 0.14)):
        b.net([P(st + td * 0.22, w0 * tr), P(st + td * 0.78, w1 * tr)], 'ct', toi(do, 0.28))
    kh = thanh(P(lm - 0.06), P(lm + 0.08), k.r(0.085), bo=False)  # khâu bạc đè lên gốc tua
    b.khoi(kh, toi(bac, 0.06))
    with b.cat(kh):
        b.bong(kh, toi(bac, 0.18), k.r(0.04), 0)
    b.khoi(tron(*P(lm + 0.13), k.r(0.07)), toi(do, 0.06), 'ct')     # nút buộc tua
    b.khoi(tron(*P(L - 0.05), k.r(0.08)), toi(bac, 0.06))         # bịt chuôi


VU_KHI_KIEU['giao_tua'] = giao_tua
