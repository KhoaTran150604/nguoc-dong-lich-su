---
name: dang-youtube
description: Đăng (lên lịch) video của kênh Song Tử Kể Sử lên YouTube bằng Claude in Chrome điều khiển YouTube Studio của người dùng – tải file, điền tiêu đề/mô tả/thẻ/playlist/đối tượng, lên lịch 18:00. Dùng khi video đã render xong và có file thông tin đăng docs/videos/<MÃ>-dang-youtube.md.
---

# Agent Đăng YouTube

Vai trò: thao tác YouTube Studio thay người dùng, **chỉ lên lịch**, không bao giờ "Công khai ngay". Trả lời bằng tiếng Việt.

## Bước 0 – BẮT BUỘC làm trước khi mở Claude in Chrome (người dùng yêu cầu 17/11/2026)
Chốt 2 trường **Tiêu đề** và **Mô tả** trong `docs/videos/<MÃ>-dang-youtube.md`, cho người dùng duyệt xong mới mở trình duyệt.
- **Tiêu đề:** `(Ngược dòng sử Việt #<số tập>) Năm <năm>: <câu móc>` – vd `(Ngược dòng sử Việt #1) Năm 938: Khi Thủy Triều Rút Trên Sông Bạch Đằng`.
- **Tiêu đề SHORT** (người dùng chốt 17/11/2026): `[Câu móc tò mò, ≤ 40 ký tự] | [Từ khóa: trận/nhân vật + năm] #[hashtag]`
  - Câu móc = đúng câu hỏi ở đầu Short, khớp chữ trên thumbnail (lấy từ `hook` trong `SHORTS` của `scripts/video/tap/<mã>.py`).
  - Từ khóa (vd "Bạch Đằng 938", "Ngô Quyền") – Short vẫn hiện khi tìm kiếm.
  - **Không ghi "Phần n"** trong tiêu đề (người lạ thấy "Phần 4" sẽ lướt qua; số phần đã có trên dải chữ trong video).
  - Cuối tiêu đề 1–2 hashtag (#lichsuvietnam, #bachdang, #ngoquyen…), số còn lại để trong mô tả. Tổng < ~70 ký tự.
  - Ví dụ E2: P1 `Một hàng cọc gỗ đánh chìm cả hạm đội? | Bạch Đằng 938 #lichsuvietnam` · P2 `Thắng giặc ngoài, chết vì người trong | Trước trận Bạch Đằng 938 #lichsuvietnam` · P3 `Một lời can bị bỏ ngoài tai | Nam Hán trước Bạch Đằng 938 #lichsuvietnam` · P4 `Giặc còn trên biển, Ngô Quyền đã làm gì? | Bạch Đằng 938 #ngoquyen` · P5 `Chỉ trong chốc lát, nước rút… | Trận Bạch Đằng 938 #lichsuvietnam` · P6 `Sau Bạch Đằng, Ngô Quyền làm gì? | Lịch sử Việt Nam 939 #ngoquyen`
  - Mô tả Short: dùng chung mẫu kênh dưới đây (dòng tên video = tiêu đề Short). Thumbnail Short: `build/short/<mã>-p<n>/THUMB-<MÃ>-P<n>.jpg`.
  - **Playlist Short: `1-2p hay ho`** (chỉ playlist này, KHÔNG thêm "Ngược Dòng Sử Việt" – người dùng chốt 17/11/2026). Các mục còn lại của Short điền như bảng mặc định video dài; thẻ dùng bộ thẻ của tập.
  - Shorts remixing: Studio chỉ có "Allow video and audio" / "Allow only audio" → chọn **Allow only audio remixing**.
  - Sau khi bấm Schedule, Studio hay báo "We had trouble saving your video, retrying…" / hộp "Unsaved changes" – **bình thường, vẫn lưu** (người dùng xác nhận 17/11/2026). Không bấm "Discard changes"; chọn "Keep editing" nếu hộp hiện, rồi kiểm tra ở Content → Shorts (trạng thái Scheduled) và trang chi tiết video.
  - Kiểm tra radio đã chọn bằng JS (`tp-yt-paper-radio-button[checked]`) trước khi Next – bấm theo toạ độ hay trượt (AI use từng bị sót). Ưu tiên bấm theo `ref` từ `find`, không theo toạ độ (trang lệch → mở nhầm "New playlist").
- **Mô tả – mẫu kênh** (chỉ thay hashtag + tên video; người dùng sẽ bổ sung thêm mục sau):
```
#SongTuKeSu #NguocDongSuViet #LichSuVietNam #<Trận/Sự kiện> #<Nhân vật>
Chúc các bạn xem video vui vẻ.

<Tiêu đề video>

►Lịch ra video:
18:00 Thứ 2, 4, 6 hằng tuần
```
Không thêm link donate/MoMo/mạng xã hội cá nhân (kênh ẩn danh).

## Mặc định cố định (người dùng chốt 17/11/2026) – KHÔNG hỏi lại
Mỗi video **chỉ tuỳ chỉnh 3 thứ: Tiêu đề, Thumbnail, Tags**. Mô tả = mẫu ở Bước 0 (chỉ thay tên video + 2 hashtag cuối). Mọi thứ khác điền y như bảng:

| Mục (YouTube Studio) | Giá trị |
|---|---|
| Audience | **No, it's not made for kids** |
| Age restriction | Không giới hạn (mặc định) |
| Paid promotion | Để mặc định (không tick) |
| AI use | **No** |
| Automatic chapters / places / concepts | Giữ bật (mặc định) |
| Video language | **Vietnamese** |
| Caption certification | None |
| Recording date / location | Để trống |
| License | Standard YouTube License · Allow embedding ✅ · Publish to subscriptions feed ✅ |
| Shorts remixing | **Don't allow remixing** |
| Category | **Education** (Type / Problems / Exam để trống) |
| Video elements (Subtitles / End screen / Cards) | **Bỏ qua**, bấm Next luôn |
| Lịch | 18:00 Thứ 2/4/6 (GMT+7) |

Thumbnail: đồ họa riêng (không lấy hình trong video), 1280×720, có nhãn "NGƯỢC DÒNG SỬ VIỆT #<số>", từ khoá lớn (địa danh/trận), vật thể chủ đề (vd cọc), nhân vật thua bị gạch X đỏ. Mẫu: `scripts/thumbnail/e2.py` → lưu cạnh video trong `video/<series>/<năm>-<Nhan-Vat>/thumbnail-<MÃ>.jpg`; gắn bằng `file_upload` vào ô Thumbnail (< 10 MB).

## Điều kiện trước khi làm
1. **Có công cụ Claude in Chrome** (tên `mcp__claude-in-chrome__*`, hoặc `mcp__remote-devices__…` khi phiên đám mây đã nối với máy người dùng). Đọc skill `anthropic-skills:chrome-browser` trước bước đầu tiên. Không có công cụ → nói rõ cần mở phiên Claude trên máy tính có cài Claude in Chrome (hoặc nối máy qua Remote Control), dừng lại.
2. **File video nằm trên máy người dùng** (Chrome chỉ chọn được file trên máy đó). Thư mục chuẩn (17/11/2026): `video/<series>/<năm>-<Nhan-Vat>/` trong dự án (vd `video/nguoc-dong-su-viet/938-Ngo-Quyen/`, không commit – đã gitignore). Cũ: `[project-film] AI History/<năm> - <nhân vật>/`. Nguồn tải: tin nhắn gửi file, GitHub `assets/<mã>/`, hoặc Drive thư mục series.
3. **Có file thông tin đăng** `docs/videos/<MÃ>-dang-youtube.md` (tiêu đề, mô tả có mục lục + nguồn, thẻ, playlist, giờ đăng). Chưa có thì soạn trước, cho người dùng duyệt.

## Quy trình (YouTube Studio)
1. Mở trang tải lên của kênh (người dùng đưa, 17/11/2026):
   `https://studio.youtube.com/channel/UCov2XGUicGnDqyU9CcZwMNg/videos/upload?d=ud&filter=%5B%5D&sort=%7B%22columnType%22%3A%22date%22%2C%22sortOrder%22%3A%22DESCENDING%22%7D`
   Kiểm tra đang đăng nhập đúng kênh **Song Tử Kể Sử** (avatar Văn – Võ). Sai kênh → dừng, hỏi.
2. Hộp "Tải video lên" → chọn file video. **Không bấm "Select files"** (hộp chọn file macOS nằm ngoài trang, Claude không điều khiển được; `file_upload` chỉ nhận < 10 MB/lần). Cách đã chạy được 17/11/2026:
   a. `split -b 9000000 <video> build/upload-chunks/part_` rồi đổi tên thành `part_xx.bin` (thư mục nằm trong `build/` nên git bỏ qua). Lưu ý: KHÔNG `cd` vào thư mục mảnh, để còn xoá được sau.
   b. `javascript_tool`: tạo `<input type=file id=claude-chunk aria-label="claude chunk input">`; khi `change` thì lưu `file.arrayBuffer()` vào `window.__chunks[file.name]`.
   c. `file_upload` từng mảnh vào ô đó, **mỗi lần một lệnh gọi riêng** (gộp nhiều mảnh trong browser_batch bị tính chung giới hạn 10 MB).
   d. Ghép theo tên đã sắp xếp → `new File([...], '<tên gốc>.mp4', {type:'video/mp4'})`; so SHA-256 (`crypto.subtle.digest`) với `shasum -a 256` của file gốc.
   e. Khớp mã → gán vào `input[type=file]` của YouTube bằng `DataTransfer`, phát sự kiện `change`; xoá ô tạm, đặt `window.__chunks=null`. Xong thì xoá `build/upload-chunks/`. Chờ tải lên xong (thanh tiến độ). Báo người dùng % tải lên ở các mốc.
3. **Chi tiết**: tiêu đề, mô tả (dán nguyên văn từ file thông tin đăng – đã chốt ở Bước 0), thumbnail (nếu có file), playlist (tạo "Ngược Dòng Sử Việt" nếu chưa có), **Không dành cho trẻ em**. "Hiện thêm": thẻ, ngôn ngữ Tiếng Việt, danh mục Giáo dục. Mục **AI use** (trong "Show more"): luôn chọn **No** (người dùng chốt 17/11/2026). **Shorts remixing**: chọn **Don’t allow remixing**. Category: Education (các ô Type/Problems để trống). Ngôn ngữ: Vietnamese.
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
Video dài: **thứ 2, thứ 4, thứ 6 lúc 18:00** (đổi 17/11/2026). Short: các ngày còn lại lúc 18:00 (Short cắt từ video dài, viết lại hook).
