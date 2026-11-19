---
name: ve-va-cham-anh
description: "Agent vẽ và chấm ảnh" – quy trình vẽ nhân vật chibi bằng code rồi tự chấm điểm so với ảnh mẫu và sửa đến khi đạt. Dùng khi người dùng muốn vẽ một nhân vật mới, sửa nhân vật đang có, hoặc chấm/đánh giá một bản vẽ nhân vật. Người dùng gọi "agent vẽ và chấm ảnh".
---

# Agent vẽ và chấm ảnh

Quy trình chuẩn để làm nhân vật chibi 2D cho phim (bắt đầu từ Tôn Ngộ Không). Gồm 2 phần: **VẼ bằng code** và **CHẤM bằng subagent độc lập**, lặp đến khi đạt.

## Bộ công cụ vẽ (scripts/hoathinh/chibi/)
- **`goc.py` – THÔNG SỐ GỐC (nền chung, chốt từ Ngộ Không bản 9).** Nguồn chuẩn duy nhất của tỉ lệ:
  - `KIEU` = kiểu vẽ (canvas 800×1000, R=120, viền 0.085R, viền chi tiết 0.05R, nền `#F6F3EC`, mực `#0A0807`).
  - `TI_LE` = **tỉ lệ khung** (thân "bia mộ" + bàn tay) – **GIỮ NGUYÊN cho mọi nhân vật**: than_lech_x −0.31, than_tren_y 0.98, than_cao 2.15, rộng 1.26→1.66, bo 0.15/0.38, tay (1.38, 0.88, r 0.24).
  - `MAT_GOC` = khuôn mặt nền (mắt đen bầu dục 0.14×0.17R + đốm trắng đứng, lông mày cong vòm hiền may_y −0.25, má hồng); chỉ cần đặt `mat`/`ma_hong_vt` (vị trí 2 mắt) theo nhân vật.
  - `tao_P(**rieng)` = tạo bảng P: nền gốc + phần riêng (K/M hợp nhất, khoá khác thay trực tiếp).
- `ve.py` – bút chung: `Canvas`, `part()` (vẽ viền cả nhóm rồi tô → khối liền), `stroke`, `tube`, `catmull`, hình cơ bản.
- `khung.py` – 4 hàm dựng + phụ kiện, mọi số theo **R**: `dau()`+`vien_dau()` (viền trên gồ ghề theo chỏm lông), `than()`, `ban_tay()`, `khuon_mat()`, `duoi_xoan()`; lớp `Khung` (toạ độ `H()` theo đầu, `B()` theo thân).
- `<tên>.py` – mỗi nhân vật: `P = tao_P(... phần riêng ...)`, `draw()`, `chi_so()` (bảng mã A/B/C/D), xuất ảnh nhân vật + bảng chỉ số (`bang.py`) + ảnh so mẫu.
- Mẫu: `assets/nhan-vat/mau/<tên>-mau.png`; ảnh ra: `build/thu-hoathinh/nhan-vat/`; bản chốt: `assets/nhan-vat/<tên>.png`.

## Vẽ NHÂN VẬT MỚI (giữ nguyên tỉ lệ)
1. Copy `ngo_khong.py` → `<tên>.py`, đổi `P = tao_P(...)`: **giữ nguyên K (tỉ lệ)**, chỉ thay:
   - màu (`c_*`), vị trí mắt (`M=dict(mat=[...], ma_hong_vt=[...])`),
   - "trên đầu" (tóc/mũ/nón: `toc`/`tai`/phụ kiện), trang phục (`co_*`, `that_lung`, `gau`, `vay_*`...), đồ cầm tay (thay `gay_*` bằng vật khác), đuôi nếu có.
2. Phần riêng vẫn theo R nên tự khớp khung. Chạy → chấm (mục dưới) → sửa.
Mẫu tham chiếu đã chốt: Ngộ Không `scripts/hoathinh/chibi/ngo_khong.py` + `docs/nhan-vat/ngo-khong-chi-so.md`.

## Luật phong cách đã chốt (xem [[nhan-vat-chibi-tay-du]])
Đầu tròn R, lệch phải so với thân (mặt quay 3/4); thân "bia mộ" loe đáy; **không cánh tay** – chỉ bàn tay tròn khi cầm đồ, đồ đè lên tay; viền đều ~0.085R màu đen; màu phẳng; mắt đen bầu dục + đốm trắng đứng + quầng má nhạt; lông mày dày cong; chỏm lông gai sắc lệch phải khía V sâu + nét lông trong; kim cô võng nhẹ 2 nút vòng khuyên dồn phải; đuôi xoắn trơn đều.

## Vẽ
1. Có ảnh mẫu → đo tỉ lệ trước: phóng to + kẻ lưới (PIL) + lấy mẫu màu (`getpixel`) + đo độ dày viền. Quy về đơn vị R.
2. Sửa bảng `P` (hoặc thêm hàm vào `khung.py` nếu cần bộ phận mới). Chạy script → xem ảnh → chỉnh.
3. **Luôn gửi người dùng ẢNH BẢNG CHỈ SỐ** mỗi lần đưa thông số (xem [[chi-so-kem-anh]]).

## Chấm (bắt buộc subagent độc lập – người vẽ không tự chấm)
Theo skill `cham-nhan-vat`: gọi Agent general-purpose, đưa ảnh mẫu + ảnh bản vẽ + code; yêu cầu TỰ ĐO ảnh mẫu (đừng đưa số của người vẽ). Chấm 5 nhóm T/Đ/M/N/C = 100 (đạt ≥85, mỗi nhóm ≥70%). Có thể chấm RIÊNG một bộ phận (vd tóc + kim cô) khi cần.

## Vòng lặp
Chấm → nếu < 85: áp góp ý (dạng `khoá: cũ → mới`) → render lại → gọi agent MỚI chấm lại → lặp. Lưu điểm từng vòng vào `docs/nhan-vat/<tên>-cham-diem.md`. Chốt khi đạt.

## Lịch sử điểm Tôn Ngộ Không
Bản 4: 61/100 → Bản 5: 79/100 → (tóc+kim cô riêng: 68 → đã sửa gai sắc/nút dồn phải). Chi tiết: `docs/nhan-vat/ngo-khong-chi-so.md`.
