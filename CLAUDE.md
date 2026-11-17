# Song Tử Kể Sử (trước: Ngược Dòng Sử Việt) – Bàn giao dự án

> File này tóm tắt toàn bộ những gì đã quyết định và làm trong Claude chat (14–15/11/2026), để tiếp tục trong Claude Code. Trả lời người dùng bằng **tiếng Việt**, giọng thân thiện, ngắn gọn.

## 0. Làm việc cloud ↔ máy nhà (LUẬT ĐỒNG BỘ – 17/11/2026)
- **`main` là nhánh chuẩn duy nhất.** Mỗi phiên cloud làm trên nhánh `claude/…` riêng → **kết thúc phiên: tạo PR vào main**, người dùng bấm Merge. Không để nhánh cloud nằm treo (17/11 đã phát hiện 2 nhánh làm song song bị lệch).
- **Máy nhà:** ngồi vào là chạy đồng bộ – nhấp đúp `dong-bo.command` (Mac) / `dong-bo.bat` (Windows), hoặc nói "đồng bộ" (skill `dong-bo`). Rời máy: commit + push.
- **Video không đi qua git:** dựng lại từ code bằng `scripts/dong_bo.py` theo danh sách `docs/videos/thanh-pham.json` (cloud thêm mục khi người dùng duyệt). Thumbnail/ảnh ≤10 MB có thể đẩy lên Drive.
- **File này là bộ nhớ chung** của mọi phiên Claude (cloud và local): cuối phiên luôn cập nhật mục 6 Trạng thái.

## 1. Người dùng & mục tiêu
- Làm thêm ngoài giờ, khoảng **1 tiếng/ngày**. Muốn **ẩn danh**, AI làm phần lớn nội dung, người dùng định hướng.
- Kỹ năng sẵn có: **Data Analyst**.
- Mục tiêu: kênh YouTube có thu nhập (YouTube là nền tảng chính trả tiền theo view cho người ở VN; TikTok Creator Rewards không mở cho VN; Facebook chỉ mời giới hạn). RPM người xem Việt rất thấp (≈150–180 USD / 1 triệu view) → cần **video dài 10–20 phút** + nguồn thu khác (tài trợ, sản phẩm số).
- Hướng đã thử và bỏ: affiliate thuần, bán template dashboard (thị trường đã có Sapo, KiotViet…), kênh "AI + data" (để dành làm hướng phụ sau).

## 2. Kênh đã chốt
| Mục | Giá trị |
|---|---|
| Tên kênh | **Song Tử Kể Sử** (đổi 16/11/2026 cho kênh rộng hơn: sử Việt, Trung Hoa/Tam Quốc, thế giới). "Ngược Dòng Sử Việt" giữ làm tên series/playlist. Setup: `docs/brand/setup-kenh.md` |
| Handle | đề xuất `@songtukesu` – người dùng đang kiểm tra |
| Nhân vật | Hai anh em sinh đôi "Văn võ song toàn": **Anh Văn** (áo vàng, kể sử, giữ nguồn) · **Em Võ** (áo đỏ, dẫn trận) – `docs/brand/nhan-vat-song-tu.md` |
| Avatar | ✅ mẫu "Văn – Võ": `assets/brand/song-tu/AVATAR-YouTube-800x800.png` (code `scripts/brand/avatar_5.py --van-vo`) |
| Chủ đề | Lịch sử Việt Nam theo dòng thời gian, kể **lùi** từ hiện tại về quá khứ |
| Persona | Người kể giấu mặt. Giọng: **ZeroTTS – Gia Huy (`giahuy`) nguyên bản** (nam, trẻ, kể chuyện, trầm ấm), chạy local, miễn phí. Chốt 16/11/2026, mặc định cho mọi video. Làm âm thanh bằng skill `giong-doc`. Vbee "Anh Khôi nâng cao" chỉ để dự phòng |
| Nhận diện | Trống đồng Đông Sơn + bản đồ Việt Nam (có **Hoàng Sa, Trường Sa**) + vành chim Lạc bay **ngược chiều kim đồng hồ** = ngược dòng thời gian. Màu: đen mực `#14110F`, vàng đồng `#C9A24A`/`#F3D27A`, đỏ sơn mài `#B3261E`, kem `#F2E6CC`. Font: Playfair Display (tiêu đề), Be Vietnam Pro (chữ) |
| Mô tả kênh | Đã dán (có dòng công khai dùng AI cho hình & giọng) |
| Đã xong | Tạo kênh thương hiệu, xác minh SĐT, avatar, banner, watermark |

## 3. Định dạng video đã chọn (trộn 3 kiểu)
1. **Slideshow ảnh AI** (ảnh tĩnh + zoom/lia nhẹ): phần cảm xúc, con người. Ảnh tạo bằng **Google Flow** (miễn phí ~50 credit/ngày; Veo 3.1 cho vài clip ngắn mở đầu). Style chữ ký đề xuất: **tranh sơn mài**.
2. **Bản đồ cổ + cờ tướng di chuyển** (kiểu kênh Sử Lược, nhưng bản đồ của mình): diễn biến, hành quân, lãnh thổ. Code ở `scripts/bandoco/`.
3. **Sa bàn động** (mặt cắt cảnh, thuyền/nước/cọc chuyển động): giải thích "vì sao thắng". Code ở `scripts/saban/`.
- **Chữ ký mỗi tập:** 3 giây đầu là **đồng hồ năm chạy ngược + bản đồ co dần**; kết bằng "Lùi tiếp: năm …". (Chưa làm mẫu – việc tiếp theo.)
- **Vùng an toàn Shorts** (đã kiểm trên iPhone 16/11): màn dài hơn 9:16 nên mất ~100px mỗi bên; thanh tab che 0–360px trên; tên kênh/tiêu đề che từ ~1440px xuống; cột nút che phải từ ~880px. → Phụ đề ở **y≈1150 (~60%)**, chữ 50px, tối đa 2 dòng, rộng ≤680px; nhãn ở y≈372; nguồn + 'minh họa' ngay dưới phụ đề; nội dung chính trong x 100–880, y 360–1440. (Quy tắc cũ '77–87%' bị che – bỏ.)
- Kịch bản Short: 130–160 từ, ~45–60 giây.

### Cách đặt tên video dài (đã chốt 17/11/2026)
- Công thức: `(Ngược Dòng Sử Việt #[số tập]) Năm [năm]: [hình ảnh/câu chuyện]` — tên series trong ngoặc đặt đầu (kiểu "Goose Goose Duck Funny Moments #1").
- Số tập đánh **#1, #2, #3…** theo thứ tự đăng (không dùng mã E2, B4… của kế hoạch trên YouTube).
- Viết hoa "Ngược Dòng Sử Việt"; năm luôn đứng ngay sau ngoặc; vế sau là hình ảnh cụ thể, **chỉ dựa trên dữ kiện đã kiểm chứng trong `kb/`**.
- Tập 1: **(Ngược Dòng Sử Việt #1) Năm 938: Khi Thủy Triều Rút Trên Sông Bạch Đằng**
- Phương án dự phòng nếu tiêu đề bị cắt trên điện thoại (~60–70 ký tự): rút thành `(Ngược Dòng #n)`.
- Mỗi video nằm trong playlist chính "Ngược Dòng Sử Việt" + 1 playlist nhánh (vd. "Trận Đánh Định Mệnh", "Tên Nước Qua Các Thời", "Kinh Đô Đã Dời", "Một Đời Trên Bản Đồ", "Sử Cũ Chép Gì?"). Thumbnail: năm to, màu vàng đồng, cùng vị trí mọi tập.

## 4. Series
Xem `docs/plan/series-nguoc-dong.md`: **38 mốc** lùi từ 1976 về Văn Lang (A hiện đại 6 · B Nguyễn/Tây Sơn 8 · C Lê/Mạc/Hồ 6 · D Trần/Lý 9 · E Đinh/Ngô/Bắc thuộc/dựng nước 9). Làm **giai đoạn A sau cùng** (nhạy cảm). Danh sách là bản nháp, phải qua quy trình nguồn.

## 5. Quy tắc nội dung (bắt buộc)
- **Chỉ dùng thông tin lịch sử có nguồn rõ ràng, được chấp nhận rộng rãi. Không tự chế.** Chỉ được kể lại hay hơn, cô đọng hơn, đổi góc nhìn.
- Quy trình mỗi tập (skills trong `.claude/skills/`):
  1. `kho-tri-thuc` – tra `kb/` trước.
  2. `nguon-lich-su` – tìm nguồn cho phần còn thiếu → `kb/draft/`.
  3. `kiem-chung-nguon` – kiểm chứng **độc lập bằng subagent** (≥2 nguồn độc lập, ≥1 nguồn cấp 1–3) → ✅/⚠️/❌.
  4. `kho-tri-thuc` – lưu hồ sơ vào `kb/`, cập nhật `kb/INDEX.md`.
  5. Viết kịch bản bằng `docs/prompts/kich-ban-short.md`, **chỉ từ dữ kiện trong kho**; chạy lại `kiem-chung-nguon` trên kịch bản.
  6. `gop-y-kich-ban` – góp ý kể chuyện (móc, liền mạch, dễ hiểu, chi tiết, cao trào, kết) bằng subagent, trước khi tạo giọng.
  5. Viết kịch bản bằng skill **`bien-kich`**: **video dài trước** (10–15 phút, chia khối 45–75s, mỗi khối cắt được thành Short), **chỉ từ dữ kiện trong kho**, mỗi câu gắn mã kho → `docs/videos/`; chạy lại `kiem-chung-nguon` trên kịch bản. (`docs/prompts/kich-ban-short.md` là prompt Short cũ.)
- Truyền thuyết/niên đại tranh luận: kể kèm "tương truyền", "theo sử cũ chép".
- Bản đồ: ghi "minh họa, ranh giới gần đúng" nếu chưa có nguồn atlas; bản đồ Việt Nam toàn cảnh hiện đại luôn có Hoàng Sa, Trường Sa; không dùng hình dạng chữ S hiện đại cho thời kỳ xưa.
- Không sao chép bản đồ/hình của kênh khác (Sử Lược, EZ Sử…), không dùng hình đối thủ, không giả giọng người thật.
- YouTube: bật khai báo nội dung AI khi có cảnh/người trông như thật; tránh nội dung rập khuôn hàng loạt (rủi ro tắt kiếm tiền). Nhạc chỉ từ YouTube Audio Library / thư viện CapCut.

## 6. Trạng thái
- ✅ **CHỐT CHUẨN (17/11/2026, người dùng chọn):** bộ công cụ **`scripts/video/`** (video dài `dung.py` + Short cắt từ video dài `short.py`, khung gần full, thumbnail `thumb_video.py` mũi tên/X) là **chuẩn duy nhất**. Short P1 chuẩn = **"Một hàng cọc gỗ đánh chìm cả hạm đội? | Bạch Đằng 938 – Phần 1"**. Kho E2 chuẩn: `kb/E2-bach-dang-938.md` (bản 16/11).
- 🗄️ **Bản cũ – KHÔNG dùng nữa** (nhánh `awesome-tesla`, gộp 17/11 chỉ để lưu): `scripts/khoi/`, Short P1 "Một vị Giao vương chưa từng có đất Giao" (đã hẹn đăng 15/11 → **người dùng cần hủy lịch/xóa trên YouTube Studio** trước khi đăng P1 chuẩn), thumbnail "bản khắc cổ", kho `kb/E2-bach-dang-938.ban-15-11.md` (chỉ để đối chiếu). Các mục bên dưới nói về khối/Vbee/`scripts/khoi` là lịch sử, không làm theo.
- **Short #1 – Bạch Đằng 938:** `docs/shorts/01-bach-dang-938.md` (kịch bản, prompt Flow 8 cảnh, các bước CapCut, tiêu đề, bảng nguồn sơ bộ). Bản nháp có giọng: `assets/short1/Short1-BachDang938-co-giong.mp4` (hình vẽ tạm, chưa nhạc, giọng Vbee). Lời đọc chia câu: `docs/shorts/01-loi-doc.txt`. Chưa tạo giọng Gia Huy cho bài này → chạy skill `giong-doc`. Mẫu thử giọng: `assets/short1/thu-giong/`. Kho: **🔍 sơ bộ, chưa kiểm chứng**.
- **Short #1 – Bạch Đằng 938:** `docs/shorts/01-bach-dang-938.md` **bản 2** (viết lại từ kho, đã qua kiểm chứng kịch bản). Kho: **`kb/E2-bach-dang-938.md` ✅** (hồ sơ mẫu đầu tiên, 15/11/2026). Giọng và bản dựng cũ trong `assets/short1/` làm theo bản 1, **cần tạo lại giọng Vbee**. "Lùi tiếp: năm 544" chờ hồ sơ E3.
- **Video dài E2 – Bạch Đằng 938:** `docs/videos/E2-bach-dang-938.md` (12 khối ≈ 13–14 phút, mỗi khối cắt được Short; đã qua kiểm chứng: **Đạt**). Kho dùng: `kb/E2-…` + `kb/E2b-boi-canh-905-937.md`. Khối 12 phần "Lùi tiếp: 544" ⏳ chờ hồ sơ E3.
- **✅ P1 ĐÃ HẸN ĐĂNG (15/11/2026, YouTube Shorts):** "Một vị Giao vương chưa từng có đất Giao | Bạch Đằng 938 · P1" – file `assets/e2/E2-K1-bando-v3.mp4`, thumbnail `assets/e2/thumb-P1.jpg`. Cài đặt: Education/Concept overview, không dành cho trẻ em, không giới hạn tuổi, Altered content = Yes, 10 hashtag + tags ẩn (không dấu #). Việc tiếp: đăng lại TikTok/Reels; đo sau 48h (views, % xem vs vuốt, sub mới); làm P2 (họ Khúc); khi có P2 gắn Related video P1→P2.
- **THUMBNAIL: kiểu "bản khắc cổ"** (chủ kênh chốt 15/11): chân dung AI qua bộ lọc nét mực gạch chéo trên giấy dó (`scripts/khoi/khac.py`) + nền bản đồ tối + chữ lớn + nhãn Pn đỏ + "BẠCH ĐẰNG 938". P1: `assets/e2/thumb-P1.jpg`. Tránh để nguyên ảnh AI (mất thiện cảm).
- **PHONG CÁCH MẶC ĐỊNH: bản đồ hoạt họa chi tiết** (`scripts/khoi/scenes_map2.py`, chủ kênh chốt 15/11): vùng tô màu + dải phân cách, sông, núi, thành, cờ tướng có khung chân dung (`assets/portraits/`), nhiều nhịp hình mỗi câu; khối chỉ 2–3 sự việc (luật "ít mà sâu").
- **Short khối 1 bản 3 (ít mà sâu):** `assets/e2/E2-K1-bando-v2.mp4` (81,8s, giọng Vbee đã cắt câu quảng cáo "Giọng đọc nhân tạo từ vbee.vn" chen trước câu cuối). Lần thu sau sửa 2 câu theo kiểm chứng: "rồi đổi" → "tức đất Giao Châu… và đổi"; câu Trần Trọng Kim (xem docs/videos).
- (Cũ) **Short khối 1 bản 2, 2 phong cách để so sánh:** `assets/e2/E2-K1-slide.mp4` (chữ & đồ họa) và `assets/e2/E2-K1-bando.mp4` (bản đồ hoạt họa, `--style map`), 61s, đã cắt đuôi "vbee.vn" (`vbee_trim_end`), **chưa nhạc**. Thumbnail `assets/e2/thumb-P1.jpg`; tiêu đề P1–P12: `docs/videos/E2-tieu-de-thumbnail.md`. Dựng bằng `scripts/khoi/render.py` + `scripts/khoi/e2_k1.json` (xem README; có chế độ `--vbee` tự cắt MP3 theo khoảng lặng). Lời cho Vbee: `assets/e2/E2-K1-loi-doc-vbee.txt`.
- Mẫu kỹ thuật đã làm: `bando-dong-…` (bản đồ phẳng), `sabandong-…` (sa bàn), `bandoco-NgoQuyen-…` (bản đồ cổ + cờ tướng, dấu X khi thắng).
- Checklist "Short đầu tiên" (23 việc): **đã xong 13** – chọn kênh, tên, tạo kênh, avatar/banner, mô tả, xác minh SĐT, prompt kịch bản, chọn giọng, chọn chủ đề, viết kịch bản, kiểm tra sơ bộ, tạo giọng. **Còn:** chốt persona (tên người kể), chọn cách làm hình, template CapCut 9:16, tạo 8 hình Flow, dựng, xem lại trên điện thoại, tiêu đề/mô tả, cài đặt khi đăng, đăng, đăng lại TikTok/Reels, đo chỉ số sau 48h.
- **Phong cách video dài (16:9) đã chốt 16/11:** `docs/plan/phong-cach-video-dai.md`. Gồm tĩnh là mặc định, bản đồ 2 tầng, kể chi tiết có nguồn, và **thư viện 12 hiệu ứng H1–H12 đã duyệt**. Code ở `scripts/hieuung/demo.py` (mỗi hiệu ứng một hàm, render nháp 540p, cache theo clip; `--final` cho 1080p), demo ở `assets/hieuung/demo-hieuung-nhap.mp4`. Người dùng muốn sửa hiệu ứng nào sẽ gọi theo mã (vd "H3 …").
- **Video dài E2 – Bạch Đằng 938:** kho ✅ `kb/E2-bach-dang-938.md`; kịch bản `docs/long/E2-bach-dang-938.md`; lời đọc `docs/videos/E2-loi-doc.txt`; cảnh `scripts/video/tap/e2.py`; giọng `assets/e2/E2-GiaHuy.*`. Bản cuối 1080p60 render bằng `dung.py e2 … --final --fps60`.
- Kế hoạch test (sau khi có vài video): so sánh bằng **trung vị view**, % xem hết, sub/1.000 view; đánh giá sau 8–10 video.

- **Short cắt từ video dài E2 (17/11/2026):** 6 phần 1–2 phút, cấu hình ở `SHORTS` trong `scripts/video/tap/e2.py`, dựng bằng `python3 scripts/video/short.py e2 <n|a-b|a,b>` → `build/short/e2-p<n>/SHORT-E2-P<n>.mp4` + `THUMB-E2-P<n>.jpg` (có thanh tiến độ `build/short/tien-do.txt`).
  - **Khung đã chốt "gần full":** cắt 700px của video 16:9 → 1080×1666 đặt ở **y=294** (từ P2, 17/11: dải tên + khung nền hạ 40px – `BAND_DY` trong `short.py`; P1 đã đăng dùng y=254), dải tên "BẠCH ĐẰNG 938 · PHẦN n" phía trên, **không phụ đề**, khung **tự lia theo cờ chân dung** (`track_flags` trong `short.py`).
  - Cấu trúc: hook = thumbnail + câu hỏi (giọng Gia Huy) → đoạn cắt → "Xem tiếp phần n+1 / bản đầy đủ trên kênh Song Tử Kể Sử" → màn đăng ký.
  - **Thumbnail đã chốt (P1):** phong cách mộc mạc như video – lấy chính cảnh trong video vẽ lại 4K, thêm **mũi tên nét đứt đỏ + dấu X** chỉ vào chi tiết chính, dải mực trên (chữ kem, dòng 2 vàng đồng, gạch đỏ), chân "PHẦN n · BẠCH ĐẰNG 938" + avatar. **Vùng an toàn Shorts (17/11, từ P2):** chữ tiêu đề hạ 50px (`HEAD_Y=140`, cũ 90), dải chân hạ 30px (`FOOT_DY=30`) để nút/chữ YouTube không che. P2–P6: `mark="ring"` (khoanh tròn) khi chi tiết không phải thất bại, `a0/a1` = điểm mũi tên. Code `scripts/video/thumb_video.py` (bảng `CFG`; `thumb.py` tự gọi khi phần có trong CFG). Người dùng KHÔNG thích kiểu vẽ màu mè/gradient/"trông như AI" (bản cũ trong `thumb.py`).
  - **Bố cục thumbnail v2 (17/11, từ P2):** trên cùng dải "BẠCH ĐẰNG 938 + PHẦN n" giống dải trong video, câu hook trong hộp ở dưới (`HOOK_Y=1530`), **không mũi tên** (rối mắt), chỉ dấu X hoặc vòng tròn (`mark='ring'`); không dải chân. `LAYOUT='v2'` trong `thumb_video.py`.
  - **Cảnh 16:9 bị xén khi cắt dọc** (khung trích dẫn `quote`, cảnh nhiều sa bàn) → `short.py` tự vẽ lại bản dọc và phủ lên (`quote_doc`, `doc_layers`); cảnh đặc biệt khai báo `SHORT_DOC` trong `tap/<mã>.py` (vd `s47` 3 sa bàn xếp dọc). Rà soát mỗi Short bằng ảnh ghép khung hình mỗi 3 giây trước khi gửi duyệt.
  - Trạng thái: **P1 xong theo khung mới** (người dùng đang đăng). **P2–P6 chưa dựng lại** khung mới; cần làm thumbnail P2–P6 theo kiểu P1 (thêm vào `CFG`) rồi `short.py e2 2-6`.
  - Thông tin đăng Short P1: `docs/videos/E2-dang-youtube.md`. Lịch: video dài T3/T5/T7 18:00, Short các ngày còn lại 18:00, chỉ lên lịch.

## 7. Việc tiếp theo (đề xuất theo thứ tự)
- **(17/11) ĐANG CHẠY: thử nghiệm 30 ngày 18/11–17/12/2026** – `docs/plan/thu-nghiem-30-ngay.md`. Video dài #1 chỉ ~7 view → ưu tiên: Short mỗi ngày (YT + TikTok + Reels) kéo về kênh, từ khóa lên đầu tiêu đề (đề xuất thay công thức tên đã chốt – chờ người dùng duyệt), mô tả có từ khóa + mục lục, thumbnail đọc được ở cỡ nhỏ, kịch bản đổi góc cho chủ đề quen. Nhịp 1 video dài/tuần. Ghi số 48h/7 ngày vào `docs/plan/theo-doi-30-ngay.csv`.
0. (17/11) Hủy lịch Short P1 cũ "Một vị Giao vương…" trên YouTube Studio → đăng Short E2 P1 chuẩn bằng skill `dang-youtube` (Claude in Chrome, máy local). Làm thumbnail P2–P6 theo mẫu P1 → dựng lại P2–P6 khung gần full → người dùng duyệt → lên lịch.
1. ~~Quy trình nguồn E2~~ (xong 15/11). Tiếp: tạo lại giọng Vbee cho Short #1 bản 2; chạy quy trình nguồn E3 (544) hoặc E1 (968).
2. Làm mẫu **đồng hồ năm chạy ngược + bản đồ co dần** (4 giây) trên nền bản đồ cổ.
3. Đóng gói code thành bộ công cụ: thư viện hình (thuyền, cọc, cờ tướng, thành, mũi tên), bản đồ theo thời kỳ, khung phụ đề, end card; mỗi tập một file cấu hình (YAML/JSON) mô tả cảnh → render.
4. Tạo 8 hình Flow theo style sơn mài, thay vào Short #1, thêm nhạc, đăng.

## 8. Cấu trúc thư mục
```
CLAUDE.md                     ← file này
.claude/skills/               ← 11 agent: nguon-lich-su, kiem-chung-nguon, kho-tri-thuc, bien-kich, gop-y-kich-ban, giong-doc (giọng + âm thanh), dung-video (dựng video từ bộ công cụ), dang-youtube (lên lịch đăng qua Claude in Chrome), dong-bo (đồng bộ cloud ↔ máy), project-checklist, vn-ai-channel-research
docs/research/01–04           ← research kênh AI VN, YouTube, audio, format slideshow
docs/plan/series-nguoc-dong.md← 38 mốc + cấu trúc tập
docs/prompts/kich-ban-short.md← prompt kịch bản
docs/shorts/01-bach-dang-938.md
docs/videos/                  ← kịch bản video dài (chia khối → Short)
kb/                           ← kho tri thức (INDEX, nguon, draft/, nhan-vat/, dia-danh/)
scripts/video/                ← BỘ CÔNG CỤ DỰNG VIDEO cả series: dung.py (bộ máy) + tap/<mã>.py (cảnh từng tập) + bando_vung.py, bando_tran.py, nhanvat.py, amthanh.py – xem skill dung-video
scripts/voice/tts.py          ← tạo giọng ZeroTTS (mặc định Gia Huy) + kiểm tra Whisper + mốc thời gian từng câu
scripts/khoi/                 ← (CŨ, không dùng – lưu lại từ nhánh awesome-tesla) dựng khối Short từ JSON
scripts/short/                ← dựng Short từ ảnh + phụ đề + giọng (scenes.py → caps.py → render.py)
scripts/bando/anim.py         ← bản đồ phẳng động
scripts/saban/sim.py          ← sa bàn mặt cắt
scripts/bandoco/              ← bản đồ cổ: build.py (nền) → animate.py (cờ, cọc, X, camera)
data/                         ← ranh giới VN/TQ/Lào/CPC từ Natural Earth (world-atlas), script trích xuất node
fonts/                        ← Playfair Display, Be Vietnam Pro (OFL, đã gộp latin+vietnamese)
assets/brand/                 ← avatar, banner, watermark, canvas thiết kế (.dc.html)
assets/short1/                ← giọng đọc + các video mẫu
```

## 9. Môi trường kỹ thuật
- Python: `pip install cairosvg pillow numpy shapely fonttools brotli`; **ffmpeg**; Node: `npm i world-atlas@2 topojson-client@3` (chạy `data/ext.js`, `data/ext2.js` để tạo lại `vn.json`, `region.json`).
- Cài font: copy `fonts/*.ttf` vào thư mục font hệ thống (`~/.fonts` hoặc `~/Library/Fonts`) rồi `fc-cache -f` (Linux).
- **Script là bản mẫu viết nhanh trong chat**: đường dẫn dữ liệu đã đổi sang tương đối (`data/`, `fonts/`) nhưng thư mục làm việc/đầu ra (`png/`, `clips/`, `frames/`) cần chạy từ đúng thư mục hoặc chỉnh lại. Nên refactor thành một package có CLI khi làm bộ công cụ (việc 7.3).
- Video: 1080×1920, 30fps, H.264 `-crf 20 -preset veryfast`, mỗi cảnh một file rồi nối bằng concat; ghép giọng bằng `-c:v copy`.
- Giọng đọc: `pip install zerotts faster-whisper`, `export HF_HUB_DISABLE_XET=1`, rồi `python scripts/voice/tts.py <loi-doc.txt> -o <out> --check` (xem skill `giong-doc`); file `.json` đi kèm cho mốc thời gian từng câu. Dự phòng Vbee: studio.vbee.vn, căn cảnh bằng `ffmpeg -af silencedetect=noise=-35dB:d=0.25`.
- **Mạng (cloud):** session dùng môi trường `nguoc-dong-lich-su` (cho phép wikisource, wikipedia, vjol, nhandan…). WebFetch bị lỗi DNS trong môi trường này → đọc nguồn bằng `curl` (Wikimedia: `index.php?title=…&action=raw` hoặc `&action=render`, UA `research-client/1.0`, nghỉ ≥5s giữa request). Host mới phải thêm vào môi trường trước.
- Giọng đọc Vbee: tạo trên studio.vbee.vn, tải MP3 về rồi đặt vào `assets/`; căn cảnh theo khoảng lặng (`ffmpeg -af silencedetect=noise=-35dB:d=0.25`).
