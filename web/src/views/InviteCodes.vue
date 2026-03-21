<template>
  <div class="invite-codes-page">
    <div class="header">
      <h2>邀请码管理</h2>
      <el-button type="primary" @click="showAddDialog">
        <el-icon><Plus /></el-icon>
        生成邀请码
      </el-button>
    </div>
    
    <el-card style="margin-top: 20px">
      <el-table :data="codes" stripe>
        <el-table-column prop="code" label="邀请码" width="180">
          <template #default="{ row }">
            <code style="background: #f5f7fa; padding: 4px 8px; border-radius: 4px">
              {{ row.code }}
            </code>
            <el-button size="small" text @click="copyCode(row.code)">
              复制
            </el-button>
          </template>
        </el-table-column>
        <el-table-column label="已使用/总次数" width="120">
          <template #default="{ row }">
            {{ row.used_count }} / {{ row.max_uses === -1 ? '无限' : row.max_uses }}
          </template>
        </el-table-column>
        <el-table-column label="有效期" width="180">
          <template #default="{ row }">
            {{ row.expires_at ? row.expires_at.substring(0, 10) : '永久' }}
          </template>
        </el-table-column>
        <el-table-column prop="note" label="备注" />
        <el-table-column label="状态" width="80">
          <template #default="{ row }">
            <el-tag :type="row.is_active ? 'success' : 'info'">
              {{ row.is_active ? '有效' : '无效' }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column label="操作" width="100">
          <template #default="{ row }">
            <el-button size="small" type="danger" @click="deleteCode(row)">
              删除
            </el-button>
          </template>
        </el-table-column>
      </el-table>
    </el-card>
    
    <!-- 生成邀请码对话框 -->
    <el-dialog v-model="dialogVisible" title="生成邀请码" width="500px">
      <el-form :model="form" :rules="rules" ref="formRef" label-width="100px">
        <el-form-item label="可用次数" prop="max_uses">
          <el-input-number v-model="form.max_uses" :min="1" :max="100" />
          <span style="margin-left: 10px; color: #999">-1 表示无限次</span>
        </el-form-item>
        <el-form-item label="有效期" prop="days_valid">
          <el-input-number v-model="form.days_valid" :min="1" :max="365" />
          <span style="margin-left: 10px; color: #999">天</span>
        </el-form-item>
        <el-form-item label="备注">
          <el-input v-model="form.note" placeholder="可选备注" />
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="dialogVisible = false">取消</el-button>
        <el-button type="primary" :loading="loading" @click="handleSubmit">
          生成
        </el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, onMounted, reactive } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import { Plus } from '@element-plus/icons-vue'
import { inviteCodes as inviteCodesApi } from '../api'

const codes = ref([])
const dialogVisible = ref(false)
const loading = ref(false)
const formRef = ref()

const form = reactive({
  max_uses: 10,
  days_valid: 30,
  note: ''
})

const rules = {
  max_uses: [{ required: true, message: '请输入可用次数', trigger: 'blur' }],
  days_valid: [{ required: true, message: '请输入有效期', trigger: 'blur' }]
}

const loadCodes = async () => {
  try {
    codes.value = await inviteCodesApi.list()
  } catch (err) {
    ElMessage.error('加载失败')
  }
}

const showAddDialog = () => {
  form.max_uses = 10
  form.days_valid = 30
  form.note = ''
  dialogVisible.value = true
}

const handleSubmit = async () => {
  const valid = await formRef.value.validate().catch(() => false)
  if (!valid) return
  
  loading.value = true
  try {
    await inviteCodesApi.create(form)
    ElMessage.success('生成成功')
    dialogVisible.value = false
    loadCodes()
  } catch (err) {
    ElMessage.error(err.response?.data?.detail || '生成失败')
  } finally {
    loading.value = false
  }
}

const deleteCode = async (row) => {
  try {
    await ElMessageBox.confirm(`确定要删除这个邀请码吗？`, '提示', { type: 'warning' })
    await inviteCodesApi.delete(row.id)
    ElMessage.success('删除成功')
    loadCodes()
  } catch (err) {
    ElMessage.error(err.response?.data?.detail || '删除失败')
  }
}

const copyCode = (code) => {
  navigator.clipboard.writeText(code)
  ElMessage.success('已复制到剪贴板')
}

onMounted(loadCodes)
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