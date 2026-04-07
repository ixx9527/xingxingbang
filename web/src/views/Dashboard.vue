<template>
  <div class="dashboard-page">
    <div class="page-header">
      <h2 class="page-title">数据概览</h2>
    </div>

    <!-- 统计卡片 -->
    <van-grid :column-num="isMobile ? 2 : 4" :gutter="12">
      <van-grid-item icon="user-o" text="孩子数量">
        <template #text>
          <div class="stat-value">{{ stats.childrenCount }}</div>
          <div class="stat-label">孩子数量</div>
        </template>
      </van-grid-item>
      <van-grid-item icon="star-o" text="今日积分">
        <template #text>
          <div class="stat-value">{{ stats.todayPoints }}</div>
          <div class="stat-label">今日积分</div>
        </template>
      </van-grid-item>
      <van-grid-item icon="fire-o" text="最高连续">
        <template #text>
          <div class="stat-value">{{ stats.maxStreak }}</div>
          <div class="stat-label">最高连续</div>
        </template>
      </van-grid-item>
      <van-grid-item icon="success" text="打卡次数">
        <template #text>
          <div class="stat-value">{{ stats.totalRecords }}</div>
          <div class="stat-label">打卡次数</div>
        </template>
      </van-grid-item>
    </van-grid>

    <!-- 孩子列表 -->
    <div class="section-card">
      <h3 class="section-title">孩子列表</h3>
      <div v-if="isMobile">
        <van-cell-group inset>
          <van-cell
            v-for="child in children"
            :key="child.id"
            :title="child.name"
            :value="`Lv.${getLevelIndex(child.total_points)}`"
            :label="`总积分: ${child.total_points} | 连续: ${child.streak_days}天`"
            is-link
            @click="viewChild(child)"
          >
            <template #icon>
              <span class="level-tag" :class="'level-' + getLevelIndex(child.total_points)">
                {{ getLevelName(child.total_points) }}
              </span>
            </template>
          </van-cell>
        </van-cell-group>
      </div>
      <table v-else class="desktop-table">
        <thead>
          <tr>
            <th>姓名</th>
            <th>总积分</th>
            <th>连续天数</th>
            <th>等级</th>
          </tr>
        </thead>
        <tbody>
          <tr v-for="child in children" :key="child.id" @click="viewChild(child)">
            <td>{{ child.name }}</td>
            <td>{{ child.total_points }}</td>
            <td>{{ child.streak_days }}</td>
            <td>
              <span class="level-tag" :class="'level-' + getLevelIndex(child.total_points)">
                {{ getLevelName(child.total_points) }}
              </span>
            </td>
          </tr>
        </tbody>
      </table>
    </div>

    <!-- 最近打卡 -->
    <div class="section-card">
      <h3 class="section-title">最近打卡</h3>
      <div v-if="isMobile">
        <van-cell-group inset>
          <van-cell
            v-for="record in recentRecords"
            :key="record.id"
            :title="record.behavior_name"
            :label="formatDate(record.created_at)"
          >
            <template #icon>
              <span style="font-size: 20px; margin-right: 8px;">{{ record.behavior_icon }}</span>
            </template>
            <template #value>
              <van-tag type="success">+{{ record.points }}</van-tag>
            </template>
          </van-cell>
        </van-cell-group>
      </div>
      <div v-else>
        <van-steps direction="vertical" :active="0">
          <van-step v-for="record in recentRecords" :key="record.id">
            <div class="step-content">
              <span class="step-icon">{{ record.behavior_icon }}</span>
              <span>{{ record.behavior_name }}</span>
              <van-tag type="success" style="margin-left: 8px;">+{{ record.points }}</van-tag>
              <span class="step-time">{{ formatDate(record.created_at) }}</span>
            </div>
          </van-step>
        </van-steps>
      </div>
    </div>

    <!-- 孩子详情弹窗 -->
    <van-popup v-model:show="showChildPopup" position="bottom" :style="{ height: '50%' }" round>
      <div class="child-popup" v-if="selectedChild">
        <h3>{{ selectedChild.name }} 详情</h3>
        <van-cell-group inset>
          <van-cell title="姓名" :value="selectedChild.name" />
          <van-cell title="生日" :value="selectedChild.birth_date" />
          <van-cell title="性别" :value="selectedChild.gender === 'male' ? '男' : '女'" />
          <van-cell title="总积分" :value="selectedChild.total_points" />
          <van-cell title="连续天数" :value="selectedChild.streak_days" />
          <van-cell title="等级">
            <template #value>
              <span class="level-tag" :class="'level-' + getLevelIndex(selectedChild.total_points)">
                {{ getLevelName(selectedChild.total_points) }}
              </span>
            </template>
          </van-cell>
        </van-cell-group>
      </div>
    </van-popup>
  </div>
</template>

<script setup>
import { ref, onMounted, computed } from 'vue'
import { children as childrenApi } from '../api'
import dayjs from 'dayjs'

const isMobile = ref(window.innerWidth < 768)

const stats = ref({
  childrenCount: 0,
  todayPoints: 0,
  maxStreak: 0,
  totalRecords: 0
})

const children = ref([])
const recentRecords = ref([])
const showChildPopup = ref(false)
const selectedChild = ref(null)

const levels = [
  { name: '萌芽宝宝', min: 0 },
  { name: '嫩芽宝宝', min: 100 },
  { name: '小树苗', min: 300 },
  { name: '成长树', min: 600 },
  { name: '茁壮树', min: 1000 },
  { name: '开花树', min: 1500 },
  { name: '结果树', min: 2500 },
  { name: '明星树', min: 4000 },
  { name: '超级星', min: 6000 },
  { name: '宇宙星神', min: 10000 }
]

const getLevelName = (points) => {
  for (let i = levels.length - 1; i >= 0; i--) {
    if (points >= levels[i].min) return levels[i].name
  }
  return levels[0].name
}

const getLevelIndex = (points) => {
  for (let i = levels.length - 1; i >= 0; i--) {
    if (points >= levels[i].min) return i
  }
  return 0
}

const formatDate = (dateStr) => {
  return dayjs(dateStr).format('MM-DD HH:mm')
}

const viewChild = async (child) => {
  try {
    const detail = await childrenApi.get(child.id)
    selectedChild.value = detail
    showChildPopup.value = true
  } catch (err) {
    console.error(err)
  }
}

onMounted(async () => {
  window.addEventListener('resize', () => {
    isMobile.value = window.innerWidth < 768
  })

  try {
    const list = await childrenApi.list()
    children.value = list

    stats.value.childrenCount = list.length
    stats.value.todayPoints = 0
    stats.value.maxStreak = 0

    for (const child of list) {
      const scores = await childrenApi.getScores(child.id)
      stats.value.todayPoints += scores.today_points
      stats.value.maxStreak = Math.max(stats.value.maxStreak, scores.streak_days)
    }

    stats.value.totalRecords = stats.value.todayPoints

    if (list.length > 0) {
      const records = await childrenApi.getRecords(list[0].id, { limit: 5 })
      recentRecords.value = records
    }
  } catch (err) {
    console.error(err)
  }
})
</script>

<style scoped>
.section-card {
  background: #fff;
  border-radius: 8px;
  margin-top: 12px;
  padding: 16px;
}

.section-title {
  font-size: 16px;
  font-weight: 500;
  color: #323233;
  margin-bottom: 12px;
}

.step-content {
  display: flex;
  align-items: center;
  gap: 8px;
}

.step-icon {
  font-size: 20px;
}

.step-time {
  color: #969799;
  font-size: 12px;
  margin-left: auto;
}

.child-popup {
  padding: 20px 16px;
}

.child-popup h3 {
  text-align: center;
  margin-bottom: 20px;
}

.desktop-table tr {
  cursor: pointer;
}
</style>