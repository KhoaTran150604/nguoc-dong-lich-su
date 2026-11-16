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

## Banner ⏳
- Kích thước 2560×1440, vùng an toàn (hiện trên mọi thiết bị) 1546×423 ở giữa.
- Ý tưởng: Anh Văn trái (bản đồ, sách sử) – Em Võ phải (chiến thuyền, lính hai phe) – giữa: "SONG TỬ KỂ SỬ" + "Văn kể sử – Võ dẫn trận".

## Việc còn lại khi đổi kênh
- [ ] Kiểm tra & đặt tên kênh + handle trên YouTube (Tùy chỉnh → Thông tin cơ bản)
- [x] Avatar
- [ ] Banner
- [ ] Watermark (avatar thu nhỏ, góc phải dưới video)
- [ ] Viết lại mô tả kênh (giữ dòng công khai dùng AI cho hình & giọng)
- [ ] Đổi end card video E2 sang logo mới, tạo playlist "Ngược Dòng Sử Việt"
