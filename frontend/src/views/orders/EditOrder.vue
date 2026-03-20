<script setup lang="ts">
import { ref, reactive, onMounted } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { ElMessage } from 'element-plus'
import { getOrder, updateOrder, createValve, updateValve, type Valve } from '@/api/orders'

const route = useRoute()
const router = useRouter()
const orderId = Number(route.params.id)

const loading = ref(false)
const currentOrderId = ref<number>(orderId)

// 表单数据
const formData = reactive({
  poNo: '',
  receiveDate: '',
  finishDate: '',
  repairStatus: 'not_started',
  customerName: '',
  contactPhone: '',
  email: '',
  address: '',
  remark: '',
})

// 阀门清单（前端使用的类型，与后端字段命名不同）
interface ValveForm {
  id?: number
  customerSn: string
  abnSn: string
  partNo: string
  description: string
  modelNo: string
  faultDescription: string
  currentStep: string
  serviceCategory: string
}

const valveList = ref<ValveForm[]>([])

// 加载订单数据
const loadOrderData = async () => {
  loading.value = true
  try {
    const data = await getOrder(orderId)

    // 填充表单数据
    formData.poNo = data.po_no || ''
    formData.receiveDate = data.receive_date || ''
    formData.finishDate = data.finish_date || ''
    formData.repairStatus = data.repair_status || 'not_started'
    formData.customerName = data.customer_name || ''
    formData.contactPhone = data.contact_phone || ''
    formData.email = data.email || ''
    formData.address = data.address || ''
    formData.remark = data.remark || ''

    // 填充阀门数据
    valveList.value = (data.valves || []).map((v: any) => ({
      id: v.id,
      customerSn: v.customer_sn || '',
      abnSn: v.abn_sn || '',
      partNo: v.part_no || '',
      description: v.description || '',
      modelNo: v.model_no || '',
      faultDescription: v.fault_description || '',
      currentStep: v.current_step || '',
      serviceCategory: v.service_category || 'NormalRepair',
    }))
    
    // 如果没有阀门，添加一个空的
    if (valveList.value.length === 0) {
      addValve()
    }
  } catch (error) {
    console.error('加载订单失败:', error)
    ElMessage.error('加载订单失败')
  } finally {
    loading.value = false
  }
}

// 添加阀门
const addValve = () => {
  valveList.value.push({
    customerSn: '',
    abnSn: '',
    partNo: '',
    description: '',
    modelNo: '',
    faultDescription: '',
    currentStep: '',
    serviceCategory: 'NormalRepair',
  })
}

// 删除阀门
const removeValve = (index: number) => {
  if (valveList.value.length === 1) {
    ElMessage.warning('至少保留一个阀门信息')
    return
  }
  valveList.value.splice(index, 1)
}

// 提交/更新阀门
const submitValve = async (valve: ValveForm, index: number) => {
  try {
    const valveData = {
      customer_sn: valve.customerSn,
      abn_sn: valve.abnSn,
      part_no: valve.partNo,
      description: valve.description,
      model_no: valve.modelNo,
      fault_description: valve.faultDescription,
      current_step: valve.currentStep,
      service_category: valve.serviceCategory,
    }
    
    if (valve.id) {
      await updateValve(currentOrderId.value, valve.id, valveData)
      ElMessage.success('阀门更新成功')
    } else {
      const res = await createValve(currentOrderId.value, valveData)
      valve.id = res.id
      ElMessage.success('阀门添加成功')
    }
  } catch (error) {
    console.error('阀门操作失败:', error)
  }
}

// 格式化日期
const formatDate = (date: string) => {
  if (!date) return null
  const d = new Date(date)
  return `${d.getFullYear()}-${String(d.getMonth() + 1).padStart(2, '0')}-${String(d.getDate()).padStart(2, '0')}`
}

// 保存订单
const handleSave = async () => {
  // 表单验证
  if (!formData.poNo) {
    ElMessage.warning('请输入订单号')
    return
  }
  if (!formData.receiveDate) {
    ElMessage.warning('请选择收货日期')
    return
  }
  if (!formData.customerName) {
    ElMessage.warning('请输入客户姓名')
    return
  }
  if (!formData.contactPhone) {
    ElMessage.warning('请输入联系电话')
    return
  }
  
  try {
    const data = {
      po_no: formData.poNo,
      receive_date: formatDate(formData.receiveDate),
      finish_date: formatDate(formData.finishDate),
      repair_status: formData.repairStatus,
      customer_name: formData.customerName,
      contact_phone: formData.contactPhone,
      email: formData.email,
      address: formData.address,
      remark: formData.remark,
    }
    
    await updateOrder(orderId, data)
    ElMessage.success('订单更新成功')
  } catch (error) {
    console.error('更新订单失败:', error)
    ElMessage.error('更新订单失败')
  }
}

// 返回
const handleBack = () => {
  router.push('/orders')
}

// 查看详情
const handleView = () => {
  router.push(`/orders/detail/${orderId}`)
}

onMounted(() => {
  loadOrderData()
})
</script>

<template>
  <div class="edit-order" v-loading="loading">
    <div class="page-header">
      <h2 class="page-title">编辑订单</h2>
      <div class="header-actions">
        <el-button @click="handleBack">返回</el-button>
        <el-button @click="handleView">查看详情</el-button>
        <el-button type="primary" @click="handleSave">保存</el-button>
      </div>
    </div>

    <!-- 订单基本信息 -->
    <el-card class="form-card">
      <template #header>
        <span class="card-title">订单基本信息</span>
      </template>
      
      <el-form :model="formData" label-position="top" class="order-form">
        <el-row :gutter="20">
          <el-col :span="8">
            <el-form-item label="PO No.(订单号)" required>
              <el-input v-model="formData.poNo" placeholder="请输入订单编号" />
            </el-form-item>
          </el-col>
          <el-col :span="8">
            <el-form-item label="Receive Date(收货日期)" required>
              <el-date-picker
                v-model="formData.receiveDate"
                type="date"
                placeholder="Select date"
                style="width: 100%"
              />
            </el-form-item>
          </el-col>
          <el-col :span="8">
            <el-form-item label="Finish Date(完成日期)">
              <el-date-picker
                v-model="formData.finishDate"
                type="date"
                placeholder="Select date"
                style="width: 100%"
              />
            </el-form-item>
          </el-col>
        </el-row>
        
        <el-form-item label="维修状态">
          <el-radio-group v-model="formData.repairStatus">
            <el-radio label="not_started">未开始维修</el-radio>
            <el-radio label="in_progress">部分维修中</el-radio>
            <el-radio label="completed">全部完成</el-radio>
          </el-radio-group>
        </el-form-item>
      </el-form>
    </el-card>

    <!-- 客户基础信息 -->
    <el-card class="form-card">
      <template #header>
        <span class="card-title">客户基础信息</span>
      </template>
      
      <el-form :model="formData" label-position="top" class="order-form">
        <el-row :gutter="20">
          <el-col :span="8">
            <el-form-item label="客户姓名" required>
              <el-input v-model="formData.customerName" placeholder="请输入客户姓名" />
            </el-form-item>
          </el-col>
          <el-col :span="8">
            <el-form-item label="联系电话" required>
              <el-input v-model="formData.contactPhone" placeholder="请输入联系电话" />
            </el-form-item>
          </el-col>
          <el-col :span="8">
            <el-form-item label="电子邮箱">
              <el-input v-model="formData.email" placeholder="请输入电子邮箱" />
            </el-form-item>
          </el-col>
        </el-row>
        
        <el-form-item label="联系地址">
          <el-input v-model="formData.address" placeholder="请输入联系地址" />
        </el-form-item>
        
        <el-form-item label="备注信息">
          <el-input
            v-model="formData.remark"
            type="textarea"
            :rows="2"
            placeholder="请输入备注信息"
          />
        </el-form-item>
      </el-form>
    </el-card>

    <!-- 阀门清单信息 -->
    <el-card class="form-card">
      <template #header>
        <span class="card-title">阀门清单信息</span>
      </template>
      
      <div class="valve-list">
        <el-card
          v-for="(valve, index) in valveList"
          :key="index"
          class="valve-item"
          shadow="never"
        >
          <template #header>
            <span class="valve-title">Product Information(产品信息)</span>
          </template>
          
          <div class="valve-form">
            <div class="valve-row">
              <div class="valve-field">
                <label>Customer SN(客户序列号)</label>
                <el-input v-model="valve.customerSn" placeholder="请输入客户序列号" />
              </div>
              <div class="valve-field">
                <label>ABN SN(艾宝尼序列号)</label>
                <el-input v-model="valve.abnSn" placeholder="请输入序列号" />
              </div>
              <div class="valve-field">
                <label>Part No.(料号)</label>
                <el-input v-model="valve.partNo" placeholder="请输入料号" />
              </div>
              <div class="valve-field">
                <label>Description(产品描述)</label>
                <el-input v-model="valve.description" placeholder="请输入产品描述" />
              </div>
              <div class="valve-field">
                <label>Model No.(型号)</label>
                <el-input v-model="valve.modelNo" placeholder="请输入型号" />
              </div>
              <div class="valve-field">
                <label>故障描述</label>
                <el-input v-model="valve.faultDescription" placeholder="请输入故障描述" />
              </div>
              <div class="valve-field">
                <label>CurrentStep(当前维修进程)</label>
                <el-input v-model="valve.currentStep" placeholder="" />
              </div>
              <div class="valve-field service-category">
                <label>Service Category(服务类型)</label>
                <el-radio-group v-model="valve.serviceCategory" size="small">
                  <el-radio label="NormalRepair">NormalRepair</el-radio>
                  <el-radio label="Warranty">Warranty</el-radio>
                </el-radio-group>
              </div>
              <div class="valve-field valve-actions">
                <label>操作</label>
                <div class="action-btns">
                  <el-button 
                    type="primary" 
                    size="small" 
                    @click="submitValve(valve, index)"
                  >
                    <el-icon><Check /></el-icon>
                    {{ valve.id ? '更新' : '提交' }}
                  </el-button>
                  <el-button type="danger" size="small" @click="removeValve(index)">
                    <el-icon><Delete /></el-icon>
                    删除
                  </el-button>
                </div>
              </div>
            </div>
          </div>
        </el-card>
        
        <el-button type="primary" plain @click="addValve" class="add-btn">
          <el-icon><Plus /></el-icon>
          添加阀门
        </el-button>
      </div>
    </el-card>
  </div>
</template>

<style scoped>
.edit-order {
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

.form-card {
  margin-bottom: 20px;
}

.card-title {
  font-size: 16px;
  font-weight: bold;
  color: #303133;
}

.order-form :deep(.el-form-item__label) {
  font-weight: 500;
  color: #606266;
}

.add-btn {
  margin-top: 10px;
}

.valve-list {
  display: flex;
  flex-direction: column;
  gap: 15px;
}

.valve-item {
  background-color: #f5f7fa;
}

.valve-title {
  font-weight: 500;
  color: #303133;
}

.valve-form {
  width: 100%;
}

.valve-row {
  display: flex;
  gap: 10px;
  align-items: flex-end;
  flex-wrap: wrap;
}

.valve-field {
  flex: 1;
  min-width: 120px;
}

.valve-field label {
  display: block;
  font-size: 12px;
  color: #606266;
  margin-bottom: 5px;
  white-space: nowrap;
}

.service-category {
  min-width: 200px;
}

.valve-actions {
  flex: 0 0 auto;
}

.action-btns {
  display: flex;
  gap: 5px;
}
</style>
