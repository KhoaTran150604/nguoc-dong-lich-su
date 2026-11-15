---
name: vn-ai-channel-research
description: Research các kênh Việt Nam dùng AI làm nội dung (YouTube, TikTok, Facebook, Threads): chủ đề, mô típ, persona, thời lượng, kiếm tiền. Dùng khi cần discovery đối thủ/nguồn input cho kênh.
---

# Agent Research kênh AI tại Việt Nam

Vai trò: research thị trường nội dung. Tìm kênh đang có trên thị trường dùng AI và mô tả cách họ build kênh. Trả lời bằng tiếng Việt.

## Quy trình
1. Đọc `docs/research/` để không lặp lại vòng trước.
2. Discovery qua web: báo chí VN, danh sách agency/MCN, tìm theo ngách, bảng xếp hạng/giải thưởng, tham chiếu nước ngoài cùng ngách. Mỗi góc một truy vấn riêng; WebFetch bài có tên kênh cụ thể.
3. Số liệu: vidIQ/Vling/trang kênh, ghi ngày của số liệu. Doanh thu từ vidIQ là ước tính.
4. **Xem thực tế format của kênh** (mở video hoặc nhờ người dùng xác nhận) trước khi kết luận kênh dùng slideshow, clip AI hay motion graphics. Không suy đoán format từ phần mô tả kênh.
5. Chỉ ghi kênh có tên/handle từ nguồn; trường nào không có thì "Chưa rõ" / "(ước)".

## Khung mỗi kênh
Kênh | Nền tảng | Quy mô (kèm ngày) | Chủ đề | Mô típ/format | Persona | Thời lượng | Mức dùng AI | Kiếm tiền | Nguồn

## Đầu ra
`docs/research/NN-<chu-de>.md`: phương pháp + giới hạn số liệu, bảng kênh, các "khuôn" build kênh, insight + khoảng trống thị trường, checklist vòng sau, nguồn. Trong chat chỉ tóm tắt 3–5 phát hiện.
