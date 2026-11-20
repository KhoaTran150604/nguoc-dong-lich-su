# Thử nghiệm hoạt họa 2D – nhật ký phiên 17–18/11/2026

Tóm tắt cuộc trao đổi về làm cảnh hoạt họa 2D (nhân vật cử động) cho kênh Song Tử Kể Sử, để phiên sau (kể cả khi đổi model) làm tiếp đúng hướng.

## 1. Kết luận đã chốt (người dùng duyệt)
- **Nhân vật hoạt họa do code tự vẽ.** Người dùng chấm khoảng **6–7/10**. Chấp nhận không đẹp bằng ảnh Google Flow vì **cử động không vỡ, không hở khớp**, đây là ưu tiên số 1.
- **Ảnh Google Flow chỉ làm mẫu tham khảo** (trang phục, màu, dáng). Không cắt ảnh Flow ra làm rối giấy: cách này đã thử và bị hở khớp ở vai.
- Gương mặt cận cảnh do code vẽ trông hơi "mặt nạ", cổ cứng. Có thể cải thiện dần, không chặn việc làm tiếp.
- Bản chất một cảnh hoạt họa có **2 phần**: (1) hình nhân vật, (2) chuyển động. Phần chuyển động luôn do code làm.

## 2. Các bản đã làm (file ở `scripts/hoathinh/`, video ở `build/thu-hoathinh/`)
| Bản | Script | Video | Nội dung | Nhận xét |
|---|---|---|---|---|
| 1 | `thu_danh_nhau.py` | `thu-danh-nhau-nhap.mp4` (540p) | Lính Việt đánh lính Nam Hán trên bãi bùn Bạch Đằng, chiều tà, 10s | Kiểu rối cắt giấy, đầu to, đơn giản |
| 2 | `thu_danh_nhau_v2.py` | `v2/thu-danh-nhau-1080p.mp4` | Vẽ lại nhân vật theo mẫu Ngô Quyền của Flow: tỉ lệ thật hơn, viền đậm, giáp vảy; Ngô Quyền hàng đầu | Đúng màu và trang phục, vẫn là hình khối |
| 3 | `thu_danh_nhau_v3.py` | `v3/thu-danh-nhau-1080p.mp4` | Ngô Quyền = rối giấy cắt từ ảnh Flow chữ T (tách nền, khớp vai và khuỷu, kiếm) | Đẹp như ảnh nhưng hở khớp vai (đã vá bằng "nắp vai"), chân đứng yên, kiếm trong vỏ → **không theo hướng này** |
| Cận cảnh | `ngo_quyen_can_canh.py` | `can-canh/ngo-quyen-can-canh.mp4` + `so-sanh-code-vs-flow.jpg` | Ngô Quyền nửa người "code vẽ hết mức": spline, bóng nhiều tầng, viền dày mỏng, giáp vảy có đinh, nền trống đồng xoay, chim Lạc; thở, chớp mắt, hét lệnh, lông mũ bay | Giáp và mũ đẹp; mặt kém ảnh Flow → người dùng chốt hướng code vẽ |
| Trận sông | `thuyen_bach_dang.py` | `thuyen/thuyen-bach-dang.mp4` | Trận trên sông Bạch Đằng 10s: thuyền nhẹ ta lao vào, bắn tên, rồi rút (giả thua); triều rút, cọc bịt sắt lộ; thuyền lớn Nam Hán đâm cọc, khựng, nghiêng. Ngô Quyền (bản cận cảnh thu nhỏ) đứng mũi thuyền gần máy quay, hét lệnh | Bám dữ kiện kho F17–F20; không vẽ tên lửa đốt thuyền (sử không chép) |

Ảnh mẫu Flow đã lưu: `assets/portraits/ngo-quyen-flow-dung.png` (đứng), `assets/portraits/ngo-quyen-flow-tpose.png` (chữ T).

## 3. Kỹ thuật cần nhớ
- **Máy local không có ffmpeg** → ghép ảnh thành MP4 bằng `swift scripts/hoathinh/anh2mp4.swift <thư mục ảnh> <fps> <out.mp4>` (AVFoundation, 16 Mbps).
- Render song song bằng `multiprocessing.Pool` (máy 16 lõi). Thời gian ước tính: bản 1 nháp khoảng 2 phút; cận cảnh 8s 1080p khoảng 1–2 phút; trận sông 10s 1080p khoảng 5–6 phút (mỗi khung khoảng 15s đơn luồng).
- Mỗi script có `--khung <giây>` để xuất khung thử trước khi dựng cả video. Luôn soát bằng ảnh ghép khung hình.
- `ngo_quyen_can_canh.py` là "bộ vẽ nét mịn" dùng lại được: `cr()` (spline), `shape()` (tô + bóng/sáng tự động + chi tiết cắt theo mảng + viền mực dày phía khuất sáng), `stroke()` (nét thon), `scales_grid()` (giáp vảy). Vẽ siêu mẫu `SS=2` rồi thu nhỏ.
  - Lỗi đã gặp: `ImageDraw` vẽ màu bán trong suốt lên RGBA sẽ **ghi đè** alpha, không trộn → phải vẽ lên lớp riêng rồi `alpha_composite` (đã sửa trong `shape()`).
- Ngô Quyền cận cảnh dùng lại trong cảnh khác: `nq_layer(t)` trong `thuyen_bach_dang.py` (render lớp cận cảnh, cắt `NQ_BOX`, thu nhỏ và ám màu nắng chiều).
- Lính trên thuyền: lớp `Crew` (kế thừa `Char2` của bản 2): `rower=True` dùng giáo làm mái chèo; `tilt` nghiêng theo thuyền.

## 4. Kiến thức đã giải thích cho người dùng (để không phải giải thích lại)
- Inkscape (miễn phí) và Illustrator (trả phí, "chuẩn ngành" vì Adobe phổ biến, đi kèm After Effects) là phần mềm vẽ vector bằng tay. Phần mềm không tự làm hình đẹp hơn, cái đẹp đến từ người vẽ.
- Thang công cụ hoạt họa 2D: Toon Boom Harmony (studio) → Illustrator + After Effects (kênh YouTube chuyên nghiệp) → Moho / Cartoon Animator (làm một mình) → Blender, OpenToonz, Synfig (miễn phí) → code (cách kênh đang làm) → AI video (Flow/Veo).
- Google Flow = labs.google/flow (làm phim AI, có mục Characters để giữ nhân vật nhất quán, mô hình ảnh Nano Banana). Google AI Studio = sân chơi cho lập trình viên, khác Flow.
- Giới hạn của code vẽ: hình hữu cơ (mặt, tay, nếp vải) khó; tốn công cho mỗi chi tiết; mỗi góc nhìn là một bản vẽ riêng; không làm được kiểu tranh cọ hay chân thực. Thế mạnh: khớp không hở, biến dạng, biểu cảm, nhân bản, nhất quán.

## 5. Việc có thể làm tiếp
- Đóng gói **bộ nhân vật dùng lại**: Ngô Quyền, lính Việt, lính Nam Hán, tướng Nam Hán, mỗi nhân vật có tư thế và biểu cảm, vẽ được cận cảnh lẫn toàn cảnh.
- Trận sông: kéo dài để thuyền giặc **lật đắm** (F20), thêm tay Ngô Quyền giơ kiếm chỉ hướng.
- Sửa mặt cận cảnh (bớt "mặt nạ", cổ mềm hơn).
- Chưa có giọng đọc và nhạc cho các cảnh thử. Chưa commit các file trong `scripts/hoathinh/`.
