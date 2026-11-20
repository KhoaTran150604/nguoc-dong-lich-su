# Trư Bát Giới (Bộ Bút) – nhật ký chấm

## Vòng 1 – 20/11/2026 – 79/100 (thiếu 1 điểm)
A 20 · B 13 · C 11 · D 12 · E 11 · F 12. Giám khảo đoán đúng Trư Bát Giới.
Bộ phận heo thêm vào `bo_phan.py`: `_tai_heo` (tai quạt cụp), `mom_heo` (mõm + 2 lỗ mũi), `mu_tron` (mũ tròn vành vàng + hoa mây),
`_bung` (áo phanh lộ bụng + rốn), `khan_co` (khăn cổ thắt nút), `cao_chin_rang` (cào 9 răng), `mat.ma_vt` (má đặt riêng).
Răng cào để viền 'trong' + `b.dang_phu` (viền ngoài 9px nuốt răng thành vạch đen).

Đã sửa theo góp ý:
- Bụng phệ phình ra ngoài thân bên phải (`ao.bung_loi`), bóng khuyết dưới-phải, bỏ vạch ngang, rốn hạ; bụng dừng trong đai (hết lòi hồng dưới đai).
- Khăn cổ cắt trong thân (hết mẩu vàng lòi ở vai); má phải dời vào 0.76 (hết đè viền đầu–tai).
- Mũ nhô khỏi đầu (vành `no` 0.05→0.12, chỏm cao hơn) – hiện trong bóng dáng; bỏ vệt sáng trên mũ vải (luật 4).
- Vành mũ nâng 0.06, mắt/mõm/miệng hạ 0.04 → mày tách vành; miệng rộng 0.34.
- Cào: thanh dày 0.17 + khâu vàng hai đầu, răng thuôn nhọn, răng giữa trùng trục, cán bắt đầu dưới răng; tai phải thu vào (chóp ≤ 1.22R).
- Không nới đáy thân: khung `map` dùng chung với Sa Tăng (luật 7), bụng lồi thay cho việc đó.

## Vòng 2 – 20/11/2026 – 83/100 ✅ ĐẠT
A 22 · B 14 · C 11 · D 12 · E 12 · F 12. Giám khảo đoán chắc Trư Bát Giới, kể cả ảnh tô đen (tai quạt + mũ + cào).

Mài thêm sau khi đạt (không chấm lại):
- Khăn cổ nâng + cổ `co_nguoi` lấp khe cằm–vai trái (thành ngấn cổ mập, hợp nhân vật).
- Bụng lồi thu nhỏ (0.93R) cho bớt viền đôi; cán cào bắt đầu thấp hơn (hết dấu "v" dưới răng giữa).
- Miệng mặc định `cuoi_mo` (khoái chí); bỏ đốm sáng trên mõm (luật 4); rốn to + rõ hơn `#D9708A`.

Chốt → `assets/nhan-vat/but/bat-gioi.png` + `bat-gioi-bieu-cam.png`.

## Sửa sau duyệt mắt – 20/11/2026
Người dùng: cổ "bị dư ra". Bỏ `co_nguoi` (cổ màu da lòi bên trái cằm) – để trống như Ngộ Không đã duyệt; khăn cổ cắt gọn trong thân; bụng lồi chỉ phình từ eo xuống (không nhú lên vai).
