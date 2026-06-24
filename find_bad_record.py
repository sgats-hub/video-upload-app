import sqlite3
import os

print("Current directory:", os.getcwd())

conn = sqlite3.connect('instance/videos.db')
cursor = conn.cursor()
cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
tables = cursor.fetchall()
print("Tables in instance/videos.db:", [t[0] for t in tables])

cursor.execute("SELECT COUNT(*) FROM video")
count = cursor.fetchone()[0]
print(f"Video count in instance/videos.db: {count}")

print("\nChecking uploaded_at values...")
cursor.execute("SELECT id, filename, uploaded_at FROM video")
rows = cursor.fetchall()

bad_records = []
for row in rows:
    vid, filename, uploaded_at = row
    if uploaded_at and len(str(uploaded_at)) < 10:
        bad_records.append((vid, filename, uploaded_at))
        print(f"Bad record - ID:{vid}, filename:{filename}, uploaded_at:{uploaded_at}")

print(f"\nTotal bad records: {len(bad_records)}")

today = '2026-06-24'
cursor.execute("SELECT id, filename, uploaded_at, status FROM video WHERE uploaded_at LIKE ?", (f'{today}%',))
today_rows = cursor.fetchall()
print(f"\nToday's videos ({today}): {len(today_rows)}")
for row in today_rows:
    print(f"ID:{row[0]}, filename:{row[1]}, uploaded_at:{row[2]}, status:{row[3]}")

conn.close()
