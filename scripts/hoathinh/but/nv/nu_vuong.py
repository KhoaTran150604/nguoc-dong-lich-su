"""Nữ Vương Nữ Nhi Quốc – spec cho Bộ Bút. Tự thiết kế (không có ảnh tham khảo), chuẩn nét: Sa Tăng Bộ Bút.

Đặc trưng: tóc đen búi cao + tóc dài buông sau lưng, rẽ ngôi lộ trán, 2 lọn ôm mặt ·
mũ phượng vàng 3 cánh nạm ngọc đỏ + tua rủ · chấm hoa điền đỏ giữa trán · mặt dịu dàng có mi ·
áo đỏ thẫm cổ chéo kem, đai vàng thắt nơ, gấu vàng · quạt lụa tròn hoa đỏ (cầm thấp).
"""
NV = dict(
    ten='Nữ Vương Nữ Nhi Quốc', ma='nu-vuong', dang='chuan',
    mau=dict(
        da='#F8D8C2', toc='#2A2230', ao='#C8333F', ao_trong='#F7EEDC', co='#F2E6CC',
        dai='#E2B13C', no='#B5822A', gau='#E2B13C', vang='#E2B13C', ngoc='#D23B3B',
        hoa='#D9485A', lua='#F7EEDC', can='#C9962E', tua='#C8333F', tai_trong='#F0B0A8',
    ),
    toc_dai=dict(
        duong=[(-1.06, -0.30), (-1.18, 0.50), (-1.40, 1.30), (-1.46, 1.78), (-1.30, 2.20, 0), (-1.02, 1.96),
               (-0.40, 1.60), (0.30, 1.50), (0.58, 2.14, 0), (0.74, 1.70), (0.80, 1.10), (0.94, 0.50), (1.00, -0.20)],
        no=0.07, soi=[[(-1.24, 1.00), (-1.34, 1.70)], [(0.70, 1.20), (0.66, 1.70)]],
    ),
    toc=dict(   # rẽ ngôi lộ trán + búi cao (bup) + 2 lọn ôm mặt
        chan=[(-1.16, 0.60), (-0.98, 0.45), (-0.86, 0.00), (-0.72, -0.20), (-0.30, -0.50), (0.20, -0.72, 0),
              (0.62, -0.48), (0.95, -0.25), (1.04, 0.30), (1.16, 0.50)],
        bup=[-115], bup_r=0.35, bup_d=1.12,
        loc=[([(-0.90, 0.05), (-0.98, 0.45), (-0.94, 0.80)], (0.20, 0.18, 0.04)),
             ([(0.92, 0.02), (0.96, 0.40), (0.90, 0.66)], (0.14, 0.12, 0.03))],
        soi=[[(-0.50, -0.70), (-0.70, -0.40)], [(0.50, -0.70), (0.74, -0.44)]],
    ),
    mien=dict(
        vanh=[(-0.95, -0.42), (-0.55, -0.72), (0.00, -0.84), (0.55, -0.76), (0.95, -0.46)], day=0.13,
        canh=[(-0.30, 0.18, 0.50), (0.30, 0.22, 0.70), (0.82, 0.14, 0.38)], truoc=0.30,
        tua=[(-1.02, -0.36, 0.66), (1.04, -0.38, 0.60)], hat=0.08, ngoc_vanh=[0.00, 0.58],
        hoa_dien=(0.34, -0.40),
    ),
    tai=dict(trai=(-0.90, 0.10, 0.05, 0.05, 0), phai=(0.90, 0.08, 0.04, 0.04, 0)),   # tai giấu trong tóc
    mat=dict(
        vt=[(0.04, 0.05), (0.66, 0.05)], bieu_cam='hien', mi=True,
        mieng='cuoi', mieng_vt=(0.37, 0.46), mieng_rong=0.26,
        mau_may='#3A2A2A', may_day=0.06, mau_ma='#F2A3A0',
    ),
    ao=dict(dai=(1.22, 1.42), v=(0.22, 0.46), gau=1.90),
    vu_khi=dict(kieu='quat_tron', quat_r=0.44, det=1.20, nan=7, tua=0.70, ha=0.05, day=0.06),
)
