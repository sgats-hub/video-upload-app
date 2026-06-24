import os
import subprocess

def get_video_codec(file_path):
    try:
        result = subprocess.run(
            ['ffmpeg', '-i', file_path],
            capture_output=True
        )
        output = result.stderr.decode('utf-8', errors='ignore')
        if 'Video: hevc' in output:
            return 'hevc'
        elif 'Video: h264' in output:
            return 'h264'
        return 'unknown'
    except Exception as e:
        print(f"检测编码失败 {file_path}: {e}")
        return 'unknown'

def convert_to_h264(input_path, output_path):
    try:
        print(f"正在转换: {input_path}")
        result = subprocess.run(
            [
                'ffmpeg', '-i', input_path,
                '-vcodec', 'libx264', '-crf', '23', '-preset', 'fast',
                '-acodec', 'aac', '-b:a', '128k',
                '-pix_fmt', 'yuv420p', '-movflags', 'faststart',
                '-y', output_path
            ],
            capture_output=True
        )
        if result.returncode == 0:
            print(f"转换成功")
            return True
        else:
            print(f"转换失败: {result.stderr.decode('utf-8', errors='ignore')}")
            return False
    except Exception as e:
        print(f"转换异常: {e}")
        return False

def main():
    uploads_dir = 'uploads'
    mp4_files = [f for f in os.listdir(uploads_dir) if f.endswith('.mp4') and not f.endswith('_temp.mp4')]
    
    print(f"找到 {len(mp4_files)} 个 mp4 文件\n")
    
    hevc_files = []
    for filename in mp4_files:
        filepath = os.path.join(uploads_dir, filename)
        codec = get_video_codec(filepath)
        print(f"{filename}: {codec}")
        if codec == 'hevc':
            hevc_files.append(filename)
    
    print(f"\n需要转换的 H.265 视频: {len(hevc_files)} 个")
    
    for filename in hevc_files:
        input_path = os.path.join(uploads_dir, filename)
        temp_path = os.path.join(uploads_dir, 'temp_' + filename)
        
        if convert_to_h264(input_path, temp_path):
            os.remove(input_path)
            os.rename(temp_path, input_path)
            print(f"已修复: {filename}")
        else:
            if os.path.exists(temp_path):
                os.remove(temp_path)
    
    print("\n修复完成！")

if __name__ == '__main__':
    main()