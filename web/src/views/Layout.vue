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
          <el-button type="danger" size="small" @click="handleLogout">
            退出
          </el-button>
        </div>
      </el-header>
      
      <el-main>
        <router-view />
      </el-main>
    </el-container>
  </el-container>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { useRouter, useRoute } from 'vue-router'
import { DataAnalysis, User, EditPen, Collection, Key } from '@element-plus/icons-vue'

const router = useRouter()
const route = useRoute()
const username = ref('')

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