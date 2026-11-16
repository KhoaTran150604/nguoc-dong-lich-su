# Phong cách video dài (16:9) – đã chốt

> Rút ra sau khi xem Sử Lược (16/11/2026). Chỉ học **nguyên tắc**, không chép bản đồ, chân dung, khung thoại hay hiệu ứng riêng của họ.
> Trạng thái: mục 0 và 4 đã chốt (16/11/2026); mục 1–3, 5 là nguyên tắc đã thống nhất. Muốn sửa hiệu ứng nào thì sửa hàm cùng tên (H1…H12) trong `scripts/hieuung/demo.py`, render lại và cập nhật bảng.

## 0. Quy trình làm video (đã duyệt 16/11)
- ✅ Chia theo cảnh + cache: sửa cảnh nào render lại cảnh đó.
- ✅ Tách lớp (nền / chuyển động / phụ đề / âm thanh).
- ✅ Bản nháp chất lượng thấp (540p, 15fps) trước; chốt xong mới render 1080p.
- ✅ Âm thanh: skill `giong-doc` (ZeroTTS Gia Huy). Lời đọc video dài ở `docs/videos/NN-loi-doc.txt`, mỗi dòng một câu phụ đề. Video 10–20 phút tạo giọng ~15–25 phút (có `--check` có thể >1 tiếng, ước tính từ Short, chưa chạy thử) → chạy nền. File `.json` mốc từng câu dùng để đặt thời lượng cảnh, và khi cắt Short từ video dài thì cắt luôn đoạn giọng tương ứng, không tạo giọng lại.
- ✅ Tăng tốc: render song song, đẩy khung hình thẳng vào ffmpeg.

## 1. Chuyển động: "tĩnh là mặc định"
- Phần lớn thời lượng là bản đồ **đứng yên**. Thứ duy nhất chuyển động là **cờ nhân vật / quân** đi theo lời kể. Khi không có gì cần đi thì để yên 5–20 giây.
- Camera chỉ lia hoặc zoom khi **chuyển sang vùng khác**, chậm và êm (ease).
- Không dùng hiệu ứng nền chạy liên tục (mây trôi, hạt bụi…). Người xem tập trung vào câu chuyện.
- Lợi ích kỹ thuật: đoạn tĩnh render bằng **1 khung hình + thời lượng**, gần như không tốn thời gian.

## 2. Bản đồ: chi tiết, sắc nét
- Vẽ nền ở **4K** (3840×2160) để zoom vào vẫn nét. Chữ địa danh vẽ vector ở **bước cuối** theo đúng độ zoom, không phóng to từ ảnh nhỏ.
- Chữ địa danh dùng Playfair Display đậm, có viền mảnh màu kem/mực để nổi trên mọi nền.
- Bộ ký hiệu riêng: núi, rừng, sông, thành, kinh đô, cửa biển. Màu theo nhận diện kênh (giấy dó, vàng đồng, đỏ sơn mài), **không** dùng màu và kiểu vẽ của Sử Lược.
- Vẫn giữ các quy tắc: "minh họa, ranh giới gần đúng"; Hoàng Sa, Trường Sa trên bản đồ toàn cảnh hiện đại; không dùng hình chữ S cho thời xưa.

## 3. Hai tầng bản đồ
| Tầng | Dùng khi | Nội dung |
|---|---|---|
| **Bản đồ vùng** (chiến lược) | Kể bối cảnh, hành quân, lãnh thổ | Toàn vùng, các phe, đường hành quân |
| **Bản đồ trận** (chiến thuật) | Đánh nhau | Nền địa hình gần (bãi sông, cửa biển, cánh đồng), các khối quân xếp hàng, có thể dùng sa bàn mặt cắt |

Chuyển tầng: zoom vào điểm giao chiến → chuyển cảnh mờ sang bản đồ trận → đánh xong zoom ra về bản đồ vùng.

## 4. Thư viện hiệu ứng chuẩn (chốt một lần, dùng lại mãi)
| # | Hành động | Hiệu ứng | Chốt |
|---|---|---|---|
| H1 | Hành quân bộ | Chỉ cờ trượt theo đường, không vẽ vệt | ✅ |
| H2 | Hành quân thủy | Thuyền gỗ buồm cánh dơi nhìn ngang, gợn sóng sau đuôi | ✅ |
| H3 | Giao chiến | Hai cờ áp sát → hai kiếm chém vào nhau (lóe sáng lúc chạm) + lửa bùng phía dưới. Hình vẽ riêng của kênh | ✅ |
| H4 | Chiếm thành | Cờ phe thắng cắm lên ký hiệu thành, màu vùng loang dần sang màu phe thắng | ✅ |
| H5 | Thắng trận | Dấu X đỏ vẽ từng nét lên cờ phe thua | ✅ |
| H6 | Thua / rút chạy | Cờ nghiêng, lùi theo đường rút, mờ dần; không vẽ vệt | ✅ |
| H7 | Phục binh | Nhiều cờ nhỏ lấp ló sau núi rừng, rồi cờ tướng hiện ra, viền sáng 1 lần | ✅ |
| H8 | Tướng tử trận | Cờ đổ, chân dung chuyển xám | ✅ |
| H9 | Hỏa công | Lửa cháy lan dần qua từng thuyền | ✅ |
| H10 | Thủy triều | Khung sa bàn nhỏ: nước lên cọc chìm, nước rút thuyền mắc cọc | ✅ |
| H11 | Thời gian trôi | Vòng trống đồng quay ngược chiều kim đồng hồ, năm chạy lùi | ✅ |
| H12 | Trích lời người xưa | Khung trích dẫn ở góc, ghi nguồn bên dưới. **Chỉ dùng cho lời được sử chép lại**, không bịa thoại | ✅ |

Demo: `assets/hieuung/demo-hieuung-nhap.mp4` · code: `scripts/hieuung/demo.py`

## 5. Kịch bản video dài: kể chi tiết, không liệt kê
- ❌ Liệt kê: "Năm 938 có trận Bạch Đằng, Ngô Quyền thắng."
- ✅ Kể: chuẩn bị → cách làm → diễn biến từng bước → vì sao thắng → hệ quả.
- **Mỗi chi tiết vẫn phải có nguồn.** Chi tiết nhiều hơn thì lấy từ **nhiều nguồn hơn**, không thêm thắt:
  - Sử Việt: Đại Việt sử ký toàn thư, Việt sử lược, Khâm định Việt sử thông giám cương mục.
  - Sử Trung Quốc chép phía đối phương (ví dụ Nam Hán): thêm bối cảnh, góc nhìn bên kia.
  - Nghiên cứu, khảo cổ: ghi rõ niên đại hiện vật thuộc trận nào.
- Chi tiết sử không chép (số ngày chuẩn bị, "làm ngày đêm"…) thì **không đưa vào**, hoặc chỉ nói khi có nhà nghiên cứu nêu và ghi rõ là ý kiến của ai.
- Khung một tập (10–15 phút): móc (30s) → bối cảnh → nhân vật → chuẩn bị → trận đánh (bản đồ trận) → vì sao thắng (sa bàn) → hệ quả → "Lùi tiếp: năm …".
