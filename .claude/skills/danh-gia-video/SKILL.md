---
name: danh-gia-video
description: Agent chấm điểm video hoạt hình 2D Gâu Nghệ trước khi đưa người dùng xem – đo máy (cắt cảnh, nháy/giật/đứng hình, sáng, màu, âm thanh) + subagent độc lập chấm bằng mắt theo chuẩn sitcom Thỏ Bảy Màu (sổ tay N1–N30, M1–M14). Chưa đạt thì sửa → render lại → chấm lại; chỉ chốt khi vượt mốc. Dùng sau mỗi lần render video hoạt hình.
---

# Đánh giá video hoạt hình (vòng chấm → sửa → chấm lại)

**Luật cứng:** KHÔNG gửi video cho người dùng xem cho tới khi đạt mốc. Tối đa **3 vòng**; nếu vẫn chưa đạt → gửi bản điểm cao nhất kèm danh sách lỗi còn lại và nói rõ "chưa đạt".

## Bước 1 – Đo bằng máy
```bash
PYTHONUTF8=1 python -W ignore scripts/hoathinh/soat_video.py <video.mp4> --moi 1.0
```
Ra `<thư mục video>/soat/`: `bao-cao.md/.json` (cảnh báo có giây), `tong-the-NN.jpg` (16 khung/ảnh, mỗi giây 1 khung), `cat-canh.jpg` (trước/sau mỗi lần cắt).
Đọc báo cáo trước; tự xem `cat-canh.jpg` + vài ảnh tổng thể ở giây có cảnh báo.

## Bước 2 – Subagent chấm độc lập
Gọi Agent (`general-purpose`), KHÔNG kể cho nó mình đã sửa gì (để chấm khách quan). Prompt gồm:
- Đường dẫn: `soat/bao-cao.md`, mọi `soat/*.jpg`, kịch bản (`docs/videos/gau-nghe/<mã>.md`), sổ tay `docs/plan/hoc-phong-cach-sitcom-vn.md` (mục 1–9: luật N1–N30, M1–M14).
- Yêu cầu: dùng Read xem TỪNG ảnh, chấm theo thang dưới, mỗi lỗi ghi **giây + mô tả + cách sửa cụ thể** (sửa trong code nào, hàm/cảnh nào nếu đoán được), trả về JSON ở cuối:
  `{"diem": {"chuyen_dong":x,"nhan_vat":x,"khung_hinh":x,"anh_sang_mau":x,"am_thanh":x,"ke_chuyen":x}, "tong":x, "loi_chan":[...], "loi":[{"t":..,"muc":..,"mo_ta":..,"sua":..}]}`

### Thang điểm 100 (chuẩn = một tập Thỏ Bảy Màu)
| Mục | Điểm | Chấm gì |
|---|---|---|
| Chuyển động / kỹ thuật | 20 | tay/chân tách khỏi người, vật xuyên nhau, nhân vật đứng lơ lửng/chìm sàn, nháy khung, giật vị trí, đứng hình chết (không chớp mắt, không khẩu hình khi nói), đạo cụ lệch tay |
| Nhân vật | 20 | đúng model (Gâu đen trắng tai lệch, người khối liền một viền), mặt có cảm xúc hợp câu thoại, nhìn về người đang nói (M4), tương phản cỡ/hình dáng (M5–M6), Gâu nổi bật, khẩu hình khớp người nói |
| Khung hình & nhịp | 15 | cắt 3–6s (N-rules), đủ cỡ cảnh (toàn/trung/cận), 3 lớp sâu (M3), không cắt cụt đầu/chữ, chữ đọc được, bố cục không trống/không rối |
| Ánh sáng & màu | 15 | màu phẳng + bóng cứng, viền dày đều, KHÔNG gradient/blur/glow, nhân vật tách khỏi nền, đồng nhất màu giữa các cảnh |
| Âm thanh | 15 | thoại rõ, đúng người, không rè/không bị nhạc lấn, SFX đúng lúc, không lặng chết, không tiếng giật quá to |
| Kể chuyện / hài | 15 | móc 3 giây đầu, mỗi kiểu có cú chốt, hình kể được khi tắt tiếng, kết có kêu gọi |

**Lỗi chặn** (có là KHÔNG đạt, bất kể điểm): tay/thân tách rời; nhân vật mất/biến dạng hỏng; khung đen/khung lỗi; thoại sai người hoặc mất tiếng; chữ sai chính tả trên hình; crash một phần video.

### Mốc đạt
- Tổng **≥ 80/100**, **không mục nào < 60%** điểm mục, **0 lỗi chặn**, và cảnh báo máy loại `nhay_hinh`/`re_tieng`/`lang_chet` đã xử lý hoặc giải thích được (vd lặng có chủ đích ở cú sốc).

## Bước 3 – Sửa & chạy lại
1. Ghi `soat/lan-<n>.md`: điểm từng mục, lỗi, việc sẽ sửa.
2. Sửa trong code video (vd `scripts/hoathinh/cau_long_video.py`, `nguoi.py`, `gau_nghe_van.py`). Ưu tiên: lỗi chặn → mục điểm thấp nhất → lỗi dễ sửa nhiều điểm. Kiểm nhanh bằng `--khung <giây>` / `--canh` trước khi render cả bài.
3. Render lại (chạy nền), quay lại Bước 1 với **subagent MỚI** (không dùng lại agent cũ để tránh thiên vị).
4. Đạt → gửi video + bảng điểm các vòng (ngắn gọn) cho người dùng.

## Ghi chú
- Điểm máy không thay mắt: báo cáo chỉ là gợi ý chỗ cần nhìn; quyết định bằng ảnh.
- Lặng/nhạc dừng "rẹt" có chủ đích (kịch bản ghi) không bị trừ.
- Lưu điểm các vòng để thấy tiến bộ; lỗi lặp ở nhiều video → cập nhật sổ tay/skill `hoat-hinh-2d`.
