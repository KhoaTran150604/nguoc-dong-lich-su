"""Tiểu yêu (lính quèn) – spec cho Bộ Bút. Tự thiết kế (không có ảnh tham khảo), chuẩn nét: Sa Tăng Bộ Bút.

Đặc trưng: da xanh lá · 2 sừng ngà nhô khỏi tóc tím than dựng gai · tai nhọn vểnh · răng nanh ·
áo lính chàm, huy hiệu tròn chữ 卒 (Tốt) trước ngực, đai đỏ · giáo mũi bạc tua đỏ (cầm thấp).
Biến thể đám đông: nv/tieu_yeu_*.py chép spec này rồi đổi màu / sừng.
"""
NV = dict(
    ten='Tiểu yêu', ma='tieu-yeu', dang='chuan',
    mau=dict(
        da='#A3D18F', toc='#4B3A63', sung='#F1E4C6', tai_trong='#83B672',
        ao='#4D5F94', ao_trong='#F1E4C6', co='#F1E4C6', dai='#D24B3C', no='#A8382D', gau='#3D4C78',
        huy='#F1E4C6', vien_huy='#D24B3C', bac='#D5DBE1', can='#9A6B3F', tua='#D24B3C',
    ),
    toc=dict(   # mái lởm chởm 2 chóp nhọn + chỏm gai dựng
        chan=[(-1.08, 0.05), (-0.92, -0.30), (-0.62, -0.48), (-0.34, -0.40), (-0.06, -0.56), (0.24, -0.44),
              (0.52, -0.60), (0.82, -0.42), (1.08, -0.02)],
        no=0.06,
        gai=[(-158, 0.16, 16, -6), (-86, 0.30, 18, 4), (-22, 0.15, 14, 10)],
        soi=[[(-0.58, -0.80), (-0.42, -0.62)], [(0.10, -0.90), (0.18, -0.72)], [(0.64, -0.80), (0.70, -0.62)]],
    ),
    sung_yeu=[dict(goc=(-0.38, -0.80), dinh=(-0.66, -1.34), day=0.24, cong=-0.06, gio=2),
              dict(goc=(0.56, -0.70), dinh=(0.98, -1.26), day=0.22, cong=0.05, gio=2)],
    tai=dict(kieu='nhon', trai=dict(goc=(-0.88, 0.06), dinh=(-1.48, -0.30), rong=0.34),
             phai=dict(goc=(0.90, 0.02), dinh=(1.28, -0.24), rong=0.22)),
    mat=dict(
        vt=[(0.04, -0.02), (0.66, -0.02)], bieu_cam='vui',
        mieng='cuoi_mo', mieng_vt=(0.36, 0.40), mieng_rong=0.30, nanh=(0.07, 0.12),
        mau_may='#2E3B2A', may_day=0.085, mau_ma='#E9A79A',
    ),
    ao=dict(dai=(1.10, 1.28), v=(0.22, 0.40), gau_rang=(1.64, 4, 0.18)),
    huy_hieu=dict(vt=(0.10, 0.72), r=0.28),
    vu_khi=dict(kieu='giao_tua', ha=0.04, mui=0.62, tua_dai=0.62, tua_rong=0.90, day=0.065),
)
