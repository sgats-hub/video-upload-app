import requests
import json
import time

BASE_URL = "http://localhost:5000"

def test_security_headers():
    """测试安全响应头"""
    print("=== 测试安全响应头 ===")
    try:
        response = requests.get(f"{BASE_URL}/api/videos")
        headers = response.headers
        
        required_headers = [
            'X-Content-Type-Options',
            'X-Frame-Options', 
            'X-XSS-Protection',
            'Content-Security-Policy',
            'Strict-Transport-Security',
            'Referrer-Policy'
        ]
        
        print("检测到的安全响应头:")
        for header in required_headers:
            if header in headers:
                print(f"  ✓ {header}: {headers[header]}")
            else:
                print(f"  ✗ {header}: 缺失")
        print()
    except Exception as e:
        print(f"  ✗ 请求失败: {e}")
        print()

def test_rate_limit():
    """测试速率限制"""
    print("=== 测试速率限制 ===")
    try:
        # 快速发送多个请求
        success_count = 0
        for i in range(110):
            response = requests.get(f"{BASE_URL}/api/videos")
            if response.status_code == 429:
                print(f"  ✓ 成功触发速率限制（第 {i+1} 次请求）")
                break
            success_count += 1
        else:
            print(f"  ✗ 未触发速率限制，成功请求 {success_count} 次")
        print()
    except Exception as e:
        print(f"  ✗ 请求失败: {e}")
        print()

def test_invalid_file_upload():
    """测试上传非法文件"""
    print("=== 测试文件类型验证 ===")
    try:
        # 尝试上传非视频文件
        files = {'file': ('test.txt', b'not a video file', 'text/plain')}
        data = {'username': 'admin', 'password': 'admin123'}
        response = requests.post(f"{BASE_URL}/api/upload", files=files, data=data)
        
        if response.status_code == 400 and '不支持的文件类型' in response.text:
            print("  ✓ 成功阻止非法文件上传")
        else:
            print(f"  ✗ 文件验证失败，状态码: {response.status_code}")
        print()
    except Exception as e:
        print(f"  ✗ 请求失败: {e}")
        print()

def test_unauthorized_access():
    """测试未授权访问"""
    print("=== 测试未授权访问 ===")
    try:
        # 尝试不带凭证上传
        files = {'file': ('test.mp4', b'test', 'video/mp4')}
        response = requests.post(f"{BASE_URL}/api/upload", files=files)
        
        if response.status_code == 403:
            print("  ✓ 成功阻止未授权上传")
        else:
            print(f"  ✗ 未授权访问检测失败，状态码: {response.status_code}")
        
        # 尝试使用错误密码
        data = {'username': 'admin', 'password': 'wrongpassword'}
        response = requests.post(f"{BASE_URL}/api/login", json=data)
        
        if response.status_code == 200:
            result = response.json()
            if result.get('success') == False or result.get('user', {}).get('role') != 'admin':
                print("  ✓ 成功阻止错误凭证")
            else:
                print("  ✗ 错误密码被接受")
        print()
    except Exception as e:
        print(f"  ✗ 请求失败: {e}")
        print()

def test_sql_injection():
    """测试SQL注入防护"""
    print("=== 测试SQL注入防护 ===")
    try:
        # 尝试SQL注入
        payload = {"username": "' OR '1'='1", "password": "any"}
        response = requests.post(f"{BASE_URL}/api/login", json=payload)
        
        if response.status_code == 200:
            result = response.json()
            if result.get('user', {}).get('role') == 'admin':
                print("  ✗ SQL注入漏洞存在！")
            else:
                print("  ✓ SQL注入被阻止")
        else:
            print("  ✓ 请求被正确处理")
        print()
    except Exception as e:
        print(f"  ✗ 请求失败: {e}")
        print()

def test_password_hashing():
    """测试密码哈希存储"""
    print("=== 测试密码哈希存储 ===")
    # 检查数据库中密码是否为哈希值
    try:
        import sqlite3
        conn = sqlite3.connect('videos.db')
        cursor = conn.cursor()
        cursor.execute("SELECT password FROM user WHERE username='admin'")
        result = cursor.fetchone()
        
        if result:
            password = result[0]
            # 哈希值通常较长且包含特定字符
            if len(password) > 50 and '$pbkdf2' in password:
                print("  ✓ 密码已使用PBKDF2哈希加密存储")
            elif len(password) > 32:
                print("  ✓ 密码已加密存储")
            else:
                print("  ✗ 密码可能以明文存储")
        conn.close()
        print()
    except Exception as e:
        print(f"  ✗ 检查失败: {e}")
        print()

def test_cors():
    """测试CORS配置"""
    print("=== 测试CORS配置 ===")
    try:
        # 模拟非允许的来源请求
        headers = {'Origin': 'http://malicious.com'}
        response = requests.get(f"{BASE_URL}/api/videos", headers=headers)
        
        cors_header = response.headers.get('Access-Control-Allow-Origin')
        if cors_header == 'http://malicious.com':
            print("  ✗ CORS配置过宽，允许非法来源")
        else:
            print("  ✓ CORS配置正确，只允许指定来源")
        print()
    except Exception as e:
        print(f"  ✗ 请求失败: {e}")
        print()

if __name__ == "__main__":
    print("=" * 60)
    print("          视频上传系统安全测试")
    print("=" * 60)
    print()
    
    test_security_headers()
    test_rate_limit()
    test_invalid_file_upload()
    test_unauthorized_access()
    test_sql_injection()
    test_password_hashing()
    test_cors()
    
    print("=" * 60)
    print("                      测试完成")
    print("=" * 60)