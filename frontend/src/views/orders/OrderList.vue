<script setup lang="ts">
import { ref, reactive, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { ElMessage, ElMessageBox } from 'element-plus'
import { getOrders, deleteOrder, type Order } from '@/api/orders'

const searchForm = reactive({
  searchType: 'po',
  poNumber: '',
  startDate: '',
  endDate: '',
})

const tableData = ref<Order[]>([])
const loading = ref(false)
const total = ref(0)
const currentPage = ref(1)
const pageSize = ref(10)

// 加载订单列表
const loadOrders = async () => {
  loading.value = true
  try {
    const params: any = {
      page: currentPage.value,
      per_page: pageSize.value
    }
    
    if (searchForm.searchType === 'po' && searchForm.poNumber) {
      params.search_type = 'po'
      params.keyword = searchForm.poNumber
    } else if (searchForm.searchType === 'time') {
      params.search_type = 'time'
      if (searchForm.startDate) params.start_date = searchForm.startDate
      if (searchForm.endDate) params.end_date = searchForm.endDate
    }
    
    const res = await getOrders(params)
    tableData.value = res.items || []
    total.value = res.total || 0
  } catch (error) {
    console.error('加载订单失败:', error)
  } finally {
    loading.value = false
  }
}

const handleSearch = () => {
  currentPage.value = 1
  loadOrders()
}

const handleReset = () => {
  searchForm.searchType = 'po'
  searchForm.poNumber = ''
  searchForm.startDate = ''
  searchForm.endDate = ''
  currentPage.value = 1
  loadOrders()
}

const handlePageChange = (page: number) => {
  currentPage.value = page
  loadOrders()
}

const handleSizeChange = (size: number) => {
  pageSize.value = size
  currentPage.value = 1
  loadOrders()
}

const router = useRouter()

const handleCreateOrder = () => {
  router.push('/orders/create')
}

const handleView = (id: number) => {
  router.push(`/orders/detail/${id}`)
}

const handleEdit = (id: number) => {
  router.push(`/orders/edit/${id}`)
}

// 删除订单
const handleDelete = async (id: number) => {
  try {
    // 显示确认对话框
    await ElMessageBox.confirm(
      '确定要删除该订单吗？删除后将无法恢复！',
      '删除确认',
      {
        confirmButtonText: '确定删除',
        cancelButtonText: '取消',
        type: 'warning',
        confirmButtonClass: 'el-button--danger'
      }
    )
    
    // 调用删除API
    await deleteOrder(id)
    ElMessage.success('订单删除成功')
    
    // 刷新列表
    loadOrders()
  } catch (error: any) {
    // 用户取消删除
    if (error === 'cancel' || error?.message === 'cancel') {
      return
    }
    console.error('删除订单失败:', error)
    ElMessage.error('删除订单失败，请重试')
  }
}

onMounted(() => {
  loadOrders()
})
</script>

<template>
  <div class="order-list">
    <el-card class="page-card">
      <template #header>
        <div class="card-header">
          <span class="title">客户订单管理</span>
          <el-button type="primary" @click="handleCreateOrder">
            <el-icon><Plus /></el-icon>
            新建订单
          </el-button>
        </div>
      </template>

      <!-- 搜索区域 -->
      <div class="search-section">
        <el-radio-group v-model="searchForm.searchType" class="search-type">
          <el-radio-button label="po">按PO查询</el-radio-button>
          <el-radio-button label="time">按时间查询</el-radio-button>
        </el-radio-group>

        <div class="search-inputs">
          <template v-if="searchForm.searchType === 'po'">
            <el-input
              v-model="searchForm.poNumber"
              placeholder="请输入PO号"
              clearable
              style="width: 200px"
            />
          </template>
          <template v-else>
            <el-date-picker
              v-model="searchForm.startDate"
              type="date"
              placeholder="开始日期"
              style="width: 150px"
            />
            <span class="date-separator">至</span>
            <el-date-picker
              v-model="searchForm.endDate"
              type="date"
              placeholder="结束日期"
              style="width: 150px"
            />
          </template>

          <el-button type="primary" @click="handleSearch">
            <el-icon><Search /></el-icon>
            查询
          </el-button>
          <el-button @click="handleReset">
            <el-icon><RefreshRight /></el-icon>
            重置
          </el-button>
        </div>
      </div>

      <!-- 数据表格 -->
      <el-table
        :data="tableData"
        v-loading="loading"
        stripe
        border
        style="width: 100%; margin-top: 20px"
        empty-text="No data"
      >
        <el-table-column prop="po_no" label="PO No.(订单号)" min-width="120" />
        <el-table-column prop="customer_name" label="Customer(客户)" min-width="120" />
        <el-table-column prop="contact_phone" label="联系方式" min-width="120" />
        <el-table-column prop="receive_date" label="Receive Date(收货时间)" min-width="150" />
        <el-table-column prop="repair_status" label="维修状态" min-width="100">
          <template #default="{ row }">
            <el-tag :type="row.repair_status === 'completed' ? 'success' : 'warning'">
              {{ row.repair_status === 'completed' ? '已完成' : row.repair_status === 'in_progress' ? '维修中' : '未开始' }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="finish_date" label="Finish Date(完成时间)" min-width="150" />
        <el-table-column prop="valve_count" label="阀门数量" min-width="100" />
        <el-table-column label="操作" fixed="right" min-width="200">
          <template #default="{ row }">
            <el-button link type="primary" size="small" @click="handleView(row.id)">查看</el-button>
            <el-button link type="primary" size="small" @click="handleEdit(row.id)">编辑</el-button>
            <el-button link type="danger" size="small" @click="handleDelete(row.id)">删除</el-button>
          </template>
        </el-table-column>
      </el-table>

      <!-- 空状态 -->
      <el-empty v-if="tableData.length === 0 && !loading" description="No data" />

      <!-- 分页 -->
      <el-pagination
        v-if="tableData.length > 0"
        class="pagination"
        background
        layout="total, sizes, prev, pager, next, jumper"
        :total="total"
        :page-sizes="[10, 20, 50, 100]"
        :page-size="pageSize"
        :current-page="currentPage"
        @current-change="handlePageChange"
        @size-change="handleSizeChange"
      />
    </el-card>
  </div>
</template>

<style scoped>
.order-list {
  height: 100%;
  width: 100%;
}

.page-card {
  min-height: 100%;
  display: flex;
  flex-direction: column;
}

.page-card :deep(.el-card__body) {
  flex: 1;
  display: flex;
  flex-direction: column;
}

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.title {
  font-size: 18px;
  font-weight: bold;
  color: #303133;
}

.search-section {
  display: flex;
  align-items: center;
  gap: 20px;
  padding: 20px;
  background-color: #f5f7fa;
  border-radius: 4px;
}

.search-type {
  flex-shrink: 0;
}

.search-inputs {
  display: flex;
  align-items: center;
  gap: 10px;
  flex-wrap: wrap;
}

.date-separator {
  color: #606266;
}

.pagination {
  margin-top: 20px;
  display: flex;
  justify-content: flex-end;
}
</style>
