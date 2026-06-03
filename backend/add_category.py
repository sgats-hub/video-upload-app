import sqlite3

# 连接数据库
conn = sqlite3.connect('instance/videos.db')
cursor = conn.cursor()

# 检查是否已存在人物传记类
cursor.execute("SELECT * FROM video_category WHERE name = '人物传记类'")
existing = cursor.fetchone()

if existing:
    print(f"人物传记类已存在，ID: {existing[0]}")
else:
    # 添加人物传记类
    cursor.execute("INSERT INTO video_category (id, name, icon) VALUES (7, '人物传记类', '📖')")
    conn.commit()
    print("人物传记类添加成功！")

# 验证结果
cursor.execute("SELECT * FROM video_category")
categories = cursor.fetchall()
print("\n当前所有分类:")
for cat in categories:
    print(f"ID: {cat[0]}, 名称: {cat[1]}, 图标: {cat[2]}")

conn.close()