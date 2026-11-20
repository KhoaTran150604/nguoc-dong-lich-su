# Thuật toán YouTube & chiến thuật kênh (ghi 20/11/2026)

> Mục đích: hiểu **cơ chế** phân phối của YouTube để chọn chủ đề/định dạng **bằng logic, không cảm tính**. Đúc kết từ buổi brainstorm 20/11 + tra cứu nguồn 2025–2026 (xem mục 9). Khi nào tactics mâu thuẫn với file khác (vd `thu-nghiem-30-ngay.md`), **lấy file này làm chuẩn** vì nó ghi lý do.

---

## 1. Mô hình gốc: YouTube KHÔNG "đẩy", nó "ghép"
Không có cái máy đi quảng bá video. YouTube là **hệ thống gợi ý**: với mỗi video, nó đi tìm *người có khả năng xem hết và thích*.
1. Video mới → **chiếu thử** cho một nhóm nhỏ (vài chục–vài trăm impression).
2. Đo 2 thứ: **CTR** (thấy thumbnail → có bấm không) và **mức hài lòng** (xem bao lâu, có xem tiếp, like/comment).
3. Tốt **so với video tương tự** → chiếu rộng hơn. Dở → dừng.

→ **Hệ quả:** packaging (tiêu đề + thumbnail) quyết định CTR, CTR quyết định video sống/chết ở vòng thử. Video dài #1 (~7 view) **chết ở vòng thử** vì: kênh mới (không có lịch sử khán giả để ghép) + từ khóa sai (không ai tra thấy) + CTR thấp. Đây là **bình thường** với kênh 0 sub.

## 2. Video "treo" ở đâu — 7 mặt tiền
| Cửa | Cơ chế | Với kênh sử |
|---|---|---|
| **Trang chủ (Home)** | Theo **lịch sử xem** từng người | Cửa lớn nhất cho video dài, kênh mới gần như trống |
| **Gợi ý / Xem tiếp (Suggested)** | "Người xem A cũng xem B" | ⭐ Quan trọng nhất: video **cùng chủ đề tự gợi ý cho nhau** |
| **Tìm kiếm (Search)** | Theo **từ khóa** | ⭐ Sử là thứ người ta **chủ động tra** → video dài sống lâu ở đây |
| **Feed Shorts** | Vuốt, auto-serve | Nguồn reach lớn nhất cho người mới biết kênh |
| Đăng ký + Thông báo | Người đã sub | Yếu khi kênh mới |
| Trang kênh / Playlist | Người đã vào kênh | Giữ chân, tăng session |
| Bên ngoài | Share TikTok/FB, nhúng | Mang khán giả của mình vào |

## 3. Hai hệ thống TÁCH BIỆT: Short vs video dài
- **Short**: người đang vuốt sẵn, feed tự nhét → impression gần như vô hạn. Đo bằng **"Viewed vs Swiped away"**, % xem, loop. → **View nhiều nhưng rẻ, khán giả không chủ đích.**
- **Video dài**: người phải *tự quyết định* bấm + bỏ ra 10–20 phút → rào cản cao → **ít view nhưng đắt** (watch time = tiền, đúng người quan tâm sử).
- **Short KHÔNG bơm view cho video dài** (từ 2022 YouTube bỏ lịch sử xem Short khỏi gợi ý video dài). Chỉ nối qua 4 cầu, đều yếu/thủ công:
  1. Sub (feed sub + thông báo nay rất yếu)
  2. Nhận diện thương hiệu (mềm, chậm)
  3. Phễu thủ công (ghim link, end screen) — bạn tự làm
  4. ⭐ **Chất lượng tệp sub**: Short *giống* nội dung dài → sub về là **đúng người chịu xem dài**
- → **Short làm 3 việc, không phải bơm view dài:** (a) nhận diện, (b) **nghiên cứu thị trường rẻ** (test hook/chủ đề trước khi bỏ công làm video 15 phút), (c) tự kiếm tiền (Shorts có chia doanh thu riêng).

## 4. ĐỊNH LUẬT SHORT TỰ CHỨA (kết luận brainstorm 20/11)
> **Mỗi Short phải sống sót khi bị chiếu LẠNH cho người chưa từng biết kênh, chưa xem gì khác.** Cái gì cần bối cảnh từ Short/video khác = **gãy**.

**Vì sao Short nhiều phần ("Phần 1/2/3…") hỏng:**
- Feed Shorts chiếu **ngẫu nhiên, không theo thứ tự**. Mỗi Short phân phối độc lập cho nhóm người khác nhau → gần như **không ai được chiếu 1→2→3 đúng thứ tự**.
- Người lạ bị nhét "Phần 4" → **không hiểu gì** → vuốt trong 2 giây → **cả 4 tín hiệu sụp**: không like, không loop, thời lượng xem thấp, vuốt sang **kênh khác**.
- Thực tế: P1 tạm ổn, P2 tụt, P3 tụt nữa, P4–P6 gần chết.
- → **Short kết bằng "xem tiếp trên kênh" thua 2 lần**: dẫn sang video dài ~0.1% (gần như 0) *và* tự giết reach của chính nó.

**Làm đúng — phân biệt 2 thứ:**
- ❌ **Nối tiếp (serial):** P4 *cần* đã xem P1 mới hiểu → gãy.
- ✅ **Cùng chủ đề (theme):** mỗi Short *tự hiểu được một mình*, chỉ chung ngách/thời kỳ.

Ví dụ Bạch Đằng — thay "Phần 1/2/3/4" bằng 4 Short **độc lập trọn vẹn**:
1. "Vì sao một hàng cọc gỗ nhấn chìm cả hạm đội Nam Hán?"
2. "Ngô Quyền canh thủy triều thế nào để thắng?"
3. "Kẻ bán nước mở đường cho giặc — Kiều Công Tiễn là ai?"
4. "Sau Bạch Đằng, Ngô Quyền bỏ chức Tiết độ sứ nghĩa là gì?"

**Công thức Short chuẩn:**
| Thành phần | Chuẩn |
|---|---|
| Độ dài | 45–60s, kịch bản ~150 từ |
| Cấu trúc | Hook (giây 1–2, chi tiết sốc nhất) → lõi → **câu chốt đóng vòng** (trọn trong Short) |
| Thumbnail + chữ màn hình | Bắt mắt, **đọc được khi tắt tiếng** (đa số Shorts xem không bật tiếng) |
| Từ khóa | **Từ khóa tò mò** (chặn vuốt) — khác từ khóa SEO của video dài |
| Chủ đề | Cùng ngách sử, **1 sự kiện / 1 Short** |

## 5. Sửa 3 "myth" phổ biến
1. ❌ **"Đăng 2 video sát nhau giành slot của nhau / bị bóp."** SAI — không có slot cố định, không có hình phạt. YouTube công khai bác bỏ; nghiên cứu 10 triệu kênh: đăng **nhiều hơn tăng trưởng nhanh hơn**. Cái *có thật* chỉ là hai video sát nhau **chia sẻ sự chú ý cùng tệp khán giả** → giãn ra là vì kinh tế chú ý, không phải phạt.
2. ⚠️ **"Đăng tối tốt hơn sáng."** Đúng một nửa: giờ đăng chỉ cho cú đẩy ban đầu (sub online). Tối tốt vì khán giả Việt online tối. Yếu tố **nhỏ** — video hay giờ xấu vẫn thắng dài hạn. Đăng trước cao điểm ~1–2h (18h–18h30 ổn).
3. ⚠️ **"Short bơm view cho video dài."** SAI về mặt thuật toán — xem mục 3.

## 6. TÓM TẮT CHIẾN THUẬT HIỆN TẠI
**Kênh sử là loại đặc biệt: evergreen + search-driven.** Người ta chủ động tra "trận Bạch Đằng", "Ngô Quyền" — năm nay, năm sau vẫn tra. → **Thư viện video dài tra cứu được = cái business.** Short là vai phụ.

6 chiến lược, mỗi cái sửa đúng 1 cái kênh mới thiếu:
| # | Chiến lược | Sửa gì | Hợp kênh sử |
|---|---|---|---|
| S1 | **Đào khe hở Search** (từ khóa sử có người tra, ít kênh làm) | Cold-start | ⭐⭐⭐ (đúng kỹ năng Data Analyst) |
| S2 | **Làm theo cụm chủ đề** (cùng thời kỳ gối nhau) | Không có catalog/session | ⭐⭐⭐ |
| S3 | **Short tự chứa cùng ngách** (KHÔNG serial, KHÔNG trend lệch) | Nhận diện + đúng sub + test | ⭐⭐ |
| S4 | Gieo khán giả từ ngoài (TikTok/FB/group sử) | Cold-start | ⭐⭐ |
| S5 | **Phòng lab packaging** (A/B thumbnail, tiêu đề) | CTR thấp | ⭐⭐⭐ |
| S6 | Nhất quán + playlist (YouTube hiểu kênh về sử VN) | Phân loại ngách | ⭐⭐ |

Ưu tiên: **S1 + S5 trước** (định lượng được, hợp Data Analyst) → **S2 (cụm)** → **S3 Short** → S4/S6 chạy nền.

## 7. QUYẾT ĐỊNH: Short-trước hay Video-dài-trước?
**Câu hỏi:** chỉ đẩy Short rồi mới làm video dài dựa trên Short cao view, hay cứ làm video dài?

**Trả lời (bằng logic): KHÔNG phải chọn 1 trong 2 — dùng Short làm *dụng cụ nghiên cứu* dẫn đường cho video dài.**
- **Pha 1 (hiện tại, ~30 ngày): Short dẫn đầu.** Bơm nhiều Short sử **tự chứa** trải nhiều chủ đề/thời kỳ. Rẻ, nhanh, thu feedback. Đo: chủ đề/hook/thời kỳ nào ăn (view, % xem, sub mới). **Đây là thu thập dữ liệu để de-risk video dài** (tránh bỏ 15 phút sản xuất vào chủ đề không ai muốn — đúng cái đã xảy ra với E2).
- **Giữ nền video dài mỏng** (≈1/tuần): video dài là tài sản evergreen, **chín chậm trong Search**, nên không để kho trống; nhưng chưa dồn lực trước khi có tín hiệu.
- **Pha 2: dồn video dài vào chủ đề đã được Short chứng minh.**

**2 lưu ý quan trọng (nếu không sẽ sai):**
1. **Short cao view ≠ chắc chắn làm video dài được.** Vì khẩu vị feed Shorts ≠ nhu cầu Search video dài. Một Short nổ nhờ chi tiết lạ có thể **không có ai tra cứu dài**. → Luôn **đối chiếu với nhu cầu Search** (mục 8) trước khi lên video dài.
2. **Đừng làm video dài = kể lại y hệt nội dung Short.** Short chứng minh "người ta muốn Bạch Đằng" → video dài **đào SÂU 15 phút** cho tệp Search, không phải bản dài của cùng câu chuyện.

→ Tinh thần: **Short = dụng cụ đo thị trường rẻ. Video dài = tài sản đắt, chỉ xây trên nền đã đo.** Đúng tinh thần "không cảm tính".

## 8. QUY TRÌNH RESEARCH TỪ KHÓA & CONTENT
Lặp lại được, chấm điểm được (hợp Data Analyst):

**Bước 1 — Danh sách hạt giống:** 38 mốc trong `series-nguoc-dong.md`.

**Bước 2 — Đo NHU CẦU (người ta muốn tới mức nào?):**
- **YouTube autocomplete** (miễn phí, trực tiếp): gõ "trận bạch đằng…", "ngô quyền…" xem gợi ý tự động = đúng cụm người ta gõ.
- **Google Trends** (chọn vùng Việt Nam, mục *YouTube Search*): so sánh tương đối nhiều chủ đề theo thời gian.
- **View của video đang có**: search chủ đề đó, top kết quả view cao = có cầu.
- (Tùy chọn) vidIQ/TubeBuddy: ước lượng search volume + điểm cạnh tranh.

**Bước 3 — Đo CẠNH TRANH (khó chen tới mức nào?):**
- Bao nhiêu kênh lớn đã làm, view của họ, **độ mới** (cũ 5 năm = cửa mở lại).
- **Khe hở = cầu cao + cạnh tranh ít/cũ/kém.**

**Bước 4 — Tín hiệu từ Short của chính mình:** thời kỳ/hook nào Short của bạn ăn → ưu tiên lên video dài.

**Bước 5 — Chấm điểm → xếp ưu tiên:** bảng `chủ đề · từ khóa chính · nhu cầu (1–5) · khe hở cạnh tranh (1–5) · góc kể riêng · chi phí sản xuất · điểm ưu tiên`. Làm từ điểm cao xuống.

**Content/góc:** sau khi chọn chủ đề, góc = **khoảng tò mò** (nghịch lý, điều SGK không kể, sử cũ chép khác nhau) — **chỉ từ dữ kiện đã kiểm chứng trong `kb/`**. Tiêu đề phải khớp **cách người ta search**.

**Khác biệt từ khóa 2 định dạng:**
- Video dài → **từ khóa SEO** (cụm người ta tra: "trận Bạch Đằng 938") đặt **đầu tiêu đề**.
- Short → **từ khóa tò mò** (chặn vuốt): "Một hàng cọc gỗ đánh chìm cả hạm đội?"

## 9. Nguồn tra (2025–2026)
- [YouTube demystifies Shorts algorithm — Yahoo/Todd Sherman](https://sports.yahoo.com/youtube-demystifies-shorts-algorithm-views-161321949.html)
- [Shorts vs long-form viewers — vidIQ](https://vidiq.com/blog/post/youtube-shorts-long-form-viewers-algorithm)
- [Shorts không kết nối thuật toán video dài — Colorado State](https://social.colostate.edu/best-practices/youtube-shorts-how-does-the-algorithm-work/)
- [Người xem đối xử video dài như Short — Tubefilter/Metricool 2026](https://www.tubefilter.com/2026/08/03/youtube-shorts-long-form-study-metricool/)
- [Nghiên cứu tần suất đăng 10 triệu kênh — vidIQ 7/2026](https://vidiq.com/research/youtube-upload-frequency-study/)
- [Shorts chief bác bỏ myth đăng nhiều bị phạt](https://feeds2.benzinga.com/news/23/08/34020532/youtube-shorts-chief-debunks-popular-myths-no-posting-10-videos-a-day-doesnt-affect-your-performance)
- ["Mỗi Short là câu chuyện tự chứa, đừng làm trailer" — podwise/Shorts strategist](https://podwise.ai/episodes/8042262)
- [Độ dài & format Shorts cho retention — Opus](https://www.opus.pro/blog/ideal-youtube-shorts-length-format-retention)
- [Hướng dẫn thuật toán 2026 — Buffer](https://buffer.com/library/youtube-algorithm/)
