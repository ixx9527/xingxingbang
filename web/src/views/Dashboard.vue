<template>
  <div class="dashboard">
    <h2>数据概览</h2>
    
    <el-row :gutter="20" style="margin-top: 20px">
      <el-col :span="6">
        <el-card shadow="hover">
          <div class="stat-card">
            <div class="stat-icon" style="background: #409eff">
              <el-icon :size="30"><User /></el-icon>
            </div>
            <div class="stat-info">
              <div class="stat-value">{{ stats.childrenCount }}</div>
              <div class="stat-label">孩子数量</div>
            </div>
          </div>
        </el-card>
      </el-col>
      
      <el-col :span="6">
        <el-card shadow="hover">
          <div class="stat-card">
            <div class="stat-icon" style="background: #67c23a">
              <el-icon :size="30"><Coin /></el-icon>
            </div>
            <div class="stat-info">
              <div class="stat-value">{{ stats.todayPoints }}</div>
              <div class="stat-label">今日积分</div>
            </div>
          </div>
        </el-card>
      </el-col>
      
      <el-col :span="6">
        <el-card shadow="hover">
          <div class="stat-card">
            <div class="stat-icon" style="background: #e6a23c">
              <el-icon :size="30"><Timer /></el-icon>
            </div>
            <div class="stat-info">
              <div class="stat-value">{{ stats.maxStreak }}</div>
              <div class="stat-label">最高连续天数</div>
            </div>
          </div>
        </el-card>
      </el-col>
      
      <el-col :span="6">
        <el-card shadow="hover">
          <div class="stat-card">
            <div class="stat-icon" style="background: #f56c6c">
              <el-icon :size="30"><Trophy /></el-icon>
            </div>
            <div class="stat-info">
              <div class="stat-value">{{ stats.totalRecords }}</div>
              <div class="stat-label">总打卡次数</div>
            </div>
          </div>
        </el-card>
      </el-col>
    </el-row>
    
    <el-row :gutter="20" style="margin-top: 20px">
      <el-col :span="12">
        <el-card>
          <template #header>
            <span>孩子列表</span>
          </template>
          <el-table :data="children" stripe>
            <el-table-column prop="name" label="姓名" />
            <el-table-column prop="total_points" label="总积分" />
            <el-table-column prop="streak_days" label="连续天数" />
            <el-table-column label="等级">
              <template #default="{ row }">
                <el-tag>{{ getLevelName(row.total_points) }}</el-tag>
              </template>
            </el-table-column>
          </el-table>
        </el-card>
      </el-col>
      
      <el-col :span="12">
        <el-card>
          <template #header>
            <span>最近打卡</span>
          </template>
          <el-timeline>
            <el-timeline-item
              v-for="record in recentRecords"
              :key="record.id"
              :timestamp="record.created_at"
              placement="top"
            >
              {{ record.behavior_name }} +{{ record.points }}分
            </el-timeline-item>
          </el-timeline>
        </el-card>
      </el-col>
    </el-row>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { User, Coin, Timer, Trophy } from '@element-plus/icons-vue'
import { children as childrenApi } from '../api'

const stats = ref({
  childrenCount: 0,
  todayPoints: 0,
  maxStreak: 0,
  totalRecords: 0
})

const children = ref([])
const recentRecords = ref([])

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

onMounted(async () => {
  try {
    const list = await childrenApi.list()
    children.value = list
    
    stats.value.childrenCount = list.length
    
    let maxStreak = 0
    let totalRecords = 0
    let todayPoints = 0
    
    for (const child of list) {
      const scores = await childrenApi.getScores(child.id)
      maxStreak = Math.max(maxStreak, scores.streak_days)
      totalRecords += scores.today_points
      
      const levelInfo = await childrenApi.getLevel(child.id)
      if (levelInfo.leveled_up_today) {
        // 可以显示升级提示
      }
    }
    
    stats.value.maxStreak = maxStreak
    stats.value.totalRecords = totalRecords
    
    // 获取最近打卡记录
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
.dashboard h2 {
  margin: 0;
}

.stat-card {
  display: flex;
  align-items: center;
  gap: 15px;
}

.stat-icon {
  width: 60px;
  height: 60px;
  border-radius: 10px;
  display: flex;
  align-items: center;
  justify-content: center;
  color: #fff;
}

.stat-info {
  flex: 1;
}

.stat-value {
  font-size: 28px;
  font-weight: bold;
  color: #333;
}

.stat-label {
  color: #999;
  font-size: 14px;
}
</style>