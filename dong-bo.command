#!/bin/bash
# Mac: nhấp đúp để đồng bộ (lần đầu: chuột phải → Open). Không cần mở Claude.
cd "$(dirname "$0")" && python3 scripts/dong_bo.py; echo; read -n1 -p "Nhấn phím bất kỳ để đóng…"
