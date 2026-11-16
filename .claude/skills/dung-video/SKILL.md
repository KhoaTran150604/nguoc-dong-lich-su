---
name: dung-video
description: Dựng video dài 16:9 (và cắt Short) cho một tập Ngược Dòng Sử Việt bằng bộ công cụ có sẵn – bản đồ vùng, bản đồ trận, cờ chân dung, hiệu ứng H1–H12, sa bàn, âm thanh, render song song 1080p60. Dùng khi kịch bản đã kiểm chứng và cần làm hình/video; KHÔNG làm lại từ đầu, chỉ viết file cảnh của tập.
---

# Agent Dựng video

Vai trò: biến kịch bản đã kiểm chứng thành video, **dùng lại bộ công cụ**, chỉ sáng tạo ở phần riêng của từng tập (chiến trường, đường hành quân, nhân vật). Trả lời bằng tiếng Việt.

## Bộ công cụ (scripts/video/)
| File | Vai trò | Dùng lại thế nào |
|---|---|---|
| `dung.py` | Bộ máy: đọc lời đọc, chia cảnh theo mốc giọng, render song song 4 nhân, cache từng cảnh, khung tĩnh dùng lại, trộn âm, xuất ảnh tĩnh | Không sửa cho từng tập |
| `tap/<mã>.py` | **File duy nhất viết mới mỗi tập**: cấu hình bản đồ, `SCENES`, `SFX`, `TAIL`, `FADE` | Sao chép `tap/e2.py` làm mẫu |
| `bando_vung.py` | Bản đồ vùng style kênh từ đường bờ thật (Natural Earth), vùng các phe tô màu minh họa, địa danh, sông, biển; camera `(lon, lat, rộng_độ)`, `lerp_cam` để lia/zoom | Đổi `bbox`, `vung`, `song`, `diadanh` |
| `bando_tran.py` | Bản đồ trận cửa sông (2 trạng thái nước, trộn theo mức triều) | Trận khác: sao chép, đổi `RIVER`, `TRIBS`, `SEA`, `ISLANDS`, nhãn |
| `nhanvat.py` | Chân dung vector style sơn mài cho cờ; ảnh thật ở `assets/nhanvat/<mã>.png` được ưu tiên | Nhân vật mới = thêm 1 dòng vào `NHANVAT` + `TEN` |
| `amthanh.py` | Âm hiệu ứng tổng hợp (không bản quyền); file thật `assets/sfx/<tên>.wav/mp3` được ưu tiên | Đã duyệt: `kiem`, `lua`, `rut`, `trong_b` (phản công), `vo_a` (thuyền vỡ), `roi`, `song` |
| `../hieuung/demo.py` | Thư viện hiệu ứng H1–H12 đã duyệt (cờ, thuyền, kiếm, lửa, X…) | Không sửa nếu người dùng không yêu cầu |

Hàm dùng chung trong `dung.py`: `bg_vung(M, cam)`, `bg_tran(BT, mức_nước)`, `bg_den()`, `dim()`, `flag(mã, phe, x, y, cỡ, tilt=, grey=, op=)`, `small_flags()` (H7), `clash()` (H3), `xmark()` (H5), `tint()` (H4), `glow()`, `link()` (quan hệ, đứt gãy), `quote()` (H12), `clock()` (H11), `logo_card()`, `saban()` (mặt cắt). Phe: `TA` (vàng đồng), `DICH` (đỏ), `GIAN` (xám).

## Quy trình một tập
1. Kịch bản đã qua `kiem-chung-nguon` + `gop-y-kich-ban` (docs/long/<mã>-….md).
2. Lời đọc `docs/videos/<MÃ>-loi-doc.txt`: mỗi dòng một câu; `# sNN` gán cảnh; `# lặng N` giữ cảnh thêm N giây (giao chiến, nước rút…); `# lặng N sNN` chèn cảnh lặng riêng (vd đồng hồ năm `s01` đầu video).
3. Chạy giọng **ngay** (lâu nhất, ~35 s/câu khi có `--check`): skill `giong-doc` → `assets/<mã>/<MÃ>-GiaHuy.mp3/.json` (chạy nền).
4. Viết `tap/<mã>.py` (sao chép e2). Mỗi cảnh một hàm `sNN(tl, d)` trả SVG lớp phủ, gọi một hàm `bg_*` để chọn nền. Chuyển động dùng `seg(tl, a, b)` theo **tỉ lệ của d** để cảnh dài/ngắn theo giọng vẫn khớp.
5. Ảnh tĩnh duyệt khung (vài giây): `python3 scripts/video/dung.py <mã> docs/videos/<MÃ>-loi-doc.txt --stills` (hoặc `--stills=s05,s12`) → `build/<mã>/stills/`. Ghép thành ảnh tổng để tự soát, rồi gửi người dùng các khung tiêu biểu.
6. Nháp 540p30: `python3 scripts/video/dung.py <mã> docs/videos/<MÃ>-loi-doc.txt assets/<mã>/<MÃ>-GiaHuy`.
7. Bản cuối: thêm `--final --fps60` → `build/<mã>/<MÃ>-1080p60.mp4`. Thời gian đo được: ~2,3 phút render cho 1 phút video (4 nhân), cảnh tĩnh nhanh hơn nhiều.
8. Sửa theo góp ý **theo mã cảnh**: chỉ cảnh có thay đổi được render lại (cache theo nội dung).

## Phong cách đã chốt (người dùng duyệt 16/11/2026) – không tự đổi
- **Tĩnh là mặc định**: chỉ cờ/thuyền di chuyển; camera lia/zoom chậm khi đổi vùng.
- **Không phụ đề, không nhãn chữ** trên hình (trừ tên trên bản đồ, khung trích H12, đồng hồ năm, end card). Ghi chú "minh họa" đưa vào **mô tả video**.
- **Bản đồ 2 tầng**: vùng (bối cảnh, hành quân) ↔ trận (giao chiến). Lùi xa vừa đủ thấy toàn trận; chi tiết: núi gạch bóng, cây, ruộng, đảo, sóng, khung viền, la bàn.
- **Cờ chân dung dẫn đoàn**: đoàn thuyền/quân luôn có cờ chỉ huy; ta = điềm tĩnh, tự tin (Ngô Quyền mũ trụ + giáp); địch = nghiêm lạnh (không quá dữ).
- Hiệu ứng H1–H12 theo `docs/plan/phong-cach-video-dai.md`; giao chiến = kiếm + lửa; thuyền vỡ không dùng lửa nếu sử không chép.
- Nhịp: kể liền mạch (không "bước 1, 2"), cao trào chậm, chèn `# lặng` cho giao chiến/nước rút.
- 1080p **60 hình/giây** cho bản cuối; nháp 540p30.

## Quy tắc nội dung khi dựng
- Hình **không được thêm dữ kiện** mà lời đọc/kho không có (lửa, phục binh, số quân, chân dung "thật"…).
- Lời trong khung H12 phải là lời sử chép, ghi nguồn; không dùng câu đã bị ❌ ở kho (vd "trăm vạn").
- Bản đồ cổ: không vẽ biên giới hiện đại, không dùng hình chữ S cho thời xưa; bản đồ Việt Nam toàn cảnh hiện đại luôn có Hoàng Sa, Trường Sa.

## Đầu ra & lưu
- Code + lời đọc + giọng commit vào repo; `build/` và `assets/bando/_cache/` không commit (tạo lại được).
- Video nháp/cuối gửi người dùng bằng SendUserFile; bản cuối lớn thì chỉ commit nếu người dùng muốn.
