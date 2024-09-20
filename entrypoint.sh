#!/bin/bash

# 檢查數據庫文件是否存在
if [ ! -f /app/data/db.sqlite3 ]; then
    # 如果不存在，運行數據庫遷移
    python manage.py makemigrations
    python manage.py migrate
else
    # 如果存在，只運行遷移（不創建新的遷移文件）
    python manage.py migrate
fi

# 執行傳遞給腳本的命令
exec "$@"