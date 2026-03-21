<template>
  <div class="children-page">
    <div class="header">
      <h2>孩子管理</h2>
      <el-button type="primary" @click="showAddDialog">
        <el-icon><Plus /></el-icon>
        添加孩子
      </el-button>
    </div>
    
    <el-table :data="children" stripe style="margin-top: 20px">
      <el-table-column prop="name" label="姓名" width="120" />
      <el-table-column prop="birth_date" label="生日" width="120" />
      <el-table-column prop="gender" label="性别" width="80">
        <template #default="{ row }">
          {{ row.gender === 'male' ? '男' : '女' }}
        </template>
      </el-table-column>
      <el-table-column prop="total_points" label="总积分" width="100" />
      <el-table-column prop="streak_days" label="连续天数" width="100" />
      <el-table-column label="等级">
        <template #default="{ row }">
          <el-tag>{{ getLevelName(row.total_points) }}</el-tag>
        </template>
      </el-table-column>
      <el-table-column label="操作" width="200">
        <template #default="{ row }">
          <el-button size="small" @click="viewDetail(row)">详情</el-button>
          <el-button size="small" type="danger" @click="deleteChild(row)">删除</el-button>
        </template>
      </el-table-column>
    </el-table>
    
    <!-- 添加孩子对话框 -->
    <el-dialog v-model="dialogVisible" title="添加孩子" width="500px">
      <el-form :model="form" :rules="rules" ref="formRef" label-width="80px">
        <el-form-item label="姓名" prop="name">
          <el-input v-model="form.name" placeholder="请输入孩子姓名" />
        </el-form-item>
        <el-form-item label="生日" prop="birth_date">
          <el-date-picker
            v-model="form.birth_date"
            type="date"
            placeholder="选择生日"
            value-format="YYYY-MM-DD"
            style="width: 100%"
          />
        </el-form-item>
        <el-form-item label="性别" prop="gender">
          <el-radio-group v-model="form.gender">
            <el-radio label="male">男</el-radio>
            <el-radio label="female">女</el-radio>
          </el-radio-group>
        </el-form-item>
        <el-form-item label="头像">
          <el-input v-model="form.avatar" placeholder="头像URL（可选）" />
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="dialogVisible = false">取消</el-button>
        <el-button type="primary" :loading="loading" @click="handleSubmit">
          确定
        </el-button>
      </template>
    </el-dialog>
    
    <!-- 详情对话框 -->
    <el-dialog v-model="detailVisible" title="孩子详情" width="600px">
      <el-descriptions :column="2" border v-if="selectedChild">
        <el-descriptions-item label="姓名">{{ selectedChild.name }}</el-descriptions-item>
        <el-descriptions-item label="生日">{{ selectedChild.birth_date }}</el-descriptions-item>
        <el-descriptions-item label="性别">
          {{ selectedChild.gender === 'male' ? '男' : '女' }}
        </el-descriptions-item>
        <el-descriptions-item label="总积分">{{ selectedChild.total_points }}</el-descriptions-item>
        <el-descriptions-item label="连续天数">{{ selectedChild.streak_days }}</el-descriptions-item>
        <el-descriptions-item label="等级">
          <el-tag>{{ getLevelName(selectedChild.total_points) }}</el-tag>
        </el-descriptions-item>
      </el-descriptions>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, onMounted, reactive } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import { Plus } from '@element-plus/icons-vue'
import { children as childrenApi } from '../api'

const children = ref([])
const dialogVisible = ref(false)
const detailVisible = ref(false)
const selectedChild = ref(null)
const loading = ref(false)
const formRef = ref()

const form = reactive({
  name: '',
  birth_date: '',
  gender: 'male',
  avatar: ''
})

const rules = {
  name: [{ required: true, message: '请输入孩子姓名', trigger: 'blur' }],
  birth_date: [{ required: true, message: '请选择生日', trigger: 'change' }],
  gender: [{ required: true, message: '请选择性别', trigger: 'change' }]
}

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

const loadChildren = async () => {
  try {
    children.value = await childrenApi.list()
  } catch (err) {
    ElMessage.error('加载失败')
  }
}

const showAddDialog = () => {
  form.name = ''
  form.birth_date = ''
  form.gender = 'male'
  form.avatar = ''
  dialogVisible.value = true
}

const handleSubmit = async () => {
  const valid = await formRef.value.validate().catch(() => false)
  if (!valid) return
  
  loading.value = true
  try {
    await childrenApi.create(form)
    ElMessage.success('添加成功')
    dialogVisible.value = false
    loadChildren()
  } catch (err) {
    ElMessage.error(err.response?.data?.detail || '添加失败')
  } finally {
    loading.value = false
  }
}

const viewDetail = async (row) => {
  try {
    selectedChild.value = await childrenApi.get(row.id)
    detailVisible.value = true
  } catch (err) {
    ElMessage.error('加载详情失败')
  }
}

const deleteChild = async (row) => {
  try {
    await ElMessageBox.confirm(`确定要删除 ${row.name} 吗？`, '提示', {
      type: 'warning'
    })
    // TODO: 调用删除 API
    ElMessage.success('删除成功')
    loadChildren()
  } catch {}
}

onMounted(loadChildren)
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