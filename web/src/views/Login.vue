<template>
  <div class="login-page">
    <div class="login-header">
      <h1>⭐ 星星榜</h1>
      <p>儿童成长打卡系统</p>
    </div>

    <van-form @submit="handleLogin" class="login-form">
      <van-field
        v-model="form.username"
        name="username"
        label="用户名"
        placeholder="请输入用户名"
        :rules="[{ required: true, message: '请输入用户名' }]"
      />
      <van-field
        v-model="form.password"
        type="password"
        name="password"
        label="密码"
        placeholder="请输入密码"
        :rules="[{ required: true, message: '请输入密码' }]"
      />
      <div style="margin: 16px;">
        <van-button round block type="primary" native-type="submit" :loading="loading">
          登录
        </van-button>
      </div>
    </van-form>

    <div class="login-footer">
      <router-link to="/register">没有账号？去注册</router-link>
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
  password: ''
})

const handleLogin = async () => {
  loading.value = true
  try {
    const data = await auth.login({
      username: form.username,
      password: form.password
    })
    localStorage.setItem('token', data.access_token)
    localStorage.setItem('refresh_token', data.refresh_token)
    localStorage.setItem('username', form.username)
    showSuccessToast('登录成功')
    router.push('/dashboard')
  } catch (err) {
    showFailToast(err.response?.data?.detail || '登录失败')
  } finally {
    loading.value = false
  }
}
</script>

<style scoped>
.login-page {
  min-height: 100vh;
  display: flex;
  flex-direction: column;
  justify-content: center;
  padding: 20px;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
}

.login-header {
  text-align: center;
  margin-bottom: 40px;
}

.login-header h1 {
  color: #fff;
  font-size: 32px;
  margin: 0;
}

.login-header p {
  color: rgba(255, 255, 255, 0.8);
  margin-top: 8px;
}

.login-form {
  background: #fff;
  border-radius: 12px;
  padding: 20px;
}

.login-footer {
  text-align: center;
  margin-top: 20px;
}

.login-footer a {
  color: rgba(255, 255, 255, 0.9);
}
</style>