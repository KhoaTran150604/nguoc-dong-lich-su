"""Thiên Bồng Nguyên Soái – spec cho Bộ Bút. Tiền kiếp Trư Bát Giới (tướng Trời oai phong).
Chuẩn nét: Sa Tăng Bộ Bút. KHÔNG bám ảnh — tự thiết kế.

Đặc trưng nhận diện (để cú lật "tướng trời → đầu heo" đọc rõ, cả ở bóng thumbnail):
da rám khoẻ · râu quai nón đậm (ra dáng lão tướng) · MIỆN VÀNG cánh đứng nạm ngọc đỏ (vương/tướng) ·
áo giao lĩnh ĐỎ THẪM viền vàng + đai vàng · cửu xỉ đinh ba (đúng binh khí Bát Giới, nối tiền kiếp). Dáng 'map'.
Mặt 'quyết' (cương nghị), miệng nghiêm. KHÔNG CỔ.
"""
NV = dict(
    ten='Thiên Bồng Nguyên Soái', ma='thien-bong', dang='map',
    mau=dict(
        da='#E7B184', toc='#3C2E24', rau='#2B2420', vang='#E0B64A', ngoc='#C7402F',
        ao='#A83228', ao_trong='#F3E9D4', co='#EAD9B8', dai='#E0B64A', gau='#86291F', no='#C7402F',
        bac='#DFE2E6', can='#B9BDC4',
    ),
    tai=dict(trai=(-0.97, 0.18, 0.19, 0.24, 12), phai=(0.99, 0.14, 0.09, 0.15, -10)),
    toc=dict(
        chan=[(-1.10, 0.02), (-0.88, -0.40), (-0.45, -0.60), (0.20, -0.64), (0.72, -0.54), (1.10, -0.06)],
        no=0.05,
        soi=[[(-0.55, -0.80), (-0.36, -0.64)], [(0.52, -0.82), (0.60, -0.64)]],
    ),
    mien=dict(   # miện vàng tướng: bỏ tua nữ (tua=[]), cánh đứng nạm ngọc, hoa điền giữa trán
        vanh=[(-1.12, -0.06), (-0.88, -0.44), (-0.45, -0.66), (0.20, -0.70), (0.72, -0.60), (1.12, -0.24)],
        day=0.14, truoc=0.10, no=0.08, hat=0.05,
        canh=[(-0.92, 0.18, 0.82), (-0.48, 0.28, 1.00), (0.05, 0.42, 1.30), (0.58, 0.30, 1.02), (0.98, 0.20, 0.84)],
        tua=[], hoa_dien=(0.05, -0.50),
    ),
    rau=dict(   # KHÁC Sa Tăng: KHÔNG quai nón – chỉ ria mép + chòm dê nhọn (lão tướng)
        mep=[(-0.22, 0.88), (0.04, 0.96), (0.28, 0.88)],   # dải nhỏ quanh cằm (không ôm má)
        no=0.02, chom=(0.24, 0.94), chom_dai=0.36,
        ria=(0.28, 0.38),                                  # ria mép 2 vạt cong xuống
        soi=[[(0.16, 1.02), (0.20, 1.16)], [(0.38, 1.00), (0.42, 1.12)]],
    ),
    mat=dict(
        vt=[(0.04, -0.03), (0.66, -0.03)], bieu_cam='quyet',
        mieng='thang', mieng_vt=(0.34, 0.40), mieng_rong=0.26,
        mau_may='#1C1712', may_day=0.115,
    ),
    ao=dict(dai=(1.20, 1.42), v=(0.22, 0.46), gau=1.90, co_day=0.13),
    vu_khi=dict(kieu='cao', tu=-0.66, den=0.66, thanh=0.17, rang_rong=0.095, rang_dai=0.40, ha=0.10),
)
