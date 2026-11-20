---
name: tham-dinh-ho-so
description: Agent (bước 2/4) thẩm định HỒ SƠ TẠO HÌNH do agent nghiên cứu xuất ra – kiểm đúng đặc trưng nhân vật, đủ chi tiết để vẽ, hợp phong cách kênh, không bôi xấu; chấm /100, chưa đạt thì trả về cho nghiên cứu lại. Dùng sau nghien-cuu-nhan-vat, trước khi vẽ.
---

# Agent thẩm định hồ sơ (bước 2/4)

Kiểm hồ sơ tạo hình (từ [[nghien-cuu-nhan-vat]]) TRƯỚC khi đưa vào vẽ, để không vẽ trúng một hồ sơ sai/thiếu. Bước 2 của pipeline [[tao-nhan-vat]].

## Cách chạy (subagent độc lập – không phải agent đã viết hồ sơ)
Gọi Agent `general-purpose`, đưa: `docs/nhan-vat/<mã>-hoso.md` + các ảnh `assets/nhan-vat/mau/<mã>/*`. Yêu cầu agent TỰ xem ảnh và đối chiếu mô tả, rồi chấm.

## Tiêu chí (100 điểm)
| Nhóm | Điểm | Đo cái gì |
|---|---|---|
| Đ. Đúng đặc trưng | 35 | Mô tả có khớp ảnh minh họa và tạo hình được đồng thuận rộng rãi không; có bịa/sai đặc điểm nào không |
| Đủ. Đủ để vẽ | 30 | Có đủ: mặt/biểu cảm, nón/mũ, tóc, tai, dáng thân, từng lớp trang phục + **mã màu hex**, vật phẩm tay phải; checklist 8–14 mục cụ thể, đo được |
| H. Hợp phong cách & an toàn | 20 | Hợp phong cách kênh (màu phẳng, chibi); **có mục cấm bôi xấu**; biểu cảm trung tính/dễ thương; không nội dung nhạy cảm |
| Ng. Nguồn | 15 | Có nguồn tra; ảnh tải về thật (>10KB) và ghi giấy phép |

**Đạt: ≥ 85/100** và mỗi nhóm ≥ 70%.

## Trả về
1. Điểm từng nhóm + lý do ngắn.
2. **Chỗ cần sửa hồ sơ** (dạng gạch đầu dòng cụ thể: thiếu gì / sai gì / thêm hex nào).
3. Tổng điểm + ĐẠT / CHƯA ĐẠT.

## Vòng sửa
Chưa đạt → gửi góp ý về [[nghien-cuu-nhan-vat]] để bổ sung hồ sơ/ảnh → thẩm định lại (agent mới). Đạt → chuyển sang vẽ bằng [[ve-va-cham-anh]] (bước 3) rồi chấm đầu ra [[cham-nhan-vat]] (bước 4).
