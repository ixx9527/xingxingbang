// pages/tasks/tasks.js
const app = getApp()

Page({
  data: {
    behaviors: [],
    categories: ['全部', '学习', '生活习惯', '运动', '其他'],
    currentCategory: 0,
    loading: true
  },

  onLoad() {
    if (!app.checkLogin()) return
    this.loadBehaviors()
  },

  async loadBehaviors() {
    this.setData({ loading: true })
    wx.showLoading({ title: '加载中...' })

    try {
      const res = await app.request({
        url: `${app.globalData.apiBase}/api/behaviors`
      })

      if (res.statusCode === 200) {
        this.setData({ behaviors: res.data })
      }
    } catch (err) {
      wx.showToast({ title: '加载失败', icon: 'none' })
    } finally {
      this.setData({ loading: false })
      wx.hideLoading()
    }
  },

  // 筛选分类
  onCategoryChange(e) {
    this.setData({ currentCategory: e.detail.value })
  },

  // 新增任务
  goAdd() {
    wx.navigateTo({ url: '/pages/tasks/edit' })
  },

  // 编辑任务
  goEdit(e) {
    const id = e.currentTarget.dataset.id
    const behavior = this.data.behaviors.find(b => b.id === id)
    if (behavior.is_system) {
      wx.showToast({ title: '系统预设不能编辑', icon: 'none' })
      return
    }
    wx.navigateTo({ url: `/pages/tasks/edit?id=${id}&name=${behavior.name}&points=${behavior.points}&category=${behavior.category}&icon=${behavior.icon}` })
  },

  // 删除任务
  async onDelete(e) {
    const id = e.currentTarget.dataset.id
    const behavior = this.data.behaviors.find(b => b.id === id)
    
    if (behavior.is_system) {
      wx.showToast({ title: '系统预设不能删除', icon: 'none' })
      return
    }

    wx.showModal({
      title: '确认删除',
      content: `确定删除「${behavior.name}」吗？`,
      success: async (res) => {
        if (res.confirm) {
          try {
            const result = await app.request({
              url: `${app.globalData.apiBase}/api/behaviors/${id}`,
              method: 'DELETE'
            })

            if (result.statusCode === 200) {
              wx.showToast({ title: '删除成功', icon: 'success' })
              this.loadBehaviors()
            }
          } catch (err) {
            wx.showToast({ title: '删除失败', icon: 'none' })
          }
        }
      }
    })
  },

  getFilteredBehaviors() {
    const { behaviors, currentCategory, categories } = this.data
    if (currentCategory == 0) return behaviors
    const cat = categories[currentCategory]
    return behaviors.filter(b => b.category === cat)
  }
})