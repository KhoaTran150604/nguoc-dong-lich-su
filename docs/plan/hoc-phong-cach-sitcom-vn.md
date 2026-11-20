# Học phong cách sitcom hoạt hình VN (tham khảo kênh Thỏ Bảy Màu)

> 18/11/2026 – xem tập "Thỏ Bảy Màu và Mắt Đo Phước Nghiệp" (18:35, 1080p), chụp **21 khung hình** ở các mốc 0:30 → 17:25 (cứ ~1 phút một khung) + ảnh poster/cảnh trên Google.
> **Chỉ học PHONG CÁCH** (nét, màu, ánh sáng, bố cục, cách kể bằng hình). KHÔNG vẽ lại nhân vật, logo, cảnh cụ thể của kênh đó. Không lưu ảnh chụp vào repo.

## 1. Nét vẽ (line art)
| Thứ | Cách họ làm | Áp dụng cho mình |
|---|---|---|
| Viền nhân vật | **Đen, đậm, đều một độ dày** (~4–5px ở 1080p), không thon đầu/đuôi, đầu nét tròn | `lw` ≈ 4.5 ở 1080p (`flat=True` đã nhân 1.45) |
| Viền nền | **Mảnh hơn viền nhân vật** (~2–3px), cùng màu đen/nâu đen; vật xa nét càng mảnh, đôi khi đổi sang màu đậm của chính vật đó | nền `w=2–3`, lớp xa `w=1.6` + màu nét nhạt |
| Nét trong | Rất ít: nếp áo 1–2 nét, nếp nhăn mặt người già, đường gỗ/tôn, vết nứt tường | Chỉ thêm nét trong khi có nghĩa; KHÔNG vẽ lông răng cưa |
| Mắt | Nhân vật chính: 2 chấm đen dọc nhỏ + má hồng tròn; người/vật phụ: tròng trắng to tròn + con ngươi đen nhỏ | Gâu Nghệ giữ mắt riêng (tròng nâu); mắt chấm chỉ dùng cho mặt nạ trắng |
| Miệng | Nét nhỏ ở giữa mặt, khi nói/ngạc nhiên là hình bầu dục tối có lưỡi hồng | khẩu hình nhỏ, đặt sát mũi |

## 2. Màu
- **Tô phẳng**, mỗi vùng 1 màu nền + 1 màu bóng. Không gradient trên nhân vật, không phát sáng, không làm mờ (blur).
- Bảng màu **ấm, hơi ngả, độ bão hoà vừa**: tường vàng kem/cam đất, tôn xanh ngọc (#3FAE8A-ish) có sọc đậm nhạt, gỗ nâu cam, gạch lát vàng–cam xen ô, da người kem nhạt, áo màu đất (nâu, đỏ đô, xám).
- Trời ban ngày **xanh trong (#9CD6F0)**, mây trắng bồng to, đáy mây có mảng xanh nhạt; cây bụi **xanh vàng chanh** tươi (#B6D84A) có mảng tối xanh lá.
- Đêm/tâm trạng: **phủ cả khung một tông** (xanh dương đậm cho đêm lũ, xanh lam lạnh cho buồn) – nhân vật cũng bị phủ màu theo, giữ nguyên viền đen.

## 3. Ánh sáng & bóng
- **Bóng cel 1 tầng, mép cứng** trên nhân vật: thân thỏ trắng → mảng xám nhạt (#D9D9D9) ở phía khuất sáng + đỉnh đầu trắng sáng nhất; người: mảng tối dưới tóc mái, dưới cằm, phía trong cánh tay.
- **Bóng đổ của vật lên vật** rõ ràng: tóc đổ lên trán, đầu đổ lên thân, tay đổ lên mặt (mảng tối bán trong suốt kiểu "multiply").
- **Nắng qua cửa sổ** = các mảng sáng hình chữ nhật xiên trên sàn; vùng ngoài nắng tối hẳn một bậc → tạo chiều sâu mà không cần gradient.
- **Bóng dưới chân** = elip tối mờ nhẹ, đặt sát chân (gần như luôn có).
- Bề mặt tường/đất có **vết loang, vệt bẩn, giấy rách** (texture nhẹ) → đỡ "phẳng nhựa".

## 4. Bố cục & máy quay
- Cỡ cảnh thay đổi liên tục: **toàn cảnh thiết lập** (nhìn từ trên cao, kiểu isometric, rất chi tiết: nhà, hàng rào tôn, ao sen, cây dừa, dây phơi đồ, đường làng, cột điện) → **trung cảnh** nhóm nhân vật đứng thành hàng → **cận mặt** khi phản ứng.
- Góc máy hài: **nghiêng khung (dutch angle)** khi cả nhóm hóng chuyện, **nhìn từ trên xuống** nhân vật nhỏ đứng giữa sàn gạch, **nhìn qua vai** (tiền cảnh là lưng/tóc một nhân vật, mờ phẳng không blur).
- Nhân vật hay đứng **sau một thanh ngang** (lan can, dây chắn, bàn) che nửa người → tạo lớp tiền cảnh.
- Nhân vật chính thường **nhỏ, ở 1/3 khung**, nền chiếm phần lớn; cận cảnh thì mặt chiếm 1/2 khung, đặt lệch tâm.
- Chi tiết đời thường Việt Nam là "gia vị": lịch bloc ngày 29, hàng rào tôn, ghế nhựa xanh, bao gạo, poster quảng cáo cũ, cột điện chằng chịt dây, hoa mai trong chậu.

## 5. Nhân vật (cách thiết kế, không chép nhân vật)
- Hình khối **cực đơn giản**: đầu tròn to, thân nhỏ, tay chân là ống tròn đầu; người: đầu chữ nhật/bầu, cổ dài mảnh.
- Diễn xuất bằng **tư thế + mắt**: mắt lim dim, mắt "> <" khi đau, mồ hôi, tay ôm mặt, ngồi xổm, chống nạnh.
- Người phụ có đặc điểm nhận ra ngay từ bóng: kính tròn, tóc búi, áo bà ba nâu, hình xăm.

## 6. Checklist trước khi gửi một khung hình
- [ ] Viền nhân vật đậm hơn viền nền? Nền xa nét mảnh/nhạt?
- [ ] Mọi mảng màu phẳng, không gradient/blur/glow?
- [ ] Có bóng cel trên nhân vật + bóng đổ vật lên vật + bóng chân?
- [ ] Nền là một **cảnh thật** có ≥5 chi tiết đời thường Việt?
- [ ] Có lớp tiền cảnh (lan can/bàn/vai) hoặc góc máy có ý đồ?
- [ ] Nhân vật không chiếm quá 1/2 khung (trừ cận mặt)?

## 7. Học thêm – đợt 2 (18/11/2026, 4 tập, 54 khung)
Tập đã xem: *Hình Tượng Đỉnh Cao* (12:30, 16 khung), *Chiến Tranh Cầu Cá P2* (15:50, 14 khung), *Thần Bài Miền Tây* (21:14, 14 khung), *Người Yêu Mới Của Chị Xô* (13:10, 10 khung – tập cũ 2021, để so sánh).

### 7.1 Điều MỚI học được (chưa có ở mục 1–6)
| # | Học được | Thấy ở | Quy tắc cho code |
|---|---|---|---|
| N1 | **Ban đêm = đổi cả bảng màu sang xanh dương/xanh tím**, không chỉ làm tối. Da trắng → xám xanh, tường → xanh đậm, nét vẫn đen. Trăng tròn trắng + vài chấm sao. Thành phố xa = khối xanh đậm có ô cửa vàng | Đỉnh Cao, Thần Bài | `tint_night(cv)`: nhân màu (0.55,0.62,0.95) + cộng chút xanh; giữ viền đen; thêm cửa sổ vàng ở nền xa |
| N2 | **Nhân vật có mảng bóng cel lớn hình lưỡi liềm** ở phía khuất sáng (đầu tròn trắng → 1/3 bên là xám xanh) | Đỉnh Cao (thỏ dưới trăng) | đầu tròn: vẽ elip lệch làm mảng bóng, cắt theo mặt nạ đầu |
| N3 | **Trong nhà dùng tông xám-xanh lạnh, tường có vết nứt mảnh** (2–3 nét đen gấp khúc), cột gỗ nâu, cửa chớp gỗ, sàn gạch ô vuông phối cảnh | Chị Xô, Đỉnh Cao | hàm `crack()` nét gấp khúc; sàn ô vuông có điểm tụ |
| N4 | **Nắng vào cửa = 1 vệt sáng hình thang** lên tường/sàn; khung tối hơn hẳn phần còn lại | Chị Xô (ghế gỗ + đèn TV) | dùng `shade()` k>1 (đã có) |
| N5 | **Cảnh hoành tráng: thêm viền đen điện ảnh** (letterbox 2.35:1) + bảng màu hơi ngả vàng-xám (bụi đất) | Cầu Cá P2 (cả tập) | tuỳ chọn `letterbox=True` cho cảnh trận đánh/cao trào |
| N6 | **Toàn cảnh nhìn từ trên cao (bird-eye/isometric)** rất chi tiết: lều, đường đất, hàng rào, đám đông vẽ bằng **bóng người đơn sắc** (xám tím, chỉ có viền) | Đỉnh Cao, Thần Bài, Cầu Cá | đám đông = nhiều đầu tròn cùng màu, chỉ vài người trước vẽ chi tiết |
| N7 | **Hậu cảnh nhiều lớp có "chữ ký" Nam Bộ**: dừa, chuối, hàng rào tôn xanh ngọc, cầu khỉ, nhà sàn trên ao bèo, mai vàng ngày Tết | Thần Bài, Cầu Cá | kho đạo cụ: `coconut()`, `ton()` (có), `mai()` (có), `cau_tre()` |
| N8 | **Cỡ cảnh cực cận**: chỉ 1 bàn tay/1 lá bài/1 vật lấp đầy khung, nền là mảng màu phẳng → nhấn chi tiết hài | Thần Bài (bàn tay + bộ bài) | thêm cỡ cảnh "insert" khi nói về một đạo cụ (vd. cọc gỗ bịt sắt) |
| N9 | **Bố cục 2 người**: một người bị **cắt mép khung** (chỉ thấy nửa đầu/vai) ở tiền cảnh, người kia rõ ở trung cảnh → đối thoại có chiều sâu | Đỉnh Cao, Chị Xô | khung C đã có, dùng cho mọi đối thoại |
| N10 | **Hiệu ứng tâm lý**: nền đen + **viền phát sáng màu** quanh nhân vật khi tưởng tượng/doạ dẫm (ngoại lệ duy nhất có "glow") | Thần Bài | chỉ dùng cho cảnh tưởng tượng, không dùng cho cảnh thường |
| N11 | **Thời tiết bằng nét**: mưa = nét chéo trắng mảnh, cả khung ám xanh xám; hoàng hôn = cam-tím, thành phố xa thành bóng phẳng | Cầu Cá P2 | `rain(cv)` nét chéo; preset `hoang_hon` |
| N12 | **Mặt người dài kiểu "hộp chữ nhật"**, mắt tròng trắng to, mí nặng, nếp nhăn 2–3 nét → người già trông ngay ra tính cách | tất cả | khi vẽ nhân vật phụ (ông đồ, lính) dùng mặt khối + mí mắt nặng |
| N13 | **Tập cũ (2021) đơn giản hơn**: nền ít chi tiết, phẳng, gần như không bóng; tập mới (2023–2024) nền dày chi tiết, có bóng & ánh sáng → **độ chi tiết nền là thứ làm phim "lên đời"** | so sánh 4 tập | ưu tiên đầu tư nền hơn nhân vật |
| N14 | Phụ đề **chữ trắng viền đen mảnh, đặt sát đáy, giữa** (tập cũ) – tập mới không có phụ đề cứng | Chị Xô | video dài: không phụ đề cứng; Short: phụ đề theo vùng an toàn của kênh |

### 7.2 Việc code cần làm từ đợt học này
1. `tint_night()` + `rain()` + preset hoàng hôn (N1, N11).
2. `crack()` vết nứt tường, sàn gạch phối cảnh (N3).
3. Đám đông bóng đơn sắc (N6) – dùng cho cảnh quân lính Bạch Đằng.
4. Cỡ cảnh "insert" cực cận đạo cụ (N8) + letterbox cho cảnh trận (N5).
5. Kho đạo cụ Nam Bộ/Bắc Bộ (N7).

### 7.3 Đã làm (18/11/2026) – `scripts/hoathinh/sitcom_fx.py`
| Hàm | Quy tắc | Ghi chú |
|---|---|---|
| `tint_night(cv, windows='#màu ô cửa')` | N1 | đổi bảng màu sang xanh, ~35% ô cửa thắp vàng, trăng + sao chỉ đặt lên trời |
| `dusk(cv)` | N11 | hoàng hôn cam-tím |
| `rain(cv)` | N11 | nét chéo trắng mảnh + ám xanh xám |
| `letterbox(cv)` | N5 | viền đen 2.35:1 |
| `crack()`, `tile_floor()` | N3 | vết nứt tường, sàn gạch phối cảnh |
| `crowd()` | N6 | đám đông bóng một màu, xa nhỏ gần to, 30% đội nón lá, vài người trước màu riêng |
| `coconut()`, `cau_tre()` | N7 | cây dừa, cầu khỉ |
| `insert_stake()` | N8 | cận cảnh cọc gỗ vót nhọn bịt sắt (dùng cho Bạch Đằng) |
Bảng thử: `build/thu-hoathinh/sitcom-fx/bang-hieu-ung.jpg`. Chưa làm: bóng lưỡi liềm (N2) cho nhân vật trắng, viền phát sáng cảnh tưởng tượng (N10).


## 8. Học thêm – đợt 3 (18/11/2026, 5 tập, 48 khung)
Tập: Cầu Cá P1, Hành Trình Chuyển Sinh, Cái Tết Của Ông Năm, Trung Tâm Giác Ngộ Internet, Kiếm Khách Số 1. Tổng cộng đã học **10 tập / ~123 khung**.

### 8.1 Điều MỚI học được
| Mã | Quy tắc | Thấy ở |
|---|---|---|
| N15 | **Phối cảnh xa = các lớp núi/đồi phẳng nhạt dần** (3–4 lớp cùng tông, lớp xa sáng & ít bão hòa hơn) thay cho sương mù/blur | Giác Ngộ (pháo đài trên đảo), Kiếm Khách (núi thủy mặc) |
| N16 | **Cảnh tuyết/bãi trắng**: nền trắng + mép bóng xanh xám, "mũ tuyết" trên đá, mái, bậc thềm | Kiếm Khách |
| N17 | **Hoàng hôn ngoài trời**: trời cam–hồng, mây xanh xám, chói nắng dạng tia cứng; góc máy thấp phối cảnh mạnh | Cầu Cá |
| N18 | **Cảnh dưới nước** = phủ cả khung một màu xanh lục ngả lam + bong bóng tròn viền mảnh | Cầu Cá |
| N19 | **Nội thất đêm ấm**: không xanh lạnh như N1 mà nâu cam, nguồn sáng là đèn bàn thờ/đèn dầu; vệt sáng cửa sổ trên tường | Cầu Cá, Tết Ông Năm |
| N20 | **Đèn rọi/giếng trời**: hình nón sáng (hình thang nhạt) từ trên xuống, phần ngoài nón tối hẳn – dùng cho cảnh "phán xét", xuất hiện kịch tính | Giác Ngộ |
| N21 | **Khung trong khung**: TV, cửa sổ, màn hình laptop chiếu "thế giới khác" (màu/phong cách khác) | Chuyển Sinh, Kiếm Khách |
| N22 | **Đạo cụ lệch thời đại làm hài** (laptop giữa nhà cổ, ghế nhựa xanh cạnh trường kỷ gỗ) – 1 món/khung, đặt chỗ dễ thấy | Kiếm Khách |
| N23 | **Tiền cảnh che góc khung** (mặt/vai nhân vật cực gần ở mép) tạo chiều sâu cảnh đối đầu | Kiếm Khách, Giác Ngộ |
| N24 | **Bối cảnh Tết/nhà Việt**: tường be trơn, lịch Tết, ghế băng gỗ, chậu mai bonsai, bộ ấm trà; nhà nhìn 3/4 có đèn lồng đỏ, luống rau, hàng rào, phố xa phía sau | Tết Ông Năm |
| N25 | **Nhà cổ/cung đình**: cửa bức bàn song gỗ ô vuông, cột gỗ có thớ, sập gỗ, chậu bonsai, núi xám nhạt qua cửa | Kiếm Khách |
| N26 | **Rừng tre**: thân tre sọc đốt, lá thành chùm có viền, 2–3 lớp xanh đậm–nhạt; bụi cây tròn viền ở chân | Kiếm Khách |
| N27 | **Khói/bụi** = cụm tròn chồng nhau màu xám phẳng, mép cứng, không blur/gradient | Giác Ngộ |
| N28 | **Đồ họa biểu tượng chèn ngang** (âm dương, ký hiệu to giữa khung trên nền trơn) để chuyển ý | Giác Ngộ |
| N29 | Nhân vật bị đánh: **mắt bầm tím** tròn, vết bùn – chi tiết hài nhỏ giữ qua nhiều cảnh (liên tục) | Kiếm Khách, Cầu Cá |
| N30 | Tập cũ (2022) đơn giản hơn: màu pastel, nền ít chi tiết → bản mới đẹp hơn nhờ **nền chi tiết + bóng** (khẳng định lại mục 1–3) | Chuyển Sinh, Tết |

### 8.2 Việc code từ đợt 3 (đề xuất)
- `sitcom_fx.layers_far(cv, y, n, col)` – núi/đồi xa nhiều lớp phẳng (N15) → dùng cho bản đồ/bờ sông Bạch Đằng.
- `sitcom_fx.snow_cap(d, pts)`, `underwater(cv)`, `spotlight(cv, x, w0, w1)`, `smoke(cv, x, y, r)` (N16, N18, N20, N27).
- `tint_warm_night(cv, lamp_xy)` (N19) – bản ấm của `tint_night`.
- Đạo cụ: `bamboo(d, x, h)` (N26), `lattice_door(d, box)` (N25), `tet_set` (lịch, mai, ấm trà – N24).
- Cảnh sử: N22 hợp với Gâu Nghệ (chó cầm cà phê sữa đá giữa trận Bạch Đằng) – nhưng lời kể sử vẫn chỉ dữ kiện ✅ trong `kb/`.


### 8.3 Đã làm (18/11/2026) – thêm vào `scripts/hoathinh/sitcom_fx.py`
Demo: `python scripts/hoathinh/sitcom_fx.py --dot3` → `build/thu-hoathinh/sitcom-fx/bang-hieu-ung-3.jpg` (8 khung).
| Hàm | Quy tắc |
|---|---|
| `layers_far(d, y, n, base, sky, bottom=)` | N15 núi xa nhiều lớp phẳng |
| `snow_ground`, `snow_cap(d, top_pts)` | N16 tuyết |
| `sunset_sky`, `sun_rays(cv, x, y)` | N17 hoàng hôn (dải màu phẳng, tia mép cứng) |
| `underwater(cv)` | N18 dưới nước |
| `tint_warm_night(cv, lamp)`, `oil_lamp`, `window_beam` | N19 đêm ấm trong nhà (quầng 2 nấc mép cứng) |
| `spotlight(cv, x, w0, w1)` | N20 đèn rọi |
| `tv_frame(cv, box, inner)` | N21 khung trong khung |
| `smoke(cv, x, y, r)` | N27 khói tròn phẳng một viền |
| `symbol_card(cv)` | N28 đồ họa chèn (mặt trống đồng giản lược) |
| `black_eye(d, x, y)` | N29 mắt bầm |
| `bamboo`, `bamboo_grove`, `bush_row` | N26 rừng tre |
| `lattice_door`, `tet_calendar`, `mai_bonsai`, `tea_set`, `wood_bench` | N24/N25 nhà Tết, nhà cổ |
Lưu ý: vẽ `K.shade`/bóng nền TRƯỚC nhân vật để không nhuộm màu lông; quầng đèn để nhẹ (×1.2) kẻo thành "mặt trời" giữa phòng.

## 9. Học kỹ một tập – đợt 4 (18/11/2026): CẢNH NHIỀU NHÂN VẬT
Tập *Mắt Đo Phước Nghiệp* (18:35), chụp **6 giây/khung ≈ 150 khung** (xem tắt tiếng). Chụp dày cho thấy nhịp cắt cảnh: trung bình **3–6 giây đổi một cỡ cảnh**, hiếm khi giữ một khung quá 8 giây. Tổng đã học: **11 tập / ~270 khung**.

### 9.1 Quy tắc dàn nhân vật (M1–M14)
| Mã | Quy tắc | Ví dụ thấy trong tập |
|---|---|---|
| M1 | **Hàng ngang "tổ đội"**: 3–5 nhân vật đứng cùng một đường đất, **chiều cao rất khác nhau** (cao gầy – tròn thấp – tí hon), mỗi con một màu chủ đạo | đứng trên boong tàu, đứng ở lan can |
| M2 | **Chồng lấn 10–30%**: không xếp đều cách nhau; con trước che một phần con sau, tạo nhóm chặt | xếp hàng trước sạp |
| M3 | **3 tầng chiều sâu**: tiền cảnh (vai/lưng/mặt cực gần, bị mép khung cắt) – trung cảnh (người nói) – hậu cảnh (đám đông bóng/nhỏ) | cảnh sân chùa, cảnh xếp hàng |
| M4 | **Mọi ánh mắt đổ về người nói**; người nói nhìn vào máy hoặc người đối diện. Ai không nói thì có **phản ứng riêng** (khoanh tay, nhíu mày, há miệng, liếc) | cảnh bàn ăn, nhóm 3 người cận cảnh |
| M5 | **Nhân vật chính nhỏ đứng cạnh người lớn cao** → tương phản kích thước là chất hài; chính được đặt ở 1/3 khung, sáng màu nhất | thỏ trắng cạnh ông già |
| M6 | **Bóng dáng (silhouette) phải khác nhau** dù tô đen: đầu tròn / đầu chữ nhật / đầu trứng hói / tai dài | cả dàn nhân vật |
| M7 | **Nhân vật quần chúng dùng lại một mẫu, đổi màu áo** (nhóm đầu trọc giống hệt nhau) – tiết kiệm mà vẫn vui | nhóm côn đồ |
| M8 | **Cảnh hội thoại 2 người: qua vai** – lưng/đầu người nghe chiếm 1/4 khung ở mép, người nói ở giữa–1/3 | ông già vs thỏ |
| M9 | **Bàn tròn / bàn ăn**: nhân vật vây quanh, một người quay lưng ở tiền cảnh, ghế nhựa đỏ, bát đĩa trên bàn | bữa cơm Tết |
| M10 | **Toàn cảnh từ trên cao (bird-eye)** để mở mỗi địa điểm; nhân vật nhỏ xíu, nhà cửa – hàng rào – cây cối chi tiết | nhà ven hồ, sạp "trung tâm" |
| M11 | **Góc ngước từ dưới lên** (nhìn qua trần nhà/mái) khi 2 người cúi nhìn xuống | 2:18 |
| M12 | **Đêm = cả khung kể cả nhân vật ám xanh** (khẳng định N1), nước có gợn trắng mảnh | cảnh lụt trên thuyền |
| M13 | **Lớp đồ họa hài đè lên**: thanh "điểm" trên đầu từng người, số âm bật lên, chữ to | thanh điểm phước |
| M14 | **Nước mắt/mồ hôi** = giọt xanh nhạt viền mảnh, bay thành dải khi khóc to | cận mặt khóc |

### 9.2 Việc code
- `scripts/hoathinh/to_doi.py`: dàn nhân vật phụ (khác khung người, khác màu) + hàm `lineup()` tự xếp chồng lấn, hướng ánh mắt về người nói (M1, M2, M4, M6).
- Khung thử nhiều nhân vật: hàng ngang ở lan can bờ sông, bàn trà đêm ấm, qua vai + đám đông (M3, M8, M9).

## 10. Mã đã có
- `scripts/hoathinh/gau_nghe_van.py` – `Dog(..., st)`; `st['flat']=True` = lối sitcom (viền đậm, bóng cel), `cup` (cầm ly cà phê), `book`, `arms`.
- `scripts/hoathinh/gau_nghe_avatar_cafe.py` – cảnh sân thượng nhìn thành phố: `cloud()` mây một viền, `top_building()` nhà nhìn từ trên.
- `scripts/hoathinh/gau_nghe_avatar_tbm.py` – cảnh bến sông, hàm `poly()`/`pline()` vẽ mảng có viền.
