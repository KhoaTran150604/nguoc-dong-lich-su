---
name: cham-nhan-vat
description: Agent chấm điểm ảnh NHÂN VẬT chibi (vẽ bằng code) so với ảnh mẫu người dùng gửi – đo tỉ lệ theo R, đặc điểm nhân vật, màu & đậm nhạt, nét viền, cảm giác chung; trả điểm /100 và góp ý dưới dạng THAY ĐỔI THÔNG SỐ trong bảng P. Chưa đạt 85 thì sửa → vẽ lại → chấm lại. Dùng sau mỗi lần vẽ/sửa nhân vật trong scripts/hoathinh/chibi/.
---

# Chấm điểm nhân vật chibi

## Khi nào dùng
Sau mỗi lần vẽ hoặc sửa nhân vật (`scripts/hoathinh/chibi/<tên>.py`), TRƯỚC khi đưa người dùng xem.

## Cách chạy (bắt buộc dùng subagent độc lập)
Người vẽ không tự chấm bài mình. Gọi Agent (general-purpose) với prompt gồm:
- Đường dẫn ảnh mẫu (`assets/nhan-vat/mau/<tên>-mau.png`), ảnh bản vẽ (`build/thu-hoathinh/nhan-vat/<tên>.png`), ảnh so sánh (`<tên>-so-mau.png`) và file code có bảng `P`.
- Yêu cầu agent TỰ ĐO ảnh mẫu (phóng to + kẻ lưới bằng Python/PIL, lấy mẫu màu bằng getpixel). Không đưa số đo của người vẽ cho agent, để tránh agent bị dẫn dắt.
- Bảng tiêu chí bên dưới và định dạng trả về.

## Tiêu chí (100 điểm)
| Nhóm | Điểm | Đo cái gì |
|---|---|---|
| T. Tỉ lệ khung | 25 | đầu tròn đúng nghĩa; R so với thân (cao, rộng trên/dưới); đầu lệch phải bao nhiêu R; bo góc thân; bàn tay (r, khoảng cách tới thân, độ cao); gậy (dài, nghiêng, dày) |
| Đ. Đặc điểm nhân vật | 25 | tai (to/nhỏ, lòng tai); chỏm lông; kim cô và nút; mặt nạ (vị trí, hình, mép lông); mắt (kiểu, cỡ, quầng); lông mày; có/không mũi miệng; cổ áo; thắt lưng và dải; váy và vệt lông; gấu răng cưa; đuôi (dày, số vòng cuộn) |
| M. Màu & đậm nhạt | 20 | so mã màu từng vùng (lệch ΔE lớn thì trừ điểm); các tầng đậm nhạt: áo trên nhạt hơn váy dưới, mặt nạ nhạt, quầng mắt hồng, lòng tai hồng, mảng tối nếu có; độ tương phản tổng thể |
| N. Nét viền | 15 | độ dày viền ngoài theo R (mẫu ≈0.085R); màu viền; viền chi tiết mỏng hơn ở đâu; nét có đều không |
| C. Cảm giác chung | 15 | nhìn lướt có thấy cùng một bộ với mẫu không; độ "dễ thương / thân thiện"; độ gọn |

**Đạt: ≥ 85/100.** Mỗi nhóm phải đạt ≥ 70% số điểm của nhóm đó.

## Định dạng trả về
1. **Bảng đo ảnh mẫu**: từng chỉ số theo R, kèm mã màu.
2. **Điểm**: từng nhóm, có lý do ngắn.
3. **Góp ý = thay đổi thông số**: liệt kê `tên_tham_số: giá trị cũ → giá trị mới (lý do)`, dùng đúng tên khoá trong bảng `P`. Việc nào cần thêm code (tính năng mới, ví dụ "quầng mắt") thì ghi riêng là `CẦN THÊM: …`.
4. Tổng điểm và kết luận ĐẠT / CHƯA ĐẠT.

## Vòng sửa
Áp dụng góp ý → chạy lại script → gọi agent chấm MỚI (không dùng lại agent cũ) → lặp đến khi đạt hoặc đủ 3 vòng. Mỗi vòng lưu điểm vào `docs/nhan-vat/<tên>-cham-diem.md`. Gửi người dùng ảnh so mẫu, ảnh bảng chỉ số và điểm.
