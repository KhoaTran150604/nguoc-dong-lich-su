---
name: nhan-vat-gemini
description: Làm một nhân vật chibi mới theo FLOW GEMINI (người dùng chốt với Trư Bát Giới, 20/11/2026) – viết prompt tạo hình tương đồng Bát Giới → Gemini vẽ ảnh mẫu (Copy lưu về) → vẽ lại bằng code theo mẫu → nhờ Gemini chấm /100, đạt 75–80 là chốt. Dùng khi người dùng muốn "làm/vẽ nhân vật <tên> bằng flow Gemini" (Đường Tăng, Sa Tăng, Bạch Long Mã…).
---

# Flow Gemini làm nhân vật chibi

Quy trình người dùng chốt khi làm **Trư Bát Giới** (20/11/2026): dùng Gemini vẽ ảnh mẫu từ prompt, vẽ lại bằng code bám mẫu, rồi **nhờ chính Gemini chấm điểm**. **Đạt 75–80 là chốt** (Bát Giới chốt ở 73, người dùng duyệt bằng mắt). Trả lời người dùng bằng tiếng Việt, ngắn gọn.

```
Tên nhân vật
  1. ✍️  prompt tạo hình  → docs/nhan-vat/prompt/<mã>.txt   (khung giống bat-gioi.txt)
  2. 🖼️  Gemini vẽ mẫu     → assets/nhan-vat/gemini/<mã>/mau.png   (Copy lưu về)
  3. 🔎  Gemini mô tả      → assets/nhan-vat/gemini/<mã>/spec.json  (màu HEX, vũ khí, mũ…)
  4. 🎨  vẽ lại bằng code  → scripts/hoathinh/chibi/<mã>.py → build/.../<mã>.png + <mã>-bang.png
  5. 🧮  Gemini chấm /100  → assets/nhan-vat/gemini/<mã>/cham-<n>.json   (≥75–80 ĐẠT)
         <75 → áp fixes (khoá bảng P: cũ→mới) → vẽ lại → chấm lại
  6. ✅  chốt              → assets/nhan-vat/<mã>.png  + báo người dùng kèm bảng chỉ số
```

`<mã>` = tên không dấu gạch nối (`bat-gioi`, `duong-tang`, `sa-tang`). Công cụ: **`scripts/hoathinh/gemini_nv.py`** (`mau` / `mota` / `cham` / `models`). Khung tỉ lệ gốc: **`scripts/hoathinh/chibi/goc.py`** – GIỮ NGUYÊN `TI_LE` cho mọi nhân vật.

## 1. Prompt tạo hình
Chép khung `docs/nhan-vat/prompt/bat-gioi.txt` → `docs/nhan-vat/prompt/<mã>.txt`. Giữ NGUYÊN khối **PROPORTIONS & CONSTRUCTION** (khung chung của kênh) + **LINE & COLOR**:
- đầu tròn to, mặt 3/4 quay phải, không cổ; thân "bia mộ" bo góc, không chân;
- KHÔNG tay/chân; cạnh trái phẳng; chỉ 1 bàn tay tròn lơ lửng bên phải cầm vật phẩm;
- viền đen đều dày `#0A0807`; màu phẳng, KHÔNG gradient/đổ bóng/blur/glow/3D.

Chỉ thay phần riêng theo nhân vật: **FACE / HEADWEAR / OUTFIT (mã màu HEX) / WEAPON**. Kết câu nhắc "Avoid: 3D render, gradients, shading, … or any left arm."

## 2. Gemini vẽ ảnh mẫu
**Key API gói miễn phí KHÔNG vẽ được ảnh** (`generate_content_free_tier_requests` limit 0 cho model image). Hai cách:
- **Gemini web + Claude in Chrome** (mặc định): mở gemini.google.com (user đã đăng nhập), dán prompt, gen, bấm **Copy** ảnh → lưu `assets/nhan-vat/gemini/<mã>/mau.png`.
- **Có billing**: `python scripts/hoathinh/gemini_nv.py mau <mã> --prompt docs/nhan-vat/prompt/<mã>.txt` (tự chạy luôn bước mô tả).

Nếu người dùng đã có sẵn ảnh mẫu Gemini (vd `assets/nhan-vat/mau/<mã>/*.png`) thì copy làm `mau.png`.

## 3. Gemini mô tả (spec.json)
`python scripts/hoathinh/gemini_nv.py mota <mã>` → đọc màu HEX, tỉ lệ, mũ/tóc, trang phục, vũ khí từ `mau.png`. Spec này dùng để vẽ code và để Gemini đối chiếu khi chấm.

## 4. Vẽ lại bằng code
Chép một nhân vật đã có trong `scripts/hoathinh/chibi/` (gần nhất về dáng) → `<mã>.py`. **GIỮ NGUYÊN `TI_LE` gốc** (`tao_P`, dáng `chuan`/`map`); NV mập dùng `dang='map'`. Chỉ đổi theo `mau.png` + `spec.json`: màu, mũ/tóc, trang phục, vật phẩm tay phải (cầm **sát thân**), vị trí mắt/mày/miệng. Luôn xuất **ảnh + bảng chỉ số** (`bang.sheet`, nhãn mã P) – [[chi-so-kem-anh]].

## 5. Gemini chấm điểm (CÁCH CHÍNH: Gemini web qua Claude in Chrome)
**Người dùng chốt (20/11/2026): chấm bằng Gemini web, không dùng API** (API free hết quota text 20 lượt/ngày). Quy trình đã chạy cho Đường Tăng (67→73→82):
1. Claude in Chrome mở `https://gemini.google.com/app`. Lần đầu: tạo chat chấm điểm — tải **2 ảnh** (ảnh mẫu `mau.png` + bản code) rồi dán prompt chấm.
2. Cách tải ảnh (né hộp thoại hệ thống): bấm nút **"+" (Upload & tools)** → `find` ô `type="file"` (thường là ref đầu trong menu upload) → `file_upload` với đường dẫn tuyệt đối. KHÔNG click "Upload files" (mở hộp thoại OS không thao tác được).
3. **Những lần sau: chấm TRONG CÙNG CHAT** (mở lại chat "chấm điểm" ở sidebar) — chỉ cần tải **bản code mới** + nhắn "đây là bản đã sửa, chấm lại so với ảnh mẫu đầu chat". Gemini nhớ ảnh mẫu + tiêu chí, so được với bản điểm trước.
4. Đọc kết quả bằng `get_page_text`.

Prompt chấm (dán nguyên văn, Ảnh 1 = mẫu, Ảnh 2 = code): dặn Gemini **BỎ QUA khung chung** (đầu/thân/tay/viền/canvas), chỉ chấm mặt & biểu cảm, màu, trang phục, mũ/tóc, vật phẩm, độ dễ thương; trả **điểm tổng /100** + bảng thành phần (mặt /25, màu /20, trang phục /20, mũ /15, vật phẩm /15, dễ thương /5) + danh sách CẦN SỬA (ưu tiên 1-3, cụ thể theo R/HEX) + kết luận ĐẠT nếu ≥75.

**≥ 75–80 → ĐẠT.** <75 → dịch `fixes` sang **thay khoá bảng P** (vd `crown_petal_w: 0.25 → 0.31`), sửa `<mã>.py`, render lại, chấm lại trong cùng chat. Thường 2–3 vòng là đạt.

_(Dự phòng, nếu key có billing: `python scripts/hoathinh/gemini_nv.py cham <mã> build/thu-hoathinh/nhan-vat/<mã>.png -n 3` → `cham-<n>.json`.)_

## 6. Chốt
Copy bản render đạt → `assets/nhan-vat/<mã>.png`. Báo người dùng điểm + gửi ảnh (kèm bảng chỉ số), hỏi duyệt. Cập nhật mục 6 Trạng thái trong `CLAUDE.md`.

## Quota Gemini (free tier)
- Vẽ ảnh qua API: **limit 0** → luôn dùng Gemini web.
- Text (mota + cham): **~20 lượt/ngày**, hết thì báo lỗi 429 "retry in …h", **reset sau ~24h**. Mỗi lần `cham -n 3` tốn 3 lượt → tính trước số vòng. Key có billing thì đặt `GEMINI_API_KEY` (biến môi trường / `.env` gốc, đã .gitignore).

## Luật xuyên suốt
- Giữ khung tỉ lệ gốc (`goc.py`) cho MỌI nhân vật – mọi nhân vật cùng đầu/thân/chiều cao.
- Không bôi xấu nhân vật; biểu cảm mặc định hiền/dễ thương.
- Vật phẩm tay phải cầm sát thân, gọn.
- Mỗi lần đưa thông số cho người dùng phải kèm ảnh bảng chỉ số ([[chi-so-kem-anh]]).
- Mẫu tham chiếu đã làm xong: Ngộ Không `ngo_khong.py`, Bát Giới `bat_gioi_gemini.py` (chốt v14).
