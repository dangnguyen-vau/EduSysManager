#!/bin/bash
# Script chạy server Sinh Viên trên port 8002

export NODE_TYPE=sv
echo "Đang chạy server Sinh Viên trên port 8002..."
cd "$(dirname "$0")"
python manage.py runserver 0.0.0.0:8002 