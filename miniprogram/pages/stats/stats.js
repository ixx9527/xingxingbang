// pages/stats/stats.js
const app = getApp()

Page({
  data: {
    children: [],
    currentChild: null,
    stats: null,
    chartData: { labels: [], values: [] },
    records: [],
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
    wx.showLoading({ title: '加载中...' })

    try {
      // 获取孩子列表
      const childrenRes = await app.request({
        url: `${app.globalData.apiBase}/api/children`
      })

      const children = childrenRes.data
      if (children.length === 0) return

      const currentChild = children[0]
      this.setData({ children, currentChild })

      // 获取积分统计
      const scoresRes = await app.request({
        url: `${app.globalData.apiBase}/api/children/${currentChild.id}/scores`
      })

      if (scoresRes.statusCode === 200) {
        this.setData({ stats: scoresRes.data })
      }

      // 获取趋势图
      const chartRes = await app.request({
        url: `${app.globalData.apiBase}/api/children/${currentChild.id}/scores/chart?days=30`
      })

      if (chartRes.statusCode === 200) {
        this.setData({ chartData: chartRes.data })
      }

      // 获取最近记录
      const recordsRes = await app.request({
        url: `${app.globalData.apiBase}/api/children/${currentChild.id}/records?limit=20`
      })

      if (recordsRes.statusCode === 200) {
        this.setData({ records: recordsRes.data })
      }
    } catch (err) {
      console.error(err)
    } finally {
      this.setData({ loading: false })
      wx.hideLoading()
    }
  },

  // 切换孩子
  switchChild(e) {
    const childId = e.detail.value
    const child = this.data.children[childId]
    this.setData({ currentChild: child })
    this.loadData()
  },

  // 格式化日期
  formatDate(dateStr) {
    if (!dateStr) return ''
    const date = new Date(dateStr)
    const month = date.getMonth() + 1
    const day = date.getDate()
    return `${month}月${day}日`
  }
})