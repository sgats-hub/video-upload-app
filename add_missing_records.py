import sqlite3
import os
from datetime import datetime

conn = sqlite3.connect('instance/videos.db')
cursor = conn.cursor()

# 获取分类信息
cursor.execute("SELECT id, name FROM video_category")
categories = {row[1]: row[0] for row in cursor.fetchall()}
print("分类信息:", categories)

# 缺失的视频文件
missing_files = [
    '20260601_164433.mp4',
    '20260601_165144.mp4',
    '20260601_165342.mp4',
    '20260601_165814.mp4',
    '20260601_171751.mp4',
    '20260601_172122.mp4',
    '20260601_172439.mp4',
    '20260601_172955.mp4',
    '20260609_150117.mp4'
]

# 获取现有的最大ID
cursor.execute("SELECT MAX(id) FROM video")
max_id = cursor.fetchone()[0] or 0
print(f"\n现有最大视频ID: {max_id}")

# 默认分类（未分类）
default_category_id = categories.get('其他', 7)

added_count = 0
for filename in missing_files:
    # 从文件名提取日期时间
    date_part = filename[:8]  # YYYYMMDD
    time_part = filename[9:15]  # HHMMSS
    
    year = date_part[:4]
    month = date_part[4:6]
    day = date_part[6:8]
    hour = time_part[:2]
    minute = time_part[2:4]
    second = time_part[4:6]
    
    uploaded_at = f'{year}-{month}-{day} {hour}:{minute}:{second}'
    
    # 获取文件大小
    file_path = os.path.join('uploads', filename)
    if os.path.exists(file_path):
        file_size = os.path.getsize(file_path)
    else:
        print(f"警告: 文件不存在 {filename}")
        continue
    
    # 插入数据库记录
    max_id += 1
    cursor.execute("""
        INSERT INTO video (id, filename, original_name, size, duration, uploaded_at, status, uploaded_by, category_id)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
    """, (max_id, filename, filename, file_size, '00:00', uploaded_at, 'completed', 1, default_category_id))
    
    added_count += 1
    print(f"添加记录: ID={max_id}, filename={filename}, size={file_size/(1024*1024):.1f}MB, uploaded_at={uploaded_at}")

conn.commit()
print(f"\n总共添加了 {added_count} 条记录")

# 验证
cursor.execute("SELECT COUNT(*) FROM video")
total = cursor.fetchone()[0]
print(f"数据库现在有 {total} 条视频记录")

conn.close()
