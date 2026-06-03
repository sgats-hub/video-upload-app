import sqlite3

# 连接数据库
conn = sqlite3.connect('instance/videos.db')
cursor = conn.cursor()

# 获取所有表
cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
tables = cursor.fetchall()
print("数据库中的表:")
for table in tables:
    print(f"  - {table[0]}")

# 检查每个表的结构
for table in tables:
    table_name = table[0]
    print(f"\n表 {table_name} 的结构:")
    cursor.execute(f"PRAGMA table_info({table_name})")
    columns = cursor.fetchall()
    for col in columns:
        print(f"  - {col[1]} ({col[2]})")

    # 获取前5条数据
    print(f"表 {table_name} 的前5条数据:")
    cursor.execute(f"SELECT * FROM {table_name} LIMIT 5")
    rows = cursor.fetchall()
    for row in rows:
        print(f"  {row}")

conn.close()