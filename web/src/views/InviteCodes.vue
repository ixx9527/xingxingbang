<template>
  <div class="invite-codes-page">
    <div class="page-header">
      <h2 class="page-title">邀请码管理</h2>
      <van-button type="primary" size="small" icon="plus" @click="showCreatePopup">生成邀请码</van-button>
    </div>

    <!-- 邀请码列表 -->
    <div v-if="isMobile">
      <van-cell-group inset>
        <van-swipe-cell v-for="code in inviteCodes" :key="code.id">
          <van-cell
            :title="code.code"
            :label="`剩余: ${code.remaining_uses}/${code.max_uses === -1 ? '无限' : code.max_uses} | ${formatDate(code.expires_at)}`"
          >
            <template #icon>
              <van-icon name="lock" size="20" style="margin-right: 8px;" />
            </template>
            <template #value>
              <van-tag v-if="code.is_active" type="success">有效</van-tag>
              <van-tag v-else type="danger">无效</van-tag>
            </template>
            <template #extra>
              <van-button size="small" type="primary" plain @click="copyCode(code.code)">复制</van-button>
            </template>
          </van-cell>
          <template #right>
            <van-button square type="danger" text="删除" @click="deleteCode(code)" />
          </template>
        </van-swipe-cell>
      </van-cell-group>
    </div>
    <table v-else class="desktop-table">
      <thead>
        <tr>
          <th>邀请码</th>
          <th>已使用/总次数</th>
          <th>有效期</th>
          <th>备注</th>
          <th>状态</th>
          <th>操作</th>
        </tr>
      </thead>
      <tbody>
        <tr v-for="code in inviteCodes" :key="code.id">
          <td>
            <code style="background: #f7f8fa; padding: 4px 8px; border-radius: 4px; font-family: monospace;">
              {{ code.code }}
            </code>
            <van-button size="small" type="primary" plain style="margin-left: 8px;" @click="copyCode(code.code)">复制</van-button>
          </td>
          <td>{{ code.used_count }} / {{ code.max_uses === -1 ? '无限' : code.max_uses }}</td>
          <td>{{ formatDate(code.expires_at) }}</td>
          <td>{{ code.note || '-' }}</td>
          <td>
            <van-tag v-if="code.is_active" type="success">有效</van-tag>
            <van-tag v-else type="danger">无效</van-tag>
          </td>
          <td>
            <van-button size="small" type="danger" @click="deleteCode(code)">删除</van-button>
          </td>
        </tr>
      </tbody>
    </table>

    <!-- 生成邀请码弹窗 -->
    <van-popup v-model:show="showCreateDialog" position="bottom" :style="{ height: '50%' }" round>
      <div class="popup-content">
        <h3>生成邀请码</h3>
        <van-form @submit="handleCreate">
          <van-field
            v-model="createForm.max_uses"
            type="number"
            label="可用次数"
            placeholder="可使用次数（-1表示无限）"
            :rules="[{ required: true, message: '请输入次数' }]"
          />
          <van-field
            v-model="createForm.days_valid"
            type="number"
            label="有效天数"
            placeholder="有效天数"
            :rules="[{ required: true, message: '请输入天数' }]"
          />
          <van-field
            v-model="createForm.note"
            label="备注"
            placeholder="备注（可选）"
          />
          <div style="margin: 16px;">
            <van-button round block type="primary" native-type="submit" :loading="loading">
              生成
            </van-button>
          </div>
        </van-form>
      </div>
    </van-popup>
  </div>
</template>

<script setup>
import { ref, reactive, onMounted } from 'vue'
import { showSuccessToast, showFailToast, showConfirmDialog } from 'vant'
import { inviteCodes as inviteCodesApi } from '../api'
import dayjs from 'dayjs'

const isMobile = ref(window.innerWidth < 768)
const inviteCodes = ref([])
const showCreateDialog = ref(false)
const loading = ref(false)

const createForm = reactive({
  max_uses: 10,
  days_valid: 30,
  note: ''
})

const formatDate = (dateStr) => {
  if (!dateStr) return '永久'
  return dayjs(dateStr).format('YYYY-MM-DD')
}

const loadInviteCodes = async () => {
  try {
    inviteCodes.value = await inviteCodesApi.list()
  } catch (err) {
    showFailToast('加载失败')
  }
}

const showCreatePopup = () => {
  createForm.max_uses = 10
  createForm.days_valid = 30
  createForm.note = ''
  showCreateDialog.value = true
}

const handleCreate = async () => {
  loading.value = true
  try {
    await inviteCodesApi.create({
      max_uses: Number(createForm.max_uses),
      days_valid: Number(createForm.days_valid),
      note: createForm.note
    })
    showSuccessToast('生成成功')
    showCreateDialog.value = false
    loadInviteCodes()
  } catch (err) {
    showFailToast(err.response?.data?.detail || '生成失败')
  } finally {
    loading.value = false
  }
}

const copyCode = async (code) => {
  try {
    await navigator.clipboard.writeText(code)
    showSuccessToast('已复制')
  } catch {
    showFailToast('复制失败')
  }
}

const deleteCode = async (code) => {
  try {
    await showConfirmDialog({
      title: '提示',
      message: '确定要删除此邀请码吗？'
    })
    await inviteCodesApi.delete(code.id)
    showSuccessToast('删除成功')
    loadInviteCodes()
  } catch (err) {
    if (err !== 'cancel') {
      showFailToast(err.response?.data?.detail || '删除失败')
    }
  }
}

onMounted(() => {
  window.addEventListener('resize', () => {
    isMobile.value = window.innerWidth < 768
  })
  loadInviteCodes()
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