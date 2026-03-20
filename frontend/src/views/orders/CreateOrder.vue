<script setup lang="ts">
import { ref, reactive, computed } from 'vue'
import { useRouter } from 'vue-router'
import { ElMessage } from 'element-plus'
import { createOrder, createValve, updateValve } from '@/api/orders'

const router = useRouter()

// 当前订单ID（创建后赋值）
const currentOrderId = ref<number | null>(null)

// 表单数据
const formData = reactive({
  // 订单基本信息
  poNo: '',
  receiveDate: '',
  finishDate: '',
  repairStatus: 'not_started',
  
  // 客户基础信息
  customerName: '',
  contactPhone: '',
  email: '',
  address: '',
  remark: '',
})

// 阀门清单
interface Valve {
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

const valveList = ref<Valve[]>([
  {
    customerSn: '',
    abnSn: '',
    partNo: '',
    description: '',
    modelNo: '',
    faultDescription: '',
    currentStep: '',
    serviceCategory: 'NormalRepair',
  }
])

// 维修方案
interface RepairPlan {
  project: string
  method: string
  duration: number
  confirmed: boolean
}

const repairPlans = ref<RepairPlan[]>([])

// 费用明细
interface FeeItem {
  type: string
  description: string
  price: number
  quantity: number
  warranty: number
}

const feeItems = ref<FeeItem[]>([])

// 计算金额
const calculateAmount = (item: FeeItem) => {
  return item.price * item.quantity
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
const submitValve = async (valve: Valve, index: number) => {
  if (!currentOrderId.value) {
    ElMessage.warning('请先保存订单基本信息')
    return
  }
  
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
      // 更新已有阀门
      await updateValve(currentOrderId.value, valve.id, valveData)
      ElMessage.success('阀门更新成功')
    } else {
      // 创建新阀门
      const res = await createValve(currentOrderId.value, valveData)
      valve.id = res.id  // 保存返回的ID
      ElMessage.success('阀门添加成功')
    }
  } catch (error) {
    console.error('阀门操作失败:', error)
  }
}

// 添加维修方案
const addRepairPlan = () => {
  repairPlans.value.push({
    project: '',
    method: 'original_parts',
    duration: 1,
    confirmed: false,
  })
}

// 删除维修方案
const removeRepairPlan = (index: number) => {
  repairPlans.value.splice(index, 1)
}

// 添加费用项目
const addFeeItem = () => {
  feeItems.value.push({
    type: 'parts',
    description: '',
    price: 0,
    quantity: 1,
    warranty: 3,
  })
}

// 删除费用项目
const removeFeeItem = (index: number) => {
  feeItems.value.splice(index, 1)
}

// 提交表单
const handleSubmit = async () => {
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
    // 格式化日期
    const formatDate = (date: string) => {
      if (!date) return null
      const d = new Date(date)
      return `${d.getFullYear()}-${String(d.getMonth() + 1).padStart(2, '0')}-${String(d.getDate()).padStart(2, '0')}`
    }
    
    // 构建订单数据（不包含阀门，阀门单独提交）
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
      valves: [],  // 空数组，阀门单独提交
      repair_plans: repairPlans.value.filter(p => p.project).map(p => ({
        project: p.project,
        method: p.method,
        duration: p.duration,
        confirmed: p.confirmed
      })),
      fee_items: feeItems.value.filter(f => f.description).map(f => ({
        type: f.type,
        description: f.description,
        price: f.price,
        quantity: f.quantity,
        warranty: f.warranty
      }))
    }
    
    console.log('提交数据:', data)
    const result = await createOrder(data)
    console.log('创建订单响应:', result)
    
    // 由于拦截器处理，直接返回 data 部分
    currentOrderId.value = (result as any).id  // 保存订单ID
    ElMessage.success('订单创建成功，现在可以提交阀门信息')
    // 不跳转，让用户继续添加阀门
  } catch (error: any) {
    console.error('创建订单失败:', error)
    ElMessage.error('创建订单失败，请检查数据')
  }
}

// 返回
const handleBack = () => {
  router.push('/orders')
}

// 完成创建
const handleFinish = () => {
  ElMessage.success('订单创建完成')
  router.push('/orders')
}
</script>

<template>
  <div class="create-order">
    <div class="page-header">
      <h2 class="page-title">新建订单</h2>
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
                    :disabled="!currentOrderId"
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

    <!-- 维修方案 -->
    <el-card class="form-card">
      <template #header>
        <span class="card-title">维修方案</span>
      </template>
      
      <div class="repair-plans">
        <el-button type="primary" plain @click="addRepairPlan" class="add-btn">
          <el-icon><Plus /></el-icon>
          添加维修项目
        </el-button>
        
        <el-card
          v-for="(plan, index) in repairPlans"
          :key="index"
          class="plan-item-card"
          shadow="never"
        >
          <div class="plan-form">
            <div class="plan-field">
              <label>维修项目</label>
              <el-input v-model="plan.project" placeholder="请输入维修项目" />
            </div>
            <div class="plan-field">
              <label>维修方式</label>
              <el-select v-model="plan.method" placeholder="请选择" style="width: 100%">
                <el-option label="原装配件更换" value="original_parts" />
                <el-option label="维修" value="repair" />
                <el-option label="更换" value="replace" />
              </el-select>
            </div>
            <div class="plan-field">
              <label>预计时长(天)</label>
              <el-input-number v-model="plan.duration" :min="1" :max="365" style="width: 100%" />
            </div>
            <div class="plan-field confirm-field">
              <label>客户确认</label>
              <el-checkbox v-model="plan.confirmed">同意</el-checkbox>
            </div>
            <div class="plan-field plan-actions">
              <label>&nbsp;</label>
              <el-button type="danger" link @click="removeRepairPlan(index)">
                <el-icon><Minus /></el-icon>
                删除
              </el-button>
            </div>
          </div>
        </el-card>
      </div>
    </el-card>

    <!-- 费用明细 -->
    <el-card class="form-card">
      <template #header>
        <span class="card-title">费用明细</span>
      </template>
      
      <div class="fee-items">
        <el-button type="primary" plain @click="addFeeItem" class="add-btn">
          <el-icon><Plus /></el-icon>
          添加费用项目
        </el-button>
        
        <el-card
          v-for="(item, index) in feeItems"
          :key="index"
          class="fee-item-card"
          shadow="never"
        >
          <div class="fee-form">
            <div class="fee-field">
              <label>费用类型</label>
              <el-select v-model="item.type" placeholder="请选择" style="width: 100%">
                <el-option label="配件费" value="parts" />
                <el-option label="人工费" value="labor" />
                <el-option label="运输费" value="shipping" />
                <el-option label="其他" value="other" />
              </el-select>
            </div>
            <div class="fee-field">
              <label>项目说明</label>
              <el-input v-model="item.description" placeholder="请输入项目说明" />
            </div>
            <div class="fee-field">
              <label>单价</label>
              <el-input-number v-model="item.price" :min="0" :precision="2" style="width: 100%" />
            </div>
            <div class="fee-field">
              <label>数量</label>
              <el-input-number v-model="item.quantity" :min="1" style="width: 100%" />
            </div>
            <div class="fee-field">
              <label>金额</label>
              <el-input :model-value="calculateAmount(item)" disabled style="width: 100%" />
            </div>
            <div class="fee-field">
              <label>保修(月)</label>
              <el-input-number v-model="item.warranty" :min="0" :max="60" style="width: 100%" />
            </div>
            <div class="fee-field fee-actions">
              <label>&nbsp;</label>
              <el-button type="danger" link @click="removeFeeItem(index)">
                <el-icon><Minus /></el-icon>
                删除
              </el-button>
            </div>
          </div>
        </el-card>
      </div>
    </el-card>

    <!-- 底部操作按钮 -->
    <div class="form-actions">
      <el-button @click="handleBack">返回</el-button>
      <el-button v-if="!currentOrderId" type="primary" @click="handleSubmit">保存订单</el-button>
      <el-button v-else type="success" @click="handleFinish">完成</el-button>
    </div>
  </div>
</template>

<style scoped>
.create-order {
  height: 100%;
  overflow-y: auto;
  padding-right: 10px;
}

.page-header {
  margin-bottom: 20px;
}

.page-title {
  font-size: 20px;
  font-weight: bold;
  color: #303133;
  margin: 0;
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

/* 阀门清单 */
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

/* 维修方案 */
.repair-plans {
  display: flex;
  flex-direction: column;
  gap: 15px;
}

.plan-item-card {
  background-color: #f5f7fa;
}

.plan-form {
  display: flex;
  gap: 15px;
  align-items: flex-end;
  flex-wrap: wrap;
}

.plan-field {
  flex: 1;
  min-width: 150px;
}

.plan-field label {
  display: block;
  font-size: 12px;
  color: #606266;
  margin-bottom: 5px;
}

.confirm-field {
  flex: 0 0 auto;
  min-width: 80px;
}

.plan-actions {
  flex: 0 0 auto;
}

/* 费用明细 */
.fee-items {
  display: flex;
  flex-direction: column;
  gap: 15px;
}

.fee-item-card {
  background-color: #f5f7fa;
}

.fee-form {
  display: flex;
  gap: 15px;
  align-items: flex-end;
  flex-wrap: wrap;
}

.fee-field {
  flex: 1;
  min-width: 120px;
}

.fee-field label {
  display: block;
  font-size: 12px;
  color: #606266;
  margin-bottom: 5px;
}

.fee-actions {
  flex: 0 0 auto;
}

/* 底部操作 */
.form-actions {
  display: flex;
  justify-content: center;
  gap: 20px;
  padding: 20px 0;
}
</style>
