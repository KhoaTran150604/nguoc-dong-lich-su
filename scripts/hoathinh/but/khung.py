"""KHUNG CHUNG (bản Bút) – mọi nhân vật chibi dùng chung một bộ xương tỉ lệ.

Số tỉ lệ lấy NGUYÊN từ `chibi/goc.py` (chốt từ Ngộ Không): đầu tròn bán kính R, thân "bia mộ"
lệch trái, MỘT bàn tay tròn lơ lửng bên phải. Không ai tự chế tỉ lệ riêng.

LUẬT VŨ KHÍ (người dùng chốt 20/11/2026 – "cầm thấp, lấy Ngộ Không làm chuẩn"):
- Trục vũ khí đi QUA TÂM BÀN TAY, nghiêng 8.7° (đầu trên ngả phải) như gậy Ngộ Không.
- ĐỈNH vũ khí (kể cả lưỡi/hoa văn trên cùng) không cao hơn tâm đầu 1.76R; CHÂN ở tâm đầu + 3.20R.
- Mỗi nhân vật chỉ MỘT tay. Bàn tay vẽ ĐÈ lên cán (đọc ra là đang nắm).

LUẬT KHÔNG CỔ (người dùng chốt 21/11/2026): nhân vật KHÔNG được có cổ – đầu đặt thẳng lên mép trên thân.
Không thêm trụ cổ, mảng da lấp khe cằm–vai, hay nâng/hạ thân để lộ cổ.
"""
import math
import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'chibi'))
from goc import KIEU, TI_LE, DANG  # noqa: E402

from but import Hinh, cong, tron  # noqa: E402

VU_KHI = dict(dinh_y=-1.76, chan_y=3.20, nghieng=8.7)    # theo R, so với TÂM ĐẦU

# Bề dày nét 3 cấp theo R (R=120 → 9 / 5 / 3.6 px)
NET = dict(ngoai=0.075, trong=0.042, ct=0.030)


class Khung:
    def __init__(self, head_c=(413, 399), R=KIEU['R'], dang='chuan', K=None):
        self.hx, self.hy = head_c
        self.R = R
        self.K = dict(TI_LE)
        self.K.update(DANG.get(dang, {}))
        if K:
            self.K.update(K)
        K = self.K
        self.bx = self.hx + K['than_lech_x'] * R
        self.top = self.hy + K['than_tren_y'] * R
        self.bot = self.top + K['than_cao'] * R
        self.ht = K['than_rong_tren'] * R / 2
        self.hb = K['than_rong_duoi'] * R / 2

    # toạ độ theo đầu / theo thân (đơn vị R)
    def H(self, dx, dy):
        return (self.hx + dx * self.R, self.hy + dy * self.R)

    def B(self, dx, dy):
        return (self.bx + dx * self.R, self.top + dy * self.R)

    def r(self, v):
        return v * self.R

    def D(self):
        return {k: v * self.R for k, v in NET.items()}

    # ── khối khung ──
    def dau(self):
        return tron(self.hx, self.hy, self.R)

    def than(self):
        """Thân 'bia mộ': hình thang loe đáy, góc trên bo nhỏ, góc dưới bo lớn – cạnh hơi phồng."""
        K, R = self.K, self.R
        x, t, b, ht, hb = self.bx, self.top, self.bot, self.ht, self.hb
        rt, rb = K['than_bo_tren'] * R, K['than_bo_duoi'] * R
        ph = 0.035 * R                                            # cạnh bên phồng nhẹ (bớt cứng)
        pts = [
            (x - ht + rt * 0.3, t), (x, t - 0.01 * R), (x + ht - rt * 0.3, t),          # vai
            (x + ht + 0.02 * R, t + rt * 0.9),
            (x + (ht + hb) / 2 + ph, (t + b) / 2),
            (x + hb, b - rb * 0.9),
            (x + hb - rb * 0.55, b - 0.02 * R), (x, b + 0.01 * R), (x - hb + rb * 0.55, b - 0.02 * R),
            (x - hb, b - rb * 0.9),
            (x - (ht + hb) / 2 - ph, (t + b) / 2),
            (x - ht - 0.02 * R, t + rt * 0.9),
        ]
        return cong(pts, 0.95)

    def nua_rong(self, y):
        t = (y - self.top) / (self.bot - self.top)
        return self.ht + (self.hb - self.ht) * t

    def tay(self):
        x, y = self.B(self.K['tay_x'], self.K['tay_y'])
        return x, y, self.K['tay_r'] * self.R

    def truc_vu_khi(self):
        """(điểm đỉnh, điểm chân, hướng đơn vị chân→đỉnh) – theo LUẬT VŨ KHÍ."""
        x, y, _ = self.tay()
        a = math.radians(VU_KHI['nghieng'])
        ux, uy = math.sin(a), -math.cos(a)                      # hướng lên, ngả phải
        y_top = self.hy + VU_KHI['dinh_y'] * self.R
        y_bot = self.hy + VU_KHI['chan_y'] * self.R
        top = (x + ux * (y - y_top) / -uy, y_top)
        bot = (x - ux * (y_bot - y) / -uy, y_bot)
        return top, bot, (ux, uy)

    def tren_truc(self, s):
        """Điểm trên trục vũ khí, s tính bằng R đo từ ĐỈNH xuống (s=0 là đỉnh)."""
        top, _, (ux, uy) = self.truc_vu_khi()
        return (top[0] - ux * s * self.R, top[1] - uy * s * self.R)


# ═══════════════════════════ DÁNG NGỰA (Bạch Long Mã) ═══════════════════════════
# Thú 4 chân dùng CÙNG R, cùng nét 3 cấp, cùng mặt đất với người (tâm đầu + 3.13R = đáy thân người),
# đầu cùng cỡ để đứng cạnh thầy trò. Thân bầu dục NẰM NGANG lùi sang TRÁI sau đầu, 4 chân ngắn mập.
# LUẬT KHÔNG CỔ áp cho ngựa: đầu đè thẳng lên góc trước-trên của thân (ngực), bờm che chỗ nối –
# không vẽ khối cổ dài.
NGUA = dict(
    dat_y=3.13,                                   # mặt đất (theo R, so với tâm đầu) – như đáy thân người
    than=[(-2.62, 1.62), (-2.40, 1.08), (-1.85, 0.84), (-1.10, 0.80), (-0.45, 0.66), (0.12, 0.82),
          (0.36, 1.42), (0.24, 2.00), (-0.40, 2.36), (-1.30, 2.44), (-2.15, 2.34), (-2.62, 1.95)],
    mom=(0.70, 0.50, 0.70, 0.48),                 # mõm bầu dục (tâm x, y, rx, ry) – liền khối đầu
    chan_tren=1.90, chan_rong=0.50, mong=0.15,    # chân: mép trên (giấu sau thân), bề ngang, cao móng
    chan_gan=(-2.26, -0.62), chan_xa=(-1.64, 0.02), xa_nang=0.07,   # x chân gần / xa; chân xa nhấc 0.07R (chiều sâu)
)


class KhungNgua(Khung):
    """Khung thú 4 chân. Đầu tròn R tại head_c (như người) + mõm; thân theo NGUA['than'] (toạ độ đầu)."""

    def __init__(self, head_c=(540, 399), R=KIEU['R'], K=None):
        super().__init__(head_c, R, 'chuan')
        self.N = dict(NGUA)
        if K:
            self.N.update(K)
        self.dat = self.hy + self.N['dat_y'] * R
        ys = [p[1] for p in self.N['than']]
        self.top, self.bot = self.hy + min(ys) * R, self.hy + max(ys) * R

    def than(self):
        return cong([self.H(*p) for p in self.N['than']], 1.0)

    def mom(self):
        from but import elip
        x, y, rx, ry = self.N['mom']
        return elip(*self.H(x, y), self.r(rx), self.r(ry))

    def dau_mom(self):
        return self.dau() + self.mom()

    def chan(self, x, xa=False):
        """Một chân (khối bo tròn) + mảng móng dưới; x theo R so với tâm đầu."""
        from but import hop
        N = self.N
        w = self.r(N['chan_rong'])
        cx = self.hx + x * self.R
        day = self.dat - (self.r(N['xa_nang']) if xa else 0)
        tren = self.hy + N['chan_tren'] * self.R
        wd = w * 0.86                                              # ống chân thon dần xuống móng
        chan = cong([(cx - w / 2, tren, 0), (cx + w / 2, tren, 0), (cx + wd / 2, day - wd * 0.40),
                     (cx + wd * 0.30, day), (cx - wd * 0.30, day), (cx - wd / 2, day - wd * 0.40)], 0.9)
        mong = chan & hop(cx - w, day - self.r(N['mong']), cx + w, day + w)
        return chan, mong
