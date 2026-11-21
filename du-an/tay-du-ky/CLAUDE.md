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
| Bạch Cốt Tinh | `bach_cot_tinh` | `assets/nhan-vat/but/bach-cot-tinh.png` | `bach-cot-tinh-bieu-cam.png` | `but/nv/bach_cot_tinh.py` | 83 ✅ |
| Nữ Vương Nữ Nhi Quốc | `nu_vuong` | `assets/nhan-vat/but/nu-vuong.png` | `nu-vuong-bieu-cam.png` | `but/nv/nu_vuong.py` | 81 ✅ |
| Tiểu yêu (lính quèn) | `tieu_yeu` (+ `_do`, `_lam`) | `assets/nhan-vat/but/tieu-yeu.png` (đỏ: `tieu-yeu-do.png`, lam: `tieu-yeu-lam.png`) | `tieu-yeu-bieu-cam.png` | `but/nv/tieu_yeu*.py` | 83 ✅ |
| Thiên Bồng Nguyên Soái (tiền kiếp Bát Giới) | `thien_bong` | `assets/nhan-vat/but/thien-bong.png` | `thien-bong-bieu-cam.png` | `but/nv/thien_bong.py` | 81 ✅ |

- Ảnh ghép 5 thầy trò (gồm ngựa): `assets/nhan-vat/but/thay-tro.png` (`but/thay_tro.py`).
- Đám đông lính yêu: `assets/nhan-vat/but/tieu-yeu-dam-dong.png` gồm 3 bản xanh, đỏ, lam. Muốn thêm lính thì chép `nv/tieu_yeu_do.py`, đổi màu, sừng và biểu cảm.
- Ngựa dùng dáng `ngua` (`KhungNgua` trong `khung.py`, `LOP_NGUA` trong `ve.py`), `head_c=(540, 399)` – cùng R, cùng mặt đất với người.
- Cần render lại / sửa nhân vật → vào `nhan-vat/`, đọc skill `bo-ve` + `tu-ve-nhan-vat`.
- ⚠️ Bát Giới + Đường Tăng chưa được duyệt mắt bản Bộ Bút. Bạch Long Mã, Bạch Cốt Tinh, Nữ Vương, Tiểu yêu người dùng đã duyệt (20/11/2026).
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
  - **Bạch Cốt Tinh 83/100** + **Nữ Vương Nữ Nhi Quốc 81/100** (20/11, tự vẽ không ảnh tham khảo vì Gemini hết lượt; người dùng đã duyệt) — `but/nv/bach_cot_tinh.py`, `but/nv/nu_vuong.py`.
  - **Tiểu yêu (lính quèn) 83/100** + 2 biến thể đỏ/lam cho đám đông (20/11, tự vẽ; người dùng đã duyệt) — `but/nv/tieu_yeu.py`, `tieu_yeu_do.py`, `tieu_yeu_lam.py`.
  - **Bạch Long Mã 81/100** – người dùng đã duyệt (20/11, dáng `ngua` – thú 4 chân, đầu đè thẳng lên ngực, không cổ) — `but/nv/bach_long_ma.py`.
  - ⚠️ Bát Giới + Đường Tăng bản Bộ Bút **chưa được người dùng duyệt bằng mắt**.
- Bộ phận dùng chung đã có: khỉ (`_gai`, `mat_na`, `duoi_xoan`, `vong_tran.nut` kim cô, `ao.vay`+`gau_rang`, `vu_khi.ha`); heo (tai/mõm, `mu` tròn/Tì Lư, `day_mu`, `ao.mo`+`bung_loi`); sư (`khan_co`, `_ca_sa`, `cao_chin_rang`, `tich_truong`); ngựa (`KhungNgua` + `chan_*`, `than_ngua`, `yen_ngua`, `khan_ngua`, `bom_*`, `tai_ngua`, `dau_ngua`, `sung_rong`, `cuong_ngua`, `duoi_ngua`).
- Nhánh cloud `claude/exciting-hawking-4tp7r5` (Sa Tăng + Bạch Long Mã bản chibi cũ) đã kéo về máy, **chưa gộp main**.

## 🎬 Short 01 / TẬP 1 — ĐÃ CHỐT (21/11/2026) · là CHUẨN cho các tập sau
- **Tên:** "Đường Tăng: lãnh đạo hay gánh nặng?" · dọc 9:16 720×1280 @24fps · **~84s, 17 cảnh**.
- **Video:** `du-an/tay-du-ky/output/short/short01-full.mp4` — dựng lại: `python scripts/hoathinh/but/short01.py`.
- **Thumbnail (dọc):** `.../banner/short01-thumbnail-doc.png` (`thumb_short01.py`) — Đường Tăng chia đôi BẤT TÀI/CHỈ HUY + dấu ?.
- **Banner đoàn 16:9:** `.../banner/short01-doan-16x9.png` (`banner_doan.py`).
- **Pipeline video:** `scripts/hoathinh/but/short01.py` (17 shot + giọng ZeroTTS cache + SFX + mux). **Storyboard** duyệt trước: `storyboard01.py`.
- **Chuẩn + điểm cải tiến tập 2:** xem `kich-ban/_CHUAN-tap-1-va-note-tap-2.md`. Đã đăng ký `docs/videos/thanh-pham.json` (mục `short_hoathinh`).

## 🎬 Short 02 / TẬP 2 — Trư Bát Giới (21/11/2026)
- **Tên:** "Trư Bát Giới: Nguyên soái nhà Trời hay kẻ ăn hại?" · dọc 9:16 720×1280 @24fps · **13 cảnh**.
- **Cú lật:** cào cỏ 5.048 cân → Thiên Bồng Nguyên Soái 8 vạn thủy quân → ghẹo Hằng Nga bị đày → dưới nước thắng Ngộ Không → Tịnh Đàn Sứ Giả (ăn cả đời).
- **Kịch bản:** `kich-ban/short-02-bat-gioi.md` — hội đồng 3 agent chấm: chính xác **93**, sức hút ~**90**, nhịp ~**86**.
- **Nhân vật mới:** Thiên Bồng Nguyên Soái `but/nv/thien_bong.py` (81/100). Hằng Nga tái dùng sprite `nu_vuong`.
- **Video:** `du-an/tay-du-ky/output/short/short02-full.mp4` — dựng lại: `python scripts/hoathinh/but/short02.py`.
- **Thumbnail (KHÁC tập 1):** `.../banner/short02-thumbnail-doc.png` (`thumb_short02.py`) — "HÀO QUANG ĐỔ BÓNG": Bát Giới màu + bóng Thiên Bồng; band KẺ ĂN HẠI vs TƯỚNG TRỜI. (Luật mới: mỗi tập 1 kiểu thumbnail riêng, không lặp khuôn.)
- **Banner 16:9:** `.../banner/short02-doan-16x9.png` (`banner_doan02.py`). **Storyboard:** `storyboard02.py`. **Title/mô tả:** `output/short02-title-mota.md`.
- **Cải tiến tập 2 đã áp:** nền mới (thiên đình/dưới nước/điện thờ), hào quang FLAT (không glow), chữ nền sáng màu kem, lip-sync 3 nhân vật.

## Việc tiếp
- ✅ **Short 02 ĐÃ ĐĂNG (21/11/2026):** Scheduled → public 21/11 19:45 (GMT+7), link `youtube.com/shorts/Um2ozL_F4HA`. Chi tiết: `docs/videos/short02-dang-youtube.md`. Tiêu đề chốt theo nhân vật: **"Trư Bát Giới (Du Ký #2)"**, playlist `Làm tí du ký`, category Film & Animation, related video = Du Ký #1. Thumbnail đã gỡ chip góc trên-trái (bị UI Short che).
- **Tập 3:** theo chuẩn, mỗi tập một kiểu thumbnail riêng; áp cải tiến trong `_CHUAN-tap-1-va-note-tap-2.md`.
- GĐ2: dời spec `but/nv/*.py` + ảnh chốt vào `du-an/tay-du-ky/nhan-vat/`, tách Bộ Bút thành lớp dùng chung, sửa import, render thử lại.
- Nhân vật mới / chuyển động nhân vật đã chốt.
