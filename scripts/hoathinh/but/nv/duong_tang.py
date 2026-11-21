"""Đường Tăng (Huyền Trang) – spec cho Bộ Bút. Chuẩn: Sa Tăng Bộ Bút (người dùng duyệt 20/11/2026).
Giữ màu + đặc trưng bản chibi cũ đã duyệt (assets/nhan-vat/duong-tang.png), vẽ lại hoàn toàn.

Đặc trưng: đầu trọc hiền · mũ Tì Lư 5 cánh sen đỏ viền vàng + 2 dải buông kem · áo vàng cổ chéo kem ·
cà sa đỏ khoác chéo lưới ô gạch vàng · đai kem thắt nơ · tích trượng vòng vàng + khoen, cán gỗ nâu. Dáng 'chuan'.
"""
NV = dict(
    ten='Đường Tăng', ma='duong-tang', dang='chuan',
    mau=dict(
        da='#F3D2A6', ao='#E6A91E', ao_trong='#F2E6CC', co='#F2E6CC', dai='#EFE2C0', no='#D4C08A', chi_mu='#B5362A',
        vang='#E6B23C', mu='#D23B2B', day_mu='#F2E6CC', ca_sa='#B5362A', luoi='#E6B23C', gau='#E6A91E',
        can='#9A7328',
    ),
    tai=dict(trai=(-0.97, 0.16, 0.19, 0.24, 12), phai=(0.99, 0.12, 0.09, 0.15, -10)),
    mu=dict(
        kieu='ti_lu',
        vanh=[(-1.12, -0.40), (-0.70, -0.62), (0.00, -0.72), (0.62, -0.68), (1.12, -0.46)],
        day=0.20, no=0.07, truoc=0.18, nu=0,
        canh=[(-0.74, 0.23, 0.42), (-0.32, 0.27, 0.56), (0.18, 0.30, 0.68), (0.62, 0.26, 0.56), (0.94, 0.19, 0.40)],
        day_bang=[(-1.00, -0.40, 1.40, 0.17), (1.00, -0.44, 1.30, 0.16)],   # buông SAU đầu
    ),
    mat=dict(
        vt=[(0.05, 0.01), (0.67, 0.01)], bieu_cam='hien',
        mieng='cuoi', mieng_vt=(0.36, 0.44), mieng_rong=0.26,
        mau_may='#4A3426', may_day=0.075,
    ),
    ao=dict(dai=(1.22, 1.38), v=(0.22, 0.46), gau=1.90, nep=[],
            ca_sa=dict(cheo=((-1.30, -0.89), (1.30, 1.84)), duoi=1.90, o=0.22, gach=0.45)),
    vu_khi=dict(kieu='tich_truong', khoen_r=0.13, khoen_lo=0.46, vong_s=0.68),
)
