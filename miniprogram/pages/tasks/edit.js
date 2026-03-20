// pages/tasks/edit.js
const app = getApp()

Page({
  data: {
    id: null,
    name: '',
    points: 3,
    category: '学习',
    icon: '📚',
    categories: ['学习', '生活习惯', '运动', '其他'],
    icons: ['📚', '🔢', '✏️', '🔤', '🎹', '⚽', '🏃', '🏊', '🛏️', '😴', '🧸', '🎨', '🚗', '🎮', '🍦', '🎬', '🤝', '🚫', '😤'],
    loading: false
  },

  onLoad(options) {
    if (options.id) {
      this.setData({
        id: options.id,
        name: options.name || '',
        points: parseFloat(options.points) || 3,
        category: options.category || '学习',
        icon: options.icon || '📚'
      })
      wx.setNavigationBarTitle({ title: '编辑任务' })
    } else {
      wx.setNavigationBarTitle({ title: '新增任务' })
    }
  },

  onNameInput(e) { this.setData({ name: e.detail.value }) },
  onPointsChange(e) {
    const type = e.currentTarget.dataset.type
    let { points } = this.data
    points = type === 'add' ? points + 1 : points - 1
    this.setData({ points })
  },
  onCategoryChange(e) { this.setData({ category: this.data.categories[e.detail.value] }) },
  onIconSelect(e) { this.setData({ icon: e.currentTarget.dataset.icon }) },

  async save() {
    const { name, points, category, icon, id } = this.data
    if (!name) { wx.showToast({ title: '请输入任务名称', icon: 'none' }); return }

    this.setData({ loading: true })
    wx.showLoading({ title: '保存中...' })

    try {
      const url = id ? `${app.globalData.apiBase}/api/behaviors/${id}` : `${app.globalData.apiBase}/api/behaviors`
      const method = id ? 'PUT' : 'POST'

      const res = await app.request({
        url,
        method,
        data: { name, points, category, icon, description: '' }
      })

      if (res.statusCode === 200) {
        wx.showToast({ title: '保存成功', icon: 'success' })
        setTimeout(() => wx.navigateBack(), 1500)
      } else {
        wx.showToast({ title: res.data.detail || '保存失败', icon: 'none' })
      }
    } catch (err) {
      wx.showToast({ title: '网络错误', icon: 'none' })
    } finally {
      this.setData({ loading: false })
      wx.hideLoading()
    }
  }
})