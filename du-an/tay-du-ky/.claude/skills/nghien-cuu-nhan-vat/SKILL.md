---
name: nghien-cuu-nhan-vat
description: Agent (bước 1/4) nghiên cứu TẠO HÌNH một nhân vật trước khi vẽ chibi – tra web + tải ẢNH MINH HỌA, rồi xuất HỒ SƠ TẠO HÌNH (mặt/biểu cảm, nón, tóc, trang phục + mã màu, vật phẩm tay phải, dáng thân) kèm checklist "phải có" và điều cấm. Dùng khi bắt đầu làm một nhân vật mới trong scripts/hoathinh/chibi/, hoặc khi người dùng muốn nghiên cứu tạo hình một nhân vật.
---

# Agent nghiên cứu tạo hình nhân vật (bước 1/4)

Thay cho việc người dùng phải feedback tay từng lần: nghiên cứu nhân vật → ra **hồ sơ tạo hình chuẩn** + **ảnh minh họa**. Hồ sơ này là "bản chuẩn" để bước 4 chấm điểm đo theo (mô tả + chi tiết trong ảnh). Là bước 1 của pipeline [[tao-nhan-vat]].

## Khi nào dùng
Trước khi vẽ một nhân vật mới (hoặc khi người dùng muốn tra tạo hình một nhân vật).

## Cách chạy (dùng subagent độc lập, có web)
Gọi Agent `general-purpose` với yêu cầu:
1. **Tra web** (WebSearch; web-fetch nếu cần) tạo hình nhân vật ở các bản phổ biến: khuôn mặt, nón/mũ, tóc, trang phục & màu, vũ khí/vật phẩm, dáng người. Ưu tiên đặc điểm đồng thuận rộng rãi.
2. **Tải 2–3 ảnh minh họa** về `assets/nhan-vat/mau/<mã>/` (ưu tiên Wikimedia Commons / nguồn công khai, có giấy phép). Tải bằng `curl -L -A "research-client/1.0" -o <file> "<URL ảnh trực tiếp>"`; kiểm tra file > 10KB; ghi nguồn + giấy phép.
3. **Viết hồ sơ** `docs/nhan-vat/<mã>-hoso.md` theo mẫu dưới.

## Mẫu HỒ SƠ TẠO HÌNH (giữ nguyên cấu trúc tiêu đề)
- `# Hồ sơ tạo hình: <Tên> (<tên gốc/xuất xứ>)`
- `## Ảnh minh họa` – danh sách đường dẫn file đã tải + mô tả/nguồn/giấy phép.
- `## Đặc điểm tạo hình` – các dòng **in đậm tên mục**: Khuôn mặt & biểu cảm (kèm LUẬT trung tính/dễ thương, không gian/xấu) · Đầu – nón/mũ · Tóc · Tai · Dáng thân (mập? hở bụng?) · Trang phục (lớp, kiểu, **màu**) · Vật phẩm tay phải (tên, hình, cách cầm – sát thân) · Phụ kiện khác.
- `## Bảng màu (hex gợi ý)` – bảng | Vùng | Hex | Ghi chú |.
- `## Checklist "phải có"` – 8–14 mục `- [ ]`, mỗi mục CỤ THỂ, đo được (đây là thước đo của bước 4).
- `## Điều CẤM` – ít nhất: không làm mặt gian/xấu/đê tiện; không bôi xấu nhân vật.
- `## Nguồn` – URL đã tra.

## Luật
- Phong cách kênh: màu phẳng, viền đều, chibi; **không bôi xấu nhân vật**, biểu cảm mặc định trung tính/dễ thương (xem [[chuan-hoat-hinh-sitcom]], [[phong-cach-ve-sitcom-vn]]).
- Ảnh minh họa chỉ để **học đặc trưng**, không sao chép nguyên vào thành phẩm.
- Hồ sơ phải tự đủ để người khác vẽ mà không hỏi lại.

## Ra
Hồ sơ `docs/nhan-vat/<mã>-hoso.md` + ảnh `assets/nhan-vat/mau/<mã>/*`. Tiếp theo: [[tham-dinh-ho-so]] (bước 2).
