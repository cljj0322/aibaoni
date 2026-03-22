<template>
  <div class="repair-workorder">
    <!-- 页面标题 -->
    <div class="page-header">
      <h2>维修工单管理</h2>
    </div>

    <!-- 主内容区 -->
    <div class="section-card">
      <div class="section-title-bar">维修工单列表</div>

      <!-- 工具栏 -->
      <div class="toolbar">
        <el-button type="primary" @click="handleNewWorkorder">
          <el-icon><Plus /></el-icon>新建维修工单
        </el-button>
        <el-input
          v-model="searchKeyword"
          placeholder="搜索工单编号/产品名称"
          clearable
          style="width: 240px; margin-left: 12px;"
          @keyup.enter="handleSearch"
        />
        <el-select
          v-model="statusFilter"
          placeholder="状态筛选"
          clearable
          style="width: 140px; margin-left: 12px;"
          @change="handleSearch"
        >
          <el-option label="待开始" value="pending" />
          <el-option label="进行中" value="in_progress" />
          <el-option label="已完成" value="completed" />
        </el-select>
        <el-button style="margin-left: 12px;" @click="handleReset">重置</el-button>
      </div>

      <!-- 数据表格 -->
      <el-table :data="workorderList" style="width: 100%;" class="data-table" v-loading="loading">
        <el-table-column prop="id" label="工单编号" width="100" />
        <el-table-column prop="product_code" label="产品代码" min-width="140" />
        <el-table-column prop="product_name" label="产品名称" min-width="160" />
        <el-table-column prop="quantity" label="数量" width="80" />
        <el-table-column prop="plan_start" label="计划开始时间" min-width="140" />
        <el-table-column prop="plan_end" label="计划结束时间" min-width="140" />
        <el-table-column prop="actual_start" label="实际开始时间" min-width="140">
          <template #default="{ row }">
            <span :class="{ 'text-muted': !row.actual_start }">
              {{ row.actual_start || '-' }}
            </span>
          </template>
        </el-table-column>
        <el-table-column prop="actual_end" label="实际结束时间" min-width="140">
          <template #default="{ row }">
            <span :class="{ 'text-muted': !row.actual_end }">
              {{ row.actual_end || '-' }}
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
        <el-table-column label="操作" width="140" fixed="right">
          <template #default="{ row }">
            <el-button type="primary" link size="small" @click="handleEditWorkorder(row)">编辑</el-button>
            <el-button type="danger" link size="small" @click="handleDeleteWorkorder(row)">删除</el-button>
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
      width="650px"
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
            <el-form-item label="产品代码" prop="product_code">
              <el-input v-model="form.product_code" placeholder="请输入产品代码" />
            </el-form-item>
          </el-col>
          <el-col :span="12">
            <el-form-item label="产品名称" prop="product_name">
              <el-input v-model="form.product_name" placeholder="请输入产品名称" />
            </el-form-item>
          </el-col>
        </el-row>
        <el-row :gutter="20">
          <el-col :span="12">
            <el-form-item label="数量" prop="quantity">
              <el-input-number v-model="form.quantity" :min="1" style="width: 100%;" />
            </el-form-item>
          </el-col>
          <el-col :span="12">
            <el-form-item label="状态" prop="status">
              <el-select v-model="form.status" placeholder="请选择状态" style="width: 100%;">
                <el-option label="待开始" value="pending" />
                <el-option label="进行中" value="in_progress" />
                <el-option label="已完成" value="completed" />
              </el-select>
            </el-form-item>
          </el-col>
        </el-row>
        <el-row :gutter="20">
          <el-col :span="12">
            <el-form-item label="计划开始时间" prop="plan_start">
              <el-date-picker
                v-model="form.plan_start"
                type="date"
                placeholder="请选择计划开始时间"
                format="YYYY-MM-DD"
                value-format="YYYY-MM-DD"
                style="width: 100%;"
              />
            </el-form-item>
          </el-col>
          <el-col :span="12">
            <el-form-item label="计划结束时间" prop="plan_end">
              <el-date-picker
                v-model="form.plan_end"
                type="date"
                placeholder="请选择计划结束时间"
                format="YYYY-MM-DD"
                value-format="YYYY-MM-DD"
                style="width: 100%;"
              />
            </el-form-item>
          </el-col>
        </el-row>
        <el-row :gutter="20">
          <el-col :span="12">
            <el-form-item label="实际开始时间">
              <el-date-picker
                v-model="form.actual_start"
                type="date"
                placeholder="请选择实际开始时间"
                format="YYYY-MM-DD"
                value-format="YYYY-MM-DD"
                style="width: 100%;"
                clearable
              />
            </el-form-item>
          </el-col>
          <el-col :span="12">
            <el-form-item label="实际结束时间">
              <el-date-picker
                v-model="form.actual_end"
                type="date"
                placeholder="请选择实际结束时间"
                format="YYYY-MM-DD"
                value-format="YYYY-MM-DD"
                style="width: 100%;"
                clearable
              />
            </el-form-item>
          </el-col>
        </el-row>
      </el-form>
      <template #footer>
        <el-button @click="dialogVisible = false">取消</el-button>
        <el-button type="primary" @click="handleSaveWorkorder">确定</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup lang="ts">
import { ref, reactive, onMounted } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import { Plus } from '@element-plus/icons-vue'
import {
  getWorkorderList,
  createWorkorder,
  updateWorkorder,
  deleteWorkorder
} from '../../api/qualityControl'

// ========== 搜索和分页 ==========
const searchKeyword = ref('')
const statusFilter = ref('')
const currentPage = ref(1)
const pageSize = ref(10)
const total = ref(0)
const loading = ref(false)

// ========== 数据列表 ==========
interface Workorder {
  id: number
  product_code: string
  product_name: string
  quantity: number
  plan_start: string
  plan_end: string
  actual_start?: string
  actual_end?: string
  status: 'pending' | 'in_progress' | 'completed'
  created_at?: string
}

const workorderList = ref<Workorder[]>([])

// ========== 弹窗和表单 ==========
const dialogVisible = ref(false)
const dialogTitle = ref('新建维修工单')
const formRef = ref()
const isEdit = ref(false)
const currentId = ref<number | null>(null)

const form = reactive({
  product_code: '',
  product_name: '',
  quantity: 1,
  plan_start: '',
  plan_end: '',
  actual_start: '',
  actual_end: '',
  status: 'pending' as 'pending' | 'in_progress' | 'completed'
})

const rules = {
  product_code: [{ required: true, message: '请输入产品代码', trigger: 'blur' }],
  product_name: [{ required: true, message: '请输入产品名称', trigger: 'blur' }],
  quantity: [{ required: true, message: '请输入数量', trigger: 'blur' }],
  plan_start: [{ required: true, message: '请选择计划开始时间', trigger: 'change' }],
  plan_end: [{ required: true, message: '请选择计划结束时间', trigger: 'change' }],
  status: [{ required: true, message: '请选择状态', trigger: 'change' }]
}

// ========== 状态映射 ==========
const statusLabel = (status: string) => {
  const map: Record<string, string> = {
    pending: '待开始',
    in_progress: '进行中',
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
    const data = await getWorkorderList({
      keyword: searchKeyword.value,
      status: statusFilter.value || 'all',
      page: currentPage.value,
      per_page: pageSize.value
    }) as any
    workorderList.value = data.items || []
    total.value = data.total || 0
  } catch {
    ElMessage.error('获取维修工单列表失败')
  } finally {
    loading.value = false
  }
}

const handleSearch = () => {
  currentPage.value = 1
  loadData()
}

const handleReset = () => {
  searchKeyword.value = ''
  statusFilter.value = ''
  currentPage.value = 1
  loadData()
}

const handleNewWorkorder = () => {
  isEdit.value = false
  currentId.value = null
  dialogTitle.value = '新建维修工单'
  Object.assign(form, {
    product_code: '',
    product_name: '',
    quantity: 1,
    plan_start: '',
    plan_end: '',
    actual_start: '',
    actual_end: '',
    status: 'pending'
  })
  dialogVisible.value = true
}

const handleEditWorkorder = (row: Workorder) => {
  isEdit.value = true
  currentId.value = row.id
  dialogTitle.value = '编辑维修工单'
  Object.assign(form, {
    product_code: row.product_code,
    product_name: row.product_name,
    quantity: row.quantity,
    plan_start: row.plan_start,
    plan_end: row.plan_end,
    actual_start: row.actual_start || '',
    actual_end: row.actual_end || '',
    status: row.status
  })
  dialogVisible.value = true
}

const handleSaveWorkorder = async () => {
  if (!formRef.value) return
  try {
    await formRef.value.validate()
    
    if (isEdit.value && currentId.value) {
      // 编辑
      await updateWorkorder(currentId.value, {
        product_code: form.product_code,
        product_name: form.product_name,
        quantity: form.quantity,
        plan_start: form.plan_start,
        plan_end: form.plan_end,
        status: form.status,
        actual_start: form.actual_start || undefined,
        actual_end: form.actual_end || undefined
      })
      ElMessage.success('更新成功')
    } else {
      // 新增
      await createWorkorder({
        product_code: form.product_code,
        product_name: form.product_name,
        quantity: form.quantity,
        plan_start: form.plan_start,
        plan_end: form.plan_end,
        status: form.status,
        actual_start: form.actual_start || undefined,
        actual_end: form.actual_end || undefined
      })
      ElMessage.success('新增成功')
    }
    
    dialogVisible.value = false
    await loadData()
  } catch {
    // 表单验证失败或API错误
  }
}

const handleDeleteWorkorder = (row: Workorder) => {
  ElMessageBox.confirm('确认删除该维修工单？', '提示', {
    confirmButtonText: '确定',
    cancelButtonText: '取消',
    type: 'warning'
  }).then(async () => {
    await deleteWorkorder(row.id)
    ElMessage.success('删除成功')
    await loadData()
  }).catch(() => {})
}

// ========== 初始化 ==========
onMounted(() => {
  loadData()
})
</script>

<style scoped lang="scss">
.repair-workorder {
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
  .el-date-editor .el-input__wrapper {
    background-color: #111;
    box-shadow: 0 0 0 1px #333 inset;
  }
  .el-input__inner {
    color: #fff;
    &::placeholder { color: #555; }
  }
  .el-input-number .el-input__wrapper {
    background-color: #111;
  }
  .el-input-number__decrease,
  .el-input-number__increase {
    background-color: #2d2d2d;
    border-color: #333;
    color: #a0a0a0;
  }
}
</style>
