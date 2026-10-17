# Hộp thư relay giữa mini-agent và Muse

Repo công khai này là "hộp thư" + "kho code" cho kiến trúc
**Muse là não, agent là tay**.

## Giao thức hộp thư (`hop_thu.jsonl`, mỗi dòng 1 JSON)

- Agent hỏi: `{"tu": "agent", "id": "<id>", "luc": "<iso>", "noi_dung": "<cau hoi>"}`
- Agent báo kết quả: `{"tu": "agent", "id": "<id>", "ket_qua_cho": "<task_id>", "luc": "<iso>", "noi_dung": "<tom tat>"}`
- Muse trả lời: `{"tu": "muse", "id": "<id>", "tra_loi_cho": "<id>", "luc": "<iso>", "noi_dung": "<tra loi>"}`

Phía Muse có hook kiểm tra file này mỗi 2 phút; có dòng `agent` mới là Muse
được đánh thức và trả lời trong chat.

## Kho code

- `manifest.json`: phiên bản hiện tại của `runner.py`, `tools.py`, `hop_thu.py`.
  Runner tự tải bản mới khi số phiên bản tăng.
- `nhiem_vu.json`: nhiệm vụ hiện tại `{"task_id": "...", "mo_ta": "...", "timeout_giay": 300}`.
- `nhiem_vu/<task_id>.py`: code nhiệm vụ do Muse viết.
- `ket_qua/<task_id>.json`: kết quả chi tiết do runner ghi.

## Quy tắc an toàn

Repo này là **công khai** để hook đọc được không cần mật khẩu. Chỉ dùng để
hỏi/đáp kỹ thuật và chứa code nhiệm vụ. **Không bao giờ ghi API key, mật khẩu,
token vào đây.**
