from werkzeug.security import generate_password_hash
import sqlite3

# 连接数据库
conn = sqlite3.connect('instance/videos.db')
cursor = conn.cursor()

# 设置新密码（这里设置为 'admin123'）
new_password = 'admin123'
hashed_password = generate_password_hash(new_password)

# 更新密码
cursor.execute("UPDATE user SET password = ? WHERE username = 'admin'", (hashed_password,))
conn.commit()

print(f"密码已重置为: {new_password}")

# 验证更新
cursor.execute("SELECT * FROM user WHERE username = 'admin'")
user = cursor.fetchone()
print(f"用户信息 - ID: {user[0]}, 用户名: {user[1]}, 角色: {user[3]}")

conn.close()