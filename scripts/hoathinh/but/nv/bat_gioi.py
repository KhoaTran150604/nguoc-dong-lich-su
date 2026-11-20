"""Trư Bát Giới – spec cho Bộ Bút. Chuẩn: Sa Tăng Bộ Bút (người dùng duyệt 20/11/2026).
Giữ màu + đặc trưng bản chibi cũ đã duyệt (assets/nhan-vat/bat-gioi.png), vẽ lại hoàn toàn.

Đặc trưng: mặt heo hồng · tai quạt cụp to · mõm bầu dục 2 lỗ mũi · mắt cười híp ^^ ·
mũ tròn đen vành vàng + hoa mây vàng · áo đen phanh ngực lộ bụng tròn + rốn · khăn cổ vàng thắt nút ·
đai vàng · cào chín răng bạc. Dáng 'map' (mập).
"""
NV = dict(
    ten='Trư Bát Giới', ma='bat-gioi', dang='map',
    mau=dict(
        da='#FBBEC4', tai_trong='#F096A6', mom='#F590A2', lo_mui='#B94458',
        mu='#2E2C33', ao='#36343C', vat='#4A4752', vang='#D3A85B', dai='#D3A85B', khan='#D3A85B', no='#B88E45',
        bac='#E2E3E6', can='#C2C5CC', ron='#D9708A', gan='#E68C9C',
    ),
    tai=dict(kieu='heo',
             trai=dict(goc=(-0.55, -0.32), dinh=(-1.62, 0.40), rong=0.95),
             phai=dict(goc=(0.62, -0.40), dinh=(1.22, 0.22), rong=0.66)),
    mu=dict(
        vanh=[(-1.20, -0.32), (-0.76, -0.56), (0.00, -0.68), (0.62, -0.64), (1.20, -0.40)],
        day=0.13, no=0.12, dinh=(0.04, -0.60), chom=(1.04, 0.66), may=(0.30, -0.94, 0.22),
    ),
    mat=dict(
        vt=[(0.00, -0.03), (0.62, -0.03)], bieu_cam='cuoi_nham',
        mieng='cuoi_mo', mieng_vt=(0.32, 0.66), mieng_rong=0.36,
        mom=dict(vt=(0.32, 0.32), rx=0.34, ry=0.22),
        ma_vt=[(-0.30, 0.26), (0.76, 0.24)],
        mau_may='#8A4A50', may_day=0.07,
    ),
    ao=dict(
        mo=[(-0.28, -0.12), (-0.50, 0.42), (-0.62, 1.00), (-0.52, 1.42), (-0.20, 1.58), (0.40, 1.60), (0.80, 1.44), (0.93, 1.08), (0.74, 0.66), (0.58, 0.30), (0.48, -0.12)],
        bung_loi=True,   # bụng phệ phình ra ngoài thân bên phải (mặt 3/4 phải),
        ron=(0.20, 1.20), dai=(1.50, 1.66), nep_mau='#55525C',
        nep=[[(-0.62, 1.82), (-0.60, 2.02)], [(0.50, 1.82), (0.54, 2.02)]],
    ),
    khan=dict(duong=[(-0.62, -0.08), (0.04, 0.08), (0.70, -0.06)], day=0.15, nut=(0.14, 0.16, 0.11),
              vat=[[(-0.22, 0.54), (0.08, 0.64)], [(0.22, 0.64), (0.52, 0.54)]]),
    co_nguoi=(-0.30, 0.86, 0.62, 0.26),   # lấp khe cằm–vai trái
    vu_khi=dict(kieu='cao', tu=-0.66, den=0.66, thanh=0.17, rang_rong=0.09),
)
