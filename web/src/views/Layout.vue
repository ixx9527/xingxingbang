<template>
  <div class="layout-container">
    <!-- 桌面端侧边栏 -->
    <div class="desktop-sidebar">
      <div class="sidebar-logo">
        <h3>⭐ 星星榜</h3>
      </div>
      <van-sidebar v-model="activeMenu" @change="onMenuChange">
        <van-sidebar-item to="/dashboard" title="概览" icon="chart-trending-o" />
        <van-sidebar-item to="/children" title="孩子管理" icon="user-o" />
        <van-sidebar-item to="/records" title="打卡记录" icon="edit" />
        <van-sidebar-item to="/behaviors" title="行为管理" icon="apps-o" />
        <van-sidebar-item to="/invite-codes" title="邀请码" icon="lock" />
      </van-sidebar>
    </div>

    <!-- 移动端顶部导航 -->
    <van-nav-bar
      class="mobile-header"
      :title="pageTitle"
      left-arrow
      @click-left="onClickLeft"
    >
      <template #right>
        <van-popover v-model:show="showUserMenu" placement="bottom-end" :actions="userActions" @select="onUserAction">
          <template #reference>
            <van-icon name="user-o" size="18" />
          </template>
        </van-popover>
      </template>
    </van-nav-bar>

    <!-- 主内容区 -->
    <div :class="isMobile ? 'mobile-content' : 'desktop-main'">
      <!-- 桌面端头部 -->
      <div v-if="!isMobile" class="desktop-header">
        <span class="user-nickname">{{ userInfo.nickname || userInfo.username }}</span>
        <van-button size="small" type="warning" @click="showPasswordPopup = true">修改密码</van-button>
        <van-button size="small" type="danger" @click="handleLogout">退出</van-button>
      </div>

      <!-- 页面内容 -->
      <div :class="isMobile ? '' : 'desktop-content'">
        <router-view />
      </div>
    </div>

    <!-- 移动端底部 TabBar -->
    <van-tabbar class="mobile-tabbar" v-model="activeTab" route>
      <van-tabbar-item to="/dashboard" icon="chart-trending-o">概览</van-tabbar-item>
      <van-tabbar-item to="/children" icon="user-o">孩子</van-tabbar-item>
      <van-tabbar-item to="/records" icon="edit">打卡</van-tabbar-item>
      <van-tabbar-item to="/behaviors" icon="apps-o">行为</van-tabbar-item>
      <van-tabbar-item to="/invite-codes" icon="lock">邀请码</van-tabbar-item>
    </van-tabbar>

    <!-- 修改密码弹窗 -->
    <van-popup v-model:show="showPasswordPopup" position="bottom" :style="{ height: '40%' }" round>
      <div class="password-popup">
        <h3>修改密码</h3>
        <van-form @submit="handleChangePassword">
          <van-field
            v-model="pwdForm.old_password"
            type="password"
            label="当前密码"
            placeholder="请输入当前密码"
            :rules="[{ required: true, message: '请输入当前密码' }]"
          />
          <van-field
            v-model="pwdForm.new_password"
            type="password"
            label="新密码"
            placeholder="请输入新密码"
            :rules="[{ required: true, message: '请输入新密码' }, { pattern: /^.{6,}$/, message: '密码至少6位' }]"
          />
          <van-field
            v-model="pwdForm.confirm_password"
            type="password"
            label="确认密码"
            placeholder="请确认新密码"
            :rules="[{ required: true, message: '请确认密码' }, { validator: validateConfirm, message: '两次密码不一致' }]"
          />
          <div style="margin: 16px;">
            <van-button round block type="primary" native-type="submit" :loading="pwdLoading">
              确定
            </van-button>
          </div>
        </van-form>
      </div>
    </van-popup>
  </div>
</template>

<script setup>
import { ref, reactive, computed, onMounted, watch } from 'vue'
import { useRouter, useRoute } from 'vue-router'
import { showToast, showSuccessToast, showFailToast } from 'vant'
import { user } from '../api'

const router = useRouter()
const route = useRoute()

// 状态
const isMobile = ref(false)
const activeMenu = ref(0)
const activeTab = ref(0)
const userInfo = ref({ id: '', username: '', nickname: '' })
const showUserMenu = ref(false)
const showPasswordPopup = ref(false)
const pwdLoading = ref(false)

const pwdForm = reactive({
  old_password: '',
  new_password: '',
  confirm_password: ''
})

// 用户菜单操作
const userActions = [
  { text: userInfo.value.nickname || userInfo.value.username || '用户', icon: 'user-o' },
  { text: '修改密码', icon: 'lock' },
  { text: '退出登录', icon: 'close' }
]

// 页面标题映射
const titleMap = {
  '/dashboard': '数据概览',
  '/children': '孩子管理',
  '/records': '打卡记录',
  '/behaviors': '行为管理',
  '/invite-codes': '邀请码'
}

const pageTitle = computed(() => titleMap[route.path] || '星星榜')

// 监听窗口大小变化
const checkMobile = () => {
  isMobile.value = window.innerWidth < 768
}

onMounted(() => {
  checkMobile()
  window.addEventListener('resize', checkMobile)
  loadUserInfo()
})

// 加载用户信息
const loadUserInfo = async () => {
  try {
    const data = await user.me()
    userInfo.value = data
  } catch (err) {
    userInfo.value.username = localStorage.getItem('username') || '用户'
  }
}

// 菜单切换
const onMenuChange = (index) => {
  const paths = ['/dashboard', '/children', '/records', '/behaviors', '/invite-codes']
  router.push(paths[index])
}

// 返回按钮（移动端）
const onClickLeft = () => {
  router.back()
}

// 用户菜单选择
const onUserAction = (action) => {
  if (action.text === '修改密码') {
    showPasswordPopup.value = true
  } else if (action.text === '退出登录') {
    handleLogout()
  }
}

// 验证密码确认
const validateConfirm = () => {
  return pwdForm.confirm_password === pwdForm.new_password
}

// 修改密码
const handleChangePassword = async () => {
  pwdLoading.value = true
  try {
    await user.changePassword({
      old_password: pwdForm.old_password,
      new_password: pwdForm.new_password
    })
    showSuccessToast('密码修改成功')
    showPasswordPopup.value = false
    pwdForm.old_password = ''
    pwdForm.new_password = ''
    pwdForm.confirm_password = ''
  } catch (err) {
    showFailToast(err.response?.data?.detail || '修改失败')
  } finally {
    pwdLoading.value = false
  }
}

// 退出登录
const handleLogout = () => {
  localStorage.removeItem('token')
  localStorage.removeItem('refresh_token')
  localStorage.removeItem('username')
  router.push('/login')
}

// 监听路由变化更新菜单状态
watch(() => route.path, (path) => {
  const paths = ['/dashboard', '/children', '/records', '/behaviors', '/invite-codes']
  const index = paths.indexOf(path)
  if (index !== -1) {
    activeMenu.value = index
    activeTab.value = index
  }
}, { immediate: true })
</script>

<style scoped>
/* 桌面端侧边栏样式 */
.sidebar-logo {
  height: 60px;
  display: flex;
  align-items: center;
  justify-content: center;
  background: #001529;
}

.sidebar-logo h3 {
  color: #fff;
  margin: 0;
  font-size: 18px;
}

.desktop-sidebar .van-sidebar {
  width: 100%;
  background: #001925;
}

.desktop-sidebar .van-sidebar-item {
  background: #001925;
  color: #bfcbd9;
  padding: 16px 12px;
}

.desktop-sidebar .van-sidebar-item--select {
  background: #1890ff;
  color: #fff;
}

/* 桌面端头部 */
.desktop-header {
  display: flex;
  align-items: center;
  gap: 12px;
}

.user-nickname {
  color: #323233;
  font-weight: 500;
}

/* 移动端头部 */
.mobile-header .van-nav-bar {
  background: #fff;
}

/* 密码弹窗 */
.password-popup {
  padding: 20px 16px;
}

.password-popup h3 {
  text-align: center;
  margin-bottom: 20px;
  color: #323233;
}

/* 移动端底部导航 */
.mobile-tabbar {
  background: #fff;
  border-top: 1px solid #ebedf0;
}
</style>