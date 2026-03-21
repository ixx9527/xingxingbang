<template>
  <el-container class="layout-container">
    <el-aside width="200px">
      <div class="logo">
        <h3>⭐ 星星榜</h3>
      </div>
      <el-menu
        :default-active="route.path"
        router
        class="el-menu-vertical"
      >
        <el-menu-item index="/dashboard">
          <el-icon><DataAnalysis /></el-icon>
          <span>概览</span>
        </el-menu-item>
        <el-menu-item index="/children">
          <el-icon><User /></el-icon>
          <span>孩子管理</span>
        </el-menu-item>
        <el-menu-item index="/records">
          <el-icon><EditPen /></el-icon>
          <span>打卡记录</span>
        </el-menu-item>
        <el-menu-item index="/behaviors">
          <el-icon><Collection /></el-icon>
          <span>行为管理</span>
        </el-menu-item>
        <el-menu-item index="/invite-codes">
          <el-icon><Key /></el-icon>
          <span>邀请码</span>
        </el-menu-item>
      </el-menu>
    </el-aside>
    
    <el-container>
      <el-header>
        <div class="header-right">
          <span class="username">{{ username }}</span>
          <el-button type="warning" size="small" @click="showPasswordDialog = true">
            修改密码
          </el-button>
          <el-button type="danger" size="small" @click="handleLogout">
            退出
          </el-button>
        </div>
      </el-header>
      
      <el-main>
        <router-view />
      </el-main>
    </el-container>
    
    <!-- 修改密码对话框 -->
    <el-dialog v-model="showPasswordDialog" title="修改密码" width="400px">
      <el-form :model="pwdForm" :rules="pwdRules" ref="pwdFormRef">
        <el-form-item label="当前密码" prop="old_password">
          <el-input v-model="pwdForm.old_password" type="password" show-password />
        </el-form-item>
        <el-form-item label="新密码" prop="new_password">
          <el-input v-model="pwdForm.new_password" type="password" show-password />
        </el-form-item>
        <el-form-item label="确认密码" prop="confirm_password">
          <el-input v-model="pwdForm.confirm_password" type="password" show-password />
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="showPasswordDialog = false">取消</el-button>
        <el-button type="primary" :loading="pwdLoading" @click="handleChangePassword">确定</el-button>
      </template>
    </el-dialog>
  </el-container>
</template>

<script setup>
import { ref, reactive, onMounted } from 'vue'
import { useRouter, useRoute } from 'vue-router'
import { ElMessage } from 'element-plus'
import { DataAnalysis, User, EditPen, Collection, Key } from '@element-plus/icons-vue'
import api from '../api'

const router = useRouter()
const route = useRoute()
const username = ref('')
const showPasswordDialog = ref(false)
const pwdLoading = ref(false)
const pwdFormRef = ref()

const pwdForm = reactive({
  old_password: '',
  new_password: '',
  confirm_password: ''
})

const validateConfirm = (rule, value, callback) => {
  if (value !== pwdForm.new_password) {
    callback(new Error('两次密码不一致'))
  } else {
    callback()
  }
}

const pwdRules = {
  old_password: [{ required: true, message: '请输入当前密码', trigger: 'blur' }],
  new_password: [
    { required: true, message: '请输入新密码', trigger: 'blur' },
    { min: 6, message: '密码至少6位', trigger: 'blur' }
  ],
  confirm_password: [
    { required: true, message: '请确认密码', trigger: 'blur' },
    { validator: validateConfirm, trigger: 'blur' }
  ]
}

const handleChangePassword = async () => {
  const valid = await pwdFormRef.value.validate().catch(() => false)
  if (!valid) return
  
  pwdLoading.value = true
  try {
    await api.post('/user/change-password', {
      old_password: pwdForm.old_password,
      new_password: pwdForm.new_password
    })
    ElMessage.success('密码修改成功')
    showPasswordDialog.value = false
  } catch (err) {
    ElMessage.error(err.response?.data?.detail || '修改失败')
  } finally {
    pwdLoading.value = false
  }
}

onMounted(() => {
  const user = localStorage.getItem('username')
  username.value = user || '用户'
})

const handleLogout = () => {
  localStorage.removeItem('token')
  localStorage.removeItem('username')
  router.push('/login')
}
</script>

<style scoped>
.layout-container {
  min-height: 100vh;
}

.el-aside {
  background: #304156;
}

.logo {
  height: 60px;
  display: flex;
  align-items: center;
  justify-content: center;
  background: #263445;
}

.logo h3 {
  color: #fff;
  margin: 0;
  font-size: 18px;
}

.el-menu-vertical {
  border: none;
  background: #304156;
}

.el-menu-item {
  color: #bfcbd9;
}

.el-menu-item:hover,
.el-menu-item.is-active {
  background: #263445 !important;
  color: #409eff !important;
}

.el-header {
  background: #fff;
  box-shadow: 0 1px 4px rgba(0,21,41,.08);
  display: flex;
  align-items: center;
  justify-content: flex-end;
  padding: 0 20px;
}

.header-right {
  display: flex;
  align-items: center;
  gap: 15px;
}

.username {
  color: #333;
}

.el-main {
  background: #f5f7fa;
  padding: 20px;
}
</style>