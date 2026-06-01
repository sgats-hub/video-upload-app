<template>
  <div class="video-list-container">
    <div v-if="videos.length === 0" class="empty-state">
      <div class="empty-icon">📭</div>
      <p>暂无视频</p>
    </div>
    
    <div v-else class="video-grid">
      <div v-for="video in videos" :key="video.id" class="video-card">
        <div class="video-thumbnail" @click="playVideo(video.url)">
          <video :src="video.url" controlslist="nodownload" class="video-preview">
            您的浏览器不支持视频播放
          </video>
          <div class="play-overlay">▶️</div>
          <div class="category-badge">{{ video.category_icon }} {{ video.category_name }}</div>
        </div>
        
        <div class="video-info">
          <h4 class="video-title">{{ video.original_name }}</h4>
          <div class="video-meta">
            <span class="meta-item">{{ video.size }}</span>
            <span class="meta-item">{{ video.uploaded_at }}</span>
          </div>
          
          <div class="video-actions">
            <button class="action-btn play-btn" title="播放" @click="playVideo(video.url)">▶️</button>
            <button class="action-btn download-btn" title="下载" @click="downloadVideo(video)">⬇️</button>
            <button v-if="isAdmin" class="action-btn edit-btn" title="编辑" @click="editVideo(video)">✏️</button>
            <button v-if="isAdmin" class="action-btn delete-btn" title="删除" @click="deleteVideo(video.id)">🗑️</button>
          </div>
        </div>
      </div>
    </div>
    
    <!-- 视频播放器模态框 -->
    <div v-if="playingVideo" class="modal-overlay" @click="playingVideo = null">
      <div class="modal-content" @click.stop>
        <button class="close-btn" @click="playingVideo = null">✕</button>
        <video :src="playingVideo" controls class="full-video">
          您的浏览器不支持视频播放
        </video>
      </div>
    </div>
    
    <!-- 编辑视频模态框 -->
    <div v-if="editingVideo" class="modal-overlay" @click="editingVideo = null">
      <div class="edit-modal-content" @click.stop>
        <button class="close-btn" @click="editingVideo = null">✕</button>
        <h3>编辑视频</h3>
        <div class="form-group">
          <label>视频名称</label>
          <input 
            v-model="editForm.name" 
            type="text" 
            class="form-input" 
            placeholder="请输入视频名称"
          >
        </div>
        <div class="form-group">
          <label>分类</label>
          <select v-model="editForm.category_id" class="form-input">
            <option v-for="cat in categories" :key="cat.id" :value="cat.id">
              {{ cat.icon }} {{ cat.name }}
            </option>
          </select>
        </div>
        <div class="form-actions">
          <button class="btn-cancel" @click="editingVideo = null">取消</button>
          <button class="btn-save" @click="saveVideo">保存</button>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref } from 'vue'

const props = defineProps({
  videos: {
    type: Array,
    default: () => []
  },
  isAdmin: {
    type: Boolean,
    default: false
  },
  username: {
    type: String,
    default: ''
  },
  password: {
    type: String,
    default: ''
  },
  categories: {
    type: Array,
    default: () => []
  }
})

const emit = defineEmits(['delete-video', 'video-updated'])

const playingVideo = ref(null)
const editingVideo = ref(null)
const editForm = ref({
  name: '',
  category_id: null
})

const playVideo = (url) => {
  playingVideo.value = url
}

const downloadVideo = (video) => {
  const link = document.createElement('a')
  link.href = video.url
  link.download = video.original_name
  document.body.appendChild(link)
  link.click()
  document.body.removeChild(link)
}

const editVideo = (video) => {
  editingVideo.value = video
  editForm.value = {
    name: video.original_name,
    category_id: video.category_id
  }
}

const saveVideo = async () => {
  if (!editForm.value.name.trim()) {
    alert('视频名称不能为空')
    return
  }
  
  try {
    const response = await fetch(`/api/videos/${editingVideo.value.id}`, {
      method: 'PUT',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        username: props.username,
        password: props.password,
        name: editForm.value.name,
        category_id: editForm.value.category_id
      })
    })
    
    console.log('Response status:', response.status)
    console.log('Response headers:', response.headers)
    
    const result = await response.json()
    console.log('Response result:', result)
    
    if (result.success) {
      emit('video-updated')
      editingVideo.value = null
      alert('修改成功')
    } else {
      alert(result.error || '修改失败')
    }
  } catch (error) {
    console.error('Error:', error)
    alert('修改失败: ' + error.message)
  }
}

const deleteVideo = async (id) => {
  if (!confirm('确定要删除这个视频吗？')) return
  
  try {
    const response = await fetch(`/api/videos/${id}`, {
      method: 'DELETE',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        username: props.username,
        password: props.password
      })
    })
    
    const result = await response.json()
    
    if (result.success) {
      emit('delete-video', id)
      alert('删除成功')
    } else {
      alert(result.error || '删除失败')
    }
  } catch (error) {
    alert('删除失败')
  }
}
</script>

<style scoped>
.video-list-container {
  background: white;
  border-radius: 16px;
  padding: 20px;
  box-shadow: 0 10px 40px rgba(0,0,0,0.1);
}

.empty-state {
  text-align: center;
  padding: 50px;
}

.empty-icon {
  font-size: 4rem;
  margin-bottom: 15px;
}

.empty-state p {
  color: #666;
  font-size: 1rem;
}

.video-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(280px, 1fr));
  gap: 20px;
}

.video-card {
  background: #f8f9fa;
  border-radius: 12px;
  overflow: hidden;
  transition: transform 0.3s ease, box-shadow 0.3s ease;
}

.video-card:hover {
  transform: translateY(-5px);
  box-shadow: 0 15px 35px rgba(0,0,0,0.15);
}

.video-thumbnail {
  position: relative;
  aspect-ratio: 16 / 9;
  overflow: hidden;
  background: #000;
}

.video-preview {
  width: 100%;
  height: 100%;
  object-fit: cover;
}

.category-badge {
  position: absolute;
  top: 10px;
  left: 10px;
  background: rgba(0,0,0,0.7);
  color: white;
  padding: 4px 10px;
  border-radius: 15px;
  font-size: 0.8rem;
}

.play-overlay {
  position: absolute;
  top: 50%;
  left: 50%;
  transform: translate(-50%, -50%);
  width: 60px;
  height: 60px;
  background: rgba(255, 255, 255, 0.9);
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 1.5rem;
  opacity: 0;
  transition: all 0.3s ease;
  cursor: pointer;
  box-shadow: 0 4px 15px rgba(0, 0, 0, 0.3);
}

.video-thumbnail:hover .play-overlay {
  opacity: 1;
}

.video-thumbnail:hover {
  cursor: pointer;
}

.video-info {
  padding: 15px;
}

.video-title {
  margin: 0 0 10px 0;
  font-size: 0.95rem;
  color: #333;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}

.video-meta {
  display: flex;
  gap: 15px;
  margin-bottom: 12px;
}

.meta-item {
  color: #888;
  font-size: 0.8rem;
}

.video-actions {
  display: flex;
  gap: 8px;
}

.action-btn {
  flex: 1;
  padding: 10px;
  border: none;
  border-radius: 8px;
  cursor: pointer;
  font-size: 1rem;
  transition: all 0.3s ease;
}

.play-btn {
  background: #a5b4fc;
  color: #4c1d95;
}

.play-btn:hover {
  background: #8b5cf6;
  color: white;
}

.download-btn {
  background: #86efac;
  color: #1e3a5f;
}

.download-btn:hover {
  background: #22c55e;
  color: white;
}

.edit-btn {
  background: #ffc107;
  color: white;
}

.edit-btn:hover {
  background: #e0a800;
}

.delete-btn {
  background: #ff6b6b;
  color: white;
}

.delete-btn:hover {
  background: #ee5a5a;
}

/* 模态框样式 */
.modal-overlay {
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background: rgba(0,0,0,0.8);
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 1000;
}

.modal-content {
  position: relative;
  max-width: 90%;
  max-height: 90%;
}

.edit-modal-content {
  position: relative;
  background: white;
  padding: 30px;
  border-radius: 16px;
  max-width: 500px;
  width: 90%;
}

.edit-modal-content h3 {
  margin: 0 0 20px 0;
  color: #333;
}

.form-group {
  margin-bottom: 20px;
}

.form-group label {
  display: block;
  margin-bottom: 8px;
  color: #555;
  font-weight: 500;
}

.form-input {
  width: 100%;
  padding: 12px;
  border: 2px solid #e0e0e0;
  border-radius: 8px;
  font-size: 1rem;
  transition: border-color 0.3s ease;
}

.form-input:focus {
  outline: none;
  border-color: #a5b4fc;
}

.form-actions {
  display: flex;
  gap: 10px;
  margin-top: 25px;
}

.btn-cancel, .btn-save {
  flex: 1;
  padding: 12px;
  border: none;
  border-radius: 8px;
  font-size: 1rem;
  cursor: pointer;
  transition: all 0.3s ease;
}

.btn-cancel {
  background: #f5f5f5;
  color: #666;
}

.btn-cancel:hover {
  background: #e0e0e0;
}

.btn-save {
  background: #a5b4fc;
  color: #4c1d95;
}

.btn-save:hover {
  background: #8b5cf6;
  color: white;
}

.close-btn {
  position: absolute;
  top: -40px;
  right: 0;
  background: rgba(255,255,255,0.2);
  border: none;
  color: white;
  font-size: 1.5rem;
  padding: 5px 12px;
  border-radius: 50%;
  cursor: pointer;
}

.full-video {
  width: 100%;
  max-height: 80vh;
  border-radius: 12px;
}
</style>