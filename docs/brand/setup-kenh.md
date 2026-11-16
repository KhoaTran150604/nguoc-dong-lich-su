# Setup kênh "Song Tử Kể Sử"

_Cập nhật 16/11/2026. Đổi từ "Ngược Dòng Sử Việt" để kênh rộng hơn (sử Việt, Trung Hoa/Tam Quốc, thế giới). "Ngược Dòng Sử Việt" giữ làm **tên series/playlist** cho chuỗi sử Việt kể lùi._

## Nhận diện
| Mục | Giá trị | Trạng thái |
|---|---|---|
| Tên kênh | **Song Tử Kể Sử** | ✅ chốt |
| Handle | đề xuất `@songtukesu` (người dùng kiểm tra còn trống) | ⏳ |
| Ý nghĩa | Chủ kênh cung Song Tử → hai anh em sinh đôi dẫn chuyện; **"Văn võ song toàn"** | ✅ |
| Nhân vật | **Anh Văn** (áo vàng, kể sử, giữ nguồn) · **Em Võ** (áo đỏ, dẫn trận) – xem `docs/brand/nhan-vat-song-tu.md` | ✅ hình · ⏳ tên gọi, số giọng |
| Màu | vàng đồng `#D9B44A`/`#C9A24A`/`#F3D27A`, đỏ sơn mài `#B3261E`, mực `#14110F`, kem `#F2E6CC` | ✅ |
| Font | Playfair Display (tiêu đề), Be Vietnam Pro (chữ) | ✅ |

## Avatar ✅ (chốt 16/11/2026)
- Mẫu đã chọn: **"Văn – Võ"** – nền chia đôi chéo vàng/đỏ, Anh Văn mở sách (huy hiệu VĂN), Em Võ kiếm + khiên (huy hiệu VÕ), ký hiệu ♊ ở trên, viền vàng đồng.
- File tải lên YouTube: `assets/brand/song-tu/AVATAR-YouTube-800x800.png` (PNG 800×800, ~170 KB)
- Bản lớn (Facebook/TikTok/in): `assets/brand/song-tu/AVATAR-2000x2000.png`
- Nguồn vector để sửa: `assets/brand/song-tu/5-phong-cach/van-vo.svg`, code `scripts/brand/avatar_5.py --van-vo` (nhân vật ở `scripts/brand/song_tu.py`)
- Cách đặt trên YouTube: YouTube Studio → Tùy chỉnh (Customization) → Xây dựng thương hiệu (Branding) → Ảnh (Picture) → Tải lên → kéo khung vừa vòng tròn → Xong → **Xuất bản**. YouTube khuyên ảnh ≥ 98×98, ≤ 4 MB, PNG/JPG.
- Các mẫu không chọn (để dùng chỗ khác): `5-phong-cach/` – sơn mài, phẳng tối giản, ấn triện, âm dương, đêm Bạch Đằng.

## Banner ✅ (bản 16/11/2026)
- File tải lên: `assets/brand/song-tu/BANNER-YouTube-2560x1440.png` (2560×1440, ~2,5 MB; YouTube cho tối đa 6 MB)
- Bố cục: nền bản đồ cổ (phần Bắc Bộ – Hoa Nam, không địa danh, không phải bản đồ Việt Nam toàn cảnh) · dải giữa tối: Anh Văn mở sách (trái), Em Võ kiếm + khiên (phải), ♊, "SONG TỬ KỂ SỬ", "Văn kể sử – Võ dẫn trận", "Chiến trận lịch sử Việt Nam & Trung Hoa qua bản đồ hoạt họa", "VIDEO MỚI HẰNG TUẦN" · rìa (chỉ TV thấy): thuyền và lính hai phe.
- Toàn bộ chữ + nhân vật nằm trong vùng an toàn 1546×423. Ảnh kiểm tra: `banner-kiem-tra-vung-an-toan.jpg`, `banner-xem-tren-dien-thoai.jpg`, `banner-xem-tren-may-tinh.jpg`.
- Code: `scripts/brand/banner.py` (sửa chữ/bố cục rồi chạy lại).
- Cách đặt: YouTube Studio → Tùy chỉnh → Xây dựng thương hiệu → Hình ảnh biểu ngữ → Tải lên → kiểm tra khung xem trước → Xong → **Xuất bản**.

## Việc còn lại khi đổi kênh
- [ ] Kiểm tra & đặt tên kênh + handle trên YouTube (Tùy chỉnh → Thông tin cơ bản)
- [x] Avatar
- [x] Banner
- [ ] Watermark (avatar thu nhỏ, góc phải dưới video)
- [ ] Viết lại mô tả kênh (giữ dòng công khai dùng AI cho hình & giọng)
- [ ] Đổi end card video E2 sang logo mới, tạo playlist "Ngược Dòng Sử Việt"
