# Bạch Long Mã (Bộ Bút) – nhật ký chấm

## Vòng 1 – 20/11/2026 – 76/100
A 18 · B 12 · C 12 · D 12 · E 10 · F 12. Người xem đoán "pony trắng / kỳ lân con"; bóng dáng dễ nhầm cừu/alpaca (đầu tròn, bờm búp tròn, đuôi cục bông, mõm lồi nhỏ).
Khung mới `KhungNgua` (khung.py, dáng `ngua`) + bộ phận ngựa trong `bo_phan.py` (duoi_ngua, chan_xa/gan, than_ngua, yen_ngua, khan_ngua, bom_sau/tren, tai_ngua, dau_ngua, sung_rong, cuong_ngua) + `LOP_NGUA` trong ve.py.

Đã sửa theo góp ý:
- Mõm to và dài: tâm (0.70, 0.50), rx 0.70, ry 0.48 (chóp mõm 1.40R). Thêm nét trong ngăn mõm với má. Lỗ mũi hình hạt đậu nghiêng 28°, đặt sát chóp mõm. Miệng rộng 0.34R.
- Đuôi đổi thành dải chữ S buông, chóp hất ra ngoài cách đất khoảng 0.4R, có sợi lông. Bờm sau gáy còn 3 búp to, thêm 2 lọn dài buông qua mép trước yên.
- Chân: bụng nâng 0.2R, chân dài khoảng 0.7R, ống chân thon xuống móng, dải móng cao 0.15R. Chân xa dịch phải thêm 0.12R và có vệt sáng mép trái.
- Đai bụng bản 0.17R, cong theo bụng, đặt giữa yên. Khăn có thêm vạt tam giác trước ngực, hoa mây 0.27R đặt trên vạt. Nút khăn to 0.3R dời ra dưới mõm, hai tà khăn bầu.
- Sừng dày 0.15–0.17R, nhánh chĩa ra sau và lên. Bóng đổ của yên đổi sang màu bóng lông; góc sau của yên hạ vào trong đường lưng.
- Chưa sửa: mắt Hiền hạ mí trên (hàm `mat` dùng chung cho 5 nhân vật, sửa sẽ đổi cả 4 nhân vật đã chốt).

## Vòng 2 – 20/11/2026 – 81/100 ✅ ĐẠT
A 20 · B 13 · C 12 · D 13 · E 11 · F 12. Người xem đoán "ngựa con / pony trắng có sừng", "ngựa rồng"; hết nhầm cừu/alpaca.

Mài thêm sau khi đạt (không chấm lại):
- Chóp đuôi thêm lọn cuộn mây r 0.19R có xoắn, cùng kiểu mây với bờm.
- Bờm sau gáy: 3 búp thu nhỏ khoảng 10% và kéo vào trong.
- Tà khăn gập vào trong, viền trong, không góp viền ngoài dày (`dang_phu`). Nút khăn có mảng sáng để tách khỏi màu mực.
- Má phải dời vào (0.78, −0.03), hết bị vành đầu cắt. Miệng lùi vào 0.08R, rộng 0.40R.
- Còn để lại: chân vẫn thẳng như cột (chưa làm khuyết khoeo, chưa nghiêng); Hiền và Vui chung kiểu mắt (do hàm `mat` dùng chung).

Chốt → `assets/nhan-vat/but/bach-long-ma.png` + `bach-long-ma-bieu-cam.png`; ghép vào `thay-tro.png` (5 nhân vật).
