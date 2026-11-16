# Phong cách video dài (16:9) – bản nháp chờ chốt

> Rút ra sau khi xem Sử Lược (16/11/2026). Chỉ học **nguyên tắc**, không chép bản đồ, chân dung, khung thoại hay hiệu ứng riêng của họ.
> Trạng thái: 🟡 nháp – người dùng duyệt từng mục rồi đổi thành ✅.

## 0. Quy trình làm video (đã duyệt 16/11)
- ✅ Chia theo cảnh + cache: sửa cảnh nào render lại cảnh đó.
- 🟡 Tách lớp (nền / chuyển động / phụ đề / âm thanh) – chờ duyệt.
- ✅ Bản nháp chất lượng thấp (540p, 15fps) trước; chốt xong mới render 1080p.
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
| # | Hành động | Hiệu ứng đề xuất | Chốt |
|---|---|---|---|
| H1 | Hành quân bộ | Cờ trượt theo đường, để lại vệt chấm mờ | 🟡 |
| H2 | Hành quân thủy | Thuyền trượt, vệt sóng chữ V phía sau | 🟡 |
| H3 | Giao chiến | Dấu va chạm đỏ sơn mài + vòng sóng đồng tỏa ra 2–3 nhịp (không dùng kiếm + lửa giống Sử Lược) | 🟡 |
| H4 | Chiếm thành | Cờ phe thắng cắm lên ký hiệu thành, màu vùng loang dần sang màu phe thắng | 🟡 |
| H5 | Thắng trận | Dấu X đỏ lên cờ phe thua (đã có trong `bandoco`) | 🟡 |
| H6 | Thua / rút chạy | Cờ nghiêng, lùi theo đường rút, mờ dần | 🟡 |
| H7 | Phục binh | Cờ hiện mờ dần từ rừng/núi, viền nhấp nháy 1 lần | 🟡 |
| H8 | Tướng tử trận | Cờ đổ, chân dung chuyển xám | 🟡 |
| H9 | Hỏa công | Lửa cháy lan trên vùng/thuyền | 🟡 |
| H10 | Thủy triều | Mực nước lên/xuống (bản đồ trận hoặc sa bàn) | 🟡 |
| H11 | Thời gian trôi | Đồng hồ năm chạy (chữ ký kênh) | 🟡 |
| H12 | Trích lời người xưa | Khung trích dẫn ở góc, ghi nguồn bên dưới. **Chỉ dùng cho lời được sử chép lại**, không bịa thoại | 🟡 |

## 5. Kịch bản video dài: kể chi tiết, không liệt kê
- ❌ Liệt kê: "Năm 938 có trận Bạch Đằng, Ngô Quyền thắng."
- ✅ Kể: chuẩn bị → cách làm → diễn biến từng bước → vì sao thắng → hệ quả.
- **Mỗi chi tiết vẫn phải có nguồn.** Chi tiết nhiều hơn thì lấy từ **nhiều nguồn hơn**, không thêm thắt:
  - Sử Việt: Đại Việt sử ký toàn thư, Việt sử lược, Khâm định Việt sử thông giám cương mục.
  - Sử Trung Quốc chép phía đối phương (ví dụ Nam Hán): thêm bối cảnh, góc nhìn bên kia.
  - Nghiên cứu, khảo cổ: ghi rõ niên đại hiện vật thuộc trận nào.
- Chi tiết sử không chép (số ngày chuẩn bị, "làm ngày đêm"…) thì **không đưa vào**, hoặc chỉ nói khi có nhà nghiên cứu nêu và ghi rõ là ý kiến của ai.
- Khung một tập (10–15 phút): móc (30s) → bối cảnh → nhân vật → chuẩn bị → trận đánh (bản đồ trận) → vì sao thắng (sa bàn) → hệ quả → "Lùi tiếp: năm …".
