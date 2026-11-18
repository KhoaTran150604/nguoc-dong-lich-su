---
name: hoat-hinh-2d
description: Làm cảnh hoạt hình 2D chibi (Anh Văn – Em Võ, Ngô Quyền, lính, thuyền) bằng code tự vẽ – đối thoại có giọng hai nhân vật + khẩu hình, kết hợp 3 phong cách đã chọn (S2 sách sử, S3 bản đồ, S1 sitcom bờ sông), nhạc nền và tiếng động tự tổng hợp. Dùng khi người dùng muốn video/Short hoạt hình nhân vật, sửa nhân vật, thêm phong cách, hoặc làm tiếp series sau Bạch Đằng 938.
---

# Agent Hoạt hình 2D (code tự vẽ)

Trả lời tiếng Việt, ngắn gọn, giải thích đơn giản (người dùng không chuyên đồ họa – thích bảng so sánh + video thử thật).

## Đã chốt (18/11/2026)
- **Nhân vật do code tự vẽ** (Pillow + NumPy). Ảnh Google Flow chỉ làm mẫu tham khảo; KHÔNG cắt ảnh làm rối giấy (hở khớp).
- **Phong cách: lai 3 kiểu người dùng chọn** – S2 "minh họa sách sử" (bối cảnh, thẻ chữ), S3 "người tối giản trên bản đồ" (hành quân, đoàn thuyền, cọc), S1 "sitcom bờ sông" (đối thoại, cận mặt, diễn biến). Mẫu và chấm điểm: `docs/plan/mau-phong-cach-hoat-hinh.md`. Chỉ học PHONG CÁCH, không vẽ nhân vật của kênh khác (Thỏ Bảy Màu…).
- **Giọng:** Anh Văn = ZeroTTS `giahuy`, Em Võ = `tiendat`. Lời thoại chỉ dữ kiện ✅ trong `kb/` (luật kênh mục 5 CLAUDE.md), gắn mã dữ kiện.
- Nhật ký đầy đủ các bản thử: `docs/plan/hoat-hoa-2d-thu-nghiem.md`.

## Bộ code (`scripts/hoathinh/`)
| File | Vai trò |
|---|---|
| `ngo_quyen_can_canh.py` | **Bộ vẽ nét mịn dùng chung**: `cr()` spline, `shape()` tô + bóng + viền mực + chi tiết cắt theo mảng, `stroke()` nét thon, `scales_grid()` giáp vảy, `paste()`; SS=2 (vẽ gấp đôi rồi thu nhỏ). Kèm Ngô Quyền cận cảnh |
| `song_tu_doi_thoai.py` | **Nhân vật Văn – Võ** `draw_char(cv, who, x, y, s, f, t, st)` (st: arms, book, blink, gaze, bigeye, brow, bounce, lean, smile), nền bờ sông `build_bg()`, cọc `stakes()`, cận cảnh nền mờ `bg_close()`, khẩu hình theo biên độ giọng |
| `mau_phong_cach.py` | 6 mẫu phong cách S1–S6 + bản đồ chỉ bờ biển `map_bg()` (không vẽ biên giới hiện đại) |
| `video_mot_phut.py` | **Mẫu video kết hợp 3 phong cách** (đoạn A/B/C theo cột `seg` trong lời thoại), thẻ chữ bật, phụ đề, chuyển cảnh mờ chéo, nhạc ngũ cung + tiếng động tự tổng hợp, ducking |
| `thoai_song_tu.py` | Tạo giọng đối thoại từ `loi.json` `[[ai, câu, đoạn], …]`, mỗi câu thử tối đa 14 lần, Whisper chấm, giữ bản đúng nhất → `thoai.wav` + `thoai.json` (mốc câu + biên độ 30fps) |
| `thuyen_bach_dang.py` | Trận sông: thuyền lớn Nam Hán `draw_ship`, thuyền nhẹ `draw_boat`, tên, nước bắn, Ngô Quyền mũi thuyền |
| `thu_danh_nhau*.py` | Các bản thử đánh nhau trên bãi (lính `Char2`) |
| `anh2mp4.swift`, `ghep_tieng.swift` | Ghép ảnh → MP4, ghép tiếng (máy local KHÔNG có ffmpeg) |

## Môi trường (máy local)
- Vẽ: `python3` hệ thống (3.9) có Pillow, NumPy, SciPy, soundfile.
- Giọng: cần Python ≥3.10 → `~/.venvs/zerotts` (tạo: `uv venv --python 3.12 ~/.venvs/zerotts && uv pip install --python ~/.venvs/zerotts/bin/python zerotts soundfile faster-whisper`). Mô hình đã cache ở `~/.cache/huggingface`.
- Đầu ra để trong `build/thu-hoathinh/<tên>/` (không lên git).

## Quy trình làm một video mới
1. Lấy dữ kiện từ `kb/` (skill `kho-tri-thuc`), viết `build/thu-hoathinh/<tên>/loi.json` – Võ hỏi, Văn đáp "Sử chép rằng…", mỗi câu gắn đoạn A/B/C.
2. Giọng: `HF_HUB_DISABLE_XET=1 ~/.venvs/zerotts/bin/python scripts/hoathinh/thoai_song_tu.py build/thu-hoathinh/<tên>/loi.json` – đọc điểm Whisper, câu <0.9 báo người dùng nghe lại.
3. Sao chép `video_mot_phut.py` làm mẫu (đổi `DIR`, thẻ chữ, đường thuyền, đạo cụ theo tập).
4. Thử khung: `python3 -W ignore scripts/hoathinh/<file>.py --khung 5 20 35` → ghép ảnh xem trước, soát lỗi (nhãn bị che, tay chồng đạo cụ, nhân vật che vật chính).
5. Dựng đủ (chạy nền, ~3–6 phút/phút video): `python3 -W ignore scripts/hoathinh/<file>.py`.
6. Gửi video, ghi lại điểm cần nghe/duyệt.

## Lưu ý đã gặp
- `ImageDraw` vẽ màu bán trong suốt lên RGBA sẽ ghi đè alpha → vẽ lớp riêng rồi `alpha_composite` (đã xử lý trong `shape()`).
- Văn cầm sách: dùng `book=True` (hai tay đỡ mép dưới qua `arm_to`), không vẽ tay đè lên trang.
- Bản đồ thời xưa: chỉ đường bờ, ghi "minh họa"; không dùng biên giới/chữ S hiện đại.
- Việc tiếp đề xuất: thử Rhubarb Lip Sync (MIT, chế độ phonetic) cho khẩu hình; đóng gói bộ nhân vật dùng chung (lính hai phe, tướng giặc, Ngô Quyền chibi); kéo dài video đủ 1 phút.
