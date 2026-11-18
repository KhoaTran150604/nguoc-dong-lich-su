# Mẫu phong cách hoạt hình 2D chibi – để duyệt cho series sau Bạch Đằng 938

_18/11/2026. Hình mẫu: `build/thu-hoathinh/mau-phong-cach/bang-mau.jpg` (S1–S6, mỗi mẫu 1080p riêng: `S1.jpg`…`S6.jpg`). Code: `scripts/hoathinh/mau_phong_cach.py`. Ảnh khung hình kênh tham khảo: `tham-khao-*.jpg` (chỉ để nghiên cứu nội bộ, không đăng)._

## 1. Các kênh đã xem (ảnh xem trước của YouTube, không phát tiếng)
| Kênh | Kiểu hình | Điều học được | Lượt xem tham khảo |
|---|---|---|---|
| **Thỏ Bảy Màu** (T7M + Sun Wolf) | Chibi tối giản, nền vẽ kỹ, cắt cảnh điện ảnh | Nhân vật đơn giản và nền đẹp; hài từ thoại; đội khoảng 7 họa sĩ diễn hoạt cùng diễn viên lồng tiếng | Chiến tranh cầu cá P1 |
| **Vạn Tích** (VN) | 2D phẳng bán thực, cung điện, mũi tên | Sử Việt dạng hoạt hình ăn khách | Hai Bà Trưng: 15,7 triệu |
| **Miền Cổ Tích** (VN) | 2D bán thực, nhân vật người lớn | Kể danh tướng (Phạm Ngũ Lão) | khoảng 600 nghìn |
| **Chioo** (VN) | Mặt meme mắt to, bản đồ, giọng hài | Sử thế giới kể kiểu hài, thân thiện | khoảng 175 nghìn |
| **EZ Sử** (VN) | Bản đồ và đồ họa chuyển động | Tóm tắt nhanh bằng bản đồ | khoảng 1,4 triệu |
| **Oversimplified** | Người que đầu tròn, bản đồ + cờ | Bản đồ là sân khấu, nhân vật cực đơn giản, hài | WW1 P1: 58 triệu |
| **History Matters** | Người khối vuông đứng trước bản đồ | Video ngắn khoảng 3–10 phút, nhân vật dễ làm hàng loạt | khoảng 500 nghìn |
| **Simple History** | 2D phẳng chi tiết vừa | Giọng nghiêm túc, đồ vật minh họa | 3,4 triệu |
| **Extra History** | Đầu tròn to, viền mảnh, nền trắng hoặc giấy | "Minh họa sách sử": rõ, sạch, tập trung | – |
| **Sam O'Nella** | Người que vẽ nguệch ngoạc | Hài thô, làm rất nhanh | 9,5 triệu |
| **bill wurtz** | Chữ và màu + bản đồ | Nhịp nhanh, chữ là hình | 186 triệu |
| **Countryballs** | Quả bóng có mắt và cờ | Cực rẻ để làm, hài | khoảng 8 triệu |
| **Kurzgesagt** | Phẳng, không viền, màu rực | Chất lượng đồ họa cao (đội lớn) | – |
| **Nobunaga no Shinobi** (anime) | Chibi anime về sử Nhật | Sử bằng chibi vẫn được đón nhận | – |

**Nhận xét chung:**
- Các kênh sử nhiều view nhất đều có nhân vật cực đơn giản cộng với một sân khấu mạnh (bản đồ hoặc nền đẹp) và lời kể hay. Chi tiết nhân vật không quyết định thành công.
- Kênh Việt làm sử bằng hoạt hình nhân vật chibi còn ít. Vạn Tích và Miền Cổ Tích là 2D bán thực, nên kiểu chibi là khoảng trống có thể chiếm.

## 2. Repo và tài nguyên miễn phí (đã kiểm giấy phép, 18/11/2026)
| Tài nguyên | Dùng để | Giấy phép | Ghi chú |
|---|---|---|---|
| **Rhubarb Lip Sync** | Khẩu hình theo âm vị (A–H/X) thay cho "đo độ to" | MIT | Có chế độ phonetic cho tiếng không phải tiếng Anh; cần thử với giọng Việt |
| **DiceBear** (các kiểu CC0: Notionists, Lorelei, Open Peeps…) | Học cách ghép nhân vật từ bộ phận + biến thể biểu cảm | Code MIT; art: 42 kiểu CC0, 14 kiểu CC BY | Kiểu CC BY phải ghi công |
| **Notion Avatar** | Bộ mắt, mày, miệng nét mảnh rất hợp phong cách | Code MIT, art CC0 | Đồ lại thành spline của mình |
| **Manim** | Đường Bézier, easing, máy quay bằng Python | MIT | Mượn hàm nội suy |
| **Open Peeps / Humaaans / Kenney Toon Characters** | Tham khảo dáng, tư thế, vai quần chúng | CC0 | Dùng kiếm tiền được |
| Motion Canvas, Remotion, rlottie, Rive, DragonBones | Ý tưởng dòng thời gian, xương, state machine | MIT (Remotion: miễn phí cho nhóm tối đa 3 người) | Không phải Python, chỉ tham khảo |
| Synfig, OpenToonz, Pencil2D, Krita, COA Tools 2 | Phần mềm có người thao tác | GPL/BSD | Không hợp cách code tự vẽ |
| ⚠️ Multiavatar, Spine, LPC, python-lottie | – | Hạn chế (cấm đóng gói lại / trả phí / share-alike / AGPL) | Tránh |

Repo "chibi generator" trên GitHub chỉ là đồ chơi (vài sao, bỏ từ 2019). **Không có repo nào chia sẻ sẵn một pipeline hoạt hình chibi hoàn chỉnh.** Bộ code tự viết của kênh hiện đã đi xa hơn các repo này.

## 3. Sáu mẫu đã vẽ (cùng nhân vật Anh Văn – Em Võ)
| Mã | Phong cách | Học từ | Hợp sử | Đọc trên ĐT | Khác biệt | Dễ làm | Linh hoạt | An toàn | **Tổng /30** |
|---|---|---|---|---|---|---|---|---|---|
| S1 | Sitcom tối giản, nền phong cảnh | Thỏ Bảy Màu | 4 | 5 | 3 | 4 | 4 | 3 | **23** |
| S2 | Minh họa sách sử, nền giấy + đạo cụ | Extra History | 5 | 4 | 3 | 4 | 4 | 4 | **24** |
| S3 | Người tối giản đứng trên bản đồ | Oversimplified / History Matters | 5 | 4 | 3 | 5 | 4 | 3 | **24** |
| S4 | Bóng tròn đội mũ | Countryballs | 3 | 5 | 3 | 5 | 3 | 2 | **21** |
| S5 | Sticker viền dày, màu kẹo | LINE sticker | 3 | 5 | 3 | 4 | 3 | 4 | **22** |
| S6 | Chibi sơn mài: nền đen, trống đồng vàng | nhận diện kênh | 5 | 4 | 5 | 4 | 4 | 5 | **27** |

Cách chấm:
- **Hợp sử:** đủ nghiêm túc cho chủ đề chiến tranh và lịch sử.
- **Khác biệt:** không lẫn với kênh khác.
- **An toàn:** rủi ro bị cho là bắt chước kênh khác, hoặc mang hàm ý meme chính trị (countryballs vốn gắn với cờ quốc gia).

## 4. Đề xuất cho series tiếp theo
**Lai 3 lớp theo vai trò cảnh**, nhân vật dùng chung một bộ code:
1. **Nhận diện chung = S6** (bảng màu sơn mài: đen, vàng đồng, đỏ son; nền trống đồng). Mở đầu, kết, thumbnail, cảnh Văn kể "Sử chép rằng…". Khác hẳn mọi kênh đã xem và khớp avatar/banner hiện có.
2. **Cảnh đối thoại = S1** (nền phong cảnh, cắt cảnh sitcom). Dùng cho đoạn Võ hỏi, Văn đáp, đã chạy thử được (video 11,8 giây có giọng và khẩu hình).
3. **Cảnh trận = S3 trên bản đồ của kênh.** Anh em chibi đứng trên bản đồ cổ, cờ chân dung di chuyển. Tận dụng bộ bản đồ `scripts/video/`, giống công thức của Oversimplified nhưng bản đồ và nhân vật là của mình.
- **S5** để dành cho Shorts, bài cộng đồng ("Team Văn hay Team Võ?") và sticker.
- **Không chọn S4**: dễ bị hiểu thành meme countryballs, không hợp chủ đề chiến tranh có người chết.

**Việc kỹ thuật tiếp theo (nếu duyệt):**
1. Thử Rhubarb với giọng Gia Huy và Tiến Đạt.
2. Đóng gói `draw_char` thành bộ nhân vật dùng chung (Văn, Võ, Ngô Quyền chibi, lính hai phe, tướng giặc).
3. Thêm nhạc nền và tiếng động.
4. Làm thử 1 phút theo công thức lai cho tập kế tiếp.
