<template>
  <div class="upload-container">
    <h3>📤 上传视频</h3>
    
    <div class="category-select">
      <label>选择分类:</label>
      <select v-model="selectedCategory" class="category-input">
        <option v-for="cat in categories" :key="cat.id" :value="cat.id">
          {{ cat.icon }} {{ cat.name }}
        </option>
      </select>
    </div>
    
    <div class="upload-box" :class="{ dragging: isDragging, uploading: isUploading }">
      <div v-if="!isUploading" class="upload-area" @click="triggerUpload" @dragover.prevent="isDragging = true" @dragleave="isDragging = false" @drop.prevent="handleDrop">
        <div class="upload-icon">📤</div>
        <h3>点击或拖拽视频文件到此处</h3>
        <p>支持 MP4, WebM, AVI, MOV 等格式</p>
        <p class="hint">最大文件大小: 500MB</p>
        <input type="file" ref="fileInput" accept="video/*" class="file-input" @change="handleFileSelect" />
      </div>
      
      <div v-else class="upload-progress">
        <div class="progress-header">
          <span class="file-name">{{ currentFile?.name }}</span>
          <span class="progress-percent">{{ uploadProgress }}%</span>
        </div>
        <div class="progress-bar">
          <div class="progress-fill" :style="{ width: uploadProgress + '%' }"></div>
        </div>
        <p class="progress-status">{{ uploadStatus }}</p>
      </div>
    </div>
    
    <div v-if="uploadedVideo" class="upload-success">
      <div class="success-icon">✓</div>
      <h4>上传成功!</h4>
      <p>{{ uploadedVideo.original_name }}</p>
      <p class="category-tag">{{ getCategoryName(uploadedVideo.category_id) }}</p>
      <button class="btn btn-primary" @click="resetUpload">继续上传</button>
    </div>
  </div>
</template>

<script setup>
import { ref } from 'vue'

const props = defineProps({
  username: {
    type: String,
    required: true
  },
  password: {
    type: String,
    required: true
  },
  categories: {
    type: Array,
    default: () => []
  }
})

const emit = defineEmits(['upload-success'])

const fileInput = ref(null)
const isDragging = ref(false)
const isUploading = ref(false)
const currentFile = ref(null)
const uploadProgress = ref(0)
const uploadStatus = ref('')
const uploadedVideo = ref(null)
const selectedCategory = ref(props.categories[0]?.id || 1)

const getCategoryName = (categoryId) => {
  const cat = props.categories.find(c => c.id === categoryId)
  return cat ? `${cat.icon} ${cat.name}` : '未分类'
}

const triggerUpload = () => {
  fileInput.value?.click()
}

const handleFileSelect = (event) => {
  const file = event.target.files?.[0]
  if (file) {
    processFile(file)
  }
}

const handleDrop = (event) => {
  isDragging.value = false
  const file = event.dataTransfer?.files?.[0]
  if (file && file.type.startsWith('video/')) {
    processFile(file)
  }
}

const processFile = async (file) => {
  if (file.size > 500 * 1024 * 1024) {
    alert('文件大小超过限制（最大500MB）')
    return
  }
  
  currentFile.value = file
  isUploading.value = true
  uploadProgress.value = 0
  uploadStatus.value = '正在上传...'
  
  await uploadToServer(file)
}

const uploadToServer = async (file) => {
  const formData = new FormData()
  formData.append('file', file)
  formData.append('username', props.username)
  formData.append('password', props.password)
  formData.append('category_id', selectedCategory.value)
  
  try {
    console.log('开始上传，目标地址:', '/api/upload')
    console.log('表单数据:', {
      username: props.username,
      password: props.password ? '***' : '',
      category_id: selectedCategory.value,
      filename: file.name,
      size: file.size
    })
    
    const response = await fetch('/api/upload', {
      method: 'POST',
      body: formData
    })
    
    console.log('响应状态:', response.status, response.statusText)
    
    const text = await response.text()
    console.log('响应内容:', text)
    
    let result
    try {
      result = JSON.parse(text)
    } catch (e) {
      throw new Error('服务器返回的不是有效的JSON: ' + text.substring(0, 100))
    }
    
    if (result.success) {
      uploadProgress.value = 100
      uploadStatus.value = '上传完成'
      
      setTimeout(() => {
        uploadedVideo.value = result.video
        isUploading.value = false
        emit('upload-success', result.video)
      }, 500)
    } else {
      throw new Error(result.error || '上传失败')
    }
  } catch (error) {
    console.error('上传失败:', error)
    uploadStatus.value = `上传失败: ${error.message}`
    isUploading.value = false
    alert(`上传失败: ${error.message}`)
  }
}

const resetUpload = () => {
  uploadedVideo.value = null
  currentFile.value = null
  uploadProgress.value = 0
}
</script>

<style scoped>
.upload-container {
  background: white;
  border-radius: 16px;
  padding: 20px;
  box-shadow: 0 10px 40px rgba(0,0,0,0.1);
}

.upload-container h3 {
  color: #333;
  margin-bottom: 15px;
  font-size: 1.2rem;
}

.category-select {
  display: flex;
  align-items: center;
  gap: 10px;
  margin-bottom: 15px;
}

.category-select label {
  color: #666;
  font-size: 0.95rem;
}

.category-input {
  padding: 8px 12px;
  border: 1px solid #ddd;
  border-radius: 8px;
  font-size: 0.95rem;
  background: white;
  cursor: pointer;
}

.category-input:focus {
  outline: none;
  border-color: #a5b4fc;
}

.upload-box {
  border: 2px dashed #ddd;
  border-radius: 12px;
  padding: 30px;
  text-align: center;
  transition: all 0.3s ease;
}

.upload-box.dragging {
  border-color: #a5b4fc;
  background: #f5f7ff;
}

.upload-box.uploading {
  border-style: solid;
  border-color: #a5b4fc;
}

.upload-area {
  cursor: pointer;
}

.upload-icon {
  font-size: 4rem;
  margin-bottom: 15px;
}

.upload-area h3 {
  color: #333;
  margin-bottom: 10px;
  font-size: 1.1rem;
}

.upload-area p {
  color: #666;
  margin-bottom: 5px;
  font-size: 0.85rem;
}

.hint {
  color: #999 !important;
  font-size: 0.75rem !important;
}

.file-input {
  display: none;
}

.upload-progress {
  text-align: left;
}

.progress-header {
  display: flex;
  justify-content: space-between;
  margin-bottom: 10px;
}

.file-name {
  font-weight: 600;
  color: #333;
  font-size: 0.9rem;
}

.progress-percent {
  color: #8b5cf6;
  font-weight: 600;
}

.progress-bar {
  height: 8px;
  background: #eee;
  border-radius: 4px;
  overflow: hidden;
  margin-bottom: 10px;
}

.progress-fill {
  height: 100%;
  background: linear-gradient(90deg, #a5b4fc, #c4b5fd);
  border-radius: 4px;
  transition: width 0.1s ease;
}

.progress-status {
  color: #666;
  font-size: 0.85rem;
}

.upload-success {
  text-align: center;
  padding: 25px;
  background: linear-gradient(135deg, #86efac, #93c5fd);
  border-radius: 12px;
  margin-top: 15px;
  color: #1e3a5f;
}

.success-icon {
  width: 50px;
  height: 50px;
  background: white;
  color: #22c55e;
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 1.5rem;
  margin: 0 auto 12px;
}

.upload-success h4 {
  font-size: 1.2rem;
  margin-bottom: 5px;
}

.upload-success p {
  opacity: 0.9;
  margin-bottom: 8px;
}

.category-tag {
  background: rgba(255,255,255,0.2);
  padding: 4px 12px;
  border-radius: 15px;
  font-size: 0.85rem;
}

.btn {
  padding: 8px 16px;
  border: none;
  border-radius: 8px;
  font-size: 0.95rem;
  cursor: pointer;
  transition: all 0.3s ease;
  margin-top: 10px;
}

.btn-primary {
  background: white;
  color: #11998e;
  font-weight: 600;
}

.btn-primary:hover {
  transform: translateY(-2px);
  box-shadow: 0 5px 15px rgba(0,0,0,0.2);
}
</style>