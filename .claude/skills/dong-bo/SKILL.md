---
name: dong-bo
description: Đồng bộ công việc giữa phiên cloud và máy nhà – pull main, báo nhánh cloud chưa gộp, dựng lại video đã duyệt mà máy còn thiếu (thanh tiến độ). Dùng khi người dùng nói "đồng bộ", khi mở phiên trên máy local, hoặc trước khi đăng YouTube.
---

# Agent Đồng bộ

Trả lời tiếng Việt, ngắn. **Không xem ảnh/khung hình** (tốn token; video đã được duyệt trên cloud) – chỉ đọc chữ.

## Trên máy local
1. Chạy `python3 scripts/dong_bo.py` (nền nếu lâu). Script: kiểm tra thay đổi chưa commit → `git pull --ff-only origin main` → báo nhánh `claude/*` chưa gộp → dựng lại Short trong `docs/videos/thanh-pham.json` mà máy chưa có hoặc đã cũ (dấu vân theo code/lời/giọng) → thanh tiến độ → "XONG".
2. Có nhánh cloud chưa gộp → báo người dùng mở PR đó trên GitHub và bấm Merge (hoặc tự gộp nếu người dùng bảo), rồi chạy lại.
3. Báo kết quả bằng thanh tiến độ cuối + đường dẫn video.
Người dùng muốn 0 token: nhấp đúp `dong-bo.command` (Mac) / `dong-bo.bat` (Windows) ở thư mục repo.

## Trên cloud – LUẬT KẾT THÚC PHIÊN (bắt buộc)
1. Commit + push nhánh phiên; **tạo PR vào `main`** và đưa link cho người dùng bấm Merge (đây là cách việc trên cloud "về nhà").
2. Video/Short được duyệt → thêm vào `docs/videos/thanh-pham.json` (kèm `phu_thuoc`: lời đọc, file .json giọng).
3. Ảnh nhỏ (≤10 MB: thumbnail…) có thể đẩy lên Drive thư mục của tập; video lớn **không** đi qua git/Drive – máy nhà tự dựng lại.
4. Cập nhật mục Trạng thái trong `CLAUDE.md` (đây là "bộ nhớ chung" giữa cloud và máy nhà).
