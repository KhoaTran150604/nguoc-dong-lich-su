---
name: bo-ve
description: Kỹ thuật vẽ nhân vật chibi bằng BỘ BÚT (scripts/hoathinh/but/, thư viện skia) – 12 luật vẽ đẹp (nét 3 cấp, bóng phẳng, khối cộng/trừ, khung chung, vũ khí thấp, một tay), API lõi, danh mục bộ phận có sẵn và cách thêm bộ phận mới. Dùng mỗi khi viết/sửa spec nhân vật trong scripts/hoathinh/but/nv/ hoặc thêm hàm bộ phận vào bo_phan.py.
---

# Bộ Bút – tự vẽ nhân vật chibi bằng code

Bộ vẽ **do Claude tự vẽ 100%** – không trace, không vector hoá ảnh AI (người dùng chốt 20/11/2026: phụ thuộc ảnh Gemini thì khó kiểm soát chất lượng). Ảnh mẫu (nếu có) chỉ để **tham khảo đặc trưng**, không để bám nét.

```
scripts/hoathinh/but/
  but.py      lõi: Hinh (khối + − &), cong/duong (Bezier mượt), net_thuon, Buc (tô/kẻ/bóng/cắt), toi/sang (màu bóng)
  khung.py    khung chung (tỉ lệ từ chibi/goc.py) + LUẬT VŨ KHÍ (truc_vu_khi, tren_truc)
  bo_phan.py  thư viện bộ phận: tai, dau_da, toc_chom, vong_tran, rau_quai_non, mat(+mieng), ao_giao_linh, chuoi_so, ban_tay, vu_khi(gay, nguyet_san)
  nv/<ma>.py  SPEC từng nhân vật (dict NV) – chỉ số liệu, không code vẽ
  ve.py       render: thứ tự LỚP cố định + CLI
```
Cài: `pip install skia-python` (đã có trên máy Windows). Chạy:
```
python scripts/hoathinh/but/ve.py <ma>                 # → build/thu-hoathinh/but/<ma>.png
python scripts/hoathinh/but/ve.py <ma> --bong-den      # + <ma>-bong.png (phép thử bóng dáng)
python scripts/hoathinh/but/ve.py <ma> --bieu-cam-bang # + <ma>-bieu-cam.png (6 biểu cảm)
python scripts/hoathinh/but/ve.py <ma> --scale 2       # ảnh 1600×2000, nét vẫn sắc
python scripts/hoathinh/but/ve.py <ma> --so-cu <ảnh cũ> # ảnh so cũ/mới
```

## 12 luật vẽ đẹp (bắt buộc)
1. **Nét 3 cấp.** Viền NGOÀI (bóng dáng cả nhân vật) dày nhất 0.075R – tự tính ở `chot_vien()`, đừng tự kẻ. Viền TRONG (ranh giới bộ phận) 0.042R. CHI TIẾT (sợi tóc, nếp áo, gờ tai) 0.030R và **thuôn hai đầu** (`b.net`). Không bao giờ dùng một độ dày cho tất cả.
2. **Khối bằng phép cộng/trừ**, không tự tính giao điểm: tóc = `dau().phong(no) & vung_tren_chan_toc`; lưỡi liềm = `tron − tron dịch`; vòng trán = `dải & đầu nở`. Hình mới nghĩ theo khối trước, nét sau.
3. **Đường cong mượt** qua điểm (`cong`, `duong`) – điểm `(x, y, 0)` là góc nhọn có chủ ý (mũi giáo, chòm râu). Không đa giác gãy khúc.
4. **Ánh sáng TRÊN-TRÁI** cho mọi nhân vật. Bóng = 1 mảng phẳng mép cứng: `b.bong(h, toi(mau), dx>0, dy>0)` trong `with b.cat(h)`. Bóng đổ lên vật khác: `b.do_bong`. Vệt sáng chỉ ở tóc/kim loại (`sang`). **CẤM gradient, blur, glow** (luật kênh).
5. **Màu bóng tự sinh** bằng `toi(mau, k)` (k 0.06 da · 0.09–0.12 vải · 0.14 kim loại) – không tự chọn màu bóng bằng mắt.
6. **Bảng màu ≤ 5 màu chính** + da + mực; một màu chủ đạo chiếm phần lớn (áo), một màu nhấn (vàng/đỏ) cho phụ kiện.
7. **Khung chung bất biến** (`khung.py` lấy tỉ lệ từ `chibi/goc.py`): đầu tròn R, thân bia mộ lệch trái, mặt 3/4 quay phải. Nhân vật vạm vỡ/mập: `dang='map'`. Không tự chế tỉ lệ thân.
8. **MỘT tay duy nhất** (bàn tay tròn bên phải), vẽ **đè lên cán** vũ khí – có nét ngón cái gợi đang nắm.
9b. **KHÔNG CÓ CỔ** (người dùng chốt 21/11/2026): đầu đặt thẳng lên mép trên thân. Không vẽ trụ cổ, không lấp khe cằm–vai bằng mảng da, không đổi khung để lộ cổ. Khe nhỏ giữa cằm và vai trái là chủ ý của khung (như Ngộ Không).
9. **Vũ khí cầm THẤP, chuẩn Ngộ Không**: trục qua tâm bàn tay, nghiêng 8.7°, đỉnh (kể cả lưỡi, hoa văn) ≤ tâm đầu − 1.76R, chân ở + 3.20R. Mọi vũ khí vẽ theo `_khung_truc(k)` → `P(s, w)` (s tính từ ĐỈNH xuống), không đặt toạ độ tự do.
10. **Thứ tự lớp cố định** (`ve.py LOP`): tai → thân/áo → phụ kiện cổ → vũ khí → đầu → tóc → vòng trán/mũ → râu → mặt → bàn tay → viền ngoài.
11. **Bóng dáng đọc được**: ảnh `--bong-den` tô đen vẫn phải nhận ra nhân vật (nhờ tóc/mũ/vũ khí). Đặc trưng nhận diện đặt ở RÌA bóng dáng, không giấu ở giữa.
12. **Mặt dễ thương, không bôi xấu**: mắt đen bầu dục + 2 đốm sáng (đốm to trên-trái), má hồng, mày thuôn. Biểu cảm là tham số (`mat.bieu_cam`: hien/vui/quyet/ngac/buon/cuoi_nham; `mat.mieng`: cuoi/cuoi_mo/o/thang/noi/None) – dùng lại khi làm hoạt hình.

## Spec nhân vật (`nv/<ma>.py`)
Chép `nv/sa_tang.py` làm mẫu. Khoá nào có thì bộ phận đó được vẽ (xem `LOP`):
- `ten, ma, dang` · `mau` (da, toc, rau, vang, ao, ao_trong, co, dai, gau, so, bac, can…)
- `tai` (trai/phai: dx, dy, rx, ry, xoay) · `toc` (chan = điểm chân tóc trái→phải, no, soi) · `vong_tran` (duong, day, hoa_van)
- `rau` (mep, no, chom, soi, ria) · `mat` (vt 2 mắt, rx, ry, bieu_cam, mieng, mieng_vt, mau_may, may_day…)
- `ao` (dai = (y0, y1) đai lưng, v = điểm cổ V, gau, co_day, nep) · `chuoi_so` · `vu_khi` (kieu + tham số)
Toạ độ đầu: (dx, dy) theo R từ TÂM ĐẦU (`k.H`). Toạ độ thân: dx từ tâm thân, dy từ MÉP TRÊN thân (`k.B`).

## Thêm bộ phận mới (mũ, tóc kiểu khác, đuôi, vũ khí…)
1. Viết hàm `ten(b, k, S)` trong `bo_phan.py`: dựng khối bằng luật 2–3, tô bằng `b.khoi(h, mau, 'trong'|'ct', dang=True/False)` (`dang=True` nếu bộ phận nằm ở rìa bóng dáng), bóng bằng luật 4–5, nét chi tiết bằng `b.net`.
2. Vũ khí mới: thêm hàm vào `VU_KHI_KIEU` – mọi điểm qua `P(s, w)`, đỉnh vũ khí ở s=0.
3. Đăng ký vào `LOP` trong `ve.py` đúng vị trí lớp (luật 10). Không phá thứ tự cũ.
4. Render thử với một nhân vật đã chốt để chắc bộ phận cũ không đổi.

## Bộ phận đang có
| Hàm | Dùng cho | Ghi chú |
|---|---|---|
| `tai` | mọi người | tai trái to, phải nhỏ (3/4) |
| `dau_da` | mọi người | bóng trăng khuyết dưới-phải |
| `toc_chom` | tóc chụp đỉnh | chân tóc theo điểm; `bup` = búp tóc xoăn thò khỏi vành đầu (chỉ đặt ở ĐỈNH, kín vòng sẽ thành bờm sư tử) |
| `vong_tran` | vòng kim loại trán | hoa văn mây ở chính diện |
| `rau_quai_non` | râu ôm hàm + chòm | `bup` búp râu ở cằm (45°–140°), `chom_dai`, `ria` tuỳ chọn |
| `mat` / `mieng` | mọi người | 6 biểu cảm (buồn có mí trĩu); miệng: cuoi, cuoi_mo, noi, o, mim, buon, thang |
| `_bup(k, goc, r, d)` | tiện ích | búp tròn quanh vành đầu – dùng cho tóc xoăn, râu rậm, lông xù |
| `ao_giao_linh` | áo cổ chéo | đúng chiều "y" (vạt trái đè phải), đai + nơ, gấu |
| `chuoi_so` | Sa Tăng | sọ dễ thương, vẽ từ ngoài vào giữa |
| `mat_na` | khỉ (Ngộ Không) | mặt nạ da 2 thùy + mõm + mũi lông, cắt trong đầu |
| `duoi_xoan` | khỉ | đuôi xoắn thuôn, toạ độ thân |
| `_gai` | tiện ích | chỏm lông gai quanh vành đầu (`gai` trong spec) |
| `ban_tay` | mọi người | đè lên cán |
| `_tai_heo` | Bát Giới | `tai.kieu='heo'`: tai quạt cụp, gốc giấu sau đầu, lòng hồng |
| `mom_heo` | Bát Giới | `mat.mom`: mõm bầu dục + 2 lỗ mũi; `mat.ma_vt` đặt má riêng khi mõm chiếm giữa mặt |
| `mu` → `mu_tron` · `mu_ti_lu` | Bát Giới · Đường Tăng | `mu.kieu`: mũ tròn vành vàng + hoa mây / mũ Tì Lư 5 cánh sen + dải buông |
| `_bung` (`ao.mo`) | Bát Giới | áo phanh lộ bụng + rốn; `bung_loi` cho bụng phình ra rìa bóng dáng |
| `khan_co` | Bát Giới | khăn cổ thắt nút + 2 vạt |
| `_ca_sa` (`ao.ca_sa`) | Đường Tăng | cà sa vắt chéo, lưới gạch so le (tối theo mảng bóng) |
| `gay_nhu_y` · `nguyet_san` · `cao_chin_rang` · `tich_truong` | Ngộ Không · Sa Tăng · Bát Giới · Đường Tăng | theo trục chuẩn; `vu_khi.ha` hạ cả vũ khí xuống |

Bộ phận có thêm tham số: `vong_tran.nut` (nút vòng khuyên kim cô thay hoa văn mây), `mat.mui` (2 lỗ mũi), `ao.vay`+`vay_soc` (váy da hổ + sọc), `ao.gau_rang` (gấu răng cưa), `tai.trong` (cỡ lòng tai), `mau.dau` (màu đầu khác màu da = lông).

**Chi tiết mảnh (răng cào, lòng vòng):** viền ngoài 9px nuốt mất chi tiết ≤ 15px thành vạch đen. Cách xử lý:
- Chi tiết mảnh: vẽ viền 'trong', không góp vào `b.dang` mà thêm vào `b.dang_phu` (chỉ dùng cho ảnh bóng dáng).
- Vòng rỗng: góp ĐĨA NGOÀI vào `b.dang`, còn lỗ thì thêm vào `b.lo` (ảnh bóng dáng sẽ khoét trắng lỗ này).
