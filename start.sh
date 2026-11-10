#!/bin/bash

# Hàm dọn dẹp (tự động tắt cả Flask lẫn Tunnel khi bạn bấm Ctrl + C)
cleanup() {
    echo -e "\n[!] Đang dừng tất cả các dịch vụ..."
    kill 0
    exit 0
}

# Bắt tín hiệu ngắt (Ctrl + C hoặc khi đóng terminal)
trap cleanup SIGINT SIGTERM

echo "[*] Đang khởi động ứng dụng Flask..."
uv run run.py &

# Chờ 2 giây để đảm bảo Flask đã kịp bind vào cổng 5000
sleep 2

echo "[*] Đang khởi động Cloudflare Tunnel..."
cloudflared tunnel run --url http://localhost:5000 flask-app &

# Giữ script chạy để chờ tín hiệu từ người dùng
wait
