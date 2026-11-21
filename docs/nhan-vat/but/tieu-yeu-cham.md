# Tiểu yêu (Bộ Bút) – nhật ký chấm

## Vòng 1 – 20/11/2026 – 83/100 ✅ ĐẠT
A 20 · B 14 · C 12 · D 13 · E 12 · F 12.
- Người xem đoán: "yêu tinh / quỷ con xanh cầm giáo", tức đúng lính canh yêu quái.
- Tự vẽ, không có ảnh tham khảo.
- Bộ phận mới trong `bo_phan.py`:
  - `tai.kieu='nhon'` (tai nhọn).
  - `sung_yeu`: sừng nón cong có gờ.
  - `mat.nanh`: răng nanh.
  - `huy_hieu`: huy hiệu tròn chữ 卒, viết bằng nét.
  - `toc.gai`: gai tóc dựng.
  - Vật cầm `giao_tua`: giáo mũi bạc có tua.

Mài thêm sau khi đạt (không chấm lại):
- Tua giáo thon lại (dài 0.62R, rộng ×0.90), thêm nút buộc dưới khâu.
- Mặc định đổi sang miệng `cuoi_mo`; nanh to 0.12R.
- Tóc:
  - Màu sáng hơn: `#4B3A63`.
  - Chỉ còn 3 gai to, tránh xa chân sừng.
  - Bỏ mái chữ V nhọn để bớt nét ma cà rồng.
- Sừng phải dài hơn, ngang sừng trái.
- Gấu áo đổi sang răng cưa (`gau_rang`) để ra áo lính.
- Còn để lại:
  - "Hiền" và "Quyết" vẫn gần giống nhau ở miệng.
  - Thân vẫn là áo giao lĩnh chung.

Biến thể đám đông (dựng từ spec gốc, không chấm riêng):
- `tieu_yeu_do`: da đỏ, một sừng, mặt quyết.
- `tieu_yeu_lam`: da lam, tóc cam, mặt ngạc nhiên.

Chốt:
- `assets/nhan-vat/but/tieu-yeu*.png`.
- Ghép 3 con: `tieu-yeu-dam-dong.png`.

**Người dùng duyệt bằng mắt – 20/11/2026.**
