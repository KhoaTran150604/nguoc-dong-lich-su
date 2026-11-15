# Dựng một khối (Short 9:16) từ file cấu hình

Mỗi khối của kịch bản video dài (`docs/videos/…`) có một file cấu hình JSON (ví dụ `e2_k1.json`). Mỗi câu trong file là một segment, gồm:
- `scene`: tên cảnh;
- `label`: nhãn ở đầu khung;
- `sub`: phụ đề, cũng là lời đọc;
- `tts`: lời đọc cho giọng tạm, số viết bằng chữ;
- `src`: nguồn hiện dưới chân khung;
- `codes`: mã dữ kiện trong kho.

## Cài đặt
```bash
pip install cairosvg pillow numpy piper-tts
```
Video dùng **ffmpeg**. Font lấy trực tiếp từ thư mục `fonts/`.

## 1. Bản giọng tạm (Piper, để duyệt hình và nhịp)
Tải model tiếng Việt `vi_VN-vais1000-medium.onnx` (kèm file `.onnx.json`) từ kho `rhasspy/piper-voices` trên Hugging Face, sau đó chạy:
```bash
python3 scripts/khoi/render.py scripts/khoi/e2_k1.json --voice <đường dẫn>/vi_VN-vais1000-medium.onnx --out assets/e2/E2-K1-giong-tam.mp4
```

## 2. Bản giọng Vbee (bản đăng)
1. Dán lời trong `assets/e2/E2-K1-loi-doc-vbee.txt` vào Vbee, chọn giọng "Anh Khôi nâng cao". **Để mỗi câu một đoạn**, sao cho giữa các câu có khoảng lặng ít nhất 0,25 giây. Tải file MP3 về.
2. Chạy:
```bash
python3 scripts/khoi/render.py scripts/khoi/e2_k1.json --vbee assets/e2/E2-K1-vbee.mp3 --out assets/e2/E2-K1.mp4
```
Script tự cắt file MP3 thành từng câu theo khoảng lặng, in ra danh sách khoảng lặng và các điểm cắt. Số điểm cắt bằng số câu trừ 1. Cảnh và phụ đề tự khớp theo giọng thật.

**Nếu cắt sai:** Vbee hay ngắt dài ở dấu "…", nên thuật toán có thể nhầm. Xem danh sách khoảng lặng script in ra, chọn đúng các chỗ ngắt giữa các câu (thường dài khoảng 0,9 giây), rồi:
- chạy lại với `--cuts 1.62 8.35 …`, hoặc
- ghi vào khóa `"vbee_cuts"` trong file JSON để lần sau tự dùng. Khối 1 đã có sẵn khóa này.

## Xem trước nhanh
Thêm `--preview 5 12 20` để xuất ảnh tĩnh tại các giây đó (vào thư mục `*_work/`) mà không phải render cả video.

## Ghi chú
- Phụ đề đặt ở khoảng 80% chiều cao khung, chữ 54px, tối đa 2 dòng. Nguồn hiện ở chân khung.
- Chữ ký 0–2,7 giây: vành chim Lạc quay ngược chiều kim đồng hồ, đồng hồ năm chạy từ 2026 về 938. Bản đồ Việt Nam hiện đại (có Hoàng Sa, Trường Sa) mờ dần.
- Chưa có nhạc nền. Thêm nhạc từ YouTube Audio Library hoặc thư viện CapCut khi dựng bản cuối.
- Thêm khối mới: viết file JSON mới. Cảnh nào chưa có thì viết thêm hàm `@scene('ten')` trong `render.py`.
