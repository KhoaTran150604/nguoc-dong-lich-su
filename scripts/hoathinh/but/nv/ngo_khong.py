"""Tôn Ngộ Không – spec cho Bộ Bút. Chuẩn: Sa Tăng Bộ Bút (người dùng duyệt 20/11/2026).
Giữ màu + đặc trưng bản chibi cũ đã duyệt (docs/nhan-vat/ngo-khong-chi-so.md), vẽ lại hoàn toàn.

Đặc trưng: đầu khỉ lông nâu cam + chỏm gai ngả phải · mặt nạ da 2 thùy + mõm · tai khỉ tròn lòng hồng ·
kim cô vàng 2 nút vòng · gậy Như Ý đỏ đầu vàng · đuôi xoắn trái · áo vàng cổ đỏ, váy da hổ, gấu răng cưa.
"""
NV = dict(
    ten='Tôn Ngộ Không', ma='ngo-khong', dang='chuan',
    mau=dict(
        da='#F7D5C2', dau='#C98450', tai='#F7D5C2', tai_trong='#F2A9A2', vang='#F3C232',
        ao='#EBB24A', ao_trong='#F6E8CF', co='#BA4139', dai='#BA4139', no='#9E3530',
        vay='#E58E2E', soc='#8A3B12', gau='#373545', can='#B9413A',
    ),
    # chỏm lông gai (góc°, dài R, nửa rộng gốc°, nghiêng đỉnh°) – ngả phải, cao nhất lệch phải
    gai=[(-162, 0.13, 13, 8), (-138, 0.22, 13, 16), (-112, 0.34, 13, 22),
         (-86, 0.46, 13, 26), (-60, 0.34, 13, 24), (-36, 0.21, 12, 18)],
    long_net=[[(-0.62, -0.86), (-0.50, -0.70)], [(-0.12, -1.06), (-0.04, -0.86)], [(0.40, -1.00), (0.40, -0.82)]],
    tai=dict(trai=(-1.08, -0.04, 0.30, 0.30, 0), phai=(1.02, -0.04, 0.19, 0.20, 0), trong=0.62),
    mat_na=dict(
        thuy=[(0.03, -0.12, 0.40), (0.65, -0.12, 0.37)],
        cam=(0.36, 0.36, 0.60, 0.50),
        mai=[(0.22, -0.64), (0.34, -0.26, 0), (0.46, -0.64)],     # mũi lông chĩa xuống giữa 2 thùy
    ),
    vong_tran=dict(
        duong=[(-1.15, -0.48), (-0.70, -0.80), (0.00, -0.92), (0.70, -0.82), (1.15, -0.46)],
        day=0.13, nut=[(0.22, -0.84, 0.12), (0.47, -0.81, 0.12)],
    ),
    mat=dict(
        vt=[(0.03, -0.08), (0.65, -0.08)], bieu_cam='vui',
        mieng='cuoi', mieng_vt=(0.36, 0.44), mieng_rong=0.30, mui=(0.35, 0.22),
        mau_may='#6B3A1E', may_day=0.08,
    ),
    ao=dict(
        dai=(0.92, 1.10), v=(0.22, 0.40),
        vay=1.10, gau_rang=(1.82, 4, 0.18),
        vay_soc=[(-0.42, 1.22, 0.30), (-0.14, 1.28, 0.34), (0.16, 1.24, 0.32), (0.46, 1.28, 0.28),
                 (-0.28, 1.54, 0.26), (0.02, 1.58, 0.26), (0.32, 1.54, 0.22)],
        nep=[[(-0.30, 0.18), (-0.18, 0.62)], [(0.46, 0.24), (0.40, 0.62)]],
    ),
    duoi=dict(root=(-0.40, 1.30), c=(-1.20, 0.82), a0=25, turns=1.30, r0=0.62, r1=0.13, w0=0.24, w1=0.13),
    vu_khi=dict(kieu='gay', day=0.115, dau=0.44, ha=0.10),
)
