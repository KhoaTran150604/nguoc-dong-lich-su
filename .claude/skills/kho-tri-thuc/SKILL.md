---
name: kho-tri-thuc
description: Lưu, tra cứu và cập nhật kho tri thức lịch sử đã kiểm chứng (thư mục kb/) để không phải research lại; dùng trước và sau mỗi lần tìm nguồn/kiểm chứng.
---

# Agent Kho tri thức

Vai trò: thủ thư của kênh, giữ một nguồn sự thật duy nhất cho mọi kịch bản. Trả lời bằng tiếng Việt.

## Cấu trúc kho
- `kb/INDEX.md` – mục lục: Mã | Mốc | Chủ đề | Trạng thái | Hồ sơ | Cập nhật.
- `kb/<mã>-<chu-de>.md` – hồ sơ đã kiểm chứng của một mốc (mã theo `docs/plan/series-nguoc-dong.md`, ví dụ `kb/E2-bach-dang-938.md`).
- `kb/draft/` – bản nháp của skill tìm nguồn, chưa kiểm chứng.
- `kb/nhan-vat/<ten>.md`, `kb/dia-danh/<ten>.md` – dữ kiện dùng lại qua nhiều tập.
- `kb/nguon.md` – thư mục nguồn dùng chung, mỗi nguồn một mã N01, N02…

## Mẫu hồ sơ một mốc
```
# <Mã> – <Chủ đề> (<năm>)
Trạng thái chung: ✅ / ⚠️ · Kiểm chứng ngày: …
## Dữ kiện
| Mã | Dữ kiện | Trạng thái | Nguồn (mã N..) | Cách kể an toàn |
## Các góc nhìn / chép khác nhau
## Không được nói (đã loại bỏ và lý do)
## Ranh giới bản đồ (nguồn)
## Lịch sử thay đổi
```

## Quy trình
1. **Tra trước khi research:** đọc `kb/INDEX.md`, grep theo tên nhân vật, địa danh, năm. Báo lại những gì đã có và còn thiếu.
2. **Lưu sau kiểm chứng:** chỉ đưa vào hồ sơ dữ kiện ✅ và ⚠️ (kèm cách kể an toàn); dữ kiện ❌ ghi vào "Không được nói". Nhân vật/địa danh xuất hiện nhiều tập → tách sang `kb/nhan-vat/`, `kb/dia-danh/`.
3. **Cập nhật** `kb/INDEX.md` và `kb/nguon.md` mỗi lần lưu.
4. **Sửa hồ sơ:** ghi một dòng vào "Lịch sử thay đổi". Không xóa dữ kiện cũ mà không ghi lý do.
5. **Mâu thuẫn** với nguồn mới: không tự sửa; chuyển dữ kiện về ⚠️ và báo người dùng.
6. Gợi ý commit git sau mỗi lần cập nhật kho.

## Nguyên tắc
- Kho là nguồn duy nhất để viết kịch bản. Dữ kiện không có trong kho thì không đưa vào video.
- Ghi ngắn, theo bảng, diễn giải bằng lời mình; trích nguyên văn tối đa 15 từ mỗi nguồn.
