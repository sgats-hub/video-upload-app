<template>
  <div class="app-container">
    <!-- 普通用户页面（默认） -->
    <div v-if="currentPage === 'viewer'" class="viewer-panel">
      <main class="main-content viewer-content">
        <div class="search-bar">
          <input 
            type="text" 
            v-model="searchKeyword" 
            placeholder="搜索视频..." 
            class="search-input"
            @keyup.enter="handleSearch"
          />
          <button class="search-btn" @click="handleSearch">🔍</button>
        </div>
        
        <div class="category-tabs">
          <button 
            v-for="cat in allCategories" 
            :key="cat.id"
            :class="['category-tab', { active: viewerSelectedCategory === cat.id }]"
            @click="viewerSelectCategory(cat.id)"
          >
            {{ cat.icon }} {{ cat.name }}
          </button>
        </div>
        
        <VideoList 
          :videos="videos" 
          :isAdmin="false"
          @delete-video="() => {}" 
        />
        
        <!-- 分页 -->
        <div v-if="totalPages > 1" class="pagination">
          <button 
            class="page-btn" 
            :disabled="currentPageNum <= 1" 
            @click="goToPage(currentPageNum - 1)"
          >
            ←
          </button>
          <span class="page-info">第 {{ currentPageNum }} / {{ totalPages }} 页 (共 {{ totalVideos }} 个视频)</span>
          <button 
            class="page-btn" 
            :disabled="currentPageNum >= totalPages" 
            @click="goToPage(currentPageNum + 1)"
          >
            →
          </button>
        </div>
        
        <!-- 联系方式和企业文化按钮 -->
        <div class="contact-footer">
          <button class="contact-btn" @click="showContactModal = true">📞 联系我们</button>
          <button class="culture-btn" @click="showCultureModal = true">📖 企业文化</button>
          <button class="message-btn" @click="openMessageBoard">💬 留言板</button>
        </div>
        
        <!-- 公司信息 -->
        <div class="company-footer">
          <p>临猗县两分钟文化</p>
        </div>
      </main>
    </div>

    <!-- 管理员页面 -->
    <div v-else-if="currentPage === 'admin'">
      <div v-if="!adminUser" class="admin-login-container">
        <div class="login-box">
          <h1>🔐 管理员登录</h1>
          <input type="text" v-model="adminUsername" placeholder="用户名" class="form-input" />
          <input type="password" v-model="adminPassword" placeholder="密码" class="form-input" />
          <button class="login-btn" @click="adminLogin">登录</button>
          <p v-if="loginError" class="error-message">{{ loginError }}</p>
          <a href="/" class="back-link">← 返回观看页面</a>
        </div>
      </div>
      
      <div v-else class="admin-panel">
        <header class="header">
          <div class="header-left">
            <h1>📹 两分钟文化</h1>
            <p>管理员面板</p>
          </div>
          <div class="header-right">
            <span class="user-info">👤 {{ adminUser.username }} (管理员)</span>
            <button class="change-pwd-btn" @click="showChangePwd = true">修改密码</button>
            <button class="logout-btn" @click="adminLogout">退出</button>
          </div>
        </header>
        
        <main class="main-content admin-content">
          <div class="upload-section">
            <VideoUpload 
              :categories="categories"
              @upload-success="handleUploadSuccess" 
            />
          </div>
          
          <div class="video-section">
            <div class="search-bar">
              <input 
                type="text" 
                v-model="searchKeyword" 
                placeholder="搜索视频..." 
                class="search-input"
                @keyup.enter="handleSearch"
              />
              <button class="search-btn" @click="handleSearch">🔍</button>
            </div>
            
            <div class="category-tabs">
              <button 
                v-for="cat in allCategories" 
                :key="cat.id"
                :class="['category-tab', { active: selectedCategory === cat.id }]"
                @click="selectCategory(cat.id)"
              >
                {{ cat.icon }} {{ cat.name }}
              </button>
            </div>
            <VideoList 
              :videos="videos" 
              :isAdmin="true"
              :categories="categories"
              @delete-video="handleDeleteVideo"
              @video-updated="handleVideoUpdate"
            />
            
            <!-- 分页 -->
            <div v-if="totalPages > 1" class="pagination">
              <button 
                class="page-btn" 
                :disabled="currentPageNum <= 1" 
                @click="goToPage(currentPageNum - 1)"
              >
                ←
              </button>
              <span class="page-info">第 {{ currentPageNum }} / {{ totalPages }} 页 (共 {{ totalVideos }} 个视频)</span>
              <button 
                class="page-btn" 
                :disabled="currentPageNum >= totalPages" 
                @click="goToPage(currentPageNum + 1)"
              >
                →
              </button>
            </div>
            
            <!-- 联系方式和企业文化按钮 -->
            <div class="contact-footer">
              <button class="contact-btn" @click="showContactModal = true">📞 联系我们</button>
              <button class="culture-btn" @click="showCultureModal = true">📖 企业文化</button>
              <button class="message-btn" @click="openMessageBoard">💬 留言板</button>
            </div>
            
            <!-- 公司信息 -->
            <div class="company-footer">
              <p>临猗县两分钟文化</p>
            </div>
          </div>
        </main>
        
        <!-- 密码修改弹窗 -->
        <div v-if="showChangePwd" class="modal-overlay" @click="closeChangePwd">
          <div class="modal-content" @click.stop>
            <button class="close-btn" @click="closeChangePwd">✕</button>
            <h3>🔐 修改密码</h3>
            <div class="form-group">
              <label>旧密码:</label>
              <input type="password" v-model="oldPassword" class="form-input" placeholder="请输入旧密码" />
            </div>
            <div class="form-group">
              <label>新密码:</label>
              <input type="password" v-model="newPassword" class="form-input" placeholder="新密码至少6位" />
            </div>
            <div class="form-group">
              <label>确认密码:</label>
              <input type="password" v-model="confirmPassword" class="form-input" placeholder="再次输入新密码" />
            </div>
            <p v-if="pwdError" class="error-message">{{ pwdError }}</p>
            <p v-if="pwdSuccess" class="success-message">{{ pwdSuccess }}</p>
            <div class="modal-actions">
              <button class="btn btn-cancel" @click="closeChangePwd">取消</button>
              <button class="btn btn-primary" @click="changePassword">确认修改</button>
            </div>
          </div>
        </div>
        
      </div>
    </div>
    
    <!-- 联系方式弹窗（全局） -->
    <div v-if="showContactModal" class="modal-overlay" @click="showContactModal = false">
      <div class="contact-modal-content" @click.stop>
        <button class="close-btn" @click="showContactModal = false">✕</button>
        <h3>📞 联系我们</h3>
        <div class="contact-info">
          <div class="contact-item">
            <span class="contact-icon">📧</span>
            <div class="contact-details">
              <div class="contact-label">联系邮箱</div>
              <div class="contact-value">yanyu1129@gmail.com</div>
            </div>
          </div>
          <div class="contact-item">
            <span class="contact-icon">📺</span>
            <div class="contact-details">
              <div class="contact-label">YouTube</div>
              <a href="https://www.youtube.com/@griggle520" target="_blank" class="contact-value link">youtube访问</a>
            </div>
          </div>
          <div class="contact-item">
            <span class="contact-icon">🎵</span>
            <div class="contact-details">
              <div class="contact-label">抖音</div>
              <div class="contact-value">73259624731</div>
            </div>
          </div>
        </div>
      </div>
    </div>
    
    <!-- 企业文化弹窗 -->
    <div v-if="showCultureModal" class="modal-overlay" @click="showCultureModal = false">
      <div class="culture-modal-container" @click.stop>
        <button class="close-btn" @click="showCultureModal = false">✕</button>
        <div class="culture-modal-content">
          <h3>🎬 两分钟文化工坊 · 企业文化</h3>
          
          <div class="culture-section">
          <h4>💡 核心理念</h4>
          <p>我们用两分钟，记录文化的温度；用视频，守护日常中的智慧与纯真</p>
        </div>
        
        <div class="culture-section">
          <h4>🧭 核心价值观</h4>
          <div class="value-item">
            <span class="value-num">1️⃣</span>
            <div class="value-content">
              <strong>匠心精神</strong>
              <p>每一帧画面，皆精雕细琢</p>
              <p>我们拒绝流水线作品，相信每一个视频都承载使命与意义</p>
            </div>
          </div>
          <div class="value-item">
            <span class="value-num">2️⃣</span>
            <div class="value-content">
              <strong>自然与生命的尊重</strong>
              <p>拥抱自然，敬畏生命</p>
              <p>我们相信，唯有理解生命的本质，内容才有灵魂</p>
              <p>不追逐短期利益，坚持人与文化的和谐共生</p>
            </div>
          </div>
          <div class="value-item">
            <span class="value-num">3️⃣</span>
            <div class="value-content">
              <strong>守住初心，抵抗商业化压力</strong>
              <p>我们不为流量妥协、不为迎合市场</p>
              <p>坚信内容的价值胜过算法的投喂</p>
            </div>
          </div>
        </div>
        
        <div class="culture-section">
          <h4>✏️ 创作态度</h4>
          <p>没有完不成的作品，只有尚未解决的问题</p>
          <p>沟通无门槛，创意无等级，我们追求"互通有无"的团队氛围</p>
          <p>我们不赶时间，但我们从不半途而废。</p>
        </div>
        
        <div class="culture-section">
          <h4>👨‍🎨 创始人精神：铃铛妙药</h4>
          <p>每个视频，都值得被反复观看</p>
          <p>我不相信天才，只有愿意用心的人</p>
          <p>鼓励天马行空的想象，但更重脚踏实地的表达</p>
        </div>
        
        <div class="culture-section">
          <h4>🧒 面向未来</h4>
          <p>我们做视频，不只是为了传播知识，更是为了让每一颗心灵，感受到被理解、被尊重、被点亮。</p>
          <p>真正的平等，始于内容的共鸣。</p>
        </div>
        
        <div class="culture-section join-us">
          <p><strong>我们期待您的加入</strong></p>
        </div>
        </div>
      </div>
    </div>
    
    <!-- 留言板弹窗 -->
    <div v-if="showMessageBoard" class="modal-overlay" @click="showMessageBoard = false">
      <div class="message-modal-content" @click.stop>
        <button class="close-btn" @click="showMessageBoard = false">✕</button>
        <h3>💬 留言板</h3>
        
        <div class="message-input-section">
          <textarea 
            v-model="newMessage" 
            class="message-input" 
            placeholder="请输入您的留言..."
            rows="3"
          ></textarea>
          <button class="message-submit-btn" @click="submitMessage">提交留言</button>
        </div>
        
        <div class="message-list">
          <div v-if="messages.length === 0" class="no-messages">
            暂无留言，快来发表第一条留言吧！
          </div>
          <div v-else v-for="(msg, index) in messages" :key="index" class="message-item">
            <div class="message-time">{{ msg.time }}</div>
            <div class="message-content">{{ maskNumbers(msg.content) }}</div>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import VideoUpload from './components/VideoUpload.vue'
import VideoList from './components/VideoList.vue'

// 页面状态
const currentPage = ref('viewer')
const adminUser = ref(null)
const adminUsername = ref('')
const adminPassword = ref('')
const loginError = ref('')
const videos = ref([])
const categories = ref([])
const selectedCategory = ref(null)
const viewerSelectedCategory = ref(null)

// 搜索和分页
const searchKeyword = ref('')
const currentPageNum = ref(1)
const perPage = ref(10)
const totalPages = ref(1)
const totalVideos = ref(0)

// 密码修改
const showChangePwd = ref(false)
const oldPassword = ref('')
const newPassword = ref('')
const confirmPassword = ref('')
const pwdError = ref('')
const pwdSuccess = ref('')
const showContactModal = ref(false)
const showCultureModal = ref(false)

// 留言板
const showMessageBoard = ref(false)
const newMessage = ref('')
const messages = ref([])
const messageError = ref('')

// 所有分类（包含"全部"）
const allCategories = computed(() => {
  return [{ id: null, name: '全部', icon: '📺' }, ...categories.value]
})

// 管理员过滤后的视频
const filteredVideos = computed(() => {
  if (!selectedCategory.value) return videos.value
  return videos.value.filter(v => v.category_id === selectedCategory.value)
})

// 普通用户过滤后的视频
const viewerFilteredVideos = computed(() => {
  if (!viewerSelectedCategory.value) return videos.value
  return videos.value.filter(v => v.category_id === viewerSelectedCategory.value)
})

// 登录
const adminLogin = async () => {
  try {
    const response = await fetch('/api/login', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      credentials: 'include',
      body: JSON.stringify({
        username: adminUsername.value,
        password: adminPassword.value,
        role: 'admin'
      })
    })
    const result = await response.json()
    if (result.success) {
      adminUser.value = result.user
      loginError.value = ''
      loadVideos()
      loadCategories()
    } else {
      loginError.value = result.error
    }
  } catch (error) {
    loginError.value = '登录失败'
  }
}

// 退出
const adminLogout = async () => {
  try {
    await fetch('/api/logout', {
      method: 'POST',
      credentials: 'include'
    })
  } catch (e) {
    // ignore
  }
  adminUser.value = null
  adminUsername.value = ''
  adminPassword.value = ''
  selectedCategory.value = null
}

// 修改密码
const changePassword = async () => {
  pwdError.value = ''
  pwdSuccess.value = ''
  
  if (!oldPassword.value) {
    pwdError.value = '请输入旧密码'
    return
  }
  
  if (!newPassword.value || newPassword.value.length < 6) {
    pwdError.value = '新密码至少需要6位'
    return
  }
  
  if (newPassword.value !== confirmPassword.value) {
    pwdError.value = '两次输入的密码不一致'
    return
  }
  
  try {
    const response = await fetch('/api/change-password', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      credentials: 'include',
      body: JSON.stringify({
        old_password: oldPassword.value,
        new_password: newPassword.value
      })
    })
    
    const result = await response.json()
    
    if (result.success) {
      pwdSuccess.value = result.message
      adminPassword.value = newPassword.value
      setTimeout(() => {
        showChangePwd.value = false
        oldPassword.value = ''
        newPassword.value = ''
        confirmPassword.value = ''
        pwdSuccess.value = ''
      }, 2000)
    } else {
      pwdError.value = result.error
    }
  } catch (error) {
    pwdError.value = '修改失败'
  }
}

// 关闭密码修改弹窗
const closeChangePwd = () => {
  showChangePwd.value = false
  oldPassword.value = ''
  newPassword.value = ''
  confirmPassword.value = ''
  pwdError.value = ''
  pwdSuccess.value = ''
}

// 留言板功能
const openMessageBoard = async () => {
  showMessageBoard.value = true
  await loadMessages()
}

const loadMessages = async () => {
  try {
    const response = await fetch('/api/messages', { credentials: 'include' })
    messages.value = await response.json()
  } catch (error) {
    console.error('加载留言失败:', error)
    messages.value = []
  }
}

const submitMessage = async () => {
  if (!newMessage.value.trim()) {
    messageError.value = '请输入留言内容'
    return
  }

  try {
    const response = await fetch('/api/messages', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      credentials: 'include',
      body: JSON.stringify({ content: newMessage.value })
    })
    
    const result = await response.json()
    
    if (result.success) {
      newMessage.value = ''
      messageError.value = ''
      await loadMessages()
    } else {
      messageError.value = result.message
    }
  } catch (error) {
    messageError.value = '提交留言失败，请稍后重试'
    console.error('提交留言失败:', error)
  }
}

// 数字脱敏函数
const maskNumbers = (text) => {
  if (!text) return ''
  return text.replace(/\d{4,}/g, (match) => {
    if (match.length <= 4) return '^_^'
    const start = match.slice(0, 2)
    const end = match.slice(-2)
    return `${start}^_^${end}`
  })
}

// 加载数据
const loadVideos = async (page = 1, keyword = '', category_id = null) => {
  try {
    const params = new URLSearchParams()
    params.set('page', page)
    params.set('per_page', perPage.value)
    if (keyword) params.set('search', keyword)
    if (category_id) params.set('category_id', category_id)
    
    const response = await fetch(`/api/videos?${params.toString()}`, { credentials: 'include' })
    const result = await response.json()
    
    videos.value = result.items || result
    totalPages.value = result.pages || 1
    totalVideos.value = result.total || videos.value.length
    currentPageNum.value = result.page || page
  } catch (error) {
    videos.value = []
  }
}

const loadCategories = async () => {
  try {
    const response = await fetch('/api/categories', { credentials: 'include' })
    categories.value = await response.json()
  } catch (error) {
    categories.value = []
  }
}

// 选择分类（管理员）
const selectCategory = (id) => {
  selectedCategory.value = id
  currentPageNum.value = 1
  loadVideos(1, searchKeyword.value, id)
}

// 搜索
const handleSearch = () => {
  currentPageNum.value = 1
  loadVideos(1, searchKeyword.value, selectedCategory.value)
}

// 分页
const goToPage = (page) => {
  if (page < 1 || page > totalPages.value) return
  loadVideos(page, searchKeyword.value, selectedCategory.value)
}

// 普通用户选择分类
const viewerSelectCategory = (id) => {
  viewerSelectedCategory.value = id
  currentPageNum.value = 1
  loadVideos(1, '', id)
}

// 上传成功
const handleUploadSuccess = (video) => {
  videos.value.unshift(video)
}

// 删除视频
const handleDeleteVideo = async (id) => {
  try {
    await fetch(`/api/videos/${id}`, {
      method: 'DELETE',
      headers: { 'Content-Type': 'application/json' },
      credentials: 'include'
    })
    videos.value = videos.value.filter(v => v.id !== id)
  } catch (error) {
    alert('删除失败')
  }
}

// 更新视频
const handleVideoUpdate = () => {
  loadVideos(currentPageNum.value, searchKeyword.value, selectedCategory.value)
}

onMounted(async () => {
  const path = window.location.pathname
  if (path === '/console' || path === '/console/') {
    currentPage.value = 'admin'
  } else {
    currentPage.value = 'viewer'
    await fetch('/api/login', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      credentials: 'include',
      body: JSON.stringify({ role: 'viewer' })
    }).catch(() => {})
  }

  loadVideos()
  loadCategories()
})
</script>

<style scoped>
/* 管理员登录 */
.admin-login-container {
  min-height: 100vh;
  display: flex;
  align-items: center;
  justify-content: center;
  background: linear-gradient(135deg, #e0e7ff 0%, #f3e8ff 100%);
}

.login-box {
  background: white;
  padding: 40px;
  border-radius: 20px;
  width: 100%;
  max-width: 350px;
  text-align: center;
}

.login-box h1 {
  font-size: 1.6rem;
  margin-bottom: 25px;
  color: #333;
}

.form-input {
  width: 100%;
  padding: 12px;
  margin-bottom: 15px;
  border: 1px solid #ddd;
  border-radius: 10px;
  font-size: 1rem;
  box-sizing: border-box;
}

.form-input:focus {
  outline: none;
  border-color: #a5b4fc;
}

.login-btn {
  width: 100%;
  padding: 12px;
  background: linear-gradient(135deg, #a5b4fc, #c4b5fd);
  color: #4c1d95;
  border: none;
  border-radius: 10px;
  font-size: 1rem;
  cursor: pointer;
}

.login-btn:hover {
  transform: translateY(-2px);
}

.error-message {
  color: #ff6b6b;
  margin-top: 10px;
}

.demo-info {
  margin-top: 20px;
  padding-top: 20px;
  border-top: 1px solid #eee;
  color: #666;
  font-size: 0.9rem;
}

.back-link {
  display: block;
  margin-top: 15px;
  color: #8b5cf6;
  text-decoration: none;
  font-size: 0.9rem;
}

.back-link:hover {
  text-decoration: underline;
}

/* 主面板样式 */
.app-container {
  min-height: 100vh;
}

.header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  color: white;
  padding: 20px;
  flex-wrap: wrap;
  gap: 15px;
}

.admin-panel .header {
  background: linear-gradient(135deg, #a5b4fc, #c4b5fd);
}

.viewer-header {
  background: linear-gradient(135deg, #86efac, #93c5fd);
}

.header-left h1 {
  font-size: 1.8rem;
  margin-bottom: 5px;
}

.header-left p {
  opacity: 0.9;
  font-size: 0.95rem;
}

.header-right {
  display: flex;
  align-items: center;
  gap: 15px;
}

.user-info {
  background: rgba(255,255,255,0.2);
  padding: 8px 15px;
  border-radius: 20px;
  font-size: 0.9rem;
}

.admin-link {
  font-size: 1.5rem;
  color: white;
  text-decoration: none;
  opacity: 0.8;
  transition: all 0.3s ease;
}

.admin-link:hover {
  opacity: 1;
  transform: scale(1.1);
}

.change-pwd-btn {
  padding: 8px 20px;
  background: rgba(255,255,255,0.2);
  border: 1px solid rgba(255,255,255,0.3);
  color: white;
  border-radius: 20px;
  cursor: pointer;
}

.change-pwd-btn:hover {
  background: rgba(255,255,255,0.3);
}

/* 弹窗样式 */
.modal-overlay {
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background: rgba(0,0,0,0.6);
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 1000;
}

.modal-content {
  background: white;
  padding: 30px;
  border-radius: 16px;
  width: 100%;
  max-width: 400px;
  position: relative;
}

.modal-content .close-btn {
  position: absolute;
  top: 15px;
  right: 15px;
  background: none;
  border: none;
  font-size: 1.2rem;
  cursor: pointer;
  color: #999;
}

.modal-content h3 {
  margin-top: 0;
  color: #333;
}

.form-group {
  margin-bottom: 15px;
}

.form-group label {
  display: block;
  margin-bottom: 5px;
  color: #666;
}

.modal-content .form-input {
  width: 100%;
  padding: 10px;
  border: 1px solid #ddd;
  border-radius: 8px;
  font-size: 1rem;
  box-sizing: border-box;
}

.modal-content .form-input:focus {
  outline: none;
  border-color: #a5b4fc;
}

.modal-content .error-message {
  color: #ff6b6b;
  margin-bottom: 10px;
}

.modal-content .success-message {
  color: #22c55e;
  margin-bottom: 10px;
}

.modal-actions {
  display: flex;
  gap: 10px;
  justify-content: flex-end;
}

.modal-actions .btn {
  padding: 10px 20px;
  border: none;
  border-radius: 8px;
  cursor: pointer;
  font-size: 0.95rem;
}

.modal-actions .btn-cancel {
  background: #eee;
  color: #666;
}

.modal-actions .btn-primary {
  background: linear-gradient(135deg, #a5b4fc, #c4b5fd);
  color: #4c1d95;
}

.main-content {
  padding: 20px;
  max-width: 1200px;
  margin: 0 auto;
}

.admin-content {
  display: grid;
  gap: 20px;
}

@media (min-width: 768px) {
  .admin-content {
    grid-template-columns: 1fr 2fr;
  }
}

.viewer-content {
  max-width: 1000px;
  padding-top: 20px;
}

/* 搜索框 */
.search-bar {
  display: flex;
  gap: 10px;
  margin-bottom: 20px;
}

.search-input {
  flex: 1;
  padding: 12px 15px;
  border: 1px solid #ddd;
  border-radius: 25px;
  font-size: 1rem;
  background: white;
}

.search-input:focus {
  outline: none;
  border-color: #a5b4fc;
}

.search-btn {
  padding: 12px 20px;
  background: linear-gradient(135deg, #a5b4fc, #c4b5fd);
  color: #4c1d95;
  border: none;
  border-radius: 25px;
  font-size: 1rem;
  cursor: pointer;
}

.search-btn:hover {
  transform: translateY(-2px);
}

.category-tabs {
  display: flex;
  gap: 10px;
  margin-bottom: 20px;
  flex-wrap: wrap;
}

.category-tab {
  padding: 10px 20px;
  border: 2px solid #ddd;
  border-radius: 25px;
  background: white;
  cursor: pointer;
  transition: all 0.3s ease;
  font-size: 0.95rem;
}

.category-tab.active {
  border-color: #a5b4fc;
  background: #a5b4fc;
  color: #4c1d95;
}

.category-tab:hover {
  border-color: #a5b4fc;
}

/* 分页 */
.pagination {
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 20px;
  margin-top: 30px;
  padding-top: 20px;
  border-top: 1px solid #eee;
}

.page-btn {
  padding: 10px 18px;
  background: white;
  border: 1px solid #ddd;
  border-radius: 8px;
  font-size: 1.1rem;
  cursor: pointer;
}

.page-btn:hover:not(:disabled) {
  background: #f5f5f5;
}

.page-btn:disabled {
  opacity: 0.5;
  cursor: not-allowed;
}

.page-info {
  color: #666;
  font-size: 0.9rem;
}

.upload-section {
  position: sticky;
  top: 20px;
}

.video-section {
  display: flex;
  flex-direction: column;
}

/* 联系方式按钮 */
.contact-footer {
  display: flex;
  justify-content: center;
  padding: 20px 0;
  margin-top: 20px;
  border-top: 1px solid #eee;
}

.company-footer {
  text-align: center;
  padding: 15px 0;
  margin-top: 10px;
  border-top: 1px solid #eee;
}

.company-footer p {
  margin: 0;
  color: #666;
  font-size: 0.9rem;
  font-weight: 500;
}

.contact-btn {
  padding: 12px 30px;
  background: linear-gradient(135deg, #a5b4fc, #c4b5fd);
  color: #4c1d95;
  border: none;
  border-radius: 25px;
  font-size: 1rem;
  cursor: pointer;
  transition: all 0.3s ease;
  box-shadow: 0 4px 15px rgba(165, 180, 252, 0.3);
}

.contact-btn:hover {
  transform: translateY(-2px);
  box-shadow: 0 6px 20px rgba(165, 180, 252, 0.4);
}

/* 联系方式模态框 */
.contact-modal-content {
  background: white;
  padding: 40px;
  border-radius: 20px;
  width: 100%;
  max-width: 450px;
  position: relative;
  box-shadow: 0 20px 60px rgba(0, 0, 0, 0.3);
}

.contact-modal-content .close-btn {
  position: absolute;
  top: 15px;
  right: 15px;
  width: 36px;
  height: 36px;
  background: linear-gradient(135deg, #f3f4f6, #e5e7eb);
  border: none;
  border-radius: 50%;
  font-size: 1.2rem;
  cursor: pointer;
  color: #6b7280;
  display: flex;
  align-items: center;
  justify-content: center;
  transition: all 0.3s ease;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
}

.contact-modal-content .close-btn:hover {
  background: linear-gradient(135deg, #fee2e2, #fecaca);
  color: #dc2626;
  transform: scale(1.1);
}

.contact-modal-content h3 {
  margin: 0 0 30px 0;
  color: #333;
  font-size: 1.5rem;
  text-align: center;
}

.contact-info {
  display: flex;
  flex-direction: column;
  gap: 20px;
}

.contact-item {
  display: flex;
  align-items: center;
  gap: 15px;
  padding: 20px;
  background: linear-gradient(135deg, #f8f9fa, #e9ecef);
  border-radius: 12px;
  transition: all 0.3s ease;
}

.contact-item:hover {
  transform: translateX(5px);
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.1);
}

.contact-icon {
  font-size: 2rem;
  width: 50px;
  height: 50px;
  display: flex;
  align-items: center;
  justify-content: center;
  background: white;
  border-radius: 50%;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
}

.contact-details {
  flex: 1;
}

.contact-label {
  font-size: 0.85rem;
  color: #666;
  margin-bottom: 5px;
  font-weight: 500;
}

.contact-value {
  font-size: 1.1rem;
  color: #333;
  font-weight: 600;
  word-break: break-all;
}

.contact-value.link {
  color: #667eea;
  text-decoration: underline;
}

.contact-value.link:hover {
  color: #8b5cf6;
}

/* 企业文化按钮 */
.culture-btn {
  padding: 12px 30px;
  background: linear-gradient(135deg, #86efac, #93c5fd);
  color: #1e3a5f;
  border: none;
  border-radius: 25px;
  font-size: 1rem;
  cursor: pointer;
  transition: all 0.3s ease;
  box-shadow: 0 4px 15px rgba(134, 239, 172, 0.3);
  margin-left: 10px;
}

.culture-btn:hover {
  transform: translateY(-2px);
  box-shadow: 0 6px 20px rgba(134, 239, 172, 0.4);
}

/* 企业文化模态框 */
.culture-modal-container {
  background: white;
  border-radius: 20px;
  width: 100%;
  max-width: 600px;
  max-height: 85vh;
  position: relative;
  box-shadow: 0 20px 60px rgba(0, 0, 0, 0.3);
}

.culture-modal-container .close-btn {
  position: absolute;
  top: 15px;
  right: 15px;
  width: 36px;
  height: 36px;
  background: linear-gradient(135deg, #f3f4f6, #e5e7eb);
  border: none;
  border-radius: 50%;
  font-size: 1.2rem;
  cursor: pointer;
  color: #6b7280;
  display: flex;
  align-items: center;
  justify-content: center;
  transition: all 0.3s ease;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
  z-index: 10;
}

.culture-modal-content {
  padding: 40px;
  max-height: 85vh;
  overflow-y: auto;
}

.culture-modal-container .close-btn:hover {
  background: linear-gradient(135deg, #fee2e2, #fecaca);
  color: #dc2626;
  transform: scale(1.1);
}

.culture-modal-content h3 {
  margin: 0 0 30px 0;
  color: #333;
  font-size: 1.5rem;
  text-align: center;
}

.culture-section {
  margin-bottom: 25px;
  padding-bottom: 20px;
  border-bottom: 1px solid #e5e7eb;
}

.culture-section:last-child {
  border-bottom: none;
  margin-bottom: 0;
  padding-bottom: 0;
}

.culture-section h4 {
  margin: 0 0 12px 0;
  color: #4c1d95;
  font-size: 1.1rem;
}

.culture-section p {
  margin: 8px 0;
  color: #555;
  line-height: 1.7;
  font-size: 0.95rem;
}

.value-item {
  display: flex;
  gap: 15px;
  margin-bottom: 20px;
}

.value-item:last-child {
  margin-bottom: 0;
}

.value-num {
  font-size: 1.5rem;
  flex-shrink: 0;
}

.value-content strong {
  display: block;
  color: #333;
  margin-bottom: 8px;
  font-size: 1rem;
}

.value-content p {
  margin: 6px 0;
  color: #666;
  font-size: 0.9rem;
}

.culture-section.join-us {
  text-align: center;
  padding: 20px;
  background: linear-gradient(135deg, #fef3c7, #fde68a);
  border-radius: 12px;
  border: none;
  margin-top: 10px;
}

.culture-section.join-us p strong {
  font-size: 1.3rem;
  color: #b45309;
  margin: 0;
}

/* 留言板样式 */
.message-btn {
  padding: 12px 30px;
  background: linear-gradient(135deg, #fde68a, #fbbf24);
  color: #92400e;
  border: none;
  border-radius: 25px;
  font-size: 1rem;
  cursor: pointer;
  transition: all 0.3s ease;
  box-shadow: 0 4px 15px rgba(251, 191, 36, 0.3);
  margin-left: 10px;
}

.message-btn:hover {
  transform: translateY(-2px);
  box-shadow: 0 6px 20px rgba(251, 191, 36, 0.4);
}

.message-modal-content {
  background: white;
  padding: 40px;
  border-radius: 20px;
  width: 100%;
  max-width: 600px;
  max-height: 85vh;
  overflow-y: auto;
  position: relative;
  box-shadow: 0 20px 60px rgba(0, 0, 0, 0.3);
}

.message-modal-content .close-btn {
  position: absolute;
  top: 15px;
  right: 15px;
  width: 36px;
  height: 36px;
  background: linear-gradient(135deg, #f3f4f6, #e5e7eb);
  border: none;
  border-radius: 50%;
  font-size: 1.2rem;
  cursor: pointer;
  color: #6b7280;
  display: flex;
  align-items: center;
  justify-content: center;
  transition: all 0.3s ease;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
  z-index: 10;
}

.message-modal-content .close-btn:hover {
  background: linear-gradient(135deg, #fee2e2, #fecaca);
  color: #dc2626;
  transform: scale(1.1);
}

.message-modal-content h3 {
  margin: 0 0 25px 0;
  color: #333;
  font-size: 1.5rem;
  text-align: center;
}

.message-input-section {
  margin-bottom: 25px;
}

.message-input {
  width: 100%;
  padding: 15px;
  border: 2px solid #e5e7eb;
  border-radius: 12px;
  font-size: 1rem;
  resize: vertical;
  font-family: inherit;
  transition: border-color 0.3s ease;
}

.message-input:focus {
  outline: none;
  border-color: #a5b4fc;
}

.message-submit-btn {
  margin-top: 15px;
  padding: 12px 30px;
  background: linear-gradient(135deg, #86efac, #93c5fd);
  color: #1e3a5f;
  border: none;
  border-radius: 25px;
  font-size: 1rem;
  cursor: pointer;
  transition: all 0.3s ease;
  box-shadow: 0 4px 15px rgba(134, 239, 172, 0.3);
}

.message-submit-btn:hover {
  transform: translateY(-2px);
  box-shadow: 0 6px 20px rgba(134, 239, 172, 0.4);
}

.message-error {
  color: #dc2626;
  margin-top: 10px;
  font-size: 0.9rem;
}

.message-list {
  max-height: 400px;
  overflow-y: auto;
}

.no-messages {
  text-align: center;
  padding: 40px 20px;
  color: #666;
  font-size: 1rem;
}

.message-item {
  padding: 15px;
  background: #f9fafb;
  border-radius: 12px;
  margin-bottom: 12px;
  border-left: 4px solid #a5b4fc;
}

.message-time {
  font-size: 0.85rem;
  color: #6b7280;
  margin-bottom: 8px;
}

.message-content {
  color: #333;
  line-height: 1.6;
  font-size: 0.95rem;
  word-break: break-all;
}

/* 移动端适配 */
@media (max-width: 768px) {
  .culture-btn {
    margin-left: 0;
    margin-top: 10px;
    width: 100%;
  }
  
  .culture-modal-content {
    padding: 25px;
    margin: 15px;
  }
}
</style>
