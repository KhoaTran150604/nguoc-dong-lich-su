# Master file – 2 dự án (sử Việt + Tây Du Ký)

> Trả lời người dùng bằng **tiếng Việt**, thân thiện, ngắn gọn.
> File gốc này cố ý **mỏng** để đỡ tốn context. Chi tiết nằm trong CLAUDE.md của từng dự án — **mở đúng file dự án đang làm**.

## 🧭 Làm dự án nào đọc file đó
| Việc đang làm | Mở file |
|---|---|
| **Vẽ nhân vật chibi, Tây Du Ký, hoạt hình nhân vật** | `du-an/tay-du-ky/CLAUDE.md` |
| **Sử Việt, Ngược Dòng, Bạch Đằng, kênh Song Tử Kể Sử, mascot Gâu Nghệ, dựng video sử** (📦 lưu trữ, ít dùng) | `du-an/nguoc-dong-su-viet/CLAUDE.md` |

- Skill cũng tách theo dự án: skill của mỗi dự án nằm trong `du-an/<dự án>/.claude/skills/` — **chỉ hiện khi làm trong nhánh đó**. Gốc chỉ giữ skill **dùng chung**: `bo-ve`, `dong-bo`, `dang-short`, `dang-youtube`.
- Khi tạo/sửa nhân vật: vào `du-an/tay-du-ky/` để prompt → nạp đúng luật vẽ, đỡ tốn token.

## 🔧 Dùng chung (cả 2 dự án)

### Bộ Bút – vẽ nhân vật (dùng chung)
- Engine: `scripts/hoathinh/but/` (skia) — `but.py` lõi, `khung.py`, `bo_phan.py`, `nv/<ma>.py` spec, `ve.py` render.
- Skill **`bo-ve`**: 12 luật vẽ đẹp (nét 3 cấp, bóng phẳng, khối cộng/trừ, khung chung, vũ khí thấp một tay, KHÔNG cổ) + API + bộ phận. Trước đây tên `but-ve`.
- Chi tiết dùng ở dự án Tây Du → `du-an/tay-du-ky/CLAUDE.md`.

### Đăng YouTube (dùng chung – Claude in Chrome)
- Skill **`dang-short`** (Short 9:16) + **`dang-youtube`** (video dài): điều khiển YouTube Studio của người dùng, tải file >10 MB không nén, điền metadata, **chỉ lên lịch, không "Công khai ngay"**. Cùng **kênh Song Tử Kể Sử** cho cả 2 dự án.
- Tây Du: Short xong → vào `du-an/tay-du-ky/upload-video/` rồi gọi `dang-short` (mục **TÂY DU** trong skill: file lấy ở `thanh-pham.json` mục `short_hoathinh`, tiêu đề/mô tả theo kịch bản Tây Du, playlist hỏi người dùng).

### Đồng bộ cloud ↔ máy nhà (LUẬT ĐỒNG BỘ)
- **`main` là nhánh chuẩn duy nhất.** Mỗi phiên cloud làm trên nhánh `claude/…` riêng → **kết thúc phiên: tạo PR vào main**, người dùng bấm Merge. Không để nhánh cloud nằm treo.
- **Máy nhà:** ngồi vào là chạy đồng bộ — nhấp đúp `dong-bo.command` (Mac) / `dong-bo.bat` (Windows), hoặc nói "đồng bộ" (skill `dong-bo`). Rời máy: commit + push.
- **Video không đi qua git:** dựng lại từ code bằng `scripts/dong_bo.py` theo `docs/videos/thanh-pham.json`. Thumbnail/ảnh ≤10 MB có thể đẩy lên Drive.

### Môi trường kỹ thuật
- Python: `pip install cairosvg pillow numpy shapely fonttools brotli skia-python` (skia cho Bộ Bút); **ffmpeg**; Node: `npm i world-atlas@2 topojson-client@3`.
- Font: copy `fonts/*.ttf` vào thư mục font hệ thống rồi `fc-cache -f` (Linux).
- Giọng đọc: `pip install zerotts faster-whisper`, `export HF_HUB_DISABLE_XET=1` (chi tiết trong dự án sử).
- Khóa API: `G:\My Drive\envpi_key.txt`.

## 📂 Cấu trúc gốc
```
CLAUDE.md                 ← file này (mỏng)
.claude/skills/           ← CHỈ skill dùng chung: bo-ve, dong-bo, dang-short, dang-youtube
chung (sắp xếp ở GĐ2)     ← Bộ Bút engine dự kiến tách ra scripts/hoathinh/but/ hiện vẫn ở chỗ cũ
du-an/
  tay-du-ky/              ← 🎯 ĐANG LÀM: CLAUDE.md + nhan-vat/ kich-ban/ animation/ + .claude/skills/
  nguoc-dong-su-viet/     ← 📦 LƯU TRỮ: CLAUDE.md + .claude/skills/ (nội dung kb/ docs/ scripts/ sẽ dời ở GĐ2)
scripts/ assets/ docs/ kb/ video/ build/ data/ fonts/   ← file hiện vẫn ở gốc; GĐ2 mới dời vào du-an/
```
> **GĐ2 (chưa làm):** dời `kb/ docs/ scripts/ assets/ video/` của từng dự án vào `du-an/…`, tách Bộ Bút thành lớp dùng chung, sửa import Python, render thử lại. Hiện mọi đường dẫn trong skill vẫn trỏ về gốc như cũ.
