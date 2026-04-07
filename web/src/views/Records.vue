<template>
  <div class="records-page">
    <div class="page-header">
      <h2 class="page-title">打卡记录</h2>
      <van-button type="primary" size="small" icon="plus" @click="showCheckinPopup">打卡</van-button>
    </div>

    <!-- 筛选 -->
    <van-cell-group inset style="margin-bottom: 12px;">
      <van-cell title="孩子">
        <template #value>
          <van-dropdown-menu>
            <van-dropdown-item v-model="selectedChildId" :options="childOptions" @change="loadRecords" />
          </van-dropdown-menu>
        </template>
      </van-cell>
      <van-cell title="日期" is-link @click="showDateFilter = true">
        <template #value>
          {{ dateRangeText || '全部' }}
        </template>
      </van-cell>
    </van-cell-group>

    <!-- 记录列表 -->
    <div v-if="isMobile">
      <van-cell-group inset>
        <van-cell
          v-for="record in records"
          :key="record.id"
          :title="record.behavior_name"
          :label="formatDate(record.created_at)"
        >
          <template #icon>
            <span style="font-size: 24px; margin-right: 8px;">{{ record.behavior_icon }}</span>
          </template>
          <template #value>
            <van-tag :type="record.points >= 0 ? 'success' : 'danger'">
              {{ record.points >= 0 ? '+' + record.points : record.points }}
            </van-tag>
          </template>
          <template #extra>
            <span style="color: #969799; font-size: 12px;">{{ record.record_type === 'good' ? '好行为' : '需改进' }}</span>
          </template>
        </van-cell>
      </van-cell-group>
    </div>
    <table v-else class="desktop-table">
      <thead>
        <tr>
          <th>图标</th>
          <th>行为</th>
          <th>积分</th>
          <th>备注</th>
          <th>类型</th>
          <th>时间</th>
        </tr>
      </thead>
      <tbody>
        <tr v-for="record in records" :key="record.id">
          <td><span style="font-size: 24px;">{{ record.behavior_icon }}</span></td>
          <td>{{ record.behavior_name }}</td>
          <td>
            <van-tag :type="record.points >= 0 ? 'success' : 'danger'">
              {{ record.points >= 0 ? '+' + record.points : record.points }}
            </van-tag>
          </td>
          <td>{{ record.note || '-' }}</td>
          <td>{{ record.record_type === 'good' ? '好行为' : '需改进' }}</td>
          <td>{{ formatDate(record.created_at) }}</td>
        </tr>
      </tbody>
    </table>

    <!-- 打卡弹窗 -->
    <van-popup v-model:show="showCheckinDialog" position="bottom" :style="{ height: '70%' }" round>
      <div class="popup-content">
        <h3>打卡</h3>
        <van-form @submit="handleCheckin">
          <van-field
            v-model="checkinForm.childName"
            label="孩子"
            readonly
            clickable
            @click="showChildPicker = true"
            :rules="[{ required: true, message: '请选择孩子' }]"
          />
          <van-field
            v-model="checkinForm.behaviorName"
            label="行为"
            readonly
            clickable
            @click="showBehaviorPicker = true"
            :rules="[{ required: true, message: '请选择行为' }]"
          />
          <van-field
            v-model="checkinForm.points"
            type="number"
            label="积分"
            placeholder="可调整积分"
          >
            <template #button>
              <van-button size="small" type="primary" @click="checkinForm.points = selectedBehavior?.points || 10">
                默认
              </van-button>
            </template>
          </van-field>
          <van-field name="record_type" label="类型">
            <template #input>
              <van-radio-group v-model="checkinForm.record_type" direction="horizontal">
                <van-radio name="good">好行为</van-radio>
                <van-radio name="bad">需改进</van-radio>
              </van-radio-group>
            </template>
          </van-field>
          <van-field
            v-model="checkinForm.note"
            label="备注"
            placeholder="可选备注"
            type="textarea"
            rows="2"
          />
          <div style="margin: 16px;">
            <van-button round block type="primary" native-type="submit" :loading="checkinLoading">
              打卡
            </van-button>
          </div>
        </van-form>
      </div>
    </van-popup>

    <!-- 孩子选择器 -->
    <van-popup v-model:show="showChildPicker" position="bottom" round>
      <van-picker
        title="选择孩子"
        :columns="childColumns"
        @confirm="onChildConfirm"
        @cancel="showChildPicker = false"
      />
    </van-popup>

    <!-- 行为选择器 -->
    <van-popup v-model:show="showBehaviorPicker" position="bottom" round>
      <van-picker
        title="选择行为"
        :columns="behaviorColumns"
        @confirm="onBehaviorConfirm"
        @cancel="showBehaviorPicker = false"
      />
    </van-popup>

    <!-- 日期筛选 -->
    <van-popup v-model:show="showDateFilter" position="bottom" round>
      <van-calendar
        type="range"
        title="选择日期范围"
        :min-date="minDate"
        :max-date="maxDate"
        @confirm="onDateConfirm"
        @cancel="showDateFilter = false"
      />
    </van-popup>
  </div>
</template>

<script setup>
import { ref, reactive, computed, onMounted } from 'vue'
import { showSuccessToast, showFailToast } from 'vant'
import { children as childrenApi, behaviors as behaviorsApi, records as recordsApi } from '../api'
import dayjs from 'dayjs'

const isMobile = ref(window.innerWidth < 768)
const children = ref([])
const behaviors = ref([])
const records = ref([])
const selectedChildId = ref(null)
const dateRange = ref([])
const showCheckinDialog = ref(false)
const showChildPicker = ref(false)
const showBehaviorPicker = ref(false)
const showDateFilter = ref(false)
const checkinLoading = ref(false)
const selectedBehavior = ref(null)

const checkinForm = reactive({
  childId: null,
  childName: '',
  behaviorId: null,
  behaviorName: '',
  points: 0,
  record_type: 'good',
  note: ''
})

const minDate = new Date(2024, 0, 1)
const maxDate = new Date()

const childOptions = computed(() =>
  children.value.map(c => ({ text: c.name, value: c.id }))
)

const childColumns = computed(() =>
  children.value.map(c => ({ text: c.name, value: c.id }))
)

const behaviorColumns = computed(() =>
  behaviors.value.map(b => ({ text: `${b.icon} ${b.name} (+${b.points})`, value: b.id, points: b.points }))
)

const dateRangeText = computed(() => {
  if (dateRange.value.length === 2) {
    return `${dayjs(dateRange.value[0]).format('MM-DD')} 至 ${dayjs(dateRange.value[1]).format('MM-DD')}`
  }
  return ''
})

const formatDate = (dateStr) => {
  return dayjs(dateStr).format('YYYY-MM-DD HH:mm')
}

const loadChildren = async () => {
  try {
    children.value = await childrenApi.list()
    if (children.value.length > 0) {
      selectedChildId.value = children.value[0].id
      checkinForm.childId = children.value[0].id
      checkinForm.childName = children.value[0].name
      loadRecords()
    }
  } catch (err) {
    showFailToast('加载孩子列表失败')
  }
}

const loadBehaviors = async () => {
  try {
    behaviors.value = await behaviorsApi.list()
  } catch (err) {
    showFailToast('加载行为列表失败')
  }
}

const loadRecords = async () => {
  if (!selectedChildId.value) return

  try {
    const params = {}
    if (dateRange.value.length === 2) {
      params.date_from = dayjs(dateRange.value[0]).format('YYYY-MM-DD')
      params.date_to = dayjs(dateRange.value[1]).format('YYYY-MM-DD')
    }
    records.value = await childrenApi.getRecords(selectedChildId.value, params)
  } catch (err) {
    showFailToast('加载记录失败')
  }
}

const showCheckinPopup = () => {
  checkinForm.behaviorId = null
  checkinForm.behaviorName = ''
  checkinForm.points = 0
  checkinForm.record_type = 'good'
  checkinForm.note = ''
  selectedBehavior.value = null
  showCheckinDialog.value = true
}

const onChildConfirm = ({ selectedOptions }) => {
  const option = selectedOptions[0]
  checkinForm.childId = option.value
  checkinForm.childName = option.text
  showChildPicker.value = false
}

const onBehaviorConfirm = ({ selectedOptions }) => {
  const option = selectedOptions[0]
  checkinForm.behaviorId = option.value
  checkinForm.behaviorName = option.text.replace(/\s*\(\+\d+\)/, '')
  checkinForm.points = option.points
  selectedBehavior.value = { id: option.value, points: option.points }
  showBehaviorPicker.value = false
}

const onDateConfirm = ({ selectedValues }) => {
  const [start, end] = selectedValues
  dateRange.value = [new Date(start), new Date(end)]
  showDateFilter.value = false
  loadRecords()
}

const handleCheckin = async () => {
  if (!checkinForm.childId || !checkinForm.behaviorId) {
    showFailToast('请选择孩子和行为')
    return
  }

  checkinLoading.value = true
  try {
    const points = checkinForm.points || selectedBehavior.value?.points || 10
    await recordsApi.create(checkinForm.childId, {
      behavior_id: checkinForm.behaviorId,
      points,
      note: checkinForm.note,
      record_type: checkinForm.record_type
    })
    showSuccessToast('打卡成功')
    showCheckinDialog.value = false
    loadRecords()
  } catch (err) {
    showFailToast(err.response?.data?.detail || '打卡失败')
  } finally {
    checkinLoading.value = false
  }
}

onMounted(() => {
  window.addEventListener('resize', () => {
    isMobile.value = window.innerWidth < 768
  })
  loadChildren()
  loadBehaviors()
})
</script>

<style scoped>
.popup-content {
  padding: 20px 16px;
}

.popup-content h3 {
  text-align: center;
  margin-bottom: 20px;
}
</style>