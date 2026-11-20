---
name: dang-short
description: Đăng (lên lịch) một Short 9:16 lên YouTube bằng Claude in Chrome – DÙNG CHUNG cho cả Short sử Việt (kênh Song Tử Kể Sử) lẫn Short hoạt hình Tây Du Ký (cùng kênh). Tải video >10 MB không nén (cắt byte + ghép trong trang), đặt tiêu đề, mô tả, thumbnail, playlist, thẻ, các mục mặc định, lên lịch. Dùng khi Short đã dựng xong (sử Việt: build/short/<mã>-p<n>/; Tây Du: du-an/tay-du-ky/output/short/).
---

# Agent Đăng Short YouTube

Trả lời tiếng Việt, ngắn. Người dùng muốn **không phải thao tác gì** và **không nén video**. Đọc skill `anthropic-skills:chrome-browser` trước bước trình duyệt đầu tiên. Quy tắc chung (không bấm "Công khai ngay" khi chưa được bảo, không đổi cài đặt kênh…) theo skill `dang-youtube`.

> **Skill dùng chung 2 dự án.** Hai nguồn Short khác nhau; **cơ chế đăng (mục 4 Quy trình Studio, cắt byte >10 MB, kiểm radio, lên lịch) y nhau — chỉ khác đường dẫn file + tiêu đề/mô tả/playlist**:
> - **Sử Việt (Song Tử Kể Sử):** làm theo mục 0–3 bên dưới (công thức tiêu đề Bạch Đằng, playlist `1-2p hay ho`, file `build/short/...`).
> - **Hoạt hình Tây Du Ký (upload ở `du-an/tay-du-ky/upload-video/`):** dùng mục **TÂY DU** ngay dưới đây thay cho mục 0–3; mục 4 Studio giữ nguyên. **Cùng kênh Song Tử Kể Sử** (giữ nguyên URL kênh ở mục 4).

## TÂY DU — Short hoạt hình (thay mục 0–3 khi đăng Short Tây Du)
- **File video:** lấy từ `docs/videos/thanh-pham.json` mục `short_hoathinh` (trường `file`, vd `du-an/tay-du-ky/output/short/short01-full.mp4` — dọc 9:16 720×1280 @24fps). Máy thiếu file → dựng lại bằng trường `lenh` của mục đó (vd `PYTHONUTF8=1 HF_HUB_DISABLE_XET=1 python scripts/hoathinh/but/short01.py`).
- **Tiêu đề / mô tả / hashtag:** theo NỘI DUNG Tây Du, **không** dùng ví dụ Bạch Đằng. Soạn từ kịch bản của tập (`du-an/tay-du-ky/kich-ban/short-01-*.md`): câu móc = câu hỏi ở đầu Short, khớp chữ trên banner. Hashtag gợi ý `#TayDuKy #Shorts` + chủ đề tập. Cho người dùng **duyệt tiêu đề + mô tả trước khi mở Chrome** (như Bước 0 của `dang-youtube`).
- **Thumbnail:** banner tập ở `du-an/tay-du-ky/output/banner/` (vd `short01-doan-16x9.png`) — dùng cho video liên quan/16:9; với Short, thumbnail tùy chỉnh thường bị chặn → theo luật "Select from video" ở mục Lưu ý.
- **Playlist:** Tây Du **chưa chốt playlist** — HỎI người dùng, đừng mặc định `1-2p hay ho` (đó là của sử Việt).
- Các mục mặc định còn lại (Audience No kids, AI use No, Vietnamese, Education, remixing, lịch) dùng chung như `dang-youtube`.

## 0. Chuẩn bị (máy local)
- File: `build/short/<mã>-p<n>/SHORT-<MÃ>-P<n>.mp4` + `THUMB-<MÃ>-P<n>.jpg`. Chưa có → dựng: `PATH=~/.local/mm/root/envs/kenh312/bin:$PATH HF_HUB_DISABLE_XET=1 python scripts/video/short.py <mã> <n>` (cần Python 3.12 + cairo + ffmpeg + ZeroTTS; môi trường micromamba `~/.local/mm/root/envs/kenh312`, cài 17/11/2026).
- Xem `them.log`: câu hook bị Whisper đánh "XEM" → báo người dùng nghe lại.

## 1. Tiêu đề (người dùng chốt 17/11/2026)
`[Câu móc tò mò, ≤ 40 ký tự] | [Từ khóa: trận/nhân vật + năm] #[hashtag]` – tổng < ~70 ký tự.
- Câu móc = đúng câu hỏi đầu Short, khớp chữ trên thumbnail (`hook` trong `SHORTS` của `scripts/video/tap/<mã>.py`).
- Có từ khóa tìm kiếm (vd "Bạch Đằng 938", "Ngô Quyền").
- **Không ghi "Phần n"** (số phần đã nằm trên dải chữ trong video).
- Cuối tiêu đề 1–2 hashtag; còn lại để mô tả.
- E2: P1 `Một hàng cọc gỗ đánh chìm cả hạm đội? | Bạch Đằng 938 #lichsuvietnam` · P2 `Thắng giặc ngoài, chết vì người trong | Trước trận Bạch Đằng 938 #lichsuvietnam` · P3 `Một lời can bị bỏ ngoài tai | Nam Hán trước Bạch Đằng 938 #lichsuvietnam` · P4 `Giặc còn trên biển, Ngô Quyền đã làm gì? | Bạch Đằng 938 #ngoquyen` · P5 `Chỉ trong chốc lát, nước rút… | Trận Bạch Đằng 938 #lichsuvietnam` · P6 `Sau Bạch Đằng, Ngô Quyền làm gì? | Lịch sử Việt Nam 939 #ngoquyen`

## 2. Mô tả = mẫu kênh của video dài (dòng giữa = tiêu đề Short)
```
#SongTuKeSu #NguocDongSuViet #LichSuVietNam #<Trận> #<Nhân vật>
Chúc các bạn xem video vui vẻ.

<Tiêu đề Short>

►Lịch ra video:
18:00 Thứ 2, 4, 6 hằng tuần
```

## 3. Các mục khác
| Mục | Giá trị |
|---|---|
| Thumbnail | `THUMB-<MÃ>-P<n>.jpg` – `file_upload` vào input file của ô Thumbnail |
| Playlist | **chỉ `1-2p hay ho`** (không thêm "Ngược Dòng Sử Việt") |
| Audience | No, it's not made for kids |
| AI use | No |
| Tags | bộ thẻ của tập (trong `docs/videos/<MÃ>-dang-youtube.md`) |
| Video language | Vietnamese · Caption certification None |
| Shorts remixing | **Allow only audio remixing** (Studio không có "Don't allow") |
| Category | Education |
| License, paid promotion, chapters… | để mặc định |
| Video elements | **Related video: gắn video dài của tập** (bấm Add ở "Related video", chọn video dài – người dùng yêu cầu 17/11/2026); Subtitles bỏ qua |
| Lịch | người dùng chọn giờ; mặc định ngày không có video dài, 18:00, múi giờ **(GMT+0700) Local Time** |

## 4. Quy trình Studio
1. `https://studio.youtube.com/channel/UCov2XGUicGnDqyU9CcZwMNg` → Create → Upload videos.
2. **Tải video không nén** (file_upload giới hạn 10 MB/lần; không bấm "Select files"):
   a. `split -b 7000000 <video> <thư mục tạm>/part-`, kiểm `shasum -a 256`.
   b. JS tạo các `<input type=file id=claude-part-a/b…>` tạm; `find` lấy ref; `file_upload` từng phần, **mỗi phần một lệnh riêng**.
   c. JS ghép `new File([a,b,…], '<tên>.mp4', {type:'video/mp4'})`, so SHA-256, khớp thì gán vào `input[type=file]` của YouTube bằng `DataTransfer` + `change`. Xoá input tạm và thư mục mảnh.
3. Điền tiêu đề (cmd+a rồi gõ), mô tả, thumbnail, playlist, audience, Show more → AI use, tags, ngôn ngữ, remix, category.
4. **Bấm theo `ref` từ `find`, không theo toạ độ** (trang lệch → mở nhầm "New playlist"). Trước khi Next, kiểm radio bằng JS: `[...document.querySelectorAll('tp-yt-paper-radio-button[checked]')].map(r=>r.innerText.trim().split('\n')[0])` – phải có "No, it's not made for kids", "No" (AI), "Allow only audio remixing".
5. Next → Next → Checks (ghi kết quả bản quyền) → Visibility → Schedule: ngày gõ vào ô date (`Nov 17, 2026` + Enter), giờ chọn option trong listbox (vd `9:45 PM`), Time zone chọn `(GMT+0700) Local Time`.
6. Bấm Schedule khi người dùng đã nói giờ (lời người dùng trong lượt chat là xác nhận).
7. Báo lỗi "We had trouble saving… retrying" / hộp "Unsaved changes" là **bình thường, vẫn lưu** → chọn "Keep editing", không "Discard changes".
8. Kiểm tra: Content → Shorts thấy "Scheduled"; mở trang chi tiết đọc lại tiêu đề/mô tả/thẻ/playlist bằng JS. Ghi link + lịch vào `docs/videos/<MÃ>-dang-youtube.md`.

## Lưu ý
- **Thumbnail tùy chỉnh bị chặn** ("One-time verification needed") khi kênh chưa xác minh và đã dùng lượt trong ngày → KHÔNG bấm Next (xác minh là việc người dùng tự làm), bấm Cancel, chọn "Select from video" → khung đầu tiên → Done (người dùng chọn cách này 17/11/2026). Ghi lại để gắn file THUMB sau khi xác minh.
- Ô Thumbnail: file input `#file-loader` (accept image/jpeg,png). Bấm Next trong wizard: một lần một bước, chờ 2s, kiểm tra màn hình (bấm liền 3 lần có thể chỉ qua 1–2 bước).
- Người dùng có thể đang bấm cùng lúc trong Chrome: thấy thứ lạ (playlist mới, chữ lạ) → dừng, hỏi.
