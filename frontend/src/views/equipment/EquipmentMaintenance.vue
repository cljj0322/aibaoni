<template>
  <div class="equipment-maintenance">
    <!-- 页面标题 -->
    <div class="page-header">
      <h2>设备维护记录管理</h2>
    </div>

    <!-- 主内容区 -->
    <div class="section-card">
      <div class="section-title-bar">设备维护记录列表</div>

      <!-- 工具栏 -->
      <div class="toolbar">
        <el-button type="primary" @click="handleNewRecord">
          <el-icon><Plus /></el-icon>新建设备维护记录
        </el-button>
        <el-select
          v-model="statusFilter"
          placeholder="状态筛选"
          clearable
          style="width: 140px; margin-left: 12px;"
          @change="handleSearch"
        >
          <el-option label="待维护" value="pending" />
          <el-option label="维护中" value="in_progress" />
          <el-option label="已完成" value="completed" />
        </el-select>
      </div>

      <!-- 数据表格 -->
      <el-table :data="recordList" style="width: 100%;" class="data-table" v-loading="loading">
        <el-table-column prop="id" label="ID" width="80" />
        <el-table-column prop="equipment_id" label="设备ID" min-width="120" />
        <el-table-column prop="equipment_name" label="设备名称" min-width="160" />
        <el-table-column prop="maintenance_type" label="维护类型" min-width="120" />
        <el-table-column prop="plan_time" label="计划时间" min-width="140" />
        <el-table-column prop="actual_time" label="实际时间" min-width="140">
          <template #default="{ row }">
            <span :class="{ 'text-muted': !row.actual_time }">
              {{ row.actual_time || '-' }}
            </span>
          </template>
        </el-table-column>
        <el-table-column prop="status" label="状态" width="100">
          <template #default="{ row }">
            <el-tag :type="statusTagType(row.status)" size="small">
              {{ statusLabel(row.status) }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="created_at" label="创建时间" min-width="160" />
        <el-table-column label="操作" width="140" fixed="right">
          <template #default="{ row }">
            <el-button type="primary" link size="small" @click="handleEditRecord(row)">编辑</el-button>
            <el-button type="danger" link size="small" @click="handleDeleteRecord(row)">删除</el-button>
          </template>
        </el-table-column>
      </el-table>

      <!-- 分页 -->
      <div class="pagination-area">
        <el-pagination
          v-model:current-page="currentPage"
          v-model:page-size="pageSize"
          :total="total"
          :page-sizes="[10, 20, 50]"
          layout="total, sizes, prev, pager, next"
          background
        />
      </div>
    </div>

    <!-- 新增/编辑弹窗 -->
    <el-dialog
      v-model="dialogVisible"
      :title="dialogTitle"
      width="600px"
      class="dark-dialog"
      destroy-on-close
    >
      <el-form
        ref="formRef"
        :model="form"
        :rules="rules"
        label-position="top"
      >
        <el-row :gutter="20">
          <el-col :span="12">
            <el-form-item label="设备ID" prop="equipment_id">
              <el-input v-model="form.equipment_id" placeholder="请输入设备ID" />
            </el-form-item>
          </el-col>
          <el-col :span="12">
            <el-form-item label="设备名称" prop="equipment_name">
              <el-input v-model="form.equipment_name" placeholder="请输入设备名称" />
            </el-form-item>
          </el-col>
        </el-row>
        <el-row :gutter="20">
          <el-col :span="12">
            <el-form-item label="维护类型" prop="maintenance_type">
              <el-input v-model="form.maintenance_type" placeholder="请输入维护类型" />
            </el-form-item>
          </el-col>
          <el-col :span="12">
            <el-form-item label="状态" prop="status">
              <el-select v-model="form.status" placeholder="请选择状态" style="width: 100%;">
                <el-option label="待维护" value="pending" />
                <el-option label="维护中" value="in_progress" />
                <el-option label="已完成" value="completed" />
              </el-select>
            </el-form-item>
          </el-col>
        </el-row>
        <el-row :gutter="20">
          <el-col :span="12">
            <el-form-item label="计划时间" prop="plan_time">
              <el-date-picker
                v-model="form.plan_time"
                type="datetime"
                placeholder="请选择计划时间"
                format="YYYY-MM-DD HH:mm"
                value-format="YYYY-MM-DD HH:mm"
                style="width: 100%;"
              />
            </el-form-item>
          </el-col>
          <el-col :span="12">
            <el-form-item label="实际时间">
              <el-date-picker
                v-model="form.actual_time"
                type="datetime"
                placeholder="请选择实际时间"
                format="YYYY-MM-DD HH:mm"
                value-format="YYYY-MM-DD HH:mm"
                style="width: 100%;"
                clearable
              />
            </el-form-item>
          </el-col>
        </el-row>
        <el-form-item label="备注">
          <el-input
            v-model="form.remark"
            type="textarea"
            :rows="3"
            placeholder="请输入备注信息"
          />
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="dialogVisible = false">取消</el-button>
        <el-button type="primary" @click="handleSaveRecord">确定</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup lang="ts">
import { ref, reactive, onMounted } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import { Plus } from '@element-plus/icons-vue'
import {
  getEquipmentMaintenanceList,
  createEquipmentMaintenance,
  updateEquipmentMaintenance,
  deleteEquipmentMaintenance
} from '../../api/equipment'

// ========== 搜索和分页 ==========
const statusFilter = ref('')
const currentPage = ref(1)
const pageSize = ref(10)
const total = ref(0)
const loading = ref(false)

// ========== 数据列表 ==========
interface MaintenanceRecord {
  id: number
  equipment_id: string
  equipment_name: string
  maintenance_type: string
  plan_time: string
  actual_time?: string
  status: 'pending' | 'in_progress' | 'completed'
  remark?: string
  created_at?: string
}

const recordList = ref<MaintenanceRecord[]>([])

// ========== 弹窗和表单 ==========
const dialogVisible = ref(false)
const dialogTitle = ref('新建设备维护记录')
const formRef = ref()
const isEdit = ref(false)
const currentId = ref<number | null>(null)

const form = reactive({
  equipment_id: '',
  equipment_name: '',
  maintenance_type: '',
  plan_time: '',
  actual_time: '',
  status: 'pending' as 'pending' | 'in_progress' | 'completed',
  remark: ''
})

const rules = {
  equipment_id: [{ required: true, message: '请输入设备ID', trigger: 'blur' }],
  equipment_name: [{ required: true, message: '请输入设备名称', trigger: 'blur' }],
  maintenance_type: [{ required: true, message: '请输入维护类型', trigger: 'blur' }],
  plan_time: [{ required: true, message: '请选择计划时间', trigger: 'change' }],
  status: [{ required: true, message: '请选择状态', trigger: 'change' }]
}

// ========== 状态映射 ==========
const statusLabel = (status: string) => {
  const map: Record<string, string> = {
    pending: '待维护',
    in_progress: '维护中',
    completed: '已完成'
  }
  return map[status] || status
}

const statusTagType = (status: string): any => {
  const map: Record<string, any> = {
    pending: 'info',
    in_progress: 'warning',
    completed: 'success'
  }
  return map[status] || 'info'
}

// ========== 方法 ==========
const loadData = async () => {
  loading.value = true
  try {
    const data = await getEquipmentMaintenanceList({
      status: statusFilter.value || 'all',
      page: currentPage.value,
      per_page: pageSize.value
    }) as any
    recordList.value = data.items || []
    total.value = data.total || 0
  } catch (error: any) {
    ElMessage.error(error.message || '获取设备维护记录失败')
  } finally {
    loading.value = false
  }
}

const handleSearch = () => {
  currentPage.value = 1
  loadData()
}

const handleNewRecord = () => {
  isEdit.value = false
  currentId.value = null
  dialogTitle.value = '新建设备维护记录'
  Object.assign(form, {
    equipment_id: '',
    equipment_name: '',
    maintenance_type: '',
    plan_time: '',
    actual_time: '',
    status: 'pending',
    remark: ''
  })
  dialogVisible.value = true
}

const handleEditRecord = (row: MaintenanceRecord) => {
  isEdit.value = true
  currentId.value = row.id
  dialogTitle.value = '编辑设备维护记录'
  Object.assign(form, {
    equipment_id: row.equipment_id,
    equipment_name: row.equipment_name,
    maintenance_type: row.maintenance_type,
    plan_time: row.plan_time,
    actual_time: row.actual_time || '',
    status: row.status,
    remark: row.remark || ''
  })
  dialogVisible.value = true
}

const handleSaveRecord = async () => {
  if (!formRef.value) return
  try {
    await formRef.value.validate()

    if (isEdit.value && currentId.value) {
      // 编辑
      await updateEquipmentMaintenance(currentId.value, {
        equipment_id: form.equipment_id,
        equipment_name: form.equipment_name,
        maintenance_type: form.maintenance_type,
        plan_time: form.plan_time,
        actual_time: form.actual_time || undefined,
        status: form.status,
        remark: form.remark
      })
      ElMessage.success('更新成功')
    } else {
      // 新增
      await createEquipmentMaintenance({
        equipment_id: form.equipment_id,
        equipment_name: form.equipment_name,
        maintenance_type: form.maintenance_type,
        plan_time: form.plan_time,
        actual_time: form.actual_time || undefined,
        status: form.status,
        remark: form.remark
      })
      ElMessage.success('新增成功')
    }

    dialogVisible.value = false
    loadData() // 重新加载数据
  } catch (error: any) {
    ElMessage.error(error.message || '保存失败')
  }
}

const handleDeleteRecord = async (row: MaintenanceRecord) => {
  try {
    await ElMessageBox.confirm('确认删除该设备维护记录？', '提示', {
      confirmButtonText: '确定',
      cancelButtonText: '取消',
      type: 'warning'
    })
    await deleteEquipmentMaintenance(row.id)
    ElMessage.success('删除成功')
    loadData() // 重新加载数据
  } catch (error: any) {
    if (error !== 'cancel') {
      ElMessage.error(error.message || '删除失败')
    }
  }
}

// ========== 初始化 ==========
onMounted(() => {
  loadData()
})
</script>

<style scoped lang="scss">
.equipment-maintenance {
  padding: 20px;
  background-color: #0d1b2a;
  min-height: 100vh;
  color: #fff;
}

.page-header {
  margin-bottom: 20px;
  h2 {
    margin: 0;
    font-size: 22px;
    color: #fff;
  }
}

.section-card {
  background-color: #1a1a1a;
  border: 1px solid #2d2d2d;
  border-radius: 6px;
  overflow: hidden;
}

.section-title-bar {
  padding: 16px 24px;
  font-size: 16px;
  font-weight: 500;
  color: #fff;
  border-bottom: 1px solid #2d2d2d;
  background-color: #1a1a1a;
}

.toolbar {
  display: flex;
  align-items: center;
  padding: 16px 24px;
  border-bottom: 1px solid #2d2d2d;
}

.data-table {
  :deep(.el-table__header-wrapper) {
    background-color: #111;
  }
  :deep(th.el-table__cell) {
    background-color: #1a1a1a;
    color: #a0a0a0;
    border-bottom: 1px solid #2d2d2d;
    font-weight: 500;
  }
  :deep(td.el-table__cell) {
    background-color: #1a1a1a;
    color: #e0e0e0;
    border-bottom: 1px solid #2d2d2d;
  }
  :deep(tr:hover td.el-table__cell) {
    background-color: #252525;
  }
  :deep(.el-table__empty-block) {
    background-color: #1a1a1a;
  }
}

.text-muted {
  color: #666;
}

.pagination-area {
  display: flex;
  justify-content: flex-end;
  padding: 16px 24px;
  border-top: 1px solid #2d2d2d;
  :deep(.el-pagination) {
    color: #a0a0a0;
    .el-pagination__total,
    .el-pagination__sizes,
    .el-pagination__jump { color: #a0a0a0; }
    .btn-prev, .btn-next { background-color: #2d2d2d; color: #a0a0a0; }
    .el-pager li { background-color: #2d2d2d; color: #a0a0a0; }
    .el-pager li.is-active { color: #409eff; }
  }
}

// 弹窗样式
:deep(.dark-dialog) {
  .el-dialog {
    background-color: #1a1a1a;
    border: 1px solid #2d2d2d;
  }
  .el-dialog__header {
    border-bottom: 1px solid #2d2d2d;
    padding: 16px 24px;
  }
  .el-dialog__title {
    color: #fff;
    font-size: 16px;
  }
  .el-dialog__body {
    padding: 20px 24px;
  }
  .el-dialog__footer {
    border-top: 1px solid #2d2d2d;
    padding: 16px 24px;
  }
  .el-form-item__label {
    color: #a0a0a0;
    font-size: 13px;
  }
  .el-input__wrapper,
  .el-select .el-input__wrapper,
  .el-date-editor .el-input__wrapper,
  .el-textarea__inner {
    background-color: #111;
    box-shadow: 0 0 0 1px #333 inset;
  }
  .el-input__inner,
  .el-textarea__inner {
    color: #fff;
    &::placeholder { color: #555; }
  }
  .el-textarea__inner {
    resize: none;
  }
}
</style>
