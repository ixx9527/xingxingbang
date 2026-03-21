<template>
  <div class="records-page">
    <div class="header">
      <h2>打卡记录</h2>
    </div>
    
    <el-card style="margin-top: 20px">
      <el-form inline>
        <el-form-item label="孩子">
          <el-select v-model="selectedChildId" placeholder="请选择孩子" @change="loadRecords">
            <el-option 
              v-for="child in children" 
              :key="child.id" 
              :label="child.name" 
              :value="child.id" 
            />
          </el-select>
        </el-form-item>
        <el-form-item label="日期">
          <el-date-picker
            v-model="dateRange"
            type="daterange"
            range-separator="至"
            start-placeholder="开始日期"
            end-placeholder="结束日期"
            @change="loadRecords"
          />
        </el-form-item>
        <el-form-item>
          <el-button type="primary" @click="showAddDialog">
            <el-icon><Plus /></el-icon>
            打卡
          </el-button>
        </el-form-item>
      </el-form>
      
      <el-table :data="records" stripe style="margin-top: 20px">
        <el-table-column prop="behavior_icon" label="图标" width="80">
          <template #default="{ row }">
            <span style="font-size: 24px">{{ row.behavior_icon }}</span>
          </template>
        </el-table-column>
        <el-table-column prop="behavior_name" label="行为" />
        <el-table-column prop="points" label="积分" width="80">
          <template #default="{ row }">
            <el-tag type="success">+{{ row.points }}</el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="note" label="备注" />
        <el-table-column prop="record_type" label="类型" width="80">
          <template #default="{ row }">
            <el-tag>{{ row.record_type === 'good' ? '好行为' : '需改进' }}</el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="created_at" label="时间" width="180" />
      </el-table>
    </el-card>
    
    <!-- 打卡对话框 -->
    <el-dialog v-model="dialogVisible" title="打卡" width="500px">
      <el-form :model="form" :rules="rules" ref="formRef" label-width="80px">
        <el-form-item label="孩子" prop="child_id">
          <el-select v-model="form.child_id" placeholder="选择孩子" style="width: 100%">
            <el-option v-for="child in children" :key="child.id" :label="child.name" :value="child.id" />
          </el-select>
        </el-form-item>
        <el-form-item label="行为" prop="behavior_id">
          <el-select v-model="form.behavior_id" placeholder="选择行为" style="width: 100%">
            <el-option 
              v-for="b in behaviors" 
              :key="b.id" 
              :label="`${b.icon} ${b.name} (+${b.points})`" 
              :value="b.id" 
            />
          </el-select>
        </el-form-item>
        <el-form-item label="积分">
          <el-input-number v-model="form.points" :min="0" :max="100" />
        </el-form-item>
        <el-form-item label="类型">
          <el-radio-group v-model="form.record_type">
            <el-radio label="good">好行为</el-radio>
            <el-radio label="bad">需改进</el-radio>
          </el-radio-group>
        </el-form-item>
        <el-form-item label="备注">
          <el-input v-model="form.note" type="textarea" rows="2" placeholder="可选备注" />
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="dialogVisible = false">取消</el-button>
        <el-button type="primary" :loading="loading" @click="handleSubmit">
          打卡
        </el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, onMounted, reactive } from 'vue'
import { ElMessage } from 'element-plus'
import { Plus } from '@element-plus/icons-vue'
import { children as childrenApi, behaviors as behaviorsApi, records as recordsApi } from '../api'

const children = ref([])
const behaviors = ref([])
const records = ref([])
const selectedChildId = ref(null)
const dateRange = ref([])
const dialogVisible = ref(false)
const loading = ref(false)
const formRef = ref()

const form = reactive({
  child_id: null,
  behavior_id: null,
  points: 0,
  record_type: 'good',
  note: ''
})

const rules = {
  child_id: [{ required: true, message: '请选择孩子', trigger: 'change' }],
  behavior_id: [{ required: true, message: '请选择行为', trigger: 'change' }]
}

const loadChildren = async () => {
  try {
    children.value = await childrenApi.list()
    if (children.value.length > 0) {
      selectedChildId.value = children.value[0].id
      loadRecords()
    }
  } catch (err) {
    ElMessage.error('加载孩子列表失败')
  }
}

const loadBehaviors = async () => {
  try {
    behaviors.value = await behaviorsApi.list()
  } catch (err) {
    ElMessage.error('加载行为列表失败')
  }
}

const loadRecords = async () => {
  if (!selectedChildId.value) return
  
  try {
    const params = {}
    if (dateRange.value && dateRange.value.length === 2) {
      params.date_from = dateRange.value[0].toISOString().split('T')[0]
      params.date_to = dateRange.value[1].toISOString().split('T')[0]
    }
    records.value = await childrenApi.getRecords(selectedChildId.value, params)
  } catch (err) {
    ElMessage.error('加载记录失败')
  }
}

const showAddDialog = () => {
  form.child_id = selectedChildId.value
  form.behavior_id = null
  form.points = 0
  form.record_type = 'good'
  form.note = ''
  dialogVisible.value = true
}

const handleSubmit = async () => {
  const valid = await formRef.value.validate().catch(() => false)
  if (!valid) return
  
  // 获取行为对应的积分
  const behavior = behaviors.value.find(b => b.id === form.behavior_id)
  const points = form.points || behavior?.points || 10
  
  loading.value = true
  try {
    await recordsApi.create(form.child_id, {
      behavior_id: form.behavior_id,
      points,
      note: form.note,
      record_type: form.record_type
    })
    ElMessage.success('打卡成功')
    dialogVisible.value = false
    loadRecords()
  } catch (err) {
    ElMessage.error(err.response?.data?.detail || '打卡失败')
  } finally {
    loading.value = false
  }
}

onMounted(() => {
  loadChildren()
  loadBehaviors()
})
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