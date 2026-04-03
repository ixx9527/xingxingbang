<template>
  <div class="behaviors-page">
    <div class="header">
      <h2>行为管理</h2>
      <el-button type="primary" @click="showAddDialog">
        <el-icon><Plus /></el-icon>
        添加行为
      </el-button>
    </div>

    <el-tabs v-model="activeTab" style="margin-top: 20px">
      <el-tab-pane v-for="cat in categories" :key="cat.value" :label="cat.label" :name="cat.value">
        <el-table :data="filteredBehaviors" stripe>
          <el-table-column prop="icon" label="图标" width="80">
            <template #default="{ row }">
              <span style="font-size: 24px">{{ row.icon }}</span>
            </template>
          </el-table-column>
          <el-table-column prop="name" label="行为名称" />
          <el-table-column prop="points" label="积分" width="100">
            <template #default="{ row }">
              <span :style="{ color: row.points < 0 ? '#F56C6C' : '#67C23A' }">
                {{ row.points > 0 ? '+' + row.points : row.points }}
              </span>
            </template>
          </el-table-column>
          <el-table-column prop="category" label="分类" width="100" />
          <el-table-column label="来源" width="120">
            <template #default="{ row }">
              <el-tag v-if="row.is_system" type="info" size="small">系统预设</el-tag>
              <el-tag v-else-if="row.is_admin" type="warning" size="small">管理员预设</el-tag>
              <el-tag v-else type="success" size="small">我的</el-tag>
            </template>
          </el-table-column>
          <el-table-column prop="description" label="描述" />
          <el-table-column label="操作" width="150">
            <template #default="{ row }">
              <el-button
                size="small"
                :disabled="!canEdit(row)"
                @click="editBehavior(row)"
              >
                编辑
              </el-button>
              <el-button
                size="small"
                type="danger"
                :disabled="!canDelete(row)"
                @click="deleteBehavior(row)"
              >
                删除
              </el-button>
            </template>
          </el-table-column>
        </el-table>
      </el-tab-pane>
    </el-tabs>
    
    <!-- 添加/编辑对话框 -->
    <el-dialog v-model="dialogVisible" :title="isEdit ? '编辑行为' : '添加行为'" width="500px">
      <el-form :model="form" :rules="rules" ref="formRef" label-width="80px">
        <el-form-item label="名称" prop="name">
          <el-input v-model="form.name" placeholder="行为名称" />
        </el-form-item>
        <el-form-item label="类型" prop="pointsType">
          <el-radio-group v-model="form.pointsType">
            <el-radio value="add">加分</el-radio>
            <el-radio value="deduct">扣分</el-radio>
          </el-radio-group>
        </el-form-item>
        <el-form-item label="积分" prop="points">
          <el-input-number v-model="form.points" :min="1" :max="100" />
          <span style="margin-left: 10px; color: #909399">
            {{ form.pointsType === 'add' ? '加分项' : '扣分项，将扣除' }} {{ form.points }} 分
          </span>
        </el-form-item>
        <el-form-item label="分类" prop="category">
          <el-select v-model="form.category" placeholder="选择分类">
            <el-option v-for="cat in categories" :key="cat.value" :label="cat.label" :value="cat.value" />
          </el-select>
        </el-form-item>
        <el-form-item label="图标">
          <el-input v-model="form.icon" placeholder=" emoji 如 ⭐" />
        </el-form-item>
        <el-form-item label="描述">
          <el-input v-model="form.description" type="textarea" rows="3" />
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="dialogVisible = false">取消</el-button>
        <el-button type="primary" :loading="loading" @click="handleSubmit">
          确定
        </el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, computed, onMounted, reactive } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import { Plus } from '@element-plus/icons-vue'
import { behaviors as behaviorsApi } from '../api'

const behaviors = ref([])
const activeTab = ref('学习')
const dialogVisible = ref(false)
const isEdit = ref(false)
const loading = ref(false)
const formRef = ref()
const editingId = ref(null)

const categories = [
  { label: '学习', value: '学习' },
  { label: '生活', value: '生活' },
  { label: '运动', value: '运动' },
  { label: '其他', value: '其他' }
]

const form = reactive({
  name: '',
  points: 10,
  pointsType: 'add',
  category: '学习',
  icon: '',
  description: ''
})

const rules = {
  name: [{ required: true, message: '请输入名称', trigger: 'blur' }],
  points: [{ required: true, message: '请输入积分', trigger: 'blur' }],
  category: [{ required: true, message: '请选择分类', trigger: 'change' }]
}

// 判断当前用户是否是管理员
const isAdmin = computed(() => {
  const userStr = localStorage.getItem('user')
  if (!userStr) return false
  try {
    const user = JSON.parse(userStr)
    return user.username === 'admin'
  } catch {
    return false
  }
})

// 判断是否可以编辑
const canEdit = (row) => {
  if (row.is_system) return false  // 系统预设不能编辑
  if (row.is_admin) return isAdmin.value  // 管理员预设只有管理员能编辑
  return true  // 用户自己的行为可以编辑
}

// 判断是否可以删除
const canDelete = (row) => {
  if (row.is_system) return false  // 系统预设不能删除
  if (row.is_admin) return isAdmin.value  // 管理员预设只有管理员能删除
  return true  // 用户自己的行为可以删除
}

const filteredBehaviors = computed(() => {
  if (activeTab.value === 'all') return behaviors.value
  return behaviors.value.filter(b => b.category === activeTab.value)
})

const loadBehaviors = async () => {
  try {
    behaviors.value = await behaviorsApi.list()
  } catch (err) {
    ElMessage.error('加载失败')
  }
}

const showAddDialog = () => {
  isEdit.value = false
  editingId.value = null
  Object.assign(form, { name: '', points: 10, pointsType: 'add', category: '学习', icon: '', description: '' })
  dialogVisible.value = true
}

const editBehavior = (row) => {
  isEdit.value = true
  editingId.value = row.id
  Object.assign(form, {
    ...row,
    points: Math.abs(row.points),
    pointsType: row.points >= 0 ? 'add' : 'deduct'
  })
  dialogVisible.value = true
}

const handleSubmit = async () => {
  const valid = await formRef.value.validate().catch(() => false)
  if (!valid) return

  loading.value = true
  try {
    const submitData = {
      ...form,
      points: form.pointsType === 'deduct' ? -form.points : form.points
    }
    if (isEdit.value) {
      await behaviorsApi.update(editingId.value, submitData)
      ElMessage.success('更新成功')
    } else {
      await behaviorsApi.create(submitData)
      ElMessage.success('添加成功')
    }
    dialogVisible.value = false
    loadBehaviors()
  } catch (err) {
    ElMessage.error(err.response?.data?.detail || '操作失败')
  } finally {
    loading.value = false
  }
}

const deleteBehavior = async (row) => {
  try {
    await ElMessageBox.confirm(`确定要删除 ${row.name} 吗？`, '提示', { type: 'warning' })
    await behaviorsApi.delete(row.id)
    ElMessage.success('删除成功')
    loadBehaviors()
  } catch (err) {
    ElMessage.error(err.response?.data?.detail || '删除失败')
  }
}

onMounted(loadBehaviors)
</script>

<style scoped>
.header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.header h2 {
  margin: 0;
}
</style>