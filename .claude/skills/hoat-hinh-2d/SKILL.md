---
name: hoat-hinh-2d
description: Làm cảnh hoạt hình 2D chibi (Anh Văn – Em Võ, Ngô Quyền, lính, thuyền) bằng code tự vẽ – đối thoại có giọng hai nhân vật + khẩu hình, kết hợp 3 phong cách đã chọn (S2 sách sử, S3 bản đồ, S1 sitcom bờ sông), nhạc nền và tiếng động tự tổng hợp. Dùng khi người dùng muốn video/Short hoạt hình nhân vật, sửa nhân vật, thêm phong cách, hoặc làm tiếp series sau Bạch Đằng 938.
---

# Agent Hoạt hình 2D (code tự vẽ)

Trả lời tiếng Việt, ngắn gọn, giải thích đơn giản (người dùng không chuyên đồ họa – thích bảng so sánh + video thử thật).

## ⭐⭐ ĐỌC TRƯỚC KHI VẼ (18/11/2026 tối): LỐI VẼ SITCOM VN + LINH VẬT GÂU NGHỆ
- **Sổ tay phong cách** (học từ ~270 khung hình / 11 tập Thỏ Bảy Màu – chỉ học lối vẽ): `docs/plan/hoc-phong-cach-sitcom-vn.md` – nét, màu, ánh sáng, bố cục, checklist 6 điểm, **mục 7: 14 quy tắc mới N1–N14** (đêm đổi bảng màu xanh, bóng lưỡi liềm, vết nứt tường, letterbox cảnh trận, đám đông bóng đơn sắc, cỡ cảnh insert…) + **mục 8: N15–N30** (núi xa nhiều lớp phẳng, tuyết, dưới nước, đêm ấm đèn dầu, đèn rọi, khung trong khung, đạo cụ lệch thời đại, tiền cảnh che góc, nhà Tết/nhà cổ/rừng tre, khói phẳng) + danh sách việc code. Làm theo sổ tay này cho mọi cảnh mới.
- Tóm tắt: **viền nhân vật đen đậm đều, viền nền mảnh hơn; tô phẳng + 1 mảng bóng cel mép cứng; bóng đổ vật lên vật + bóng chân; nền là cảnh thật nhiều chi tiết đời thường Việt; nhân vật nhỏ trong khung; KHÔNG gradient/blur/glow** (người dùng chê "nhìn rất giả").
- **Linh vật mới: Gâu Nghệ** (Border Collie đen trắng, tai lệch, khung người Anh Văn, không mặc đồ) – `scripts/hoathinh/gau_nghe_van.py`, dùng `st['flat']=True`. Mẫu cảnh: `gau_nghe_avatar_cafe.py` (sân thượng, cà phê sữa đá), `gau_nghe_avatar_tbm.py` (bến sông).
- **Bộ hiệu ứng + đạo cụ** `scripts/hoathinh/sitcom_fx.py`: `tint_night`, `dusk`, `rain`, `letterbox`, `crack`, `tile_floor`, `crowd`, `coconut`, `cau_tre`, `insert_stake` (mục 7.3) + đợt 3: `layers_far`, `snow_*`, `sun_rays`, `underwater`, `tint_warm_night`, `spotlight`, `tv_frame`, `smoke`, `bamboo_grove`, `lattice_door`, `mai_bonsai`, `tea_set`… (mục 8.3, demo `--dot3`).
- **Cảnh nhiều nhân vật** (sổ tay mục 9, M1–M14): hàng ngang cao thấp khác nhau + chồng lấn, mọi ánh mắt về người nói, 3 tầng (lưng tiền cảnh – người nói – đám đông). Dàn phụ thử: `scripts/hoathinh/to_doi.py` (Mít, Mướp, Sào, Đậu – hàm `side(cv, key, x, gy, k, look=)`, `back_head()`) → `build/thu-hoathinh/to-doi/bang-to-doi.jpg`.
- **Học phim mẫu:** chụp **6 giây/khung** cả tập, xem TẮT TIẾNG (người dùng yêu cầu); ghép 4 khung/ảnh bằng canvas trong trang để xem nhanh.
- Thân + tay + chân vẽ bằng `blob` (một viền liền) – người dùng rất ghét tay lệch khỏi người.

## ⭐ CHUẨN (18/11/2026, người dùng duyệt "đẹp, ưng"): SITCOM NỀN CHI TIẾT
- **Mẫu chuẩn:** `scripts/hoathinh/sitcom_20s.py` → `build/thu-hoathinh/sitcom-20s/sitcom-20s-van-vo.mp4` (21s, Võ khoe cắm cọc lúc nước lên – Văn "Sử chép rằng…" – triều rút – cọc trôi mất).
- **Ngôn ngữ hình** (chỉ học phong cách sitcom hoạt hình VN, KHÔNG vẽ nhân vật kênh khác dù người dùng nhờ – đã từ chối vẽ Thỏ Bảy Màu, dùng Văn – Võ):
  - Nhân vật **nhỏ, đơn giản** (toàn cảnh `SC=0.85`); **nền vẽ thật chi tiết**: đồ vật cũ, thớ gỗ, đinh, vết vá, chum, rổ, lau sậy, tre, chuối (`scripts/hoathinh/ben_song.py`).
  - **Ánh sáng**: tách lớp nền + lớp nhân vật → `anhsang.ap_dung(nền, nhân vật, 'diu')` (bóng đổ, viền nắng, 3 tông); đồ vật nền "nướng" bóng bằng `noi_khoi`. Thêm bóng mềm dưới chân.
  - **Màu dịu** (người dùng chê bản đầu "sáng quá"): preset `'diu'` = **chiều dịu**, mặc định. Các kiểu khác để dùng theo cảnh: `thu_anh_sang.py` (B sớm sương, C trưa nắng, D hoàng hôn, E xế chiều trầm, F đêm trăng + đèn lồng) – bảng `build/thu-hoathinh/sitcom-20s/anh-sang/bang-anh-sang.jpg`.
  - **Nhịp hài**: toàn → cận người nói → cận phản ứng → thẻ chữ bật → zoom giật + rung vào mặt ngơ ngác → lùi ra lộ câu chốt; gài chi tiết hài ở hậu cảnh (cọc trôi); hiệu ứng `sweat`, `qmarks`, `shock_lines`, `sparkles`; nhạc vui dừng "rẹt" ở cú sốc, kết kèn buồn.
  - Dữ kiện sử chỉ ở lời Anh Văn + thẻ "Sử chép" (mã kho); tình huống hài của Võ là hư cấu của người dẫn.
- **Máy Windows:** `pip install --user pillow numpy scipy soundfile imageio-ffmpeg zerotts faster-whisper`; luôn đặt `PYTHONUTF8=1` (lỗi đọc JSON tiếng Việt); ffmpeg lấy từ `imageio_ffmpeg`; khung tạm để ngoài Google Drive (`tempfile`). Giọng: `PYTHONUTF8=1 HF_HUB_DISABLE_XET=1 python scripts/hoathinh/thoai_song_tu.py <loi.json>`.

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
