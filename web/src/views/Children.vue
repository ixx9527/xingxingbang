<template>
  <div class="children-page">
    <div class="page-header">
      <h2 class="page-title">孩子管理</h2>
      <van-button type="primary" size="small" icon="plus" @click="showAddPopup">添加孩子</van-button>
    </div>

    <!-- 孩子列表 -->
    <div v-if="isMobile">
      <van-cell-group inset>
        <van-swipe-cell v-for="child in children" :key="child.id">
          <van-cell
            :title="child.name"
            :value="`总积分: ${child.total_points}`"
            :label="`连续: ${child.streak_days}天 | ${getLevelName(child.total_points)}`"
            is-link
            @click="viewDetail(child)"
          >
            <template #icon>
              <van-icon name="user-o" size="20" style="margin-right: 8px;" />
            </template>
          </van-cell>
          <template #right>
            <van-button square type="danger" text="删除" @click="deleteChild(child)" />
          </template>
        </van-swipe-cell>
      </van-cell-group>
    </div>
    <table v-else class="desktop-table">
      <thead>
        <tr>
          <th>姓名</th>
          <th>生日</th>
          <th>性别</th>
          <th>总积分</th>
          <th>连续天数</th>
          <th>等级</th>
          <th>操作</th>
        </tr>
      </thead>
      <tbody>
        <tr v-for="child in children" :key="child.id">
          <td>{{ child.name }}</td>
          <td>{{ child.birth_date }}</td>
          <td>{{ child.gender === 'male' ? '男' : '女' }}</td>
          <td>{{ child.total_points }}</td>
          <td>{{ child.streak_days }}</td>
          <td>
            <span class="level-tag" :class="'level-' + getLevelIndex(child.total_points)">
              {{ getLevelName(child.total_points) }}
            </span>
          </td>
          <td>
            <van-button size="small" @click="viewDetail(child)">详情</van-button>
            <van-button size="small" type="danger" @click="deleteChild(child)">删除</van-button>
          </td>
        </tr>
      </tbody>
    </table>

    <!-- 添加孩子弹窗 -->
    <van-popup v-model:show="showAddDialog" position="bottom" :style="{ height: '60%' }" round>
      <div class="popup-content">
        <h3>添加孩子</h3>
        <van-form @submit="handleSubmit">
          <van-field
            v-model="form.name"
            label="姓名"
            placeholder="请输入孩子姓名"
            :rules="[{ required: true, message: '请输入姓名' }]"
          />
          <van-field
            v-model="form.birth_date"
            label="生日"
            placeholder="请选择生日"
            readonly
            clickable
            @click="showDatePicker = true"
            :rules="[{ required: true, message: '请选择生日' }]"
          />
          <van-field name="gender" label="性别">
            <template #input>
              <van-radio-group v-model="form.gender" direction="horizontal">
                <van-radio name="male">男</van-radio>
                <van-radio name="female">女</van-radio>
              </van-radio-group>
            </template>
          </van-field>
          <van-field
            v-model="form.avatar"
            label="头像"
            placeholder="头像URL（可选）"
          />
          <div style="margin: 16px;">
            <van-button round block type="primary" native-type="submit" :loading="loading">
              确定
            </van-button>
          </div>
        </van-form>
      </div>
    </van-popup>

    <!-- 生日选择器 -->
    <van-popup v-model:show="showDatePicker" position="bottom" round>
      <van-date-picker
        v-model="selectedDate"
        title="选择生日"
        :min-date="minDate"
        :max-date="maxDate"
        @confirm="onDateConfirm"
        @cancel="showDatePicker = false"
      />
    </van-popup>

    <!-- 详情弹窗 -->
    <van-popup v-model:show="showDetailDialog" position="bottom" :style="{ height: '50%' }" round>
      <div class="popup-content" v-if="selectedChild">
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
import { ref, reactive, onMounted } from 'vue'
import { showSuccessToast, showFailToast, showConfirmDialog } from 'vant'
import { children as childrenApi } from '../api'

const isMobile = ref(window.innerWidth < 768)
const children = ref([])
const showAddDialog = ref(false)
const showDetailDialog = ref(false)
const showDatePicker = ref(false)
const selectedChild = ref(null)
const loading = ref(false)

const selectedDate = ref([
  new Date().getFullYear().toString(),
  (new Date().getMonth() + 1).toString(),
  new Date().getDate().toString()
])

const minDate = new Date(2010, 0, 1)
const maxDate = new Date()

const form = reactive({
  name: '',
  birth_date: '',
  gender: 'male',
  avatar: ''
})

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

const loadChildren = async () => {
  try {
    children.value = await childrenApi.list()
  } catch (err) {
    showFailToast('加载失败')
  }
}

const showAddPopup = () => {
  form.name = ''
  form.birth_date = ''
  form.gender = 'male'
  form.avatar = ''
  showAddDialog.value = true
}

const onDateConfirm = ({ selectedValues }) => {
  form.birth_date = `${selectedValues[0]}-${selectedValues[1]}-${selectedValues[2]}`
  showDatePicker.value = false
}

const handleSubmit = async () => {
  loading.value = true
  try {
    await childrenApi.create(form)
    showSuccessToast('添加成功')
    showAddDialog.value = false
    loadChildren()
  } catch (err) {
    showFailToast(err.response?.data?.detail || '添加失败')
  } finally {
    loading.value = false
  }
}

const viewDetail = async (child) => {
  try {
    selectedChild.value = await childrenApi.get(child.id)
    showDetailDialog.value = true
  } catch (err) {
    showFailToast('加载详情失败')
  }
}

const deleteChild = async (child) => {
  try {
    await showConfirmDialog({
      title: '提示',
      message: `确定要删除 ${child.name} 吗？`
    })
    // TODO: 调用删除 API
    showSuccessToast('删除成功')
    loadChildren()
  } catch {
    // 用户取消
  }
}

onMounted(() => {
  window.addEventListener('resize', () => {
    isMobile.value = window.innerWidth < 768
  })
  loadChildren()
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