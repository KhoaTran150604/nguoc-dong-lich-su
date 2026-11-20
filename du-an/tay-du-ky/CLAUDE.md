# Dự án: Tây Du Ký (vẽ nhân vật chibi + hoạt hình)

> Dự án **đang làm**. Trả lời người dùng bằng **tiếng Việt**, thân thiện, ngắn gọn.
> Luật chung (đồng bộ cloud↔máy, môi trường) nằm ở `CLAUDE.md` gốc. File này chỉ về **nhân vật + kịch bản + animation** của Tây Du Ký.

## Cấu trúc dự án
```
du-an/tay-du-ky/
  CLAUDE.md          ← file này
  nhan-vat/          ← SPEC nhân vật + ẢNH ĐÃ CHỐT + phiếu nhận diện + nhật ký chấm
  kich-ban/          ← kịch bản tập
  animation/         ← cảnh hoạt hình
```
> **Dời file vào đây là việc của GĐ2** (đang chờ test). Hiện code/asset vẫn ở vị trí cũ:
> - Bộ Bút (engine dùng chung): `scripts/hoathinh/but/` — `but.py` lõi, `khung.py`, `bo_phan.py`, `nv/<ma>.py` spec, `ve.py` render.
> - Ảnh nhân vật đã chốt: `assets/nhan-vat/but/` (`<ma>.png` + `<ma>-bieu-cam.png`), ghép `thay-tro.png`.
> - Phiếu + nhật ký chấm: `docs/nhan-vat/but/<ma>.md`, `<ma>-cham.md`.

## 📸 Lấy ảnh nhân vật đã chốt (cho animation / kịch bản)
> Đây là "bộ nhớ chung" của dự án: file này nạp khi làm trong BẤT KỲ thư mục con nào (`nhan-vat/`, `kich-ban/`, `animation/`), nên animation luôn biết lấy ảnh ở đâu.

| Nhân vật | Mã | Ảnh toàn thân | Biểu cảm | Spec code | Điểm |
|---|---|---|---|---|---|
| Sa Tăng | `sa_tang` | `assets/nhan-vat/but/sa-tang.png` | `sa-tang-bieu-cam.png` | `but/nv/sa_tang.py` | 82 ✅ |
| Ngộ Không | `ngo_khong` | `assets/nhan-vat/but/ngo-khong.png` | `ngo-khong-bieu-cam.png` | `but/nv/ngo_khong.py` | 87 ✅ |
| Bát Giới | `bat_gioi` | `assets/nhan-vat/but/bat-gioi.png` | `bat-gioi-bieu-cam.png` | `but/nv/bat_gioi.py` | 83 ⚠️ |
| Đường Tăng | `duong_tang` | `assets/nhan-vat/but/duong-tang.png` | `duong-tang-bieu-cam.png` | `but/nv/duong_tang.py` | 83 ⚠️ |
| Bạch Long Mã | `bach_long_ma` | `assets/nhan-vat/but/bach-long-ma.png` | `bach-long-ma-bieu-cam.png` | `but/nv/bach_long_ma.py` | 81 ✅ |

- Ảnh ghép 5 thầy trò (gồm ngựa): `assets/nhan-vat/but/thay-tro.png` (`but/thay_tro.py`).
- Ngựa dùng dáng `ngua` (`KhungNgua` trong `khung.py`, `LOP_NGUA` trong `ve.py`), `head_c=(540, 399)` – cùng R, cùng mặt đất với người.
- Cần render lại / sửa nhân vật → vào `nhan-vat/`, đọc skill `bo-ve` + `tu-ve-nhan-vat`.
- ⚠️ Bát Giới + Đường Tăng chưa được duyệt mắt bản Bộ Bút. Bạch Long Mã người dùng đã duyệt (20/11/2026).
- **GĐ2:** các ảnh/spec trên sẽ dời vào `du-an/tay-du-ky/nhan-vat/`; bảng này cập nhật đường dẫn mới khi dời.

## Công cụ & skill
- **Vẽ nhân vật (dùng chung):** Bộ Bút + skill **`bo-ve`** (12 luật vẽ đẹp, API, bộ phận). Trước đây tên là `but-ve`.
- **Làm 1 nhân vật mới (tự vẽ):** skill **`tu-ve-nhan-vat`** — chỉ cần tên hoặc ảnh tham khảo → phiếu nhận diện → spec `but/nv/<ma>.py` → render `but/ve.py <ma> --bong-den --bieu-cam-bang` → chấm → chốt.
- **Chấm nhân vật:** skill **`cham-but`** (subagent độc lập chấm /100, không tốn quota Gemini). **Đạt ≥80 mới chốt** (duyệt mắt có thể 73+).
- **Hoạt hình:** skill **`hoat-hinh-2d`** (cảnh chibi có giọng + khẩu hình).
- Flow cũ (Gemini, chibi cũ): `nhan-vat-gemini`, `tao-nhan-vat`, `nghien-cuu-nhan-vat`, `tham-dinh-ho-so`, `cham-nhan-vat`, `ve-va-cham-anh` — giữ để tham khảo, **mặc định dùng Bộ Bút**.

## Luật vẽ Bộ Bút (bắt buộc)
- **Tự vẽ 100% bằng code** (thư viện skia): khối cộng/trừ, Bezier mượt, nét 3 cấp tự tính viền ngoài, bóng phẳng tự sinh. **KHÔNG vector hoá / bám ảnh Gemini** (khó kiểm soát chất lượng). Ảnh Gemini chỉ để **tham khảo**.
- **Mọi nhân vật chung khung gốc** (`khung.py`); nhân vật mập dùng dáng `map`. Giữ khung khi vẽ nhân vật mới.
- **KHÔNG CỔ:** đầu đặt thẳng lên thân, không vẽ cổ, không lấp khe cằm–vai (luật ghi trong `khung.py` + skill `bo-ve`; đã gỡ bộ phận `co_nguoi`).
- **Vũ khí cầm THẤP** chuẩn Ngộ Không: trục qua tâm tay, nghiêng 8.7°, đỉnh ≤ tâm đầu − 1.76R. **Mỗi nhân vật MỘT bàn tay**, vẽ đè lên cán.
- Chi tiết mảnh không góp viền ngoài dày → dùng `b.dang_phu` / `b.lo`.
- Khi sửa 3–4 vòng mà điểm không lên → **đổi cách làm**, đừng chỉnh tiếp.
- Đưa thông số vẽ là phải **gửi kèm ảnh bảng chỉ số** có nhãn mã.

## Trạng thái nhân vật (20/11/2026)
- **✅ ĐỦ 4 THẦY TRÒ + BẠCH LONG MÃ bằng Bộ Bút** (`assets/nhan-vat/but/`):
  - **Sa Tăng 82/100** (CHUẨN mẫu cho nhân vật sau) — `but/nv/sa_tang.py`. Người dùng đã duyệt.
  - **Ngộ Không 87/100** (đạt ngay vòng đầu) — `but/nv/ngo_khong.py`.
  - **Bát Giới 83/100** — `but/nv/bat_gioi.py`.
  - **Đường Tăng 83/100** — `but/nv/duong_tang.py`.
  - **Bạch Long Mã 81/100** – người dùng đã duyệt (20/11, dáng `ngua` – thú 4 chân, đầu đè thẳng lên ngực, không cổ) — `but/nv/bach_long_ma.py`.
  - ⚠️ Bát Giới + Đường Tăng bản Bộ Bút **chưa được người dùng duyệt bằng mắt**.
- Bộ phận dùng chung đã có: khỉ (`_gai`, `mat_na`, `duoi_xoan`, `vong_tran.nut` kim cô, `ao.vay`+`gau_rang`, `vu_khi.ha`); heo (tai/mõm, `mu` tròn/Tì Lư, `day_mu`, `ao.mo`+`bung_loi`); sư (`khan_co`, `_ca_sa`, `cao_chin_rang`, `tich_truong`); ngựa (`KhungNgua` + `chan_*`, `than_ngua`, `yen_ngua`, `khan_ngua`, `bom_*`, `tai_ngua`, `dau_ngua`, `sung_rong`, `cuong_ngua`, `duoi_ngua`).
- Nhánh cloud `claude/exciting-hawking-4tp7r5` (Sa Tăng + Bạch Long Mã bản chibi cũ) đã kéo về máy, **chưa gộp main**.

## Việc tiếp
- GĐ2: dời spec `but/nv/*.py` + ảnh chốt vào `du-an/tay-du-ky/nhan-vat/`, tách Bộ Bút thành lớp dùng chung, sửa import, render thử lại.
- Nhân vật mới / chuyển động nhân vật đã chốt.
