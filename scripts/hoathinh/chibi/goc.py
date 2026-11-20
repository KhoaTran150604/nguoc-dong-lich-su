"""THÔNG SỐ GỐC – nền chung cho MỌI nhân vật chibi (chốt từ Tôn Ngộ Không bản 9, 20/11/2026).

Đây là "bộ xương" tỉ lệ: vẽ nhân vật mới chỉ cần kế thừa file này rồi THAY phần riêng
(màu, tóc/mũ, trang phục, đồ cầm tay, vị trí mắt) – KHÔNG đổi TI_LE để mọi nhân vật cùng khung.

Dùng:  from goc import tao_P
        P = tao_P(head_c=(413, 399), c_da='#...', M=dict(mat=[...]), ... phần riêng ...)

Mọi số theo R = bán kính đầu. 3 nhóm gốc:
  KIEU   – kiểu vẽ (khung canvas, R, độ dày viền, màu nền/mực).
  TI_LE  – TỈ LỆ KHUNG (thân + bàn tay) = dáng chung, GIỮ NGUYÊN.
  MAT_GOC – khuôn mặt nền (mắt, lông mày, má); chỉnh nhẹ theo nhân vật nếu cần.
"""
import copy

# ── KIỂU VẼ ───────────────────────────────────────────────────────────────────
KIEU = dict(
    canvas=(800, 1000), R=120,          # khung ảnh & bán kính đầu chuẩn
    vien=0.085, vien_ct=0.05,           # viền ngoài / viền chi tiết (×R)
    c_bg='#F6F3EC', c_ink='#0A0807',    # nền · mực viền (đen)
)

# ── TỈ LỆ KHUNG (thân "bia mộ" + bàn tay) – GIỮ NGUYÊN cho mọi nhân vật ────────
TI_LE = dict(
    than_lech_x=-0.31,     # thân lệch TRÁI 0.31R so với đầu (đầu quay 3/4 sang phải)
    than_tren_y=0.98,      # mép trên thân ≈ đáy đầu
    than_cao=2.15,         # thân cao 2.15R (đầu : thân ≈ 0.58)
    than_rong_tren=1.26, than_rong_duoi=1.66,   # loe đáy (A-line)
    than_bo_tren=0.15, than_bo_duoi=0.38,        # bo góc trên/dưới
    tay_x=1.38, tay_y=0.88, tay_r=0.24,          # bàn tay tròn lơ lửng (chỉ khi cầm đồ)
)

# ── KHUÔN MẶT NỀN ─────────────────────────────────────────────────────────────
# `mat` (vị trí 2 mắt) và `ma_hong_vt` đặt theo từng nhân vật (mặt quay 3/4).
MAT_GOC = dict(
    vien_mat=5, kieu_mat='oval', mat_rx=0.14, mat_ry=0.17, glint=(0.05, 0.09),   # mắt đen bầu dục + đốm trắng đứng
    mat_r=0.14, con_nguoi_r=0.085, nhin=(0.0, 0.0),
    may_y=-0.25, may_rong=0.40, may_cong=0.22, may_day=0.085, may_nghieng=-0.03,  # lông mày cong vòm hiền, gần mắt
    mieng=None,                                  # mặc định không miệng
    ma_hong=(0.22, 0.21), mau_ma='#F2A9A2',      # quầng má hồng
)

# ── BẢNG MÀU GỢI Ý (nhân vật tự ghi đè) ───────────────────────────────────────
MAU_GOI_Y = dict(
    c_da='#FBD9CF',        # da/mặt
    c_shirt='#F6E8CF',     # áo trong
    c_trim='#BA4139', c_belt='#BA4139',          # viền cổ / thắt lưng (đỏ)
    c_gold='#F3C232', c_gold_dk='#B8861A',       # phụ kiện vàng
    c_hem='#373545',       # nền tối (gấu áo)
)


# ── DÁNG NGƯỜI (build) – chuẩn hoá để mọi nhân vật MẬP dùng CHUNG một dáng ───────
# GIỮ NGUYÊN than_cao & than_lech_x (mọi nhân vật CÙNG chiều cao, cùng khung, khớp
# đỉnh đầu/vai/đáy thân) – dáng chỉ đổi BỀ NGANG + bo góc. NV mập (Bát Giới, Sa
# Tăng…) dùng dang='map' để nhất quán, KHÔNG tự chế số riêng từng nhân vật.
DANG = {
    'chuan': {},                                                   # như Ngộ Không
    'map': dict(than_rong_tren=1.46, than_rong_duoi=2.00,          # thân rộng hơn
                than_bo_tren=0.26, than_bo_duoi=0.54),             # bo góc tròn hơn
}


def tao_P(dang='chuan', **rieng):
    """Tạo bảng P: nền gốc + DÁNG (DANG) + phần riêng (rieng).
    K và M được HỢP NHẤT (chỉ ghi đè khoá truyền vào); các khoá khác thay trực tiếp."""
    P = dict(copy.deepcopy(KIEU))
    P['K'] = copy.deepcopy(TI_LE)
    P['K'].update(DANG.get(dang, {}))                              # dáng người; GIỮ than_cao → cùng chiều cao
    P['dang'] = dang
    P['M'] = copy.deepcopy(MAT_GOC)
    for k, v in rieng.items():
        if k in ('K', 'M') and isinstance(v, dict):
            P[k].update(v)
        else:
            P[k] = v
    return P
