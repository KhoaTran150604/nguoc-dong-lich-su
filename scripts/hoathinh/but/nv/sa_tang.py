"""Sa Tăng (Sa Ngộ Tịnh) – spec cho bộ Bút. Tự thiết kế, KHÔNG bám ảnh Gemini.

Đặc trưng nhận diện: da ngăm · tóc + râu quai nón đỏ nâu · vòng trán vàng · chuỗi sọ nhỏ ở cổ ·
áo xanh rêu cổ chéo · nguyệt nha sản (mũi giáo + lưỡi liềm trăng). Dáng 'map' (vạm vỡ).
"""
NV = dict(
    ten='Sa Tăng', ma='sa-tang', dang='map',
    mau=dict(
        da='#C99B6E', toc='#8C3A2B', rau='#8C3A2B', vang='#D9A93A',
        ao='#5E7B50', ao_trong='#F2E8D2', co='#EFE4CC', dai='#EFE4CC',
        so='#F8F4EA', bac='#D5DBE1', gau='#46613E',
    ),
    toc=dict(
        chan=[(-1.10, 0.02), (-0.88, -0.38), (-0.45, -0.58), (0.20, -0.62), (0.72, -0.52), (1.10, -0.06)],
        bup=[-140, -108, -76, -44], bup_r=0.15, bup_d=0.92,   # tóc xoăn rối
        soi=[[(-0.55, -0.80), (-0.36, -0.64)], [(0.02, -0.88), (0.14, -0.70)], [(0.52, -0.82), (0.60, -0.64)]],
    ),
    vong_tran=dict(
        duong=[(-1.15, -0.06), (-0.90, -0.44), (-0.45, -0.65), (0.20, -0.69), (0.72, -0.59), (1.15, -0.24)],
        day=0.14, hoa_van=(0.26, -0.60),
    ),
    rau=dict(   # dải râu ôm HÀM (chừa má + miệng lộ da)
        mep=[(-1.06, 0.20), (-0.78, 0.38), (-0.42, 0.56), (-0.02, 0.64), (0.40, 0.64), (0.72, 0.50), (0.92, 0.32), (1.06, 0.15)],
        mep_bup=[0.10, 0.24, 0.38, 0.62, 0.76, 0.90], mep_bup_r=0.11,
        no=0.05, chom=(0.36, 1.00), chom_dai=0.43,
        bup=[52, 76, 100, 124, 146], bup_r=0.15, bup_d=0.99,   # râu rậm phình khỏi hàm
        soi=[[(-0.66, 0.70), (-0.58, 0.84)], [(-0.14, 0.86), (-0.08, 0.98)], [(0.50, 0.80), (0.54, 0.92)]],
    ),
    tai=dict(trai=(-0.97, 0.18, 0.19, 0.24, 12), phai=(0.99, 0.14, 0.09, 0.15, -10)),
    mat=dict(
        vt=[(0.05, -0.03), (0.67, -0.03)], bieu_cam='hien',
        mieng='cuoi', mieng_vt=(0.36, 0.38), mieng_rong=0.28,
        mau_may='#5A2219', may_day=0.085,
    ),
    ao=dict(dai=(1.22, 1.42), v=(0.22, 0.46), gau=1.90),
    chuoi_so=dict(duong=[(-0.44, 0.06), (-0.30, 0.30), (0.00, 0.46), (0.34, 0.50), (0.60, 0.36), (0.70, 0.10)], so=6, r=0.13),
    vu_khi=dict(kieu='nguyet_san', liem_s=0.84, liem_det=1.22),
)
