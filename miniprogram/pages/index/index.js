// pages/index/index.js
const app = getApp()

Page({
  data: {
    children: [],
    currentChild: null,
    behaviors: [],
    deductBehaviors: [],
    todayScore: 0,
    totalScore: 0,
    streakDays: 0,
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

      if (childrenRes.statusCode !== 200) {
        wx.showToast({ title: '获取数据失败', icon: 'none' })
        return
      }

      const children = childrenRes.data
      if (children.length === 0) {
        wx.showModal({
          title: '提示',
          content: '请先添加孩子',
          showCancel: false,
          success: () => wx.switchTab({ url: '/pages/profile/profile' })
        })
        return
      }

      // 选第一个孩子
      const currentChild = children[0]
      this.setData({ children, currentChild })

      // 获取行为列表
      const behaviorsRes = await app.request({
        url: `${app.globalData.apiBase}/api/behaviors`
      })

      const allBehaviors = behaviorsRes.data
      // 分类：加分行为和扣分行为
      const plus = allBehaviors.filter(b => b.points > 0)
      const minus = allBehaviors.filter(b => b.points < 0)
      this.setData({ behaviors: plus, deductBehaviors: minus })

      // 获取积分统计
      const scoresRes = await app.request({
        url: `${app.globalData.apiBase}/api/children/${currentChild.id}/scores`
      })

      if (scoresRes.statusCode === 200) {
        this.setData({
          todayScore: scoresRes.data.today_points,
          totalScore: scoresRes.data.total_points,
          streakDays: scoresRes.data.streak_days
        })
      }
    } catch (err) {
      wx.showToast({ title: '网络错误', icon: 'none' })
    } finally {
      this.setData({ loading: false })
      wx.hideLoading()
    }
  },

  // 切换孩子
  switchChild(e) {
    const childId = e.currentTarget.dataset.id
    const child = this.data.children.find(c => c.id === childId)
    this.setData({ currentChild: child })
    this.loadScores()
  },

  async loadScores() {
    const { currentChild } = this.data
    if (!currentChild) return

    const res = await app.request({
      url: `${app.globalData.apiBase}/api/children/${currentChild.id}/scores`
    })

    if (res.statusCode === 200) {
      this.setData({
        todayScore: res.data.today_points,
        totalScore: res.data.total_points,
        streakDays: res.data.streak_days
      })
    }
  },

  // 打卡
  async onCheckin(e) {
    const { id, points, name } = e.currentTarget.dataset
    const { currentChild } = this.data

    wx.showModal({
      title: '确认打卡',
      content: `确定完成「${name}」吗？`,
      success: async (res) => {
        if (res.confirm) {
          wx.showLoading({ title: '打卡中...' })

          try {
            const result = await app.request({
              url: `${app.globalData.apiBase}/api/children/${currentChild.id}/records`,
              method: 'POST',
              data: {
                behavior_id: id,
                points: points,
                record_type: 'auto'
              }
            })

            if (result.statusCode === 200) {
              wx.showToast({ title: '打卡成功！', icon: 'success' })
              this.loadScores()
            } else {
              wx.showToast({ title: '打卡失败', icon: 'none' })
            }
          } catch (err) {
            wx.showToast({ title: '网络错误', icon: 'none' })
          } finally {
            wx.hideLoading()
          }
        }
      }
    })
  },

  // 扣分
  onDeduct(e) {
    const { id, name } = e.currentTarget.dataset
    const { currentChild } = this.data

    wx.showModal({
      title: '扣分确认',
      content: `确定要扣「${name}」吗？`,
      success: async (res) => {
        if (res.confirm) {
          wx.showLoading({ title: '处理中...' })

          try {
            const result = await app.request({
              url: `${app.globalData.apiBase}/api/children/${currentChild.id}/records`,
              method: 'POST',
              data: {
                behavior_id: id,
                points: -1,  // 扣分
                record_type: 'deduct'
              }
            })

            if (result.statusCode === 200) {
              wx.showToast({ title: '已扣分', icon: 'success' })
              this.loadScores()
            }
          } catch (err) {
            wx.showToast({ title: '网络错误', icon: 'none' })
          } finally {
            wx.hideLoading()
          }
        }
      }
    })
  },

  // 跳转到统计页
  goStats() {
    wx.switchTab({ url: '/pages/stats/stats' })
  },

  // 跳转到任务管理
  goTasks() {
    wx.navigateTo({ url: '/pages/tasks/tasks' })
  }
})