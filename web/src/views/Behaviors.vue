<template>
  <div class="behaviors-page">
    <div class="page-header">
      <h2 class="page-title">行为管理</h2>
      <div class="header-actions">
        <van-button v-if="isAdmin" type="warning" size="small" icon="replay" @click="resetBehaviors">重置预设</van-button>
        <van-button type="primary" size="small" icon="plus" @click="showAddPopup">添加行为</van-button>
      </div>
    </div>

    <!-- 分类标签 -->
    <van-tabs v-model:active="activeTab" sticky shrink @change="loadBehaviors">
      <van-tab v-for="cat in categories" :key="cat.value" :title="cat.label" :name="cat.value" />
    </van-tabs>

    <!-- 行为列表 -->
    <div v-if="isMobile" style="margin-top: 12px;">
      <van-cell-group inset>
        <van-swipe-cell v-for="behavior in filteredBehaviors" :key="behavior.id">
          <van-cell
            :title="`${behavior.icon} ${behavior.name}`"
            :value="`${behavior.points >= 0 ? '+' : ''}${behavior.points}`"
            :label="behavior.description || behavior.category"
          >
            <template #icon>
              <van-tag v-if="behavior.is_numeric" type="primary" size="medium" style="margin-right: 4px;">数值</van-tag>
              <van-tag v-if="behavior.is_admin" type="warning" size="medium" style="margin-right: 4px;">预设</van-tag>
              <van-tag v-else type="success" size="medium" style="margin-right: 4px;">我的</van-tag>
            </template>
            <template #extra>
              <van-icon v-if="canEdit(behavior)" name="edit" @click="editBehavior(behavior)" />
            </template>
          </van-cell>
          <template #right>
            <van-button v-if="canDelete(behavior)" square type="danger" text="删除" @click="deleteBehavior(behavior)" />
          </template>
        </van-swipe-cell>
      </van-cell-group>
    </div>
    <table v-else class="desktop-table" style="margin-top: 12px;">
      <thead>
        <tr>
          <th>图标</th>
          <th>行为名称</th>
          <th>积分</th>
          <th>类型</th>
          <th>分类</th>
          <th>来源</th>
          <th>描述</th>
          <th>操作</th>
        </tr>
      </thead>
      <tbody>
        <tr v-for="behavior in filteredBehaviors" :key="behavior.id">
          <td><span style="font-size: 24px;">{{ behavior.icon }}</span></td>
          <td>{{ behavior.name }}</td>
          <td :style="{ color: behavior.points < 0 ? '#ee0a24' : '#07c160' }">
            {{ behavior.points >= 0 ? '+' + behavior.points : behavior.points }}
          </td>
          <td>
            <van-tag v-if="behavior.is_numeric" type="primary" size="small">数值类</van-tag>
            <van-tag v-else type="default" size="small">普通</van-tag>
          </td>
          <td>{{ behavior.category }}</td>
          <td>
            <van-tag v-if="behavior.is_admin" type="warning" size="small">预设</van-tag>
            <van-tag v-else type="success" size="small">我的</van-tag>
          </td>
          <td>{{ behavior.description || '-' }}</td>
          <td>
            <van-button v-if="canEdit(behavior)" size="small" @click="editBehavior(behavior)">编辑</van-button>
            <van-button v-if="canDelete(behavior)" size="small" type="danger" @click="deleteBehavior(behavior)">删除</van-button>
          </td>
        </tr>
      </tbody>
    </table>

    <!-- 添加/编辑弹窗 -->
    <van-popup v-model:show="showAddDialog" position="bottom" :style="{ height: '80%' }" round>
      <div class="popup-content">
        <h3>{{ isEdit ? '编辑行为' : '添加行为' }}</h3>
        <van-form @submit="handleSubmit">
          <van-field
            v-model="form.name"
            label="名称"
            placeholder="行为名称"
            :rules="[{ required: true, message: '请输入名称' }]"
          />
          <van-field name="is_numeric" label="数值类">
            <template #input>
              <van-switch v-model="form.is_numeric" />
            </template>
            <template #extra>
              <span style="color: #969799; font-size: 12px;">
                {{ form.is_numeric ? '用户打卡时可输入实际数值' : '固定积分' }}
              </span>
            </template>
          </van-field>
          <van-field
            v-if="form.is_numeric"
            v-model="form.name_template"
            label="模板名称"
            placeholder="如：阅读{n}分钟"
          />
          <van-field
            v-if="form.is_numeric"
            v-model="form.default_n"
            type="number"
            label="默认数值"
            placeholder="对应积分的数值"
          />
          <van-field name="pointsType" label="类型">
            <template #input>
              <van-radio-group v-model="form.pointsType" direction="horizontal">
                <van-radio name="add">加分</van-radio>
                <van-radio name="deduct">扣分</van-radio>
              </van-radio-group>
            </template>
          </van-field>
          <van-field
            v-model="form.points"
            type="number"
            label="积分"
            placeholder="积分值"
            :rules="[{ required: true, message: '请输入积分' }]"
          >
            <template #extra>
              <span style="color: #969799;">
                {{ form.pointsType === 'add' ? '加分' : '扣分' }} {{ form.points }} 分
              </span>
            </template>
          </van-field>
          <van-field
            v-model="form.category"
            label="分类"
            readonly
            clickable
            @click="showCategoryPicker = true"
            :rules="[{ required: true, message: '请选择分类' }]"
          />
          <van-field
            v-model="form.icon"
            label="图标"
            placeholder="emoji 如 ⭐"
          />
          <van-field
            v-model="form.description"
            label="描述"
            type="textarea"
            rows="3"
            placeholder="行为描述（可选）"
          />
          <div style="margin: 16px;">
            <van-button round block type="primary" native-type="submit" :loading="loading">
              确定
            </van-button>
          </div>
        </van-form>
      </div>
    </van-popup>

    <!-- 分类选择器 -->
    <van-popup v-model:show="showCategoryPicker" position="bottom" round>
      <van-picker
        title="选择分类"
        :columns="categoryColumns"
        @confirm="onCategoryConfirm"
        @cancel="showCategoryPicker = false"
      />
    </van-popup>
  </div>
</template>

<script setup>
import { ref, reactive, computed, onMounted } from 'vue'
import { showSuccessToast, showFailToast, showConfirmDialog } from 'vant'
import { behaviors as behaviorsApi } from '../api'

const isMobile = ref(window.innerWidth < 768)
const behaviors = ref([])
const activeTab = ref('all')
const showAddDialog = ref(false)
const showCategoryPicker = ref(false)
const isEdit = ref(false)
const loading = ref(false)
const editingId = ref(null)

const categories = [
  { label: '全部', value: 'all' },
  { label: '学习', value: '学习' },
  { label: '生活', value: '生活' },
  { label: '运动', value: '运动' },
  { label: '其他', value: '其他' }
]

const categoryColumns = computed(() =>
  categories.filter(c => c.value !== 'all').map(c => ({ text: c.label, value: c.value }))
)

const form = reactive({
  name: '',
  points: 10,
  pointsType: 'add',
  category: '学习',
  icon: '',
  description: '',
  is_numeric: false,
  name_template: '',
  default_n: 1
})

const isAdmin = computed(() => {
  const username = localStorage.getItem('username')
  return username === 'admin'
})

const canEdit = (row) => {
  if (isAdmin.value) return true
  return !row.is_admin
}

const canDelete = (row) => {
  if (isAdmin.value) return true
  return !row.is_admin
}

const filteredBehaviors = computed(() => {
  if (activeTab.value === 'all') return behaviors.value
  return behaviors.value.filter(b => b.category === activeTab.value)
})

const loadBehaviors = async () => {
  try {
    behaviors.value = await behaviorsApi.list(activeTab.value === 'all' ? null : activeTab.value)
  } catch (err) {
    showFailToast('加载失败')
  }
}

const showAddPopup = () => {
  isEdit.value = false
  editingId.value = null
  Object.assign(form, {
    name: '',
    points: 10,
    pointsType: 'add',
    category: '学习',
    icon: '',
    description: '',
    is_numeric: false,
    name_template: '',
    default_n: 1
  })
  showAddDialog.value = true
}

const editBehavior = (row) => {
  isEdit.value = true
  editingId.value = row.id
  Object.assign(form, {
    name: row.name,
    points: Math.abs(row.points),
    pointsType: row.points >= 0 ? 'add' : 'deduct',
    category: row.category,
    icon: row.icon || '',
    description: row.description || '',
    is_numeric: row.is_numeric || false,
    name_template: row.name_template || '',
    default_n: row.default_n || 1
  })
  showAddDialog.value = true
}

const onCategoryConfirm = ({ selectedOptions }) => {
  form.category = selectedOptions[0].value
  showCategoryPicker.value = false
}

const handleSubmit = async () => {
  loading.value = true
  try {
    const submitData = {
      name: form.name,
      points: form.pointsType === 'deduct' ? -form.points : form.points,
      category: form.category,
      icon: form.icon,
      description: form.description,
      name_template: form.is_numeric ? form.name_template : null,
      default_n: form.is_numeric ? form.default_n : null
    }
    if (isEdit.value) {
      await behaviorsApi.update(editingId.value, submitData)
      showSuccessToast('更新成功')
    } else {
      await behaviorsApi.create(submitData)
      showSuccessToast('添加成功')
    }
    showAddDialog.value = false
    loadBehaviors()
  } catch (err) {
    showFailToast(err.response?.data?.detail || '操作失败')
  } finally {
    loading.value = false
  }
}

const deleteBehavior = async (row) => {
  try {
    await showConfirmDialog({
      title: '提示',
      message: `确定要删除 ${row.name} 吗？`
    })
    await behaviorsApi.delete(row.id)
    showSuccessToast('删除成功')
    loadBehaviors()
  } catch (err) {
    if (err !== 'cancel') {
      showFailToast(err.response?.data?.detail || '删除失败')
    }
  }
}

const resetBehaviors = async () => {
  try {
    await showConfirmDialog({
      title: '提示',
      message: '确定要重置预设行为吗？这将恢复所有默认行为，但不会影响您自定义的行为。'
    })
    const res = await behaviorsApi.reset()
    showSuccessToast(res.message)
    loadBehaviors()
  } catch (err) {
    if (err !== 'cancel') {
      showFailToast(err.response?.data?.detail || '重置失败')
    }
  }
}

onMounted(() => {
  window.addEventListener('resize', () => {
    isMobile.value = window.innerWidth < 768
  })
  loadBehaviors()
})
</script>

<style scoped>
.header-actions {
  display: flex;
  gap: 8px;
}

.popup-content {
  padding: 20px 16px;
}

.popup-content h3 {
  text-align: center;
  margin-bottom: 20px;
}
</style>