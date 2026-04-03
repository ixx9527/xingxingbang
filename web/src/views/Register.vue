<template>
  <div class="login-container">
    <el-card class="login-card">
      <template #header>
        <div class="card-header">
          <h2>⭐ 注册账号</h2>
          <p>需要邀请码才能注册</p>
        </div>
      </template>
      
      <el-form :model="form" :rules="rules" ref="formRef" @submit.prevent="handleRegister">
        <el-form-item prop="username">
          <el-input 
            v-model="form.username" 
            placeholder="用户名"
            :prefix-icon="User"
            size="large"
          />
        </el-form-item>
        
        <el-form-item prop="nickname">
          <el-input 
            v-model="form.nickname" 
            placeholder="昵称"
            :prefix-icon="UserFilled"
            size="large"
          />
        </el-form-item>
        
        <el-form-item prop="password">
          <el-input 
            v-model="form.password" 
            type="password" 
            placeholder="密码"
            :prefix-icon="Lock"
            size="large"
            show-password
          />
        </el-form-item>
        
        <el-form-item prop="confirmPassword">
          <el-input 
            v-model="form.confirmPassword" 
            type="password" 
            placeholder="确认密码"
            :prefix-icon="Lock"
            size="large"
            show-password
            @keyup.enter="handleRegister"
          />
        </el-form-item>
        
        <el-form-item prop="invite_code">
          <el-input 
            v-model="form.invite_code" 
            placeholder="邀请码"
            :prefix-icon="Key"
            size="large"
          />
        </el-form-item>
        
        <el-form-item>
          <el-button 
            type="primary" 
            size="large" 
            style="width: 100%" 
            :loading="loading"
            @click="handleRegister"
          >
            注册
          </el-button>
        </el-form-item>
      </el-form>
      
      <div class="footer">
        <router-link to="/login">已有账号？登录</router-link>
      </div>
    </el-card>
  </div>
</template>

<script setup>
import { ref, reactive } from 'vue'
import { useRouter } from 'vue-router'
import { ElMessage } from 'element-plus'
import { User, Lock, UserFilled, Key } from '@element-plus/icons-vue'
import { auth } from '../api'

const router = useRouter()
const formRef = ref()
const loading = ref(false)

const form = reactive({
  username: '',
  nickname: '',
  password: '',
  confirmPassword: '',
  invite_code: ''
})

const validatePass2 = (rule, value, callback) => {
  if (value !== form.password) {
    callback(new Error('两次输入密码不一致'))
  } else {
    callback()
  }
}

const rules = {
  username: [{ required: true, message: '请输入用户名', trigger: 'blur' }],
  nickname: [{ required: true, message: '请输入昵称', trigger: 'blur' }],
  password: [
    { required: true, message: '请输入密码', trigger: 'blur' },
    { min: 6, message: '密码至少6位', trigger: 'blur' }
  ],
  confirmPassword: [
    { required: true, message: '请确认密码', trigger: 'blur' },
    { validator: validatePass2, trigger: 'blur' }
  ],
  invite_code: [{ required: true, message: '请输入邀请码', trigger: 'blur' }]
}

const handleRegister = async () => {
  const valid = await formRef.value.validate().catch(() => false)
  if (!valid) return

  loading.value = true
  try {
    const { confirmPassword, ...data } = form
    const res = await auth.register(data)
    localStorage.setItem('token', res.access_token)
    localStorage.setItem('user', JSON.stringify({ username: form.username }))
    ElMessage.success('注册成功')
    router.push('/')
  } catch (err) {
    ElMessage.error(err.response?.data?.detail || '注册失败')
  } finally {
    loading.value = false
  }
}
</script>

<style scoped>
.login-container {
  min-height: 100vh;
  display: flex;
  align-items: center;
  justify-content: center;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
}

.login-card {
  width: 400px;
}

.card-header {
  text-align: center;
}

.card-header h2 {
  margin: 0;
  color: #333;
}

.card-header p {
  margin: 5px 0 0;
  color: #999;
  font-size: 14px;
}

.footer {
  text-align: center;
  margin-top: 10px;
}

.footer a {
  color: #409eff;
  text-decoration: none;
}
</style>