# Ngược Dòng Sử Việt – Bàn giao dự án

> File này tóm tắt toàn bộ những gì đã quyết định và làm trong Claude chat (14–15/11/2026), để tiếp tục trong Claude Code. Trả lời người dùng bằng **tiếng Việt**, giọng thân thiện, ngắn gọn.

## 1. Người dùng & mục tiêu
- Làm thêm ngoài giờ, khoảng **1 tiếng/ngày**. Muốn **ẩn danh**, AI làm phần lớn nội dung, người dùng định hướng.
- Kỹ năng sẵn có: **Data Analyst**.
- Mục tiêu: kênh YouTube có thu nhập (YouTube là nền tảng chính trả tiền theo view cho người ở VN; TikTok Creator Rewards không mở cho VN; Facebook chỉ mời giới hạn). RPM người xem Việt rất thấp (≈150–180 USD / 1 triệu view) → cần **video dài 10–20 phút** + nguồn thu khác (tài trợ, sản phẩm số).
- Hướng đã thử và bỏ: affiliate thuần, bán template dashboard (thị trường đã có Sapo, KiotViet…), kênh "AI + data" (để dành làm hướng phụ sau).

## 2. Kênh đã chốt
| Mục | Giá trị |
|---|---|
| Tên kênh | **Ngược Dòng Sử Việt** |
| Handle | `@nguocdongsuviet` đã có người dùng → người dùng chọn handle khác (hỏi lại để ghi) |
| Chủ đề | Lịch sử Việt Nam theo dòng thời gian, kể **lùi** từ hiện tại về quá khứ |
| Persona | Người kể giấu mặt. Giọng: **ZeroTTS – `huuduc` (Hữu Đức)** chạy local, gần giọng cũ Vbee "Anh Khôi nâng cao" (nam, lớn tuổi, kể chuyện). Vbee giữ làm dự phòng. Skill `giong-doc` |
| Nhận diện | Trống đồng Đông Sơn + bản đồ Việt Nam (có **Hoàng Sa, Trường Sa**) + vành chim Lạc bay **ngược chiều kim đồng hồ** = ngược dòng thời gian. Màu: đen mực `#14110F`, vàng đồng `#C9A24A`/`#F3D27A`, đỏ sơn mài `#B3261E`, kem `#F2E6CC`. Font: Playfair Display (tiêu đề), Be Vietnam Pro (chữ) |
| Mô tả kênh | Đã dán (có dòng công khai dùng AI cho hình & giọng) |
| Đã xong | Tạo kênh thương hiệu, xác minh SĐT, avatar, banner, watermark |

## 3. Định dạng video đã chọn (trộn 3 kiểu)
1. **Slideshow ảnh AI** (ảnh tĩnh + zoom/lia nhẹ): phần cảm xúc, con người. Ảnh tạo bằng **Google Flow** (miễn phí ~50 credit/ngày; Veo 3.1 cho vài clip ngắn mở đầu). Style chữ ký đề xuất: **tranh sơn mài**.
2. **Bản đồ cổ + cờ tướng di chuyển** (kiểu kênh Sử Lược, nhưng bản đồ của mình): diễn biến, hành quân, lãnh thổ. Code ở `scripts/bandoco/`.
3. **Sa bàn động** (mặt cắt cảnh, thuyền/nước/cọc chuyển động): giải thích "vì sao thắng". Code ở `scripts/saban/`.
- **Chữ ký mỗi tập:** 3 giây đầu là **đồng hồ năm chạy ngược + bản đồ co dần**; kết bằng "Lùi tiếp: năm …". (Chưa làm mẫu – việc tiếp theo.)
- Phụ đề: đặt thấp (~77–87% chiều cao khung 9:16), chữ 54px, tối đa 2 dòng.
- Kịch bản Short: 130–160 từ, ~45–60 giây.

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
- Truyền thuyết/niên đại tranh luận: kể kèm "tương truyền", "theo sử cũ chép".
- Bản đồ: ghi "minh họa, ranh giới gần đúng" nếu chưa có nguồn atlas; bản đồ Việt Nam toàn cảnh hiện đại luôn có Hoàng Sa, Trường Sa; không dùng hình dạng chữ S hiện đại cho thời kỳ xưa.
- Không sao chép bản đồ/hình của kênh khác (Sử Lược, EZ Sử…), không dùng hình đối thủ, không giả giọng người thật.
- YouTube: bật khai báo nội dung AI khi có cảnh/người trông như thật; tránh nội dung rập khuôn hàng loạt (rủi ro tắt kiếm tiền). Nhạc chỉ từ YouTube Audio Library / thư viện CapCut.

## 6. Trạng thái
- **Short #1 – Bạch Đằng 938:** `docs/shorts/01-bach-dang-938.md` (kịch bản, prompt Flow 8 cảnh, các bước CapCut, tiêu đề, bảng nguồn sơ bộ). Bản nháp có giọng: `assets/short1/Short1-BachDang938-co-giong.mp4` (hình vẽ tạm, chưa nhạc, giọng Vbee). Giọng ZeroTTS: `assets/short1/voice-HuuDuc.mp3` + `.json` (lời đọc: `docs/shorts/01-loi-doc.txt`) – **chờ người dùng nghe duyệt**. Kho: **🔍 sơ bộ, chưa kiểm chứng**.
- Mẫu kỹ thuật đã làm: `bando-dong-…` (bản đồ phẳng), `sabandong-…` (sa bàn), `bandoco-NgoQuyen-…` (bản đồ cổ + cờ tướng, dấu X khi thắng).
- Checklist "Short đầu tiên" (23 việc): **đã xong 13** – chọn kênh, tên, tạo kênh, avatar/banner, mô tả, xác minh SĐT, prompt kịch bản, chọn giọng, chọn chủ đề, viết kịch bản, kiểm tra sơ bộ, tạo giọng. **Còn:** chốt persona (tên người kể), chọn cách làm hình, template CapCut 9:16, tạo 8 hình Flow, dựng, xem lại trên điện thoại, tiêu đề/mô tả, cài đặt khi đăng, đăng, đăng lại TikTok/Reels, đo chỉ số sau 48h.
- Kế hoạch test (sau khi có vài video): so sánh bằng **trung vị view**, % xem hết, sub/1.000 view; đánh giá sau 8–10 video.

## 7. Việc tiếp theo (đề xuất theo thứ tự)
1. Chạy quy trình nguồn đầy đủ cho **E2 – Bạch Đằng 938** → hồ sơ mẫu đầu tiên `kb/E2-bach-dang-938.md`; sửa kịch bản Short #1 nếu cần.
2. Làm mẫu **đồng hồ năm chạy ngược + bản đồ co dần** (4 giây) trên nền bản đồ cổ.
3. Đóng gói code thành bộ công cụ: thư viện hình (thuyền, cọc, cờ tướng, thành, mũi tên), bản đồ theo thời kỳ, khung phụ đề, end card; mỗi tập một file cấu hình (YAML/JSON) mô tả cảnh → render.
4. Tạo 8 hình Flow theo style sơn mài, thay vào Short #1, thêm nhạc, đăng.

## 8. Cấu trúc thư mục
```
CLAUDE.md                     ← file này
.claude/skills/               ← 6 agent: nguon-lich-su, kiem-chung-nguon, kho-tri-thuc, giong-doc, project-checklist, vn-ai-channel-research
docs/research/01–04           ← research kênh AI VN, YouTube, audio, format slideshow
docs/plan/series-nguoc-dong.md← 38 mốc + cấu trúc tập
docs/prompts/kich-ban-short.md← prompt kịch bản
docs/shorts/01-bach-dang-938.md
kb/                           ← kho tri thức (INDEX, nguon, draft/, nhan-vat/, dia-danh/)
scripts/voice/tts.py          ← tạo giọng ZeroTTS + kiểm tra Whisper + mốc thời gian từng câu
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
