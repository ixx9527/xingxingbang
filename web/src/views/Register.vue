<template>
  <div class="register-page">
    <div class="register-header">
      <h1>⭐ 注册账号</h1>
      <p>需要邀请码才能注册</p>
    </div>

    <van-form @submit="handleRegister" class="register-form">
      <van-field
        v-model="form.username"
        name="username"
        label="用户名"
        placeholder="请输入用户名"
        :rules="[{ required: true, message: '请输入用户名' }]"
      />
      <van-field
        v-model="form.nickname"
        name="nickname"
        label="昵称"
        placeholder="请输入昵称"
        :rules="[{ required: true, message: '请输入昵称' }]"
      />
      <van-field
        v-model="form.password"
        type="password"
        name="password"
        label="密码"
        placeholder="请输入密码（至少6位）"
        :rules="[{ required: true, message: '请输入密码' }, { pattern: /^.{6,}$/, message: '密码至少6位' }]"
      />
      <van-field
        v-model="form.confirmPassword"
        type="password"
        name="confirmPassword"
        label="确认密码"
        placeholder="请确认密码"
        :rules="[{ required: true, message: '请确认密码' }, { validator: validateConfirm, message: '两次密码不一致' }]"
      />
      <van-field
        v-model="form.invite_code"
        name="invite_code"
        label="邀请码"
        placeholder="请输入邀请码"
        :rules="[{ required: true, message: '请输入邀请码' }]"
      />
      <div style="margin: 16px;">
        <van-button round block type="primary" native-type="submit" :loading="loading">
          注册
        </van-button>
      </div>
    </van-form>

    <div class="register-footer">
      <router-link to="/login">已有账号？去登录</router-link>
    </div>
  </div>
</template>

<script setup>
import { ref, reactive } from 'vue'
import { useRouter } from 'vue-router'
import { showSuccessToast, showFailToast } from 'vant'
import { auth } from '../api'

const router = useRouter()
const loading = ref(false)

const form = reactive({
  username: '',
  nickname: '',
  password: '',
  confirmPassword: '',
  invite_code: ''
})

const validateConfirm = () => {
  return form.confirmPassword === form.password
}

const handleRegister = async () => {
  loading.value = true
  try {
    const data = await auth.register({
      username: form.username,
      nickname: form.nickname,
      password: form.password,
      invite_code: form.invite_code
    })
    localStorage.setItem('token', data.access_token)
    localStorage.setItem('refresh_token', data.refresh_token)
    localStorage.setItem('username', form.username)
    showSuccessToast('注册成功')
    router.push('/dashboard')
  } catch (err) {
    showFailToast(err.response?.data?.detail || '注册失败')
  } finally {
    loading.value = false
  }
}
</script>

<style scoped>
.register-page {
  min-height: 100vh;
  display: flex;
  flex-direction: column;
  justify-content: center;
  padding: 20px;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
}

.register-header {
  text-align: center;
  margin-bottom: 30px;
}

.register-header h1 {
  color: #fff;
  font-size: 28px;
  margin: 0;
}

.register-header p {
  color: rgba(255, 255, 255, 0.8);
  margin-top: 8px;
}

.register-form {
  background: #fff;
  border-radius: 12px;
  padding: 20px;
}

.register-footer {
  text-align: center;
  margin-top: 20px;
}

.register-footer a {
  color: rgba(255, 255, 255, 0.9);
}
</style>