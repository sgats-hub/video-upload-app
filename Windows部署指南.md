# Windows服务器部署指南

## 📋 部署前准备

### 1. 服务器要求
- Windows Server 2016/2019/2022 或 Windows 10/11
- 至少 2GB 内存
- 至少 50GB 硬盘空间（用于存储视频）
- 公网IP地址

### 2. 需要安装的软件

| 软件 | 用途 | 下载地址 |
|------|------|---------|
| Python 3.8+ | 后端运行环境 | https://www.python.org/downloads/ |
| NSSM | 将Flask注册为Windows服务 | https://nssm.cc/download |
| Nginx for Windows | 前端Web服务器 | http://nginx.org/en/download.html |
| FFmpeg | 视频压缩（可选） | https://ffmpeg.org/download.html |

---

## 🚀 部署步骤

### 第一步：上传项目文件

将以下文件上传到服务器（建议放在 `C:\inetpub\wwwroot\video-upload-app\`）：

```
video-upload-app/
├── backend/          # 后端代码
│   ├── app.py
│   └── ...
├── dist/             # 前端编译产物
│   ├── index.html
│   └── assets/
├── deploy_windows.bat
├── install_service.bat
└── nginx_windows.conf
```

### 第二步：安装Python

1. 下载 Python 3.8+ 安装包
2. 安装时勾选 **"Add Python to PATH"**
3. 验证安装：
   ```cmd
   python --version
   pip --version
   ```

### 第三步：运行部署脚本

1. 右键点击 `deploy_windows.bat`
2. 选择 **"以管理员身份运行"**
3. 等待脚本完成

### 第四步：安装NSSM

1. 下载 NSSM：https://nssm.cc/download
2. 解压后找到 `nssm.exe`（根据系统选择 win32 或 win64）
3. 将 `nssm.exe` 复制到 `C:\Windows\System32\`

### 第五步：安装后端服务

1. 右键点击 `install_service.bat`
2. 选择 **"以管理员身份运行"**
3. 服务会自动启动

验证服务状态：
```cmd
sc query VideoUploadApp
```

### 第六步：安装Nginx

1. 下载 Nginx for Windows：http://nginx.org/en/download.html
2. 解压到 `C:\nginx\`
3. 复制 `nginx_windows.conf` 内容到 `C:\nginx\conf\nginx.conf`
4. **修改配置文件中的路径**：
   - 将 `D:/path/to/video-upload-app/dist` 改为实际路径
   - 例如：`C:/inetpub/wwwroot/video-upload-app/dist`

启动Nginx：
```cmd
cd C:\nginx
start nginx
```

验证Nginx运行：
```cmd
tasklist /fi "imagename eq nginx.exe"
```

### 第七步：配置防火墙

打开端口 80、443、5000、5173：
```cmd
netsh advfirewall firewall add rule name="HTTP" dir=in action=allow protocol=tcp localport=80
netsh advfirewall firewall add rule name="HTTPS" dir=in action=allow protocol=tcp localport=443
netsh advfirewall firewall add rule name="Flask" dir=in action=allow protocol=tcp localport=5000
```

### 第八步：配置域名DNS

在你的域名服务商后台（购买2mintuevideos.com的地方）：

1. 添加 **A记录**：
   - 主机记录：`@`
   - 记录类型：`A`
   - 记录值：你的服务器公网IP

2. 添加 **A记录**：
   - 主机记录：`www`
   - 记录类型：`A`
   - 记录值：你的服务器公网IP

---

## 🔒 配置HTTPS（推荐）

### 方法一：使用Let's Encrypt（推荐）

1. 下载 win-acme：https://www.win-acme.com/
2. 解压到 `C:\win-acme\`
3. 运行：
   ```cmd
   cd C:\win-acme
   wacs.exe
   ```
4. 按提示选择：
   - N：创建新证书
   - 4：手动输入域名
   - 输入：`2mintuevideos.com,www.2mintuevideos.com`
   - 选择验证方式（推荐DNS验证）

### 方法二：使用自签名证书（测试用）

```powershell
# 创建自签名证书
New-SelfSignedCertificate -DnsName "2mintuevideos.com","www.2mintuevideos.com" -CertStoreLocation "cert:\LocalMachine\My"
```

---

## 📊 服务管理

### Flask后端服务

```cmd
# 启动
nssm start VideoUploadApp

# 停止
nssm stop VideoUploadApp

# 重启
nssm restart VideoUploadApp

# 查看状态
sc query VideoUploadApp

# 删除服务
nssm remove VideoUploadApp confirm
```

### Nginx服务

```cmd
# 启动
cd C:\nginx
start nginx

# 停止
nginx -s stop

# 重启
nginx -s reload

# 测试配置
nginx -t
```

---

## 🔧 常见问题

### 1. 端口被占用

查看端口占用：
```cmd
netstat -ano | findstr :80
netstat -ano | findstr :5000
```

结束占用进程：
```cmd
taskkill /PID 进程ID /F
```

### 2. 服务无法启动

查看服务日志：
```cmd
type C:\inetpub\wwwroot\video-upload-app\backend\logs\stderr.log
```

### 3. 无法访问网站

检查防火墙：
```cmd
netsh advfirewall show allprofiles
```

检查Nginx配置：
```cmd
cd C:\nginx
nginx -t
```

### 4. 视频上传失败

检查uploads目录权限：
- 右键 `backend\uploads` 文件夹
- 属性 → 安全 → 编辑
- 添加 IIS_IUSRS 用户，给予完全控制权限

---

## 📝 访问地址

部署完成后：

| 用户类型 | 访问地址 |
|---------|---------|
| 普通用户 | http://2mintuevideos.com/ |
| 管理员 | http://2mintuevideos.com/console |

**默认管理员账户**：
- 用户名：`admin`
- 密码：`admin123`

⚠️ **请登录后立即修改密码！**

---

## 🔄 开机自启动

### Flask服务（已配置）
NSSM服务已设置为自动启动（SERVICE_AUTO_START）

### Nginx服务

创建启动脚本 `start_nginx.bat`：
```cmd
@echo off
cd C:\nginx
start nginx
```

将脚本放到 `C:\ProgramData\Microsoft\Windows\Start Menu\Programs\StartUp\`

---

## 📈 性能优化

### 1. 增加Nginx worker进程
修改 `nginx.conf`：
```nginx
worker_processes  4;  # 根据CPU核心数设置
```

### 2. 启用缓存
在 `nginx.conf` 的 http 块中添加：
```nginx
proxy_cache_path C:/nginx/cache levels=1:2 keys_zone=video_cache:10m max_size=1g inactive=60m;

location /api/videos/ {
    proxy_cache video_cache;
    proxy_cache_valid 200 60m;
    # ... 其他配置
}
```

### 3. 限制上传速度
在 `nginx.conf` 中添加：
```nginx
client_max_body_size 5G;
client_body_timeout 300s;
```
