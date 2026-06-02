import requests
import os

def test_upload():
    url = 'http://localhost:5000/api/upload'
    
    # 查找现有的视频文件用于测试
    video_files = []
    for f in os.listdir('.'):
        if f.lower().endswith(('.mp4', '.avi', '.mov', '.webm', '.mkv')):
            video_files.append(f)
    
    if not video_files:
        print("错误: 当前目录没有找到视频文件")
        print("请将一个视频文件放在此目录下，或修改脚本使用正确的文件路径")
        return
    
    test_file = video_files[0]
    print(f"找到测试视频: {test_file}")
    
    file_size = os.path.getsize(test_file)
    print(f"文件大小: {file_size / (1024 * 1024):.2f} MB")
    
    # 检查文件大小是否超过限制
    if file_size > 500 * 1024 * 1024:
        print("警告: 文件大小超过500MB限制，可能会失败")
    
    with open(test_file, 'rb') as f:
        files = {'file': (test_file, f, 'video/mp4')}
        data = {
            'username': 'admin',
            'password': 'admin123',
            'category_id': 1
        }
        
        print(f"\n正在上传到: {url}")
        print(f"数据: {data}")
        
        try:
            response = requests.post(url, files=files, data=data, timeout=300)
            print(f"\n响应状态码: {response.status_code}")
            print(f"响应内容: {response.text}")
            
            try:
                result = response.json()
                if result.get('success'):
                    print("\n✅ 上传成功!")
                    print(f"视频ID: {result['video']['id']}")
                    print(f"文件名: {result['video']['original_name']}")
                    print(f"保存路径: {result['video']['url']}")
                else:
                    print(f"\n❌ 上传失败: {result.get('error')}")
            except:
                print(f"\n响应不是有效的JSON")
                
        except requests.exceptions.Timeout:
            print("❌ 上传超时")
        except requests.exceptions.ConnectionError:
            print("❌ 连接失败，请确保后端服务正在运行")
        except Exception as e:
            print(f"❌ 上传失败: {e}")

if __name__ == '__main__':
    test_upload()
