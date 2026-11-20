# Tôn Ngộ Không – chỉ số vẽ (bản 9 – CHỐT, 19–20/11/2026)

**Người dùng duyệt "ổn rồi" ở bản 9.** Ảnh chính thức: `assets/nhan-vat/ngo-khong.png` · bảng chỉ số: `assets/nhan-vat/ngo-khong-bang.png`.

- Code nhân vật: `scripts/hoathinh/chibi/ngo_khong.py` (bảng `P`) · khung chung: `scripts/hoathinh/chibi/khung.py` (`dau` + `vien_dau`, `than`, `ban_tay`, `khuon_mat`, `duoi_xoan`) · bút: `ve.py` · bảng ảnh: `bang.py`.
- **Mọi số theo R (bán kính đầu), R = 120px.** Đổi R thì cả nhân vật co giãn.
- Quy trình làm: skill **`ve-va-cham-anh`** ("agent vẽ và chấm ảnh"). Lịch sử điểm: bản4 61 → bản5 79 → bản6 79 → bản7 83 → bản8 (đang chấm) → **bản9 chốt theo ý người dùng**.

## A. Khung chung (dùng cho mọi nhân vật)
| Mã | Chỉ số |
|---|---|
| A1 | Đầu TRÒN R=120 · viền 0.085R màu đen `#0A0807` · viền chi tiết 0.05R |
| A2 | Đầu lệch PHẢI 0.31R so với thân (mặt quay 3/4) · đáy đầu chạm vai |
| A3 | Thân "bia mộ" loe đáy: cao 2.15R, vai rộng 1.26R → đáy 1.66R |
| A4 | Đầu : thân ≈ 0.58 (đầu to, thân lùn – khớp mẫu) |
| A5 | Không cánh tay – chỉ bàn tay tròn r=0.24R cách thân ~0.35R, đồ đè lên tay |

## B. Đầu & mặt
| Mã | Chỉ số |
|---|---|
| B1 | Tai: trái r=0.31R (lòng hồng, nét gập "<"), phải r=0.21R (khuất) · vành tai màu da |
| B2 | Chỏm lông: gai mềm lệch phải, khía V vừa, có nét lông trong; viền trên đầu gồ ghề theo lông (không tròn trơn) |
| B3 | Kim cô võng nhẹ (sag 0.07R), dày 0.12R · 2 nút vòng khuyên (lõi tối) dồn sát + lệch phải |
| B4 | Mặt nạ lệch phải, mép lông xù cả vòng, chừa viền má nâu |
| B5 | Mắt đen bầu dục 0.28×0.34R, đốm trắng đứng giữa |
| B6 | Lông mày cong vòm, dày 0.085R, hạ gần mắt (cách 0.25R), đuôi hạ = hiền |
| B7 | Không miệng (đúng mẫu) · má hồng `#F2A9A2` quanh mắt |

## C. Trang phục (chi tiết)
| Mã | Chỉ số |
|---|---|
| C1 | Áo trên `#EBB24A` + **nếp gấp** · cổ chéo viền đỏ `#BA4139` · áo trong kem `#F6E8CF` |
| C2 | Thắt lưng đỏ 0.92–1.10R · nút + 2 dải · đường ngăn áo/váy |
| C3 | Váy da hổ `#E58E2E` + **sọc da hổ** (vạch ngắn) + 5 khía răng cưa mép |
| C4 | Gấu răng cưa ở 1.82R, 4 răng · nền tím than `#373545` |

## D. Đuôi · gậy
| Mã | Chỉ số |
|---|---|
| D1 | Đuôi xoắn trơn đều, dày 0.19→0.10R, cuộn 1.35 vòng, có nét sáng trong cuộn |
| D2 | Gậy dày 0.23R, nghiêng ~11°, đầu vàng 0.44R có vạch chia |
