// pages/login/login.js
const app = getApp()

Page({
  data: {
    username: '',
    password: '',
    loading: false
  },

  onLoad() {
    // 检查是否已登录
    const token = wx.getStorageSync('token')
    if (token) {
      wx.switchTab({ url: '/pages/index/index' })
    }
  },

  // 输入处理
  onUsernameInput(e) {
    this.setData({ username: e.detail.value })
  },

  onPasswordInput(e) {
    this.setData({ password: e.detail.value })
  },

  // 登录
  async login() {
    const { username, password } = this.data
    
    if (!username || !password) {
      wx.showToast({ title: '请填写完整', icon: 'none' })
      return
    }

    this.setData({ loading: true })
    wx.showLoading({ title: '登录中...' })

    try {
      const res = await wx.request({
        url: `${app.globalData.apiBase}/api/auth/login`,
        method: 'POST',
        data: { username, password }
      })

      if (res.statusCode === 200) {
        app.login(res.data.access_token)
        wx.showToast({ title: '登录成功', icon: 'success' })
        setTimeout(() => {
          wx.switchTab({ url: '/pages/index/index' })
        }, 1500)
      } else {
        wx.showToast({ title: res.data.detail || '登录失败', icon: 'none' })
      }
    } catch (err) {
      wx.showToast({ title: '网络错误', icon: 'none' })
    } finally {
      this.setData({ loading: false })
      wx.hideLoading()
    }
  },

  // 跳转到注册
  goRegister() {
    wx.navigateTo({ url: '/pages/register/register' })
  }
})