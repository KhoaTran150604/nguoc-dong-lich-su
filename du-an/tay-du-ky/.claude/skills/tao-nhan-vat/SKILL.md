---
name: tao-nhan-vat
description: Điều phối toàn bộ pipeline 4 bước làm một nhân vật chibi mới – nghiên cứu tạo hình (web + ảnh) → thẩm định hồ sơ → vẽ bằng code → chấm điểm đầu ra đạt 80 mới ra thành phẩm. Dùng khi người dùng muốn "tạo nhân vật <tên>" và không muốn feedback tay từng lần.
---

# Tạo nhân vật chibi – pipeline 4 bước

Mục tiêu: người dùng chỉ cần nói tên nhân vật; các agent tự nghiên cứu → tự chấm, không cần người dùng feedback từng lần. Thành phẩm chỉ ra khi đạt **≥ 80 điểm** so với hồ sơ.

```
Tên nhân vật
   │
1. 🔎 nghien-cuu-nhan-vat   → docs/nhan-vat/<mã>-hoso.md + assets/nhan-vat/mau/<mã>/*.jpg
   │                           (mô tả + ẢNH minh họa + checklist "phải có" + điều cấm)
2. ✅ tham-dinh-ho-so        → chấm hồ sơ /100; chưa đạt → quay lại bước 1
   │
3. 🎨 ve-va-cham-anh (vẽ)    → scripts/hoathinh/chibi/<mã>.py → build/.../<mã>.png + <mã>-bang.png
   │                           (sửa bảng P theo hồ sơ; giữ nguyên TI_LE gốc)
4. 🧮 cham-nhan-vat (≥80)    → chấm bản vẽ theo HỒ SƠ + ẢNH; <80 → sửa P → vẽ lại → chấm lại
   │
Thành phẩm (đạt 80) → gửi người dùng
```

## Quy ước tên & đường dẫn
- `<mã>` = tên không dấu, gạch nối (vd `bat-gioi`, `ngo-khong`, `sa-tang`).
- Hồ sơ: `docs/nhan-vat/<mã>-hoso.md` · Ảnh mẫu: `assets/nhan-vat/mau/<mã>/` · Code: `scripts/hoathinh/chibi/<mã>.py` · Ảnh ra: `build/thu-hoathinh/nhan-vat/<mã>.png` · Điểm: `docs/nhan-vat/<mã>-cham-diem.md`.

## Chạy
1. **Nghiên cứu** – [[nghien-cuu-nhan-vat]] (subagent có web): ra hồ sơ + ảnh.
2. **Thẩm định** – [[tham-dinh-ho-so]] (subagent): chưa đạt thì bổ sung hồ sơ rồi thẩm định lại.
3. **Vẽ** – [[ve-va-cham-anh]]: copy một nhân vật đã có trong `scripts/hoathinh/chibi/` → `<mã>.py`, **giữ nguyên `K` (TI_LE gốc)**, chỉ thay màu/mắt/nón/tóc/trang phục/vật phẩm theo hồ sơ. Luôn xuất ảnh + bảng chỉ số ([[chi-so-kem-anh]]).
4. **Chấm đạt 80** – [[cham-nhan-vat]]: subagent mới mỗi vòng; <80 thì áp góp ý (dạng `khoá: cũ → mới`) → vẽ lại → chấm lại (tối đa 3 vòng). Đạt → chốt vào `assets/nhan-vat/<mã>.png`, báo người dùng.

## Luật xuyên suốt
- Giữ nguyên khung tỉ lệ gốc (`scripts/hoathinh/chibi/goc.py`) cho mọi nhân vật.
- **Không bôi xấu nhân vật**; biểu cảm mặc định trung tính/dễ thương.
- Vật phẩm tay phải cầm **sát thân**, gọn.
- Mỗi lần đưa thông số cho người dùng phải kèm ảnh bảng chỉ số ([[chi-so-kem-anh]]).
- Mẫu tham chiếu khung: Ngộ Không `scripts/hoathinh/chibi/ngo_khong.py`.
