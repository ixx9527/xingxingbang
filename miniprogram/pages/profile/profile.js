// pages/profile/profile.js
const app = getApp()

Page({
  data: {
    userInfo: null,
    children: [],
    loading: true
  },

  onLoad() {
    if (!app.checkLogin()) return
  },

  onShow() {
    if (app.checkLogin()) {
      this.loadData()
    }
  },

  async loadData() {
    this.setData({ loading: true })
    try {
      const token = wx.getStorageSync('token')
      // 这里简化处理，直接从缓存获取
      this.setData({
        userInfo: { nickname: wx.getStorageSync('username') || '家长' },
        children: []
      })

      const res = await app.request({
        url: `${app.globalData.apiBase}/api/children`
      })
      if (res.statusCode === 200) {
        this.setData({ children: res.data })
      }
    } catch (err) {
      console.error(err)
    } finally {
      this.setData({ loading: false })
    }
  },

  // 添加孩子
  goAddChild() {
    wx.showModal({
      title: '添加孩子',
      content: '请在 Web 端管理孩子',
      showCancel: false
    })
  },

  // 退出登录
  logout() {
    wx.showModal({
      title: '确认退出',
      content: '确定要退出登录吗？',
      success: (res) => {
        if (res.confirm) {
          app.logout()
        }
      }
    })
  }
})