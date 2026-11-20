"""Bạch Cốt Tinh – spec cho Bộ Bút. Tự thiết kế (không có ảnh tham khảo), chuẩn nét: Sa Tăng Bộ Bút.

Đặc trưng: da trắng sứ · tóc bạc dài buông sau lưng, mái bằng + 2 lọn ôm mặt · trâm xương + nơ tím ·
mắt hơi híp tinh nghịch có mi · áo trắng cổ chéo viền tím, đai tím thắt nơ, gấu tím ·
gậy xương đầu sọ nhỏ dễ thương (cầm thấp). Dễ thương – tinh quái, KHÔNG đáng sợ.
"""
NV = dict(
    ten='Bạch Cốt Tinh', ma='bach-cot-tinh', dang='chuan',
    mau=dict(
        da='#FBEDE8', toc='#D9D6EA', ao='#F6F3FA', ao_trong='#E6DCF2', co='#8E6BB8', dai='#8E6BB8',
        no='#6F4F99', gau='#8E6BB8', xuong='#EFE8DA', no_toc='#8E6BB8', tai_trong='#F0C6CF',
    ),
    toc_dai=dict(   # tóc sau lưng thò khỏi viền thân 2 bên, đuôi sóng; bên phải dừng sau vai (xa bàn tay)
        duong=[(-1.06, -0.30), (-1.18, 0.50), (-1.40, 1.30), (-1.46, 1.78), (-1.30, 2.20, 0), (-1.02, 1.96),
               (-0.40, 1.60), (0.30, 1.50), (0.58, 2.14, 0), (0.74, 1.70), (0.80, 1.10), (0.94, 0.50), (1.00, -0.20)],
        no=0.07, soi=[[(-1.24, 1.00), (-1.34, 1.70)], [(0.70, 1.20), (0.66, 1.70)]],
    ),
    toc=dict(   # mái bằng cắt chóp mềm (chóp −0.28R, khe −0.45R) + 2 lọn ôm mặt
        chan=[(-1.16, 0.62), (-0.96, 0.52), (-0.84, -0.06), (-0.62, -0.28), (-0.44, -0.45, 0), (-0.22, -0.27),
              (0.00, -0.45, 0), (0.24, -0.27), (0.46, -0.45, 0), (0.66, -0.28), (0.84, -0.12),
              (0.93, 0.10), (1.02, 0.50), (1.16, 0.56)],
        no=0.07, bong=(0.14, 0.0),
        loc=[([(-0.88, 0.05), (-0.96, 0.45), (-0.92, 0.80)], (0.20, 0.18, 0.04)),
             ([(0.90, 0.02), (0.94, 0.40), (0.88, 0.70)], (0.14, 0.13, 0.03))],
        soi=[[(-0.40, -0.95), (-0.36, -0.58)], [(0.00, -0.98), (0.00, -0.60)], [(0.40, -0.94), (0.38, -0.58)],
             [(0.70, -0.74), (0.66, -0.50)]],
    ),
    tram=dict(vt=(-0.66, -0.80), goc=-40, dai=0.60, r=0.09, no=(-0.10, -1.05, 0.19)),
    tai=dict(trai=(-0.90, 0.10, 0.05, 0.05, 0), phai=(0.90, 0.08, 0.04, 0.04, 0)),   # tai giấu trong tóc
    mat=dict(
        vt=[(0.04, 0.03), (0.66, 0.03)], bieu_cam='hien', mi=True,
        mi_xech=dict(hien=0.30, quyet=0.45, vui=0.12),          # mí trên xếch: mắt híp tinh nghịch
        mieng='cuoi', mieng_vt=(0.37, 0.44), mieng_rong=0.24,
        mau_may='#7A6A8C', may_day=0.06, mau_ma='#EDC2D8',
    ),
    ao=dict(dai=(1.22, 1.42), v=(0.22, 0.46), gau=1.90),
    vu_khi=dict(kieu='gay_xuong', so_r=0.30, day=0.07, no_co=0.19),
)
