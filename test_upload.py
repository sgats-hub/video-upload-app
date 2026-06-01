import requests

url = 'http://localhost:5000/api/upload'

# 创建测试文件
with open('test_video.txt', 'rb') as f:
    files = {'file': f}
    data = {
        'username': 'admin',
        'password': 'admin123',
        'category_id': 1
    }
    
    print(f"正在上传到: {url}")
    print(f"数据: {data}")
    
    try:
        response = requests.post(url, files=files, data=data)
        print(f"响应状态码: {response.status_code}")
        print(f"响应内容: {response.text}")
    except Exception as e:
        print(f"上传失败: {e}")
