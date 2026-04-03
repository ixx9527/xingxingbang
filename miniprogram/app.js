// app.js - 星星榜小程序
App({
  globalData: {
    apiBase: 'http://xingxingbang.ixx9527.xin',
    userInfo: null,
    token: null
  },
  
  onLaunch() {
    // 检查登录状态
    const token = wx.getStorageSync('token')
    if (token) {
      this.globalData.token = token
    }
  },
  
  // 登录
  login(token) {
    this.globalData.token = token
    wx.setStorageSync('token', token)
  },
  
  // 登出
  logout() {
    this.globalData.token = null
    wx.removeStorageSync('token')
    wx.redirectTo({ url: '/pages/login/login' })
  },
  
  // 检查登录
  checkLogin() {
    const token = this.globalData.token || wx.getStorageSync('token')
    if (!token) {
      wx.redirectTo({ url: '/pages/login/login' })
      return false
    }
    return true
  },
  
  // 封装请求
  request(options) {
    const token = this.globalData.token || wx.getStorageSync('token')
    return wx.request({
      ...options,
      header: {
        'Authorization': `Bearer ${token}`,
        'Content-Type': 'application/json',
        ...options.header
      }
    })
  }
})