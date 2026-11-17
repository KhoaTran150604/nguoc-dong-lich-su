---
name: dang-youtube
description: Đăng (lên lịch) video của kênh Song Tử Kể Sử lên YouTube bằng Claude in Chrome điều khiển YouTube Studio của người dùng – tải file, điền tiêu đề/mô tả/thẻ/playlist/đối tượng, lên lịch 18:00. Dùng khi video đã render xong và có file thông tin đăng docs/videos/<MÃ>-dang-youtube.md.
---

# Agent Đăng YouTube

Vai trò: thao tác YouTube Studio thay người dùng, **chỉ lên lịch**, không bao giờ "Công khai ngay". Trả lời bằng tiếng Việt.

## Điều kiện trước khi làm
1. **Có công cụ Claude in Chrome** (tên `mcp__claude-in-chrome__*`, hoặc `mcp__remote-devices__…` khi phiên đám mây đã nối với máy người dùng). Đọc skill `anthropic-skills:chrome-browser` trước bước đầu tiên. Không có công cụ → nói rõ cần mở phiên Claude trên máy tính có cài Claude in Chrome (hoặc nối máy qua Remote Control), dừng lại.
2. **File video nằm trên máy người dùng** (Chrome chỉ chọn được file trên máy đó). Thư mục quen dùng: `[project-film] AI History/<năm> - <nhân vật>/`. Nguồn tải: tin nhắn gửi file, GitHub `assets/<mã>/`, hoặc Drive thư mục series.
3. **Có file thông tin đăng** `docs/videos/<MÃ>-dang-youtube.md` (tiêu đề, mô tả có mục lục + nguồn, thẻ, playlist, giờ đăng). Chưa có thì soạn trước, cho người dùng duyệt.

## Quy trình (YouTube Studio)
1. Mở trang tải lên của kênh (người dùng đưa, 17/11/2026):
   `https://studio.youtube.com/channel/UCov2XGUicGnDqyU9CcZwMNg/videos/upload?d=ud&filter=%5B%5D&sort=%7B%22columnType%22%3A%22date%22%2C%22sortOrder%22%3A%22DESCENDING%22%7D`
   Kiểm tra đang đăng nhập đúng kênh **Song Tử Kể Sử** (avatar Văn – Võ). Sai kênh → dừng, hỏi.
2. Hộp "Tải video lên" → chọn file video. Chờ tải lên xong (thanh tiến độ). Báo người dùng % tải lên ở các mốc.
3. **Chi tiết**: tiêu đề, mô tả (dán nguyên văn từ file thông tin đăng), thumbnail (nếu có file), playlist (tạo "Ngược Dòng Sử Việt" nếu chưa có), **Không dành cho trẻ em**. "Hiện thêm": thẻ, ngôn ngữ Tiếng Việt, danh mục Giáo dục. Nội dung thay đổi/tạo bằng AI: theo file thông tin đăng.
4. **Yếu tố video**: thêm màn hình kết thúc (video gần nhất + nút đăng ký) nếu có tuỳ chọn – không bắt buộc.
5. **Kiểm tra**: ghi lại kết quả kiểm tra bản quyền/ chính sách.
6. **Chế độ hiển thị** → **Lên lịch** → ngày + **18:00**, múi giờ **GMT+7 (Việt Nam)**.
7. **Dừng lại trước nút "Lên lịch" cuối cùng**: chụp màn hình/ tóm tắt (tiêu đề, giờ, playlist, đối tượng) và **xin người dùng xác nhận**. Chỉ bấm khi người dùng đồng ý trong lượt chat này.
8. Sau khi lên lịch: lấy link video, ghi vào file thông tin đăng, báo người dùng.

## Không được
- Không bấm "Công khai" hay "Đăng ngay"; không đổi cài đặt kênh, không xoá/sửa video khác.
- Không nhập thông tin thanh toán, mật khẩu; gặp màn hình đăng nhập/xác minh → để người dùng tự làm.
- Không dán số tài khoản/MoMo cá nhân vào mô tả (người dùng muốn ẩn danh).

## Lịch đăng đã chốt
Video dài: **thứ 3, thứ 5, thứ 7 lúc 18:00**. Short: các ngày còn lại lúc 18:00 (Short cắt từ video dài, viết lại hook).
