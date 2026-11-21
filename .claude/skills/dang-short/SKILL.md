---
name: dang-short
description: Đăng (lên lịch) một Short 9:16 lên YouTube bằng Claude in Chrome – DÙNG CHUNG cho cả Short sử Việt (kênh Song Tử Kể Sử) lẫn Short hoạt hình Tây Du Ký (cùng kênh). Tải video >10 MB không nén (cắt byte + ghép trong trang), đặt tiêu đề, mô tả, thumbnail, playlist, thẻ, các mục mặc định, lên lịch. Dùng khi Short đã dựng xong (sử Việt: build/short/<mã>-p<n>/; Tây Du: du-an/tay-du-ky/output/short/).
---

# Agent Đăng Short YouTube

Trả lời tiếng Việt, ngắn. Người dùng muốn **không phải thao tác gì** và **không nén video**. Đọc skill `anthropic-skills:chrome-browser` trước bước trình duyệt đầu tiên. Quy tắc chung (không bấm "Công khai ngay" khi chưa được bảo, không đổi cài đặt kênh…) theo skill `dang-youtube`.

> **Skill dùng chung 2 dự án.** Hai nguồn Short khác nhau; **cơ chế đăng (mục 4 Quy trình Studio, cắt byte >10 MB, kiểm radio, lên lịch) y nhau — chỉ khác đường dẫn file + tiêu đề/mô tả/playlist**:
> - **Sử Việt (Song Tử Kể Sử):** làm theo mục 0–3 bên dưới (công thức tiêu đề Bạch Đằng, playlist `1-2p hay ho`, file `build/short/...`).
> - **Hoạt hình Tây Du Ký (upload ở `du-an/tay-du-ky/upload-video/`):** dùng mục **TÂY DU** ngay dưới đây thay cho mục 0–3; mục 4 Studio giữ nguyên. **Cùng kênh Song Tử Kể Sử** (giữ nguyên URL kênh ở mục 4).

## TÂY DU — Short hoạt hình (thay mục 0–3 khi đăng Short Tây Du) — CHUẨN chốt 21/11/2026
> Short 01 (Đường Tam Tạng) + Short 02 (Trư Bát Giới) đã đăng. Bảng dưới là **giá trị cố định**, lần sau chỉ đổi phần in nghiêng. Quy trình click: xem **mục 4T**.

| Mục | Giá trị Tây Du (cố định trừ phần *in nghiêng*) |
|---|---|
| **File video** | `du-an/tay-du-ky/output/short/short0*<n>*-full.mp4` (dọc 9:16 720×1280 @24fps, ~6–7 MB → **dưới 10 MB, tải thẳng, KHÔNG cắt byte**). Thiếu file → dựng lại `PYTHONUTF8=1 python scripts/hoathinh/but/short0*<n>*.py`. |
| **Tiêu đề** | **`<Tên nhân vật> (Du Ký #<n>)`** — đặt tên theo nhân vật chính, KHÔNG dùng câu hook dài (người dùng chốt 21/11). Vd `Đường Tam Tạng (Du Ký #1)`, `Trư Bát Giới (Du Ký #2)`. |
| **Mô tả** | Mẫu kênh (xem khối dưới bảng). |
| **Thumbnail** | `du-an/tay-du-ky/output/banner/short0*<n>*-thumbnail-doc.png` (dọc). **Tải thẳng được, KHÔNG bị chặn xác minh** (khác lưu ý cũ của sử Việt). ⚠️ Khi render thumbnail: **đừng để chữ/nhãn ở góc trên-trái** (đăng Short bị UI che) — Short 02 đã gỡ chip góc trong `thumb_short02.py`. |
| **Playlist** | **`Làm tí du ký`** (đã chốt — tick trong dropdown, KHÔNG phải `1-2p hay ho`). |
| **Category** | **Film & Animation** (KHÔNG phải Education — vì là hoạt hình; mặc định upload đã là Film & Animation). |
| **Related video** | Gắn **video Du Ký tập trước / tập #1** (Video elements → Related video → Add → chọn — hiện chỉ có 1 video nên chọn luôn). |
| Audience / AI / Language / Remixing | No kids · No AI · Vietnamese · Allow only audio remixing. |
| Lịch | người dùng chọn giờ (mặc định 18:00 GMT+7); **phải là giờ TƯƠNG LAI** — kiểm `new Date()` bằng JS, nếu đã qua thì chọn slot kế tiếp. |

Mô tả (mẫu kênh — dòng thứ 3 = tiêu đề):
```
#TayDuKy #<Tag nhân vật> #<Tag phụ> #HoatHinh #Shorts
Chúc các bạn xem video vui vẻ.

<Tên nhân vật> (Du Ký #<n>)

<2–4 câu kể cú lật / bí mật nhân vật, kết bằng 1 câu hỏi mời comment>
```
Tags: `Tây Du Ký, <nhân vật chính>, <tiền kiếp/liên quan>, Tôn Ngộ Không, Đường Tăng, Sa Tăng, hoạt hình, phim hoạt hình Việt, chibi, Short`.

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

## 4T. Quy trình click cụ thể — TÂY DU (đã chạy Short 02, 21/11/2026)
> Video < 10 MB nên BỎ bước cắt byte của mục 4.2. Dùng Claude in Chrome, thao tác theo `ref` từ `find` (ổn định hơn toạ độ), xen `screenshot` để kiểm.

0. **Chép file vào thư mục phiên trước** (⚠️ `file_upload` CHỈ đọc được file trong thư mục làm việc của phiên — `du-an/tay-du-ky/upload-video/`; scratchpad & đường dẫn ngoài đều bị chặn):
   `cp output/short/short0<n>-full.mp4 upload-video/` và `cp output/banner/short0<n>-thumbnail-doc.png upload-video/`. Xong việc thì **xoá 2 file này**.
1. `tabs_context_mcp` → `navigate` tới `https://studio.youtube.com/channel/UCov2XGUicGnDqyU9CcZwMNg` → click **Create** (góc phải trên) → **Upload videos**.
2. **Video:** `find "file input for video upload"` → ref `file-input (hidden)` → `file_upload` thẳng file mp4 (1 lần). Chờ ~5s, màn hình sang trang **Details** (title tạm = tên file).
3. **Title:** click ô Title → `ctrl+a` → `Delete` → `type` `"<Tên nhân vật> (Du Ký #<n>)"`.
4. **Description:** `find "Description textbox"` → click ref → `type` cả khối mô tả (xuống dòng bằng `\n` trong text là được).
5. **Thumbnail:** `find "thumbnail image file input"` → ref `file-input (hidden)` (KHÁC input video) → `file_upload` file png. Preview phải đổi sang thumbnail mới.
6. **Playlist:** click ô **Select** của Playlists → tick **`Làm tí du ký`** → **Done**.
7. **Audience:** `find "No, it's not made for kids radio"` → click ref.
8. **AI content:** `scroll_to` + click radio **No** (`find "No, AI wasn't used"`). (Advanced settings thường đã bung sẵn — có nút "Hide advanced settings".)
9. **Tags:** `find "Tags input field"` → click ô Tags → `type` chuỗi thẻ ngăn cách bằng `, ` → gõ thêm **một dấu `,`** cuối để chốt thẻ cuối.
10. **Remixing:** `find "Allow only audio remixing radio"` → click ref.
11. **Language:** `find "Video language Select"` → click → `find "Vietnamese language option"` → click option (danh sách rất dài, chọn theo ref off-screen là được).
12. **Category:** kiểm `find "Category dropdown"` thấy nút **Film & Animation** là đúng (mặc định). Không cần đổi.
13. **Kiểm radio bằng JS** (mục 4.4): phải có `No, it's not made for kids`, `No` (AI), `Allow only audio remixing`.
14. **Next** → **Video elements:** click **Add** ở "Related video" → trong "Choose specific video" click video **Du Ký tập #1** → về trang thấy tên video ở dòng Related video.
15. **Next** → **Initial check** (ghi Copyright / Community Guidelines "No issues") → **Next** → **Visibility**.
16. **Schedule:** cuộn xuống → click khối **Schedule** để bung → ô **date**: click → lịch hiện ra, click **số ngày** muốn (hôm nay có vòng tròn). Ô **time**: click mở listbox → **đừng gõ tay** (gõ `ctrl+a`+type bị chọn cả trang, không vào ô) → `find "<H:MM PM> time option"` → click **option** đúng giờ. **Time zone:** click → chọn **`(GMT+0700) Local Time`** (đầu danh sách).
    - ⚠️ Sau khi đổi về GMT+7, nếu nút Schedule xám + báo "Select a time in the future" → giờ đã qua, kiểm `new Date()` rồi chọn slot kế (Short 02 trễ 19:30 → dời 19:45).
17. Click **Schedule** (lời người dùng = xác nhận giờ). Hộp **"Video scheduled"** hiện link `youtube.com/shorts/<id>` → **Close**.
18. **Dọn:** xoá 2 file tạm ở `upload-video/`, `tabs_close_mcp` tab, ghi `docs/videos/short0<n>-dang-youtube.md` (link + lịch + mọi giá trị đã dùng).

## Lưu ý
- **Thumbnail tùy chỉnh bị chặn** ("One-time verification needed") khi kênh chưa xác minh và đã dùng lượt trong ngày → KHÔNG bấm Next (xác minh là việc người dùng tự làm), bấm Cancel, chọn "Select from video" → khung đầu tiên → Done (người dùng chọn cách này 17/11/2026). Ghi lại để gắn file THUMB sau khi xác minh.
- Ô Thumbnail: file input `#file-loader` (accept image/jpeg,png). Bấm Next trong wizard: một lần một bước, chờ 2s, kiểm tra màn hình (bấm liền 3 lần có thể chỉ qua 1–2 bước).
- Người dùng có thể đang bấm cùng lúc trong Chrome: thấy thứ lạ (playlist mới, chữ lạ) → dừng, hỏi.
