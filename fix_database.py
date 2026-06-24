import sqlite3
import os

conn = sqlite3.connect('instance/videos.db')
cursor = conn.cursor()

cursor.execute("SELECT id, filename, uploaded_at FROM video")
rows = cursor.fetchall()

fixed_count = 0
for row in rows:
    vid, filename, uploaded_at = row
    if uploaded_at and len(str(uploaded_at)) < 10:
        try:
            date_part = filename[:8]
            time_part = filename[9:15]
            if len(date_part) == 8 and len(time_part) == 6:
                year = date_part[:4]
                month = date_part[4:6]
                day = date_part[6:8]
                hour = time_part[:2]
                minute = time_part[2:4]
                second = time_part[4:6]
                correct_date = f'{year}-{month}-{day} {hour}:{minute}:{second}'
                cursor.execute("UPDATE video SET uploaded_at = ? WHERE id = ?", (correct_date, vid))
                fixed_count += 1
                print(f"Fixed ID:{vid}, filename:{filename}, uploaded_at:{uploaded_at} -> {correct_date}")
        except Exception as e:
            print(f"Failed to fix ID:{vid}, filename:{filename}, error:{e}")

conn.commit()
print(f"\nFixed {fixed_count} records")

cursor.execute("SELECT COUNT(*) FROM video")
total = cursor.fetchone()[0]
print(f"Total videos: {total}")

today = '2026-06-24'
cursor.execute("SELECT id, filename, uploaded_at, status FROM video WHERE uploaded_at LIKE ?", (f'{today}%',))
today_rows = cursor.fetchall()
print(f"\nToday's videos ({today}): {len(today_rows)}")
for row in today_rows:
    print(f"ID:{row[0]}, filename:{row[1]}, uploaded_at:{row[2]}, status:{row[3]}")

conn.close()
