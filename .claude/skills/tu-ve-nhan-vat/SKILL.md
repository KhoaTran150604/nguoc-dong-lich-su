---
name: tu-ve-nhan-vat
description: Làm một nhân vật chibi mới theo FLOW TỰ VẼ (người dùng chốt 20/11/2026, thay flow Gemini) – người dùng chỉ cần nói TÊN hoặc gửi ẢNH THAM KHẢO; Claude lập phiếu nhận diện → viết spec cho Bộ Bút → render → subagent chấm ≥80 → chốt kèm bảng biểu cảm. Dùng khi người dùng muốn "vẽ/làm/tạo nhân vật <tên>", sửa nhân vật đã làm bằng Bộ Bút, hoặc vẽ lại nhân vật cũ cho đẹp hơn.
---

# Tự vẽ nhân vật (Bộ Bút)

**Nguyên tắc:** Claude tự thiết kế và tự vẽ bằng code (skill [[but-ve]]). Không vector hoá ảnh AI, không bám nét ảnh Gemini. Ảnh người dùng gửi chỉ là tham khảo đặc trưng. Trả lời tiếng Việt, ngắn gọn.

```
Tên / ảnh tham khảo
  1. 📋 phiếu nhận diện   → docs/nhan-vat/but/<ma>.md
  2. ✍️  spec Bộ Bút        → scripts/hoathinh/but/nv/<ma_gach_duoi>.py   (+ bộ phận mới nếu thiếu)
  3. 🎨 render             → build/thu-hoathinh/but/<ma>.png · -bong.png · -bieu-cam.png
  4. 🔍 tự soát bằng mắt   → sửa lỗi hiển nhiên trước
  5. 🧮 chấm ≥ 80          → skill [[cham-but]] (subagent mới mỗi vòng)
  6. ✅ chốt               → assets/nhan-vat/but/<ma>.png + <ma>-bieu-cam.png, báo người dùng
```
`<ma>` = tên không dấu, gạch nối (`sa-tang`); file spec dùng gạch dưới (`sa_tang.py`).

## 1. Phiếu nhận diện (`docs/nhan-vat/but/<ma>.md`)
Ngắn, 1 trang. Nếu nhân vật lịch sử/văn học: tra nguồn (Tây Du Ký, tranh dân gian, phim kinh điển) – có thể dùng skill `nghien-cuu-nhan-vat` cho nhân vật lạ. Ghi:
- **Phải có (3–6 đặc trưng nhận diện)**: thứ khiến người xem gọi đúng tên ngay (vd Sa Tăng: râu quai nón đỏ, chuỗi sọ, nguyệt nha sản).
- **Bảng màu** (mã HEX, ≤5 màu chính + da) và màu chủ đạo.
- **Dáng**: `chuan` hay `map`. **Vũ khí/vật cầm tay** (một tay, cầm thấp).
- **Tính cách → biểu cảm mặc định** (hien/vui/quyet…).
- **Cấm**: điều làm sai/bôi xấu nhân vật; không chép nhân vật của kênh khác.
Nếu người dùng gửi ảnh: rút đặc trưng từ ảnh vào phiếu, ghi "ảnh tham khảo: <đường dẫn>". Không đo nét từ ảnh.

## 2. Viết spec
Chép `scripts/hoathinh/but/nv/sa_tang.py` → `nv/<ma>.py`, thay số liệu theo phiếu. Bộ phận chưa có (mũ, đuôi, vũ khí mới…) → thêm vào `bo_phan.py` theo mục "Thêm bộ phận mới" trong [[but-ve]], tuân 12 luật vẽ đẹp. Giữ khung chung; một tay; vũ khí theo trục chuẩn.

## 3–4. Render + tự soát
```
python scripts/hoathinh/but/ve.py <ma> --bong-den --bieu-cam-bang
```
Đọc cả 3 ảnh. Tự sửa ngay: bộ phận lệch/đè sai lớp, hở viền, đặc trưng "phải có" bị khuất, vũ khí vượt đỉnh chuẩn, màu bẩn.

## 5. Chấm
Theo [[cham-but]]: subagent mới mỗi vòng, đạt **≥ 80**. Dưới 80: sửa theo góp ý → render → chấm lại (tối đa 4 vòng).

## 6. Chốt
- Copy `<ma>.png` và `<ma>-bieu-cam.png` → `assets/nhan-vat/but/`.
- Gửi người dùng (SendUserFile): ảnh toàn thân + bảng biểu cảm + điểm. Nếu vẽ lại nhân vật cũ: kèm ảnh so cũ/mới (`--so-cu`).
- Người dùng góp ý → sửa spec (góp ý theo khoá spec, vd "rau.mep hạ 0.1R") → render → gửi lại.
- Cập nhật mục 6 Trạng thái trong `CLAUDE.md`.

## Ghi nhớ
- Mỗi nhân vật chỉ MỘT tay; vũ khí cầm thấp theo chuẩn Ngộ Không (luật 8–9 trong [[but-ve]]).
- Không gradient/blur/glow. Biểu cảm mặc định hiền, dễ thương.
- Bộ phận dùng chung sửa ở `bo_phan.py` → render lại MỌI nhân vật đã chốt để kiểm không vỡ.
- Flow cũ (`nhan-vat-gemini`, `tao-nhan-vat`, bộ `chibi/`) giữ để tham chiếu, không dùng cho nhân vật mới.
