import os
import subprocess

def get_video_codec(file_path):
    result = subprocess.run(['ffmpeg', '-i', file_path], capture_output=True)
    output = result.stderr.decode('utf-8', errors='ignore')
    if 'Video: hevc' in output:
        return 'HEVC (H.265)'
    elif 'Video: h264' in output:
        return 'H.264'
    return 'unknown'

uploads_dir = 'uploads'
mp4_files = [f for f in os.listdir(uploads_dir) if f.endswith('.mp4') and not f.endswith('_temp.mp4')]

print("=== 修复后视频编码格式 ===")
hevc_count = 0
h264_count = 0
for filename in mp4_files:
    filepath = os.path.join(uploads_dir, filename)
    codec = get_video_codec(filepath)
    print(f"{filename}: {codec}")
    if codec == 'HEVC (H.265)':
        hevc_count += 1
    elif codec == 'H.264':
        h264_count += 1

print(f"\nH.264 视频: {h264_count} 个")
print(f"HEVC (H.265) 视频: {hevc_count} 个")

# 清理临时文件
temp_files = [f for f in os.listdir(uploads_dir) if f.endswith('_temp.mp4') or f.endswith('_temp.mov')]
if temp_files:
    print(f"\n清理临时文件 ({len(temp_files)} 个):")
    for f in temp_files:
        os.remove(os.path.join(uploads_dir, f))
        print(f"  删除: {f}")

print("\n验证完成！")