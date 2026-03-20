// pages/register/register.js
const app = getApp()

Page({
  data: {
    username: '',
    password: '',
    confirmPassword: '',
    nickname: '',
    inviteCode: '',
    loading: false
  },

  onLoad() {},

  onInput(e) {
    const field = e.currentTarget.dataset.field
    this.setData({ [field]: e.detail.value })
  },

  async register() {
    const { username, password, confirmPassword, nickname, inviteCode } = this.data

    if (!username || !password || !nickname || !inviteCode) {
      wx.showToast({ title: '请填写完整', icon: 'none' })
      return
    }

    if (password !== confirmPassword) {
      wx.showToast({ title: '两次密码不一致', icon: 'none' })
      return
    }

    if (password.length < 6) {
      wx.showToast({ title: '密码至少6位', icon: 'none' })
      return
    }

    this.setData({ loading: true })
    wx.showLoading({ title: '注册中...' })

    try {
      const res = await wx.request({
        url: `${app.globalData.apiBase}/api/auth/register`,
        method: 'POST',
        data: { username, password, nickname, invite_code: inviteCode }
      })

      if (res.statusCode === 200) {
        app.login(res.data.access_token)
        wx.showToast({ title: '注册成功！', icon: 'success' })
        setTimeout(() => {
          wx.switchTab({ url: '/pages/index/index' })
        }, 1500)
      } else {
        wx.showToast({ title: res.data.detail || '注册失败', icon: 'none' })
      }
    } catch (err) {
      wx.showToast({ title: '网络错误', icon: 'none' })
    } finally {
      this.setData({ loading: false })
      wx.hideLoading()
    }
  }
})