from flask import Flask, request, jsonify, send_from_directory, abort
from flask_sqlalchemy import SQLAlchemy
from flask_cors import CORS
from werkzeug.security import generate_password_hash, check_password_hash
import os
import uuid
import mimetypes
from datetime import datetime, timedelta

# 简单的速率限制（基于IP）
RATE_LIMIT = {}
RATE_LIMIT_MAX = 100  # 每分钟最多100次请求
RATE_LIMIT_WINDOW = 60  # 时间窗口（秒）

# 尝试导入 ffmpeg
try:
    import ffmpeg
    FFMPEG_AVAILABLE = True
except ImportError:
    FFMPEG_AVAILABLE = False

app = Flask(__name__)

# CORS配置（生产环境请修改为实际域名）
CORS(app, supports_credentials=True, origins=[
    "http://localhost:5173",
    "http://localhost:5174",
    "https://2mintuevideos.com",
    "https://www.2mintuevideos.com",
    "http://2mintuevideos.com",
    "http://www.2mintuevideos.com"
], methods=["GET", "POST", "DELETE", "PUT", "OPTIONS"], allow_headers=["Content-Type"])

# 配置数据库
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///videos.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['UPLOAD_FOLDER'] = 'uploads'
app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', 'default-secret-key-change-in-production')
app.config['MAX_CONTENT_LENGTH'] = 5 * 1024 * 1024 * 1024  # 5GB

db = SQLAlchemy(app)

# 创建uploads目录
os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)

# 安全响应头中间件
@app.after_request
def set_security_headers(response):
    response.headers['X-Content-Type-Options'] = 'nosniff'
    response.headers['X-Frame-Options'] = 'DENY'
    response.headers['X-XSS-Protection'] = '1; mode=block'
    response.headers['Content-Security-Policy'] = "default-src 'self'; img-src 'self' data:; media-src 'self'"
    response.headers['Strict-Transport-Security'] = 'max-age=31536000; includeSubDomains'
    response.headers['Referrer-Policy'] = 'strict-origin-when-cross-origin'
    return response

# 速率限制中间件
@app.before_request
def rate_limit():
    client_ip = request.remote_addr
    
    now = datetime.now()
    if client_ip not in RATE_LIMIT:
        RATE_LIMIT[client_ip] = {'count': 1, 'timestamp': now}
    else:
        elapsed = (now - RATE_LIMIT[client_ip]['timestamp']).total_seconds()
        if elapsed > RATE_LIMIT_WINDOW:
            RATE_LIMIT[client_ip] = {'count': 1, 'timestamp': now}
        else:
            RATE_LIMIT[client_ip]['count'] += 1
            if RATE_LIMIT[client_ip]['count'] > RATE_LIMIT_MAX:
                abort(429, description="请求过于频繁，请稍后再试")

# 允许的视频MIME类型
ALLOWED_MIME_TYPES = {
    'video/mp4',
    'video/avi',
    'video/quicktime',
    'video/x-ms-wmv',
    'video/x-flv',
    'video/x-matroska',
    'video/webm'
}

# 验证文件MIME类型
def validate_file_type(file):
    """检查文件的实际内容类型"""
    file.seek(0)
    header = file.read(256)
    file.seek(0)
    
    # 简单的魔数检查
    if header.startswith(b'\x00\x00\x00\x18ftyp') or header.startswith(b'\x00\x00\x00\x1cftyp'):
        return 'video/mp4'
    elif header.startswith(b'RIFF') and b'AVI ' in header[:12]:
        return 'video/avi'
    elif header.startswith(b'\x00\x00\x00 ftypqt'):
        return 'video/quicktime'
    elif header.startswith(b'WEBM'):
        return 'video/webm'
    elif header.startswith(b'MKV'):
        return 'video/x-matroska'
    
    # 使用mimetypes猜测
    mime_type = mimetypes.guess_type(file.filename)[0]
    return mime_type

# 用户模型
class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(50), unique=True, nullable=False)
    password = db.Column(db.String(100), nullable=False)
    role = db.Column(db.String(20), default='viewer')  # admin 或 viewer

    def to_dict(self):
        return {
            'id': self.id,
            'username': self.username,
            'role': self.role
        }

# 视频分类模型
class VideoCategory(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50), unique=True, nullable=False)
    icon = db.Column(db.String(50), default='📁')

    def to_dict(self):
        return {
            'id': self.id,
            'name': self.name,
            'icon': self.icon
        }

# 视频模型
class Video(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    filename = db.Column(db.String(255), nullable=False)
    original_name = db.Column(db.String(255), nullable=False)
    size = db.Column(db.Integer, nullable=False)
    duration = db.Column(db.String(20))
    uploaded_at = db.Column(db.DateTime, default=datetime.now)
    status = db.Column(db.String(20), default='completed')
    uploaded_by = db.Column(db.Integer, db.ForeignKey('user.id'))
    category_id = db.Column(db.Integer, db.ForeignKey('video_category.id'))

    category = db.relationship('VideoCategory', backref='videos')

    def to_dict(self):
        return {
            'id': self.id,
            'filename': self.filename,
            'original_name': self.original_name,
            'size': self.format_size(self.size),
            'duration': self.duration,
            'uploaded_at': self.uploaded_at.strftime('%Y-%m-%d %H:%M'),
            'status': self.status,
            'category_id': self.category_id,
            'category_name': self.category.name if self.category else '未分类',
            'category_icon': self.category.icon if self.category else '📁',
            'url': f'/api/videos/{self.filename}'
        }
    
    @staticmethod
    def format_size(bytes):
        if bytes < 1024:
            return f"{bytes} B"
        if bytes < 1024 * 1024:
            return f"{bytes / 1024:.1f} KB"
        return f"{bytes / (1024 * 1024):.1f} MB"

# 创建数据库表
with app.app_context():
    db.create_all()
    # 创建默认管理员账户（如果不存在）
    if not User.query.filter_by(username='admin').first():
        # 使用哈希加密存储密码
        hashed_password = generate_password_hash('admin123')
        admin = User(username='admin', password=hashed_password, role='admin')
        db.session.add(admin)
        db.session.commit()
        print("默认管理员账户已创建: admin / admin123")
    
    # 创建默认分类（如果不存在）
    default_categories = [
        {'name': '学习类', 'icon': '📚'},
        {'name': '工作类', 'icon': '💼'},
        {'name': '生活类', 'icon': '🏠'},
        {'name': '访谈类', 'icon': '🎤'},
        {'name': '人物传记类', 'icon': '📖'},
        {'name': '娱乐类', 'icon': '🎮'},
        {'name': '其他', 'icon': '📁'}
    ]
    for cat in default_categories:
        if not VideoCategory.query.filter_by(name=cat['name']).first():
            category = VideoCategory(name=cat['name'], icon=cat['icon'])
            db.session.add(category)
            db.session.commit()
            print(f"分类已创建: {cat['icon']} {cat['name']}")

# 登录API
@app.route('/api/login', methods=['POST'])
def login():
    data = request.json
    username = data.get('username')
    password = data.get('password')
    role = data.get('role', 'viewer')
    
    if role == 'viewer':
        # 普通用户无需验证，直接登录
        return jsonify({
            'success': True,
            'user': {'username': username or 'viewer', 'role': 'viewer'}
        })
    
    # 管理员需要验证
    user = User.query.filter_by(username=username).first()
    
    if user and check_password_hash(user.password, password) and user.role == 'admin':
        return jsonify({
            'success': True,
            'user': user.to_dict()
        })
    
    return jsonify({'success': False, 'error': '用户名或密码错误'}), 401

# 获取当前用户信息
@app.route('/api/user', methods=['GET'])
def get_user():
    return jsonify({'success': True, 'user': None})

# 修改密码
@app.route('/api/change-password', methods=['POST'])
def change_password():
    data = request.json
    username = data.get('username')
    old_password = data.get('old_password')
    new_password = data.get('new_password')
    
    user = User.query.filter_by(username=username).first()
    
    if not user:
        return jsonify({'success': False, 'error': '用户不存在'}), 404
    
    # 使用哈希验证旧密码
    if not check_password_hash(user.password, old_password):
        return jsonify({'success': False, 'error': '旧密码错误'}), 403
    
    if not new_password or len(new_password) < 6:
        return jsonify({'success': False, 'error': '新密码至少需要6位'}), 400
    
    # 使用哈希加密新密码
    user.password = generate_password_hash(new_password)
    db.session.commit()
    
    return jsonify({'success': True, 'message': '密码修改成功'})

# 获取分类列表
@app.route('/api/categories', methods=['GET'])
def get_categories():
    categories = VideoCategory.query.all()
    
    # 定义期望的分类顺序
    desired_order = [
        '学习类',
        '工作类', 
        '生活类',
        '访谈类',
        '人物传记类',
        '娱乐类',
        '其他'
    ]
    
    # 按照期望顺序排序
    categories.sort(key=lambda x: desired_order.index(x.name) if x.name in desired_order else len(desired_order))
    
    return jsonify([cat.to_dict() for cat in categories])

# 留言板功能
MESSAGES_FILE = 'messages.txt'
MAX_MESSAGES_SIZE = 5 * 1024 * 1024 * 1024  # 5GB

def get_file_size(filepath):
    """获取文件大小"""
    try:
        return os.path.getsize(filepath)
    except:
        return 0

def format_time():
    """获取当前时间格式化字符串"""
    return datetime.now().strftime('%Y-%m-%d %H:%M:%S')

@app.route('/api/messages', methods=['GET'])
def get_messages():
    """获取留言列表"""
    messages = []
    if os.path.exists(MESSAGES_FILE):
        try:
            with open(MESSAGES_FILE, 'r', encoding='utf-8') as f:
                for line in f:
                    line = line.strip()
                    if line:
                        # 格式: [时间] 留言内容
                        if line.startswith('['):
                            parts = line.split(']', 1)
                            if len(parts) == 2:
                                messages.append({
                                    'time': parts[0][1:],
                                    'content': parts[1].strip()
                                })
                        else:
                            messages.append({
                                'time': '',
                                'content': line
                            })
        except Exception as e:
            print(f"读取留言文件失败: {e}")
    
    # 返回最近的消息（最多100条）
    return jsonify(messages[-100:])

@app.route('/api/messages', methods=['POST'])
def add_message():
    """添加留言"""
    data = request.json
    content = data.get('content', '').strip()
    
    if not content:
        return jsonify({'success': False, 'message': '留言内容不能为空'}), 400
    
    # 检查文件大小
    current_size = get_file_size(MESSAGES_FILE)
    if current_size >= MAX_MESSAGES_SIZE:
        return jsonify({'success': False, 'message': '留言板已满，无法添加新留言'}), 400
    
    # 写入留言
    try:
        timestamp = format_time()
        with open(MESSAGES_FILE, 'a', encoding='utf-8') as f:
            f.write(f'[{timestamp}] {content}\n')
        return jsonify({'success': True, 'message': '留言成功'})
    except Exception as e:
        return jsonify({'success': False, 'message': f'保存留言失败: {str(e)}'}), 500

# 配置常量
MAX_FILE_SIZE = 5 * 1024 * 1024 * 1024  # 5GB
MAX_VIDEO_COUNT = 10000  # 最多1万个视频

# 视频压缩函数
def compress_video(input_path, output_path):
    """
    使用 H.265 编码压缩视频
    """
    try:
        probe = ffmpeg.probe(input_path)
        video_stream = next((stream for stream in probe['streams'] if stream['codec_type'] == 'video'), None)
        
        if not video_stream:
            return False, "未找到视频流"
        
        # 获取原始视频参数
        width = video_stream['width']
        height = video_stream['height']
        fps = eval(video_stream.get('r_frame_rate', '30/1'))
        
        # 构建压缩命令（更快的预设和稍高的CRF值）
        (
            ffmpeg
            .input(input_path)
            .output(
                output_path,
                vcodec='libx265',
                crf=32,  # 质量控制，0-51，32适合网络传输，文件更小
                preset='fast',  # 更快的压缩速度
                acodec='aac',
                audio_bitrate='128k',
                s=f"{width}x{height}",
                r=fps,
                movflags='faststart'  # 优化流媒体播放
            )
            .overwrite_output()
            .run(capture_stdout=True, capture_stderr=True)
        )
        
        original_size = os.path.getsize(input_path)
        compressed_size = os.path.getsize(output_path)
        compression_ratio = (1 - compressed_size / original_size) * 100
        
        print(f"视频压缩完成: {original_size/1024/1024:.2f} MB -> {compressed_size/1024/1024:.2f} MB ({compression_ratio:.1f}% 压缩率)")
        
        return True, f"压缩完成，节省 {compression_ratio:.1f}% 空间"
    
    except Exception as e:
        print(f"视频压缩失败: {str(e)}")
        return False, str(e)

# API路由
@app.route('/api/upload', methods=['POST'])
def upload_video():
    print("收到上传请求")
    print("请求方法:", request.method)
    print("请求表单:", request.form)
    print("请求文件:", request.files)
    # 检查是否为管理员
    data = request.form
    username = data.get('username')
    password = data.get('password')
    category_id = data.get('category_id', 1)
    
    user = User.query.filter_by(username=username).first()
    if not user or not check_password_hash(user.password, password) or user.role != 'admin':
        return jsonify({'success': False, 'error': '无权限上传'}), 403
    
    if 'file' not in request.files:
        return jsonify({'error': 'No file uploaded'}), 400
    
    file = request.files['file']
    if file.filename == '':
        return jsonify({'error': 'No file selected'}), 400
    
    # 验证文件类型（检查实际内容）
    mime_type = validate_file_type(file)
    if mime_type not in ALLOWED_MIME_TYPES:
        return jsonify({'success': False, 'error': '不支持的文件类型，请上传视频文件'}), 400
    
    # 检查文件大小
    file.seek(0, os.SEEK_END)
    file_size = file.tell()
    file.seek(0)
    
    if file_size > MAX_FILE_SIZE:
        return jsonify({'success': False, 'error': f'文件大小超过限制（最大5GB）'}), 400
    
    # 检查视频数量限制
    video_count = Video.query.count()
    if video_count >= MAX_VIDEO_COUNT:
        return jsonify({'success': False, 'error': f'视频数量已达上限（最多{MAX_VIDEO_COUNT}个）'}), 400
    
    # 生成唯一文件名
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    ext = os.path.splitext(file.filename)[1].lower()
    new_filename = f"{timestamp}.mp4"  # 统一转换为MP4格式
    file_path = os.path.join(app.config['UPLOAD_FOLDER'], new_filename)
    temp_path = os.path.join(app.config['UPLOAD_FOLDER'], f"{timestamp}_temp{ext}")
    
    # 先保存原始文件到临时位置
    file.save(temp_path)
    
    # 压缩视频（如果 ffmpeg 可用）
    if FFMPEG_AVAILABLE and ext in ['.mp4', '.avi', '.mov', '.wmv', '.flv', '.mkv']:
        success, message = compress_video(temp_path, file_path)
        if not success:
            # 压缩失败，使用原始文件
            os.rename(temp_path, file_path)
            print(f"压缩失败，使用原始文件: {message}")
        else:
            # 压缩成功，删除临时文件
            os.remove(temp_path)
    else:
        # ffmpeg 不可用或非视频文件，直接重命名
        os.rename(temp_path, file_path)
        if not FFMPEG_AVAILABLE:
            print("ffmpeg 不可用，跳过视频压缩")
    
    # 保存到数据库
    video = Video(
        filename=new_filename,
        original_name=file.filename,
        size=os.path.getsize(file_path),
        duration='00:00',
        uploaded_by=user.id,
        category_id=int(category_id)
    )
    db.session.add(video)
    db.session.commit()
    
    return jsonify({
        'success': True,
        'video': video.to_dict()
    })

@app.route('/api/videos', methods=['GET'])
def get_videos():
    category_id = request.args.get('category_id')
    search = request.args.get('search', '')
    page = int(request.args.get('page', 1))
    per_page = int(request.args.get('per_page', 10))
    
    query = Video.query
    
    if category_id:
        query = query.filter_by(category_id=category_id)
    
    if search:
        query = query.filter(Video.original_name.ilike(f'%{search}%'))
    
    query = query.order_by(Video.uploaded_at.desc())
    
    paginated = query.paginate(page=page, per_page=per_page, error_out=False)
    
    return jsonify({
        'items': [v.to_dict() for v in paginated.items],
        'total': paginated.total,
        'page': paginated.page,
        'per_page': paginated.per_page,
        'pages': paginated.pages
    })

@app.route('/api/videos/<int:id>', methods=['DELETE', 'PUT'])
def video_actions(id):
    # 检查是否为管理员
    data = request.json
    username = data.get('username')
    password = data.get('password')
    
    user = User.query.filter_by(username=username).first()
    if not user or not check_password_hash(user.password, password) or user.role != 'admin':
        return jsonify({'success': False, 'error': '无权限操作'}), 403
    
    video = Video.query.get(id)
    if not video:
        return jsonify({'success': False, 'error': '视频不存在'}), 404
    
    if request.method == 'DELETE':
        # 删除文件
        file_path = os.path.join(app.config['UPLOAD_FOLDER'], video.filename)
        if os.path.exists(file_path):
            os.remove(file_path)
        
        # 删除数据库记录
        db.session.delete(video)
        db.session.commit()
        
        return jsonify({'success': True})
    
    elif request.method == 'PUT':
        new_name = data.get('name')
        category_id = data.get('category_id')
        
        if not new_name:
            return jsonify({'success': False, 'error': '视频名称不能为空'}), 400
        
        video.original_name = new_name
        if category_id is not None and category_id != '' and category_id != 'null':
            video.category_id = int(category_id)
        
        db.session.commit()
        
        return jsonify({'success': True, 'video': video.to_dict()})
    
    if not video:
        return jsonify({'success': False, 'error': '视频不存在'}), 404
    
    video.original_name = new_name
    if category_id is not None and category_id != '' and category_id != 'null':
        video.category_id = int(category_id)
    
    db.session.commit()
    print("Video updated successfully")
    
    return jsonify({'success': True, 'video': video.to_dict()})

@app.route('/api/videos/<filename>', methods=['GET'])
def serve_video(filename):
    return send_from_directory(app.config['UPLOAD_FOLDER'], filename)

if __name__ == '__main__':
    print("=== Registered Routes ===")
    for rule in app.url_map.iter_rules():
        print(f"{rule} -> {rule.endpoint} (methods: {rule.methods})")
    app.run(debug=True, port=5000)