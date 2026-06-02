from flask import Flask, request, jsonify, send_from_directory, abort
from flask_sqlalchemy import SQLAlchemy
from flask_cors import CORS
from werkzeug.security import generate_password_hash, check_password_hash
import os
import uuid
import mimetypes
from datetime import datetime, timedelta
import threading  # 💡 引入多线程支持

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

# ✅ 修正一：CORS 配置加上了你的前端 8088 端口
CORS(app, supports_credentials=True, origins=[
    "http://localhost:8088",  # 👈 你的 Nginx 前端本地端口
    "http://localhost:5173",
    "http://localhost:5174",
    "https://2minutevideos.com",  # 👈 你的正式域名
    "https://www.2minutevideos.com",
    "http://2minutevideos.com",
    "http://www.2minutevideos.com"
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
    'video/mp4', 'video/avi', 'video/quicktime', 'video/x-ms-wmv',
    'video/x-flv', 'video/x-matroska', 'video/webm'
}

# 验证文件MIME类型
def validate_file_type(file):
    file.seek(0)
    header = file.read(256)
    file.seek(0)
    if header.startswith(b'\x00\x00\x00\x18ftyp') or header.startswith(b'\x00\x00\x00\x1cftyp') or header.startswith(b'\x00\x00\x00 ftyp'):
        return 'video/mp4'
    elif header.startswith(b'RIFF') and b'AVI ' in header[:12]:
        return 'video/avi'
    elif header.startswith(b'\x00\x00\x00 ftypqt') or header.startswith(b'qt  '):
        return 'video/quicktime'
    elif header.startswith(b'WEBM'):
        return 'video/webm'
    elif header.startswith(b'MKV'):
        return 'video/x-matroska'
    elif header.startswith(b'FLV'):
        return 'video/x-flv'
    elif header.startswith(b'ASF'):
        return 'video/x-ms-wmv'
    
    mime_type = mimetypes.guess_type(file.filename)[0]
    if mime_type is None:
        ext = os.path.splitext(file.filename)[1].lower()
        ext_mapping = {
            '.mp4': 'video/mp4', '.avi': 'video/avi', '.mov': 'video/quicktime',
            '.webm': 'video/webm', '.mkv': 'video/x-matroska', '.flv': 'video/x-flv', '.wmv': 'video/x-ms-wmv'
        }
        mime_type = ext_mapping.get(ext)
    return mime_type

# 用户模型
class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(50), unique=True, nullable=False)
    password = db.Column(db.String(100), nullable=False)
    role = db.Column(db.String(20), default='viewer')

    def to_dict(self):
        return {'id': self.id, 'username': self.username, 'role': self.role}

# 视频分类模型
class VideoCategory(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50), unique=True, nullable=False)
    icon = db.Column(db.String(50), default='📁')

    def to_dict(self):
        return {'id': self.id, 'name': self.name, 'icon': self.icon}

# 视频模型
class Video(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    filename = db.Column(db.String(255), nullable=False)
    original_name = db.Column(db.String(255), nullable=False)
    size = db.Column(db.Integer, nullable=False)
    duration = db.Column(db.String(20))
    uploaded_at = db.Column(db.DateTime, default=datetime.now)
    status = db.Column(db.String(20), default='processing')  # 💡 默认改成 processing（处理中）
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
        if bytes < 1024: return f"{bytes} B"
        if bytes < 1024 * 1024: return f"{bytes / 1024:.1f} KB"
        return f"{bytes / (1024 * 1024):.1f} MB"

with app.app_context():
    db.create_all()
    if not User.query.filter_by(username='admin').first():
        db.session.add(User(username='admin', password=generate_password_hash('admin123'), role='admin'))
        db.session.commit()
    
    default_categories = [
        {'name': '学习类', 'icon': '📚'}, {'name': '工作类', 'icon': '💼'},
        {'name': '生活类', 'icon': '🏠'}, {'name': '访谈类', 'icon': '🎤'},
        {'name': '人物传记类', 'icon': '📖'}, {'name': '娱乐类', 'icon': '🎮'},
        {'name': '其他', 'icon': '📁'}
    ]
    for cat in default_categories:
        if not VideoCategory.query.filter_by(name=cat['name']).first():
            db.session.add(VideoCategory(name=cat['name'], icon=cat['icon']))
            db.session.commit()

# 登录API
@app.route('/api/login', methods=['POST'])
def login():
    data = request.json
    username = data.get('username')
    password = data.get('password')
    role = data.get('role', 'viewer')
    
    if role == 'viewer':
        return jsonify({'success': True, 'user': {'username': username or 'viewer', 'role': 'viewer'}})
    
    user = User.query.filter_by(username=username).first()
    if user and check_password_hash(user.password, password) and user.role == 'admin':
        return jsonify({'success': True, 'user': user.to_dict()})
    return jsonify({'success': False, 'error': '用户名或密码错误'}), 401

@app.route('/api/user', methods=['GET'])
def get_user():
    return jsonify({'success': True, 'user': None})

@app.route('/api/change-password', methods=['POST'])
def change_password():
    data = request.json
    username = data.get('username')
    old_password = data.get('old_password')
    new_password = data.get('new_password')
    
    user = User.query.filter_by(username=username).first()
    if not user: return jsonify({'success': False, 'error': '用户不存在'}), 404
    if not check_password_hash(user.password, old_password):
        return jsonify({'success': False, 'error': '旧密码错误'}), 403
    if not new_password or len(new_password) < 6:
        return jsonify({'success': False, 'error': '新密码至少需要6位'}), 400
    
    user.password = generate_password_hash(new_password)
    db.session.commit()
    return jsonify({'success': True, 'message': '密码修改成功'})

@app.route('/api/categories', methods=['GET'])
def get_categories():
    categories = VideoCategory.query.all()
    desired_order = ['学习类', '工作类', '生活类', '访谈类', '人物传记类', '娱乐类', '其他']
    categories.sort(key=lambda x: desired_order.index(x.name) if x.name in desired_order else len(desired_order))
    return jsonify([cat.to_dict() for cat in categories])

MESSAGES_FILE = 'messages.txt'
MAX_MESSAGES_SIZE = 5 * 1024 * 1024 * 1024

@app.route('/api/messages', methods=['GET'])
def get_messages():
    messages = []
    if os.path.exists(MESSAGES_FILE):
        try:
            with open(MESSAGES_FILE, 'r', encoding='utf-8') as f:
                for line in f:
                    line = line.strip()
                    if line and line.startswith('['):
                        parts = line.split(']', 1)
                        if len(parts) == 2:
                            messages.append({'time': parts[0][1:], 'content': parts[1].strip()})
        except Exception as e: print(f"读取留言文件失败: {e}")
    return jsonify(messages[-100:])

@app.route('/api/messages', methods=['POST'])
def add_message():
    data = request.json
    content = data.get('content', '').strip()
    if not content: return jsonify({'success': False, 'message': '留言内容不能为空'}), 400
    if os.path.exists(MESSAGES_FILE) and os.path.getsize(MESSAGES_FILE) >= MAX_MESSAGES_SIZE:
        return jsonify({'success': False, 'message': '留言板已满，无法添加新留言'}), 400
    try:
        with open(MESSAGES_FILE, 'a', encoding='utf-8') as f:
            f.write(f'[{datetime.now().strftime("%Y-%m-%d %H:%M:%S")}] {content}\n')
        return jsonify({'success': True, 'message': '留言成功'})
    except Exception as e: return jsonify({'success': False, 'message': f'保存留言失败: {str(e)}'}), 500

MAX_FILE_SIZE = 500 * 1024 * 1024  # 统一前后端为 500MB
MAX_VIDEO_COUNT = 10000

# ✅ 修正二：后台多线程异步压缩函数（不阻塞主响应）
def async_video_processing(app_context, temp_path, file_path, video_id, ext):
    """在子线程中安全运行的视频处理逻辑"""
    with app_context:  # 必须激活 Flask 上下文才能操作数据库
        video = Video.query.get(video_id)
        if not video: return
        
        try:
            success = False
            if FFMPEG_AVAILABLE and ext in ['.mp4', '.avi', '.mov', '.wmv', '.flv', '.mkv']:
                print(f"[后台线程] 开始压缩视频 ID: {video_id}...")
                probe = ffmpeg.probe(temp_path)
                video_stream = next((stream for stream in probe['streams'] if stream['codec_type'] == 'video'), None)
                
                if video_stream:
                    width = video_stream['width']
                    height = video_stream['height']
                    fps = eval(video_stream.get('r_frame_rate', '30/1'))
                    
                    (
                        ffmpeg.input(temp_path)
                        .output(file_path, vcodec='libx265', crf=32, preset='fast',
                                acodec='aac', audio_bitrate='128k', s=f"{width}x{height}",
                                r=fps, movflags='faststart')
                        .overwrite_output().run(capture_stdout=True, capture_stderr=True)
                    )
                    success = True
            
            if success:
                if os.path.exists(temp_path): os.remove(temp_path)
                print(f"[后台线程] 视频 ID {video_id} 压缩成功")
            else:
                # 压缩不可用或失败，回滚使用原始文件
                if os.path.exists(temp_path):
                    if os.path.exists(file_path): os.remove(file_path)
                    os.rename(temp_path, file_path)
                print(f"[后台线程] 跳过或压缩失败，已将原始文件存盘")
            
            # 更新状态为完成，更新最终的物理文件大小
            video.status = 'completed'
            video.size = os.path.getsize(file_path)
            db.session.commit()
            
        except Exception as e:
            print(f"[后台线程] 处理视频异常: {str(e)}")
            if os.path.exists(temp_path) and not os.path.exists(file_path):
                os.rename(temp_path, file_path)
            video.status = 'completed'  # 即使失败也让它能看
            db.session.commit()

@app.route('/api/upload', methods=['POST'])
def upload_video():
    try:
        data = request.form
        username = data.get('username')
        password = data.get('password')
        category_id = data.get('category_id', 1)
        
        user = User.query.filter_by(username=username).first()
        if not user or not check_password_hash(user.password, password) or user.role != 'admin':
            return jsonify({'success': False, 'error': '无权限上传'}), 403
        
        if 'file' not in request.files:
            return jsonify({'success': False, 'error': '请选择要上传的文件'}), 400
        
        file = request.files['file']
        if file.filename == '':
            return jsonify({'success': False, 'error': '请选择要上传的文件'}), 400
        
        file.seek(0, os.SEEK_END)
        file_size = file.tell()
        file.seek(0)
        
        if file_size > MAX_FILE_SIZE:
            return jsonify({'success': False, 'error': '文件大小超过限制（最大500MB）'}), 400
        
        mime_type = validate_file_type(file)
        if mime_type is None or mime_type not in ALLOWED_MIME_TYPES:
            return jsonify({'success': False, 'error': '不支持的文件类型，请上传视频文件'}), 400
        
        if Video.query.count() >= MAX_VIDEO_COUNT:
            return jsonify({'success': False, 'error': '视频数量已达上限'}), 400
        
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        ext = os.path.splitext(file.filename)[1].lower()
        new_filename = f"{timestamp}.mp4"
        file_path = os.path.join(app.config['UPLOAD_FOLDER'], new_filename)
        temp_path = os.path.join(app.config['UPLOAD_FOLDER'], f"{timestamp}_temp{ext}")
        
        # 快速保存原始流到临时文件
        file.save(temp_path)
        
        # 先在数据库里建档挂号（状态为处理中 processing）
        video = Video(
            filename=new_filename,
            original_name=file.filename,
            size=file_size,
            duration='00:00',
            uploaded_by=user.id,
            category_id=int(category_id),
            status='processing'
        )
        db.session.add(video)
        db.session.commit()
        
        # 💡 ✅ 核心拯救：开启后台子线程异步执行 FFmpeg 转码，彻底解放主线程
        # 传递 app_context 确保子线程有数据库访问权限
        thr = threading.Thread(
            target=async_video_processing, 
            args=(app.app_context(), temp_path, file_path, video.id, ext)
        )
        thr.start()
        
        # 🚀 秒级给前端交卷，Cloudflare 100秒的 524 限制直接失效！
        return jsonify({
            'success': True,
            'video': video.to_dict()
        })
        
    except Exception as e:
        return jsonify({'success': False, 'error': f'服务器内部错误: {str(e)}'}), 500

@app.route('/api/videos', methods=['GET'])
def get_videos():
    category_id = request.args.get('category_id')
    search = request.args.get('search', '')
    page = int(request.args.get('page', 1))
    per_page = int(request.args.get('per_page', 10))
    
    query = Video.query
    if category_id: query = query.filter_by(category_id=category_id)
    if search: query = query.filter(Video.original_name.ilike(f'%{search}%'))
    
    query = query.order_by(Video.uploaded_at.desc())
    paginated = query.paginate(page=page, per_page=per_page, error_out=False)
    
    return jsonify({
        'items': [v.to_dict() for v in paginated.items],
        'total': paginated.total,
        'page': paginated.page,
        'per_page': paginated.per_page,
        'pages': paginated.pages
    })

# ✅ 修正三：理顺并修复 video_actions 的 PUT/DELETE 分支嵌套逻辑
@app.route('/api/videos/<int:id>', methods=['DELETE', 'PUT'])
def video_actions(id):
    print(f"===== [{datetime.now()}] video_actions 请求 =====")
    print(f"请求方法: {request.method}")
    print(f"视频ID: {id}")
    
    data = request.json or {}
    print(f"请求数据: {data}")
    
    username = data.get('username')
    password = data.get('password')
    
    print(f"用户名: {username}")
    
    user = User.query.filter_by(username=username).first()
    if not user:
        print("错误: 用户不存在")
        return jsonify({'success': False, 'error': '无权限操作'}), 403
    
    if not check_password_hash(user.password, password):
        print("错误: 密码不正确")
        return jsonify({'success': False, 'error': '无权限操作'}), 403
    
    if user.role != 'admin':
        print("错误: 非管理员用户")
        return jsonify({'success': False, 'error': '无权限操作'}), 403
    
    video = Video.query.get(id)
    if not video:
        print("错误: 视频不存在")
        return jsonify({'success': False, 'error': '视频不存在'}), 404
    
    if request.method == 'DELETE':
        print(f"开始删除视频: {video.filename}")
        
        file_path = os.path.join(app.config['UPLOAD_FOLDER'], video.filename)
        # 同时也检查并清理可能遗留的临时转码文件
        temp_name = video.filename.replace('.mp4', '_temp')
        for f in os.listdir(app.config['UPLOAD_FOLDER']):
            if f.startswith(temp_name):
                try: 
                    os.remove(os.path.join(app.config['UPLOAD_FOLDER'], f))
                    print(f"清理临时文件: {f}")
                except Exception as e: 
                    print(f"清理临时文件失败: {e}")
                
        if os.path.exists(file_path):
            os.remove(file_path)
            print(f"已删除文件: {file_path}")
        
        db.session.delete(video)
        db.session.commit()
        print(f"视频 {id} 删除成功")
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

@app.route('/api/videos/<filename>', methods=['GET'])
def serve_video(filename):
    return send_from_directory(app.config['UPLOAD_FOLDER'], filename)

if __name__ == '__main__':
    app.run(debug=True, port=5000)