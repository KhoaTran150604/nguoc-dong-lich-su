---
name: giong-doc
description: Tạo giọng đọc cho Short/video bằng ZeroTTS chạy local (thay Vbee, miễn phí, không giới hạn), tự kiểm tra phát âm bằng Whisper và xuất mốc thời gian từng câu cho phụ đề. Dùng sau khi kịch bản đã qua kiem-chung-nguon.
---

# Agent Giọng đọc

Vai trò: biến kịch bản đã kiểm chứng thành file giọng + mốc thời gian. Trả lời bằng tiếng Việt.

## Công cụ
- `scripts/voice/tts.py` – dùng [ZeroTTS](https://github.com/zeroweight-ai/ZeroTTS) (MIT, chạy CPU, ~900 MB weights, tải lần đầu).
- Giọng kênh: **`huuduc` (Hữu Đức)** – nam, lớn tuổi, kể chuyện, trầm, điềm đạm; `cfg 2.0`. Gần "Anh Khôi nâng cao" (Vbee) nhất trong 8 giọng có sẵn (cao độ ~115 Hz so với 112 Hz).
- Không clone giọng Vbee / giọng người thật (quy tắc kênh). Muốn giọng riêng: tự thu giọng mình ≥10 giây → clone tại platform.zeroweight.ai/audio → tải `.zip` → `tts.add_voices(zip)`.

## Cài đặt (một lần)
```bash
pip install zerotts faster-whisper
export HF_HUB_DISABLE_XET=1   # proxy/mạng chặn Xet → tải weights qua HTTP thường
```

## Quy trình
1. Tạo file lời đọc `docs/shorts/NN-loi-doc.txt` từ kịch bản: **mỗi dòng = một câu phụ đề** (≤ ~2 dòng phụ đề 28 ký tự), dòng trống = hết đoạn (nghỉ 0,6 s), dòng `#` = ghi chú. Giữ đúng chữ của kịch bản đã kiểm chứng; số năm viết bằng số (tool tự đọc thành chữ).
2. Chạy:
   ```bash
   python scripts/voice/tts.py docs/shorts/NN-loi-doc.txt -o assets/shortN/voice-HuuDuc --check
   ```
   → `voice-HuuDuc.mp3` (−16 LUFS) + `voice-HuuDuc.json` (start/end từng câu, điểm, chữ Whisper nghe được).
   Short ~50 s: ~1 phút không `--check`, ~5–8 phút có `--check` (4 nhân CPU).
3. Đọc báo cáo cuối: các câu "XEM" → **người dùng nghe lại đúng các câu đó**. Câu sai thật thì:
   - `--retake 5,15` (đổi seed riêng các câu đó), hoặc
   - viết lại câu cho dễ đọc (tách câu dài, tránh tên riêng ở đầu câu: "Khi ấy, Ngô Quyền…"), không đổi nghĩa.
4. Dùng `.json` để đặt thời lượng phụ đề/cảnh (thay cho căn tay bằng `silencedetect`).

## Tham số hay dùng
| Tham số | Mặc định | Ghi chú |
|---|---|---|
| `--voice` | huuduc | `giahuy` trẻ hơn, `quangminh` rõ chữ hơn nhưng giọng tin tức |
| `--cfg` | 2.0 | 1.0 rõ chữ hơn chút nhưng giọng kém ổn định |
| `--speed` | 1.0 | 0.93–0.97 cho chậm, trầm hơn |
| `--gap` / `--para-gap` | 0.25 / 0.6 | nghỉ giữa câu / đoạn |
| `--seed` | 7 | cùng seed + cùng chữ = cùng kết quả |
| `--tries` / `--pass-score` | 4 / 0.95 | số lần đọc lại tối đa / ngưỡng đạt khi `--check` |

## Hạn chế đã biết (test 16/11/2026, Short #1)
- Độ rõ toàn bài (Whisper chấm, bỏ qua tr/ch, d/gi/r, s/x): **Vbee 0,94 – ZeroTTS 0,92**.
- Hay méo: **"Ngô Quyền"** (→ "Ngu/Ngụ quyền"), "cọc" (→ "tọc"), đôi khi thêm chữ ở cuối câu ngắn ("tiếp" → "tiếp tục").
- Whisper cũng nghe nhầm: "Hoằng" → "Hoàng", "giấu" → "dấu", "Bạch Đằng" → "Bạch Đẳng" ngay cả với giọng Vbee → điểm "XEM" không chắc là lỗi, **luôn để người nghe quyết**.
- 16/11: người dùng nghe thấy **Anh Khôi (Vbee) ấm và hay hơn Hữu Đức**. Đang thử bản làm ấm (`assets/short1/thu-giong/`, lọc `bass=g=4:f=140,equalizer=f=3500:t=q:w=1.2:g=-3,deesser,aecho=0.8:0.6:40:0.12` + `--speed 0.94`). Chưa chốt thì **Vbee vẫn là giọng chính**, ZeroTTS dùng cho bản nháp/căn thời gian.
- Vbee vẫn là phương án dự phòng cho tập quan trọng hoặc câu ZeroTTS không đọc được.
