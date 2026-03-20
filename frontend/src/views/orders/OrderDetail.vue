<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { ElMessage } from 'element-plus'
import { getOrder } from '@/api/orders'

const route = useRoute()
const router = useRouter()
const orderId = Number(route.params.id)

const loading = ref(false)
const orderData = ref<any>({})

// 加载订单详情
const loadOrderDetail = async () => {
  loading.value = true
  try {
    const res = await getOrder(orderId)
    orderData.value = res
  } catch (error) {
    console.error('加载订单详情失败:', error)
    ElMessage.error('加载订单详情失败')
  } finally {
    loading.value = false
  }
}

// 返回列表
const handleBack = () => {
  router.push('/orders')
}

// 编辑订单
const handleEdit = () => {
  router.push(`/orders/edit/${orderId}`)
}

// 状态显示文本
const getStatusText = (status: string) => {
  const statusMap: Record<string, string> = {
    'not_started': '未开始',
    'in_progress': '维修中',
    'completed': '已完成'
  }
  return statusMap[status] || status
}

// 状态标签类型
const getStatusType = (status: string) => {
  const typeMap: Record<string, any> = {
    'not_started': 'info',
    'in_progress': 'warning',
    'completed': 'success'
  }
  return typeMap[status] || ''
}

// 维修方式显示
const getMethodText = (method: string) => {
  const methodMap: Record<string, string> = {
    'original_parts': '原装配件更换',
    'repair': '维修',
    'replace': '更换'
  }
  return methodMap[method] || method
}

// 费用类型显示
const getFeeTypeText = (type: string) => {
  const typeMap: Record<string, string> = {
    'parts': '配件费',
    'labor': '人工费',
    'shipping': '运输费',
    'other': '其他'
  }
  return typeMap[type] || type
}

onMounted(() => {
  loadOrderDetail()
})
</script>

<template>
  <div class="order-detail" v-loading="loading">
    <div class="page-header">
      <h2 class="page-title">订单详情</h2>
      <div class="header-actions">
        <el-button @click="handleBack">返回</el-button>
        <el-button type="primary" @click="handleEdit">编辑</el-button>
      </div>
    </div>

    <!-- 订单基本信息 -->
    <el-card class="detail-card">
      <template #header>
        <span class="card-title">订单基本信息</span>
      </template>
      <el-descriptions :column="3" border>
        <el-descriptions-item label="PO No.(订单号)">{{ orderData.po_no }}</el-descriptions-item>
        <el-descriptions-item label="Receive Date(收货日期)">{{ orderData.receive_date }}</el-descriptions-item>
        <el-descriptions-item label="Finish Date(完成日期)">{{ orderData.finish_date || '-' }}</el-descriptions-item>
        <el-descriptions-item label="维修状态">
          <el-tag :type="getStatusType(orderData.repair_status)">
            {{ getStatusText(orderData.repair_status) }}
          </el-tag>
        </el-descriptions-item>
      </el-descriptions>
    </el-card>

    <!-- 客户基础信息 -->
    <el-card class="detail-card">
      <template #header>
        <span class="card-title">客户基础信息</span>
      </template>
      <el-descriptions :column="3" border>
        <el-descriptions-item label="客户姓名">{{ orderData.customer_name }}</el-descriptions-item>
        <el-descriptions-item label="联系电话">{{ orderData.contact_phone }}</el-descriptions-item>
        <el-descriptions-item label="电子邮箱">{{ orderData.email || '-' }}</el-descriptions-item>
        <el-descriptions-item label="联系地址" :span="3">{{ orderData.address || '-' }}</el-descriptions-item>
        <el-descriptions-item label="备注信息" :span="3">{{ orderData.remark || '-' }}</el-descriptions-item>
      </el-descriptions>
    </el-card>

    <!-- 阀门清单信息 -->
    <el-card class="detail-card">
      <template #header>
        <span class="card-title">阀门清单信息 ({{ orderData.valves?.length || 0 }})</span>
      </template>
      <el-table :data="orderData.valves || []" border stripe>
        <el-table-column prop="customer_sn" label="Customer SN(客户序列号)" min-width="140" />
        <el-table-column prop="abn_sn" label="ABN SN(艾宝尼序列号)" min-width="140" />
        <el-table-column prop="part_no" label="Part No.(料号)" min-width="100" />
        <el-table-column prop="description" label="Description(产品描述)" min-width="150" />
        <el-table-column prop="model_no" label="Model No.(型号)" min-width="100" />
        <el-table-column prop="fault_description" label="故障描述" min-width="120" />
        <el-table-column prop="current_step" label="CurrentStep(当前维修进程)" min-width="150" />
        <el-table-column prop="service_category" label="Service Category(服务类型)" min-width="120" />
      </el-table>
    </el-card>

    <!-- 维修方案 -->
    <el-card class="detail-card">
      <template #header>
        <span class="card-title">维修方案 ({{ orderData.repair_plans?.length || 0 }})</span>
      </template>
      <el-table :data="orderData.repair_plans || []" border stripe>
        <el-table-column prop="project" label="维修项目" min-width="150" />
        <el-table-column prop="method" label="维修方式" min-width="120">
          <template #default="{ row }">
            {{ getMethodText(row.method) }}
          </template>
        </el-table-column>
        <el-table-column prop="duration" label="预计时长(天)" min-width="100" />
        <el-table-column prop="confirmed" label="客户确认" min-width="80">
          <template #default="{ row }">
            <el-tag :type="row.confirmed ? 'success' : 'info'">
              {{ row.confirmed ? '已确认' : '未确认' }}
            </el-tag>
          </template>
        </el-table-column>
      </el-table>
    </el-card>

    <!-- 费用明细 -->
    <el-card class="detail-card">
      <template #header>
        <span class="card-title">费用明细 ({{ orderData.fee_items?.length || 0 }})</span>
      </template>
      <el-table :data="orderData.fee_items || []" border stripe>
        <el-table-column prop="type" label="费用类型" min-width="100">
          <template #default="{ row }">
            {{ getFeeTypeText(row.type) }}
          </template>
        </el-table-column>
        <el-table-column prop="description" label="项目说明" min-width="150" />
        <el-table-column prop="price" label="单价" min-width="80" />
        <el-table-column prop="quantity" label="数量" min-width="80" />
        <el-table-column prop="amount" label="金额" min-width="80">
          <template #default="{ row }">
            {{ (row.price * row.quantity).toFixed(2) }}
          </template>
        </el-table-column>
        <el-table-column prop="warranty" label="保修(月)" min-width="80" />
      </el-table>
    </el-card>
  </div>
</template>

<style scoped>
.order-detail {
  height: 100%;
  overflow-y: auto;
  padding-right: 10px;
}

.page-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 20px;
}

.page-title {
  font-size: 20px;
  font-weight: bold;
  color: #303133;
  margin: 0;
}

.header-actions {
  display: flex;
  gap: 10px;
}

.detail-card {
  margin-bottom: 20px;
}

.card-title {
  font-size: 16px;
  font-weight: bold;
  color: #303133;
}
</style>
