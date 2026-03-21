<template>
  <div class="quality-control">
    <div class="page-header">
      <h2>质量控制</h2>
    </div>

    <el-tabs v-model="activeTab" class="quality-tabs">

      <!-- ========== 质量检查记录管理 ========== -->
      <el-tab-pane label="质量检查记录管理" name="inspection">
        <!-- 操作区域 -->
        <div class="toolbar">
          <el-button type="primary" @click="router.push('/quality-control/create')">
            <el-icon><Plus /></el-icon>新建质量检查记录
          </el-button>
        </div>

        <!-- 数据表格 -->
        <el-table :data="inspectionList" style="width: 100%;" class="data-table">
          <el-table-column prop="id" label="ID" width="80" />
          <el-table-column prop="plan_id" label="生产计划ID" min-width="140" />
          <el-table-column prop="product_code" label="产品代码" min-width="140" />
          <el-table-column prop="inspect_time" label="检查时间" min-width="160" />
          <el-table-column prop="result" label="检查结果" width="110">
            <template #default="{ row }">
              <el-tag :type="resultTagType(row.result)" size="small">
                {{ resultLabel(row.result) }}
              </el-tag>
            </template>
          </el-table-column>
          <el-table-column prop="created_at" label="创建时间" min-width="160" />
          <el-table-column label="操作" width="140" fixed="right">
            <template #default="{ row }">
              <el-button type="primary" link size="small" @click="handleEditInspection(row)">编辑</el-button>
              <el-button type="danger" link size="small" @click="handleDeleteInspection(row)">删除</el-button>
            </template>
          </el-table-column>
        </el-table>

        <!-- 分页 -->
        <div class="pagination-area">
          <el-pagination
            v-model:current-page="inspectionPage"
            v-model:page-size="inspectionPageSize"
            :total="inspectionTotal"
            :page-sizes="[10, 20, 50]"
            layout="total, sizes, prev, pager, next"
            background
          />
        </div>
      </el-tab-pane>

      <!-- ========== 维修质量管理 ========== -->
      <el-tab-pane label="维修计划管理" name="workorder">
        <!-- 操作区域 -->
        <div class="toolbar">
          <el-button type="primary" @click="handleNewWorkorder">
            <el-icon><Plus /></el-icon>新建维修工单
          </el-button>
          <el-select
            v-model="workorderStatusFilter"
            placeholder="状态筛选"
            clearable
            style="width: 140px; margin-left: 10px;"
            @change="handleWorkorderSearch"
          >
            <el-option label="待开始" value="pending" />
            <el-option label="进行中" value="in_progress" />
            <el-option label="已完成" value="completed" />
          </el-select>
        </div>

        <!-- 数据表格 -->
        <el-table :data="workorderList" style="width: 100%;" class="data-table">
          <el-table-column prop="id" label="ID" width="80" />
          <el-table-column prop="product_code" label="产品代码" min-width="140" />
          <el-table-column prop="product_name" label="产品名称" min-width="140" />
          <el-table-column prop="quantity" label="数量" width="90" />
          <el-table-column prop="plan_start" label="计划开始时间" min-width="160" />
          <el-table-column prop="plan_end" label="计划结束时间" min-width="160" />
          <el-table-column prop="status" label="状态" width="100">
            <template #default="{ row }">
              <el-tag :type="workorderTagType(row.status)" size="small">
                {{ workorderStatusLabel(row.status) }}
              </el-tag>
            </template>
          </el-table-column>
          <el-table-column prop="created_at" label="创建时间" min-width="160" />
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
            v-model:current-page="workorderPage"
            v-model:page-size="workorderPageSize"
            :total="workorderTotal"
            :page-sizes="[10, 20, 50]"
            layout="total, sizes, prev, pager, next"
            background
          />
        </div>
      </el-tab-pane>

    </el-tabs>

    <!-- 维修工单弹窗 -->
    <el-dialog
      v-model="workorderDialogVisible"
      :title="workorderDialogTitle"
      width="600px"
      class="dark-dialog"
    >
      <el-form
        ref="workorderFormRef"
        :model="workorderForm"
        :rules="workorderRules"
        label-position="top"
      >
        <el-row :gutter="20">
          <el-col :span="12">
            <el-form-item label="产品代码" prop="product_code">
              <el-input v-model="workorderForm.product_code" placeholder="请输入产品代码" />
            </el-form-item>
          </el-col>
          <el-col :span="12">
            <el-form-item label="产品名称" prop="product_name">
              <el-input v-model="workorderForm.product_name" placeholder="请输入产品名称" />
            </el-form-item>
          </el-col>
        </el-row>
        <el-row :gutter="20">
          <el-col :span="12">
            <el-form-item label="数量" prop="quantity">
              <el-input-number v-model="workorderForm.quantity" :min="1" style="width: 100%;" />
            </el-form-item>
          </el-col>
          <el-col :span="12">
            <el-form-item label="状态" prop="status">
              <el-select v-model="workorderForm.status" placeholder="请选择状态" style="width: 100%;">
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
                v-model="workorderForm.plan_start"
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
                v-model="workorderForm.plan_end"
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
                v-model="workorderForm.actual_start"
                type="date"
                placeholder="请选择实际开始时间"
                format="YYYY-MM-DD"
                value-format="YYYY-MM-DD"
                style="width: 100%;"
              />
            </el-form-item>
          </el-col>
          <el-col :span="12">
            <el-form-item label="实际结束时间">
              <el-date-picker
                v-model="workorderForm.actual_end"
                type="date"
                placeholder="请选择实际结束时间"
                format="YYYY-MM-DD"
                value-format="YYYY-MM-DD"
                style="width: 100%;"
              />
            </el-form-item>
          </el-col>
        </el-row>
      </el-form>
      <template #footer>
        <el-button @click="workorderDialogVisible = false">Cancel</el-button>
        <el-button type="primary" @click="handleSaveWorkorder">OK</el-button>
      </template>
    </el-dialog>

  </div>
</template>

<script setup lang="ts">
import { ref, reactive, onMounted, watch } from 'vue'
import { useRouter } from 'vue-router'
import { ElMessage, ElMessageBox } from 'element-plus'
import { Plus, Close, Delete } from '@element-plus/icons-vue'
import {
  getInspectionList, deleteInspection, updateInspection,
  getWorkorderList, createWorkorder, updateWorkorder, deleteWorkorder
} from '../../api/qualityControl'

// ========== 当前标签页 ==========
const activeTab = ref('inspection')
const router = useRouter()

// ========== 质量检查记录 ==========

const showInspectionForm = ref(false)
const inspectionFormTitle = ref('新建质量检查记录')
const inspectionFormRef = ref()
const inspectionPage = ref(1)
const inspectionPageSize = ref(10)
const inspectionTotal = ref(0)
const inspectionList = ref<any[]>([])
const inspectionKeyword = ref('')

const inspectionForm = reactive({
  id: null as number | null,
  plan_id: '',
  product_code: '',
  inspect_time: '',
  result: '',
  remark: '',
  defects: [] as Array<{ type: string; description: string; quantity: number }>
})

const inspectionRules = {
  plan_id: [{ required: true, message: '请输入生产计划ID', trigger: 'blur' }],
  product_code: [{ required: true, message: '请输入产品代码', trigger: 'blur' }],
  inspect_time: [{ required: true, message: '请选择检查时间', trigger: 'change' }],
  result: [{ required: true, message: '请选择检查结果', trigger: 'change' }]
}

const resultLabel = (result: string) => {
  const map: Record<string, string> = { pass: '合格', fail: '不合格', recheck: '待复检' }
  return map[result] || result
}

const resultTagType = (result: string) => {
  const map: Record<string, string> = { pass: 'success', fail: 'danger', recheck: 'warning' }
  return map[result] || 'info'
}

const toggleInspectionForm = () => {
  showInspectionForm.value = !showInspectionForm.value
  if (showInspectionForm.value) {
    inspectionFormTitle.value = '新建质量检查记录'
    handleResetInspectionForm()
  }
}

const addDefect = () => {
  inspectionForm.defects.push({ type: '', description: '', quantity: 1 })
}

const removeDefect = (index: number) => {
  inspectionForm.defects.splice(index, 1)
}

const handleResetInspectionForm = () => {
  inspectionForm.id = null
  inspectionForm.plan_id = ''
  inspectionForm.product_code = ''
  inspectionForm.inspect_time = ''
  inspectionForm.result = ''
  inspectionForm.remark = ''
  inspectionForm.defects = []
  inspectionFormRef.value?.clearValidate()
}

// 加载质量检查记录列表
const loadInspectionList = async () => {
  try {
    const data = await getInspectionList({
      keyword: inspectionKeyword.value,
      page: inspectionPage.value,
      per_page: inspectionPageSize.value
    }) as any
    inspectionList.value = data.items || []
    inspectionTotal.value = data.total || 0
  } catch {
    ElMessage.error('获取质量检查记录列表失败')
  }
}

const handleSaveInspection = async () => {
  if (!inspectionFormRef.value) return
  try {
    await inspectionFormRef.value.validate()
    if (inspectionForm.id) {
      await updateInspection(inspectionForm.id, inspectionForm)
      ElMessage.success('更新成功')
    }
    showInspectionForm.value = false
    await loadInspectionList()
  } catch {
    // 表单验证失败
  }
}

const handleEditInspection = (row: any) => {
  inspectionFormTitle.value = '编辑质量检查记录'
  Object.assign(inspectionForm, {
    id: row.id,
    plan_id: row.plan_id,
    product_code: row.product_code,
    inspect_time: row.inspect_time,
    result: row.result,
    remark: row.remark || '',
    defects: row.defects ? [...row.defects] : []
  })
  showInspectionForm.value = true
}

const handleDeleteInspection = (row: any) => {
  ElMessageBox.confirm('确认删除该质量检查记录？', '提示', {
    confirmButtonText: '确定',
    cancelButtonText: '取消',
    type: 'warning'
  }).then(async () => {
    await deleteInspection(row.id)
    ElMessage.success('删除成功')
    await loadInspectionList()
  }).catch(() => {})
}

// 分页变化
watch([inspectionPage, inspectionPageSize], () => {
  loadInspectionList()
})

// ========== 维修工单 ==========

const workorderPage = ref(1)
const workorderPageSize = ref(10)
const workorderTotal = ref(0)
const workorderList = ref<any[]>([])
const workorderStatusFilter = ref('')
const workorderDialogVisible = ref(false)
const workorderDialogTitle = ref('新建维修工单')
const workorderFormRef = ref()

const workorderForm = reactive({
  id: null as number | null,
  product_code: '',
  product_name: '',
  quantity: 1,
  plan_start: '',
  plan_end: '',
  actual_start: '',
  actual_end: '',
  status: ''
})

const workorderRules = {
  product_code: [{ required: true, message: '请输入产品代码', trigger: 'blur' }],
  product_name: [{ required: true, message: '请输入产品名称', trigger: 'blur' }],
  quantity: [{ required: true, message: '请输入数量', trigger: 'blur' }],
  plan_start: [{ required: true, message: '请选择计划开始时间', trigger: 'change' }],
  plan_end: [{ required: true, message: '请选择计划结束时间', trigger: 'change' }],
  status: [{ required: true, message: '请选择状态', trigger: 'change' }]
}

const workorderStatusLabel = (status: string) => {
  const map: Record<string, string> = { pending: '待开始', in_progress: '进行中', completed: '已完成' }
  return map[status] || status
}

const workorderTagType = (status: string) => {
  const map: Record<string, string> = { pending: 'info', in_progress: 'warning', completed: 'success' }
  return map[status] || 'info'
}

// 加载维修工单列表
const loadWorkorderList = async () => {
  try {
    const data = await getWorkorderList({
      status: workorderStatusFilter.value || 'all',
      page: workorderPage.value,
      per_page: workorderPageSize.value
    }) as any
    workorderList.value = data.items || []
    workorderTotal.value = data.total || 0
  } catch {
    ElMessage.error('获取维修工单列表失败')
  }
}

const handleWorkorderSearch = async () => {
  workorderPage.value = 1
  await loadWorkorderList()
}

const handleNewWorkorder = () => {
  workorderDialogTitle.value = '新建维修工单'
  Object.assign(workorderForm, {
    id: null, product_code: '', product_name: '',
    quantity: 1, plan_start: '', plan_end: '',
    actual_start: '', actual_end: '', status: ''
  })
  workorderDialogVisible.value = true
}

const handleEditWorkorder = (row: any) => {
  workorderDialogTitle.value = '编辑维修工单'
  Object.assign(workorderForm, { ...row })
  workorderDialogVisible.value = true
}

const handleSaveWorkorder = async () => {
  if (!workorderFormRef.value) return
  try {
    await workorderFormRef.value.validate()
    if (workorderForm.id) {
      await updateWorkorder(workorderForm.id, workorderForm)
      ElMessage.success('更新成功')
    } else {
      await createWorkorder({
        product_code: workorderForm.product_code,
        product_name: workorderForm.product_name,
        quantity: workorderForm.quantity,
        plan_start: workorderForm.plan_start,
        plan_end: workorderForm.plan_end,
        status: workorderForm.status,
        actual_start: workorderForm.actual_start || undefined,
        actual_end: workorderForm.actual_end || undefined
      })
      ElMessage.success('新增成功')
    }
    workorderDialogVisible.value = false
    await loadWorkorderList()
  } catch {
    // 表单验证失败
  }
}

const handleDeleteWorkorder = (row: any) => {
  ElMessageBox.confirm('确认删除该维修工单？', '提示', {
    confirmButtonText: '确定',
    cancelButtonText: '取消',
    type: 'warning'
  }).then(async () => {
    await deleteWorkorder(row.id)
    ElMessage.success('删除成功')
    await loadWorkorderList()
  }).catch(() => {})
}

// 分页变化
watch([workorderPage, workorderPageSize], () => {
  loadWorkorderList()
})

// ========== 初始化 ==========
onMounted(async () => {
  await loadInspectionList()
  await loadWorkorderList()
})
</script>

<style scoped lang="scss">
.quality-control {
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

.quality-tabs {
  :deep(.el-tabs__header) {
    background-color: #1b2838;
    margin-bottom: 0;
    padding: 0 10px;
    border-bottom: 1px solid #2d3d4f;
  }
  :deep(.el-tabs__item) {
    color: #a0b4c8;
    font-size: 14px;
    &.is-active { color: #409eff; }
    &:hover { color: #fff; }
  }
  :deep(.el-tabs__active-bar) { background-color: #409eff; }
  :deep(.el-tabs__content) {
    background-color: #1b2838;
    padding: 20px;
    border-radius: 0 0 4px 4px;
  }
}

.toolbar {
  display: flex;
  align-items: center;
  margin-bottom: 16px;
}

// 嵌入式表单
.add-form-section {
  margin-bottom: 20px;
  background-color: #0d1b2a;
  border-radius: 4px;
  border: 1px solid #2d3d4f;
  overflow: hidden;
}

.add-form-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 12px 20px;
  background-color: #243447;
  border-bottom: 1px solid #2d3d4f;
}

.add-form-title {
  font-size: 15px;
  font-weight: 500;
  color: #fff;
}

.inline-form {
  padding: 20px;

  :deep(.el-form-item__label) {
    color: #a0b4c8;
    font-size: 13px;
    padding-bottom: 4px;
  }
  :deep(.el-input__wrapper),
  :deep(.el-select .el-input__wrapper) {
    background-color: #1b2838;
    box-shadow: 0 0 0 1px #2d3d4f inset;
  }
  :deep(.el-input__inner) {
    color: #fff;
    &::placeholder { color: #4a5a6b; }
  }
  :deep(.el-date-editor .el-input__wrapper) {
    background-color: #1b2838;
    box-shadow: 0 0 0 1px #2d3d4f inset;
  }
  :deep(.el-input-number .el-input__wrapper) {
    background-color: #1b2838;
    box-shadow: 0 0 0 1px #2d3d4f inset;
  }
  :deep(.el-input-number__decrease),
  :deep(.el-input-number__increase) {
    background-color: #2d3d4f;
    border-color: #2d3d4f;
    color: #fff;
  }
}

// 缺陷列表
.defect-section {
  background-color: #243447;
  border-radius: 4px;
  padding: 16px;
  margin-bottom: 20px;
  border: 1px solid #2d3d4f;
}

.defect-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 14px;
}

.defect-title {
  font-size: 14px;
  font-weight: 500;
  color: #a0b4c8;
}

.defect-item {
  padding-bottom: 4px;
}

.add-form-actions {
  display: flex;
  gap: 10px;
  padding-top: 10px;
  border-top: 1px solid #2d3d4f;
}

// 数据表格
.data-table {
  :deep(.el-table__header-wrapper) {
    background-color: #0d1b2a;
  }
  :deep(th.el-table__cell) {
    background-color: #0d1b2a;
    color: #a0b4c8;
    border-bottom: 1px solid #2d3d4f;
  }
  :deep(td.el-table__cell) {
    background-color: #1b2838;
    color: #e0e8f0;
    border-bottom: 1px solid #2d3d4f;
  }
  :deep(tr:hover td.el-table__cell) {
    background-color: #243447;
  }
  :deep(.el-table__empty-block) {
    background-color: #1b2838;
  }
}

.pagination-area {
  display: flex;
  justify-content: flex-end;
  margin-top: 16px;
  :deep(.el-pagination) {
    color: #a0b4c8;
    .el-pagination__total,
    .el-pagination__sizes,
    .el-pagination__jump { color: #a0b4c8; }
    .btn-prev, .btn-next { background-color: #243447; color: #a0b4c8; }
    .el-pager li { background-color: #243447; color: #a0b4c8; }
    .el-pager li.is-active { color: #409eff; }
  }
}

// 维修工单弹窗
:deep(.dark-dialog) {
  .el-dialog {
    background-color: #1b2838;
    border: 1px solid #2d3d4f;
  }
  .el-dialog__header { border-bottom: 1px solid #2d3d4f; }
  .el-dialog__title { color: #fff; }
  .el-dialog__footer { border-top: 1px solid #2d3d4f; }
  .el-form-item__label { color: #a0b4c8; }
  .el-input__wrapper,
  .el-select .el-input__wrapper,
  .el-date-editor .el-input__wrapper {
    background-color: #0d1b2a;
    box-shadow: 0 0 0 1px #2d3d4f inset;
  }
  .el-input__inner { color: #fff; }
  .el-input-number .el-input__wrapper { background-color: #0d1b2a; }
  .el-input-number__decrease,
  .el-input-number__increase {
    background-color: #2d3d4f;
    border-color: #2d3d4f;
    color: #fff;
  }
}
</style>
