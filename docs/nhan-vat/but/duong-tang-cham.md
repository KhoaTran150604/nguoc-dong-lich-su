# Đường Tăng (Bộ Bút) – nhật ký chấm

## Vòng 1 – 20/11/2026 – 78/100
A 19 · B 14 · C 10 · D 12 · E 11 · F 12. Người lớn đoán Đường Tăng; trẻ em dễ nhầm "vua tóc vàng" (dải mũ giống tóc, đầu trượng giống quyền trượng).
Bộ phận mới trong `bo_phan.py`: `mu_ti_lu` (5 cánh sen + vành + dải buông; `mu()` điều phối theo `kieu`), `_ca_sa` (cà sa lưới gạch),
`tich_truong` (mũi nhọn + vòng rỗng + 2 khoen + cán gỗ), `co_nguoi` (cổ lấp khe cằm–vai), `b.lo` (lỗ rỗng giữ trắng trong ảnh bóng dáng).

Đã sửa theo góp ý:
- Lấp khe cổ (`co_nguoi`), hết vạch chữ L + lỗ hở ở cả ảnh bóng dáng.
- Dải mũ hẹp 0.15R, tô phẳng kem `#F2E6CC` + chỉ đỏ giữa, đẩy ra xa má, đuôi én → không còn giống tóc.
- Cà sa vắt chéo thật (~46°, từ vai trái xuống hông phải), lộ tam giác áo vàng trên-phải; gạch 0.45×0.22R, nét 0.025R; lưới trong mảng bóng tối theo.
- Tích trượng: cán dừng dưới vòng (hết cục đen trong lòng vòng), khoen 0.13R viền mảnh, mũi nhọn dài 0.35R; lỗ vòng giữ rỗng trong ảnh tô đen.
- Cánh sen bỏ nụ tròn (đầu nhọn), 2 cánh ngoài thu vào khung đầu; vành mũ nâng 0.06R + mắt hạ 0.04R (mày "Ngạc nhiên" không chạm vành).

## Vòng 2 – 20/11/2026 – 83/100 ✅ ĐẠT
A 21 · B 14 · C 11 · D 12 · E 12 · F 13. Người lớn đoán ngay Đường Tăng; hết nhầm "vua tóc vàng".

Mài thêm sau khi đạt (không chấm lại):
- Dải mũ buông SAU đầu/tai/vai (`day_mu`, lớp đầu tiên): mặt tròn liền, tai lộ, hết nêm đen + khối đen ở chân dải; đuôi loe lệch ra ngoài như vải.
- Khoen tích trượng treo vào vòng ở 4h/8h, chồng lên viền vòng (hết dáng "quả cầu chữ thập").
- Vành mũ 0.20R: vàng – lõi đỏ – vàng, một nét trong mỗi mép, bỏ sọc bóng.
- Gấu áo dùng chung màu áo `#E6A91E` (gom sắc vàng).

Chốt → `assets/nhan-vat/but/duong-tang.png` + `duong-tang-bieu-cam.png`.

## Sửa sau duyệt mắt – 20/11/2026
Người dùng: cổ "bị dư ra". Bỏ `co_nguoi` (cục cổ màu da lòi bên trái cằm) – để trống như Ngộ Không đã duyệt (dải mũ đã buông sau đầu nên không còn nêm đen).
