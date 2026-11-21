---
name: cham-but
description: Chấm điểm /100 một nhân vật vẽ bằng Bộ Bút bằng SUBAGENT ĐỘC LẬP (Claude nhìn ảnh, không dùng Gemini) theo phiếu nhận diện + 12 luật vẽ đẹp; trả góp ý dạng "khoá spec: cũ → mới". Dưới 80 thì sửa → vẽ lại → chấm lại. Dùng sau mỗi lần render nhân vật trong scripts/hoathinh/but/.
---

# Chấm nhân vật Bộ Bút (≥ 80 mới đưa người dùng xem)

Người chấm là **subagent mới mỗi vòng** (không mang theo suy nghĩ của người vẽ → khách quan hơn). Không cần Gemini, không tốn quota.

## Chuẩn bị (người vẽ làm)
```
python scripts/hoathinh/but/ve.py <ma> --bong-den --bieu-cam-bang
```
→ `build/thu-hoathinh/but/<ma>.png`, `<ma>-bong.png`, `<ma>-bieu-cam.png`. Có **phiếu nhận diện** `docs/nhan-vat/but/<ma>.md` (xem skill `tu-ve-nhan-vat`).

## Gọi subagent (Agent, general-purpose) – prompt mẫu
> Bạn là giám khảo thiết kế nhân vật hoạt hình chibi cho kênh YouTube lịch sử Việt. Đọc phiếu nhận diện `<đường dẫn phiếu>` và luật vẽ trong `.claude/skills/bo-ve/SKILL.md` (mục "12 luật vẽ đẹp"). Xem 3 ảnh: `<ma>.png` (toàn thân), `<ma>-bong.png` (bóng dáng tô đen), `<ma>-bieu-cam.png` (6 biểu cảm). Không đọc code. Chấm khắt khe theo thang dưới, trả về:
> 1. Bảng điểm từng mục + lý do 1 câu.
> 2. TỔNG /100.
> 3. Tối đa 5 việc CẦN SỬA, xếp theo mức ảnh hưởng, mỗi việc cụ thể theo R hoặc mã màu (vd "râu: mép giữa hạ thấp 0.1R", "áo #5E7B50 hơi xỉn → xanh rêu sáng hơn"). Không khen chung chung.
> 4. Nếu một người xem bình thường nhìn ảnh mà không biết tên, họ đoán là ai?

| Mục | Điểm | Đạt khi |
|---|---|---|
| A. Nhận diện | 25 | đủ mọi đặc trưng "phải có" trong phiếu; người xem đoán đúng tên |
| B. Khung & luật | 15 | đúng khung chung, MỘT tay, vũ khí thấp (đỉnh không vượt chuẩn Ngộ Không), mặt 3/4 phải |
| C. Nét | 15 | 3 cấp rõ (ngoài dày, trong vừa, chi tiết mảnh thuôn); không hở, không răng cưa |
| D. Màu & bóng | 15 | ≤5 màu chính hài hoà; bóng phẳng đúng hướng sáng trên-trái; không gradient/glow |
| E. Hình khối & bóng dáng | 15 | ảnh tô đen vẫn nhận ra; khối chồng hợp lý; không chi tiết vụn/rối |
| F. Mặt & dễ thương | 15 | mắt/mày/miệng rõ ở cỡ nhỏ; 6 biểu cảm phân biệt được; không bôi xấu |

## Sau khi chấm
- Lưu kết quả vào `docs/nhan-vat/but/<ma>-cham.md` (mỗi vòng một mục: ngày, điểm, việc sửa).
- **≥ 80 → ĐẠT**, chuyển bước chốt trong `tu-ve-nhan-vat`.
- **< 80** → dịch từng việc sửa thành thay đổi spec (`nv/<ma>.py`) hoặc thay đổi hàm bộ phận (nếu lỗi nằm ở bộ phận dùng chung thì sửa ở `bo_phan.py` và kiểm lại các nhân vật khác). Render lại, gọi **subagent mới** chấm lại. Tối đa 4 vòng; quá 4 vòng thì gửi người dùng bản tốt nhất kèm điểm và các điểm còn vướng.
- **Chống lật qua lật lại** (bài học Sa Tăng 69→77→78→82): giám khảo mới mỗi vòng có thể đòi ngược vòng trước (vòng 3 đòi sọ trắng + cán vàng, vòng 4 đòi ngược lại). Từ vòng 2, đưa kèm `<ma>-cham.md` vào prompt và dặn: "không đòi đảo lại điều đã sửa theo vòng trước, trừ khi nó làm hỏng nhận diện". Khi hai vòng mâu thuẫn, giữ theo phiếu nhận diện.
- Bàn tay tách thân là chủ ý của khung – ghi rõ trong prompt để giám khảo không trừ điểm.
- Người vẽ **tự xem ảnh trước** khi gọi giám khảo – lỗi hiển nhiên (bộ phận lệch, hở, đè sai lớp) sửa luôn, không tốn vòng chấm.
