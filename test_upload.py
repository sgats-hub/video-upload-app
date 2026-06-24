import requests
import json

# 测试分类API
print("=== 测试分类API ===")
try:
    response = requests.get('http://localhost:5000/api/categories')
    print(f"状态码: {response.status_code}")
    print(f"响应内容: {response.text}")
except Exception as e:
    print(f"请求失败: {e}")

# 测试登录
print("\n=== 测试登录 ===")
try:
    # 使用新密码登录
    login_data = {'username': 'admin', 'password': 'admin123', 'role': 'admin'}
    response = requests.post('http://localhost:5000/api/login', json=login_data)
    print(f"状态码: {response.status_code}")
    print(f"响应内容: {response.text}")
    
    # 保存session
    session = requests.Session()
    session.cookies.update(response.cookies)
    
    # 测试上传（模拟一个小文件）
    print("\n=== 测试上传API ===")
    # 创建一个小的测试文件
    with open('test_video.mp4', 'wb') as f:
        f.write(b'\x00\x00\x00\x18ftypmp42\x00\x00\x00\x00mp42isom')
    
    with open('test_video.mp4', 'rb') as f:
        upload_data = {'category_id': '7'}
        files = {'file': ('test_video.mp4', f, 'video/mp4')}
        response = session.post('http://localhost:5000/api/upload', data=upload_data, files=files)
        print(f"状态码: {response.status_code}")
        print(f"响应内容: {response.text}")
        
except Exception as e:
    print(f"请求失败: {e}")