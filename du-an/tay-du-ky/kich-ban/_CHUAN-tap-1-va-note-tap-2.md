# Chuẩn Tập 1 (Short 01) — áp cho các tập sau

> **Short 01 "Đường Tăng: lãnh đạo hay gánh nặng?" ĐÃ CHỐT (21/11/2026) — đây là STANDARD.**
> Tập 2 làm tốt hơn nhưng **không được tụt dưới chuẩn này**.
> Video: `du-an/tay-du-ky/output/short/short01-full.mp4` (~84s). Dựng lại: `python scripts/hoathinh/but/short01.py`.

## ✅ CHUẨN phải giữ (tập nào cũng theo)
**Định dạng**
- Dọc **9:16 (720×1280)**, **24fps**, độ dài **~80–90s**.
- Banner kèm: **16:9 (1920×1080)** cả đoàn, nhân vật KHÔNG che/cắt (`banner_doan.py`).

**Thumbnail / ảnh mở đầu (BẮT BUỘC có chữ — thuật toán YouTube)**
- **DỌC 9:16 (1080×1920)** vì là Short (`thumb_short01.py`).
- Phong cách giật gân: **nhân vật chính CHIA ĐÔI** 2 phe tương phản (xám lạnh ⟷ vàng hào quang) + **dấu "?"** to ở giữa + đường xé sáng.
- Chữ to, **viền dày** (dễ đọc thu nhỏ). Góc trái: **#Du Ký <n>** nhỏ + **keyword tên nhân vật** (vd ĐƯỜNG TĂNG).
- Hai nhãn hai phe ở band dưới (vd BẤT TÀI ⟷ CHỈ HUY) + câu phụ nhỏ.

**Quy trình (bắt buộc theo thứ tự)**
1. Nhân vật vẽ bằng **Bộ Bút** (tự vẽ code, không vector hoá ảnh).
2. **Storyboard tĩnh** — mỗi cảnh 1 hình, lời dẫn để DƯỚI hình — người dùng duyệt trọn mạch TRƯỚC.
3. Duyệt xong mới **render video**.

**Giọng (ZeroTTS)** — cache ở `build/thu-hoathinh/<tap>/voices.npz` (render lại rất nhanh)
- Dẫn = `giahuy` · Đường Tăng = `tiendat` · Bát Giới = `quangminh` · Sa Tăng = `huuduc`.
- Giọng nữ nếu cần: `baotrang`, `hamy`, `kimoanh`, `maichi`.

**Cấu trúc kể (gây tranh luận, chia phe comment)**
- HOOK (nghịch lý/câu hỏi) → HỒI 1 dựng vấn đề → **HỒI 2 CÚ LẬT** → điểm nổ comment → HỒI 3 chốt → **CTA chia phe**.

**Luật hình**
- **KHÔNG thanh phụ đề đen** dưới màn (lời dẫn chỉ ở storyboard).
- Chữ trên **nền sáng phải màu KEM** (không nâu đậm — bị chìm).
- **Đội hình đoàn (trái→phải): Sa Tăng · ngựa · Đường Tăng (giữa) · Bát Giới · Ngộ Không (dẫn, phải).**
- Cảnh đi: **động tác ĐI BỘ** (bước, hơi waddle) — **KHÔNG nhảy/nhún**; nền cuộn.
- **Mỗi nhân vật có đất diễn + thoại riêng** (tập 1: Đường Tăng, Bát Giới, Sa Tăng đều có câu).
- Nhân vật **không che nhau** ở cảnh tập thể.

**Âm**
- Nhạc ngũ cung + drone trầm; SFX whoosh/thud; **ducking** nhạc xuống dưới giọng.

## ⬆️ Cải tiến cho TẬP 2 (làm tốt hơn tập 1)
- **Lip-sync mượt hơn**: thêm khẩu hình, khớp âm kỹ hơn (tập 1 mới nhép 4 mức theo RMS).
- **Cảnh tĩnh bớt tĩnh**: thêm chuyển động nhẹ (nhân vật thở/cử tay, parallax nền, Ken Burns có chủ đích).
- **Đa dạng nền**: tập 1 xài lại hang / đường xa / thẻ tối hơi nhiều — vẽ thêm bối cảnh mới cho mỗi cú lật.
- **Yêu quái**: cảnh "bị bắt" (batcoc) đang dùng bóng đen + nhãn chữ — tập 2 nếu kịp thì vẽ yêu quái thật bằng Bộ Bút.
- **Nhạc nền chất hơn**, nhịp khớp đúng khoảnh khắc cú lật.
- **Cân nhịp lời dẫn**: câu dẫn dài thì đẩy bớt dữ kiện lên chữ chạy/montage, giọng chỉ đọc câu đắt.
- **Chuyển cảnh**: tập 1 fade đen đơn giản — thử whip/trượt khớp whoosh.

## 📌 Công cụ đã có (tái dùng)
- `scripts/hoathinh/but/short01.py` — pipeline video full (17 shot, giọng, SFX, mux). Cảnh mới = thêm nhánh `if shot == ...` trong `render_frame` + thêm dòng vào `LINES`.
- `scripts/hoathinh/but/storyboard01.py` — render storyboard tĩnh (mỗi cảnh 1 hình) + ảnh web cho artifact.
- `scripts/hoathinh/but/banner_doan.py` — banner 16:9 cả đoàn.
- `walk_tf()` trong short01.py — động tác đi bộ (đã chốt, không nhảy).
