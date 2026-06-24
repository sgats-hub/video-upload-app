import sqlite3
import os

conn = sqlite3.connect('instance/videos.db')
cursor = conn.cursor()

cursor.execute("SELECT filename FROM video")
db_filenames = set(row[0] for row in cursor.fetchall())

uploads_dir = 'uploads'
all_files = os.listdir(uploads_dir)
mp4_files = [f for f in all_files if f.endswith('.mp4')]

print(f"数据库记录数: {len(db_filenames)}")
print(f"uploads目录mp4文件数: {len(mp4_files)}")

missing_files = [f for f in mp4_files if f not in db_filenames]
print(f"\n缺少数据库记录的视频文件数: {len(missing_files)}")

if missing_files:
    print("\n缺少记录的视频文件:")
    for f in sorted(missing_files):
        print(f"  - {f}")

conn.close()
