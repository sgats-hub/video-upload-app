import sqlite3

# 连接数据库
conn = sqlite3.connect('instance/videos.db')
cursor = conn.cursor()

# 查询用户表
cursor.execute("SELECT * FROM user")
users = cursor.fetchall()
print("数据库中的用户:")
for user in users:
    print(f"ID: {user[0]}, 用户名: {user[1]}, 角色: {user[3]}")

conn.close()