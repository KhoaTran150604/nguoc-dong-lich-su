---
name: giong-doc
description: Làm âm thanh cho video của kênh – tạo giọng đọc bằng ZeroTTS (giọng mặc định Gia Huy, chạy local, miễn phí), tự kiểm tra phát âm, xuất mốc thời gian từng câu, rồi ghép giọng + nhạc nền vào video. Dùng khi kịch bản đã qua kiem-chung-nguon hoặc khi video đã dựng xong cần lồng tiếng.
---

# Agent Giọng đọc & âm thanh

Vai trò: biến kịch bản đã kiểm chứng thành giọng đọc, rồi lồng giọng (và nhạc) vào video. Trả lời bằng tiếng Việt.

## Giọng kênh (đã chốt 16/11/2026)
- **Gia Huy (`giahuy`), nguyên bản**: không trộn, không làm ấm, `cfg 1.0`, tốc độ 1.0. Đây là mặc định của `scripts/voice/tts.py`, **không cần truyền tham số**.
- Người dùng đã nghe so với Vbee Anh Khôi, Hữu Đức và các bản trộn/làm ấm, rồi chọn Gia Huy nguyên bản. Không tự đổi giọng hay thêm xử lý nếu người dùng không yêu cầu.
- Không clone giọng Vbee hay giọng người thật (quy tắc kênh).
- Dự phòng: Vbee "Anh Khôi nâng cao" (studio.vbee.vn) cho câu ZeroTTS đọc mãi không đúng.

## Cài đặt (một lần mỗi máy/phiên)
```bash
pip install zerotts faster-whisper
export HF_HUB_DISABLE_XET=1   # proxy/mạng chặn Xet → tải weights qua HTTP thường (~900 MB lần đầu)
```

## Quy trình

### Bước 1: File lời đọc
Tạo `docs/shorts/NN-loi-doc.txt` (video dài thì dùng `docs/videos/NN-loi-doc.txt`) từ kịch bản **đã kiểm chứng**:
- **Mỗi dòng = một câu phụ đề** (≤ 2 dòng phụ đề, ~28 ký tự/dòng).
- Dòng trống = hết đoạn (nghỉ 0,6 s). Dòng bắt đầu bằng `#` là ghi chú, không đọc.
- Giữ nguyên chữ của kịch bản. Số năm viết bằng số, tool tự đọc thành chữ ("938" → "chín trăm ba mươi tám").
- Tên riêng khó đọc ở đầu câu ("Ngô Quyền…") thì có thể đệm từ dẫn ("Khi ấy, Ngô Quyền…"), **không đổi nghĩa**.

### Bước 2: Tạo giọng
```bash
python scripts/voice/tts.py docs/shorts/NN-loi-doc.txt -o assets/shortN/voice-GiaHuy --check
```
Đầu ra:
- `voice-GiaHuy.mp3`: giọng đọc, chuẩn hoá −16 LUFS.
- `voice-GiaHuy.json`: `start`/`end` từng câu, điểm, chữ Whisper nghe được → **dùng để đặt thời lượng phụ đề và cảnh**, không phải căn tay.

Thời gian: Short ~50 s mất ~1 phút (không `--check`), ~5–8 phút (có `--check`). Video 10–20 phút nên chạy nền.

### Bước 3: Người dùng nghe duyệt
- Báo các câu "XEM" ở cuối log. **Gửi file mp3 cho người dùng nghe**: Claude không nghe được, còn Whisper có thể nghe nhầm.
- Câu sai thật: đọc lại riêng câu đó bằng `--retake 5,15` (giữ nguyên các câu khác), hoặc sửa câu ở Bước 1.

### Bước 4: Ghép vào video
Video đã dựng (không tiếng) + giọng:
```bash
ffmpeg -i video.mp4 -i voice-GiaHuy.mp3 -map 0:v -map 1:a -c:v copy -c:a aac -b:a 192k -shortest out.mp4
```
Có nhạc nền (chỉ nhạc YouTube Audio Library / thư viện CapCut). Nhạc nhỏ ~15% và tự hạ khi có giọng:
```bash
ffmpeg -i video.mp4 -i voice-GiaHuy.mp3 -stream_loop -1 -i nhac.mp3 -filter_complex \
 "[1:a]asplit=2[v1][v2];[2:a]volume=0.15[m];[m][v1]sidechaincompress=threshold=0.03:ratio=6:attack=20:release=400[duck];[duck][v2]amix=inputs=2:duration=shortest:normalize=0,afade=t=out:st=END-1.5:d=1.5[a]" \
 -map 0:v -map "[a]" -c:v copy -c:a aac -b:a 192k -shortest out.mp4
```
(Thay `END-1.5` bằng số giây cụ thể: lấy `duration` trong `.json` trừ 1,5.)

Kiểm tra cuối: `ffmpeg -i out.mp4 -af ebur128 -f null -` → khoảng −14 đến −16 LUFS. Gửi video cho người dùng xem lại trên điện thoại.

## Tham số (chỉ dùng khi người dùng yêu cầu)
| Tham số | Mặc định | Ghi chú |
|---|---|---|
| `--voice` | giahuy | giọng nam khác: `huuduc` (lớn tuổi), `quangminh` (tin tức), `tiendat` (sôi nổi); trộn: `"giahuy:0.7+huuduc:0.3"` |
| `--cfg` | 1.0 | cao hơn = bám giọng chặt hơn, chậm gấp đôi |
| `--speed` | 1.0 | <1 chậm, >1 nhanh, giữ cao độ |
| `--warm` | 0 | làm ấm 0–1 (tăng trầm, giảm chói, chút vang) |
| `--gap` / `--para-gap` | 0.25 / 0.6 | nghỉ giữa câu / đoạn (giây) |
| `--seed` | 7 | cùng seed + cùng chữ = cùng kết quả |
| `--check` / `--tries` / `--pass-score` | tắt / 4 / 0.95 | Whisper nghe lại, đọc lại tối đa N lần khi điểm < ngưỡng |
| `--retake` | — | danh sách số câu cần đọc lại với seed khác |

## Hạn chế đã biết (test Short #1, 16/11/2026)
- ZeroTTS hay méo "Ngô Quyền" (→ "Ngu/Ngụ quyền") và "cọc" (→ "tọc"); đôi khi đọc thừa chữ cuối câu ngắn ("tiếp" → "tiếp tục").
- Whisper cũng nghe nhầm cả với giọng Vbee ("Hoằng" → "Hoàng", "giấu" → "dấu", tr/ch, d/gi/r): điểm "XEM" chỉ để khoanh vùng, **người nghe mới là người quyết**.
- Repo chỉ có 8 giọng (4 nam, 4 nữ), không ghi vùng miền. Clone giọng mới phải qua platform.zeroweight.ai (tải `.zip` → `--voice <tên>` sau khi `tts.add_voices(zip)`).
