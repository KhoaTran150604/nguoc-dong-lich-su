# Bạch Cốt Tinh (Bộ Bút) – nhật ký chấm

## Vòng 1 – 20/11/2026 – 79/100
A 18 · B 14 · C 13 · D 11 · E 10 · F 13. Người xem đoán "cô bé phù thuỷ tóc bạc cầm gậy đầu lâu"; mái tóc giống mũ trùm.
Tự vẽ, không có ảnh tham khảo (Gemini hết lượt). Bộ phận mới trong `bo_phan.py`:
- `toc_dai`: tóc dài buông sau đầu và thân, là lớp đầu tiên.
- `tram_xuong`: trâm xương + nơ.
- `gay_xuong`: gậy xương có sọ nhỏ trên đỉnh, nơ ruy băng, đầu khớp ở chuôi.
- `_so_nho`.
- `mat.mi`: lông mi.
- `mat.mi_xech`: mí trên xếch theo từng biểu cảm.
- `toc.loc`: lọn tóc ôm mặt.
- `toc.bong`: chỉnh hướng bóng tóc.

Đã sửa theo góp ý:
- Mái cắt 5 chóp mềm: chóp ở −0.28R, khe ở −0.45R. Bóng tóc chỉ để nửa phải (`bong=(0.14, 0)`), bỏ dải xám ngang. Có 5 nét sợi tóc. Thêm 2 lọn ôm mặt buông tới +0.80R.
- Tóc đổi sang bạc ánh tím `#D9D6EA` để tách khỏi áo trắng.
- Tóc sau lưng thò ra ngoài viền thân hai bên, đuôi sóng. Bên phải dừng sau vai, cách bàn tay xa.
- Gậy xương: sọ to lên r 0.30R, chỉ nới xuống dưới (đỉnh giữ nguyên). Khâu tím đổi thành nơ ruy băng có 2 đuôi bay sang phải, không góp viền ngoài dày (`dang_phu`). Trâm xương nhô khỏi vành tóc.
- Mắt "hiền" hạ mí, xếch đuôi (mắt híp tinh nghịch). "Quyết" xếch sâu hơn để khác "hiền".
- Chưa sửa: đường gấu tím cụt ở mảng bóng phải. Đây là hàm áo dùng chung, 4 nhân vật đã chốt cũng như vậy.

## Vòng 2 – 20/11/2026 – 83/100 ✅ ĐẠT
A 20 · B 14 · C 13 · D 11 · E 11 · F 14. Người xem đoán "cô phù thủy tóc tím cầm gậy đầu lâu". Khán giả quen phim 1986 đoán ra Bạch Cốt Tinh nhờ trâm xương, gậy sọ, áo trắng.

Mài thêm sau khi đạt (không chấm lại):
- Tóc sau lưng: mép trái liền một đường, nới ra −1.46R. Hai đuôi nhọn, không còn móc cong. Đuôi bên phải dài tới +2.14R, vẫn cách bàn tay.
- Chỏm tóc còn 4 sợi ngắn, không chạm mái, để đỡ giống mũ bảo hiểm.
- Nơ tóc to 0.19R, dời lên (−0.10, −1.05) cho nhô khỏi viền đầu, màu đậm `#8E6BB8`.
- Sọ trên gậy: hàm thò rõ dưới sọ nên ảnh tô đen ra hình sọ, đỉnh sọ giữ nguyên.
- Còn để lại: tóc vẫn ngả tím lilac; tông áo nhạt hơn hẳn nhóm thầy trò.

Chốt → `assets/nhan-vat/but/bach-cot-tinh.png` + `bach-cot-tinh-bieu-cam.png`.

**Người dùng duyệt bằng mắt – 20/11/2026.**
