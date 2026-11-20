---
name: cham-nhan-vat
description: Agent (bước 4/4) chấm điểm ảnh NHÂN VẬT chibi (vẽ bằng code) so với HỒ SƠ TẠO HÌNH (mô tả + ảnh minh họa) – đo tỉ lệ theo R, đặc điểm nhân vật, màu & đậm nhạt, nét viền, cảm giác chung; trả điểm /100 và góp ý dưới dạng THAY ĐỔI THÔNG SỐ trong bảng P. Chưa đạt 80 thì sửa → vẽ lại → chấm lại. Dùng sau mỗi lần vẽ/sửa nhân vật trong scripts/hoathinh/chibi/.
---

# Chấm điểm nhân vật chibi (bước 4/4)

## Khi nào dùng
Sau mỗi lần vẽ/sửa nhân vật (`scripts/hoathinh/chibi/<mã>.py`), TRƯỚC khi đưa người dùng xem. Bước 4 của pipeline [[tao-nhan-vat]].

## Chấm theo cái gì
**Hồ sơ tạo hình** `docs/nhan-vat/<mã>-hoso.md` (từ [[nghien-cuu-nhan-vat]], đã qua [[tham-dinh-ho-so]]) + **ảnh minh họa** `assets/nhan-vat/mau/<mã>/*`. Hồ sơ thay cho feedback tay của người dùng: đo bản vẽ theo **mô tả + chi tiết trong ảnh**, trọng tâm là mục **Checklist "phải có"**.

## Cách chạy (bắt buộc subagent độc lập – người vẽ không tự chấm)
Gọi Agent `general-purpose` với prompt gồm:
- Hồ sơ `docs/nhan-vat/<mã>-hoso.md`, ảnh minh họa `assets/nhan-vat/mau/<mã>/*`, ảnh bản vẽ `build/thu-hoathinh/nhan-vat/<mã>.png`, ảnh bảng chỉ số `<mã>-bang.png`, và file code có bảng `P`.
- Yêu cầu agent TỰ xem ảnh minh họa (phóng to, lấy mẫu màu `getpixel` bằng PIL nếu cần) và đối chiếu từng mục checklist. Không đưa số đo của người vẽ cho agent.

## Tiêu chí (100 điểm)
| Nhóm | Điểm | Đo cái gì |
|---|---|---|
| CL. Checklist "phải có" | 35 | Từng mục trong hồ sơ: ĐẠT / THIẾU / SAI. Đây là trọng tâm (nón, màu áo, hở bụng, vật phẩm đúng & cầm sát thân, biểu cảm đúng…) |
| Đ. Đặc điểm & biểu cảm | 20 | Khớp ảnh minh họa: mặt, tai, tóc/nón, dáng; **biểu cảm trung tính/dễ thương – KHÔNG gian/xấu** (sai điều cấm = trừ nặng) |
| T. Tỉ lệ khung | 15 | Đầu tròn R; thân (cao/rộng/bo); đầu lệch phải; bàn tay; vật phẩm (dài, nghiêng, dày, **khoảng cách tới thân – phải sát**) |
| M. Màu & đậm nhạt | 15 | So mã màu hồ sơ với từng vùng (ΔE lớn thì trừ); các tầng đậm nhạt hợp lý |
| N+C. Nét viền & cảm giác chung | 15 | Viền đều ~0.085R; nhìn lướt có nhận ra đúng nhân vật, dễ thương, gọn |

**Đạt: ≥ 80/100** và mỗi nhóm ≥ 70%. (Target 80 – chốt 20/11/2026 theo yêu cầu người dùng.)

## Định dạng trả về
1. **Checklist đối chiếu**: từng mục hồ sơ → ĐẠT/THIẾU/SAI + ghi chú.
2. **Điểm**: từng nhóm, lý do ngắn.
3. **Góp ý = thay đổi thông số**: `tên_tham_số: cũ → mới (lý do)` đúng khoá bảng `P`; việc cần thêm code ghi `CẦN THÊM: …`.
4. Tổng điểm + ĐẠT / CHƯA ĐẠT.

## Vòng sửa
Áp góp ý → chạy lại script → gọi agent chấm MỚI → lặp đến khi đạt **80** hoặc đủ 3 vòng. Mỗi vòng lưu điểm vào `docs/nhan-vat/<mã>-cham-diem.md`. Đạt → gửi người dùng ảnh bản vẽ + bảng chỉ số + điểm.
