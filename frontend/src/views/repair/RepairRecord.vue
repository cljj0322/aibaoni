<template>
  <div class="repair-record">
    <!-- 页面标题 -->
    <div class="page-header">
      <h2>阀门维修过程记录单</h2>
      <div class="header-actions">
        <el-button type="primary" @click="handleSave">
          <el-icon><DocumentChecked /></el-icon>保存
        </el-button>
        <el-button type="info" @click="handlePrint">
          <el-icon><Printer /></el-icon>打印
        </el-button>
      </div>
    </div>

    <!-- 基本信息 -->
    <el-card class="section-card">
      <template #header>
        <span class="section-title">基本信息</span>
      </template>
      <el-row :gutter="20">
        <el-col :span="8">
          <el-form-item label="艾宝尼SN" required>
            <el-input 
              v-model="formData.abn_sn" 
              placeholder="请扫码输入SN或按回车键确认"
              @keyup.enter="handleScanSN"
            />
          </el-form-item>
        </el-col>
        <el-col :span="8">
          <el-form-item label="Customer SN(客户序列号)">
            <el-input v-model="formData.customer_sn" disabled />
          </el-form-item>
        </el-col>
        <el-col :span="8">
          <el-form-item label="PO No.(订单号)">
            <el-input v-model="formData.po_no" disabled />
          </el-form-item>
        </el-col>
      </el-row>
      <el-row :gutter="20">
        <el-col :span="24">
          <el-form-item label="当前步骤">
            <el-input v-model="formData.current_step" type="textarea" :rows="2" />
          </el-form-item>
        </el-col>
      </el-row>
    </el-card>

    <!-- 产品信息 -->
    <el-card class="section-card">
      <template #header>
        <span class="section-title">Product Information(产品信息)</span>
      </template>
      <el-row :gutter="20">
        <el-col :span="6">
          <el-form-item label="Part No.(料号)">
            <el-input v-model="formData.part_no" />
          </el-form-item>
        </el-col>
        <el-col :span="6">
          <el-form-item label="Description(产品描述)">
            <el-input v-model="formData.description" />
          </el-form-item>
        </el-col>
        <el-col :span="6">
          <el-form-item label="Model No.(型号)">
            <el-input v-model="formData.model_no" />
          </el-form-item>
        </el-col>
        <el-col :span="6">
          <el-form-item label="故障描述">
            <el-input v-model="formData.fault_description" />
          </el-form-item>
        </el-col>
      </el-row>
      <el-row :gutter="20">
        <el-col :span="24">
          <el-form-item label="Service Category(服务类型)">
            <el-radio-group v-model="formData.service_category">
              <el-radio label="NormalRepair">NormalRepair</el-radio>
              <el-radio label="Warranty">Warranty</el-radio>
            </el-radio-group>
          </el-form-item>
        </el-col>
      </el-row>
    </el-card>

    <!-- 步骤导航 -->
    <div class="step-navigation">
      <el-button @click="prevStep">上一步</el-button>
      <span class="step-info">当前步骤: {{ currentStep }}/3</span>
      <el-button type="primary" @click="nextStep">下一步</el-button>
    </div>

    <!-- 维修前准备 -->
    <el-card class="section-card">
      <template #header>
        <div class="section-header">
          <span class="section-title">维修前准备</span>
          <div class="section-operators">
            <el-input v-model="formData.prepare_operator" placeholder="作业人" style="width: 120px; margin-right: 10px;" />
            <el-date-picker v-model="formData.prepare_date" type="date" placeholder="日期" style="width: 140px;" value-format="YYYY-MM-DD" />
          </div>
        </div>
      </template>
      <el-table :data="formData.prepare_items" border style="width: 100%">
        <el-table-column type="index" label="序号" width="80" />
        <el-table-column label="准备项目" min-width="200">
          <template #default="{ row }">
            <el-input v-model="row.item_name" placeholder="请输入准备项目" />
          </template>
        </el-table-column>
        <el-table-column label="要求" min-width="200">
          <template #default="{ row }">
            <el-input v-model="row.requirement" placeholder="请输入要求" />
          </template>
        </el-table-column>
        <el-table-column label="结果" width="150">
          <template #default="{ row }">
            <el-radio-group v-model="row.result">
              <el-radio label="OK">OK</el-radio>
              <el-radio label="NG">NG</el-radio>
            </el-radio-group>
          </template>
        </el-table-column>
        <el-table-column label="备注" min-width="150">
          <template #default="{ row }">
            <el-input v-model="row.remark" placeholder="请输入备注" />
          </template>
        </el-table-column>
        <el-table-column label="操作" width="80">
          <template #default="{ row, $index }">
            <el-button type="danger" link @click="removePrepareItem($index)">删除</el-button>
          </template>
        </el-table-column>
      </el-table>
      <div class="table-actions">
        <el-button type="primary" link @click="addPrepareItem">
          <el-icon><Plus /></el-icon>添加准备项
        </el-button>
      </div>
    </el-card>

    <!-- 维修步骤 -->
    <el-card class="section-card">
      <template #header>
        <div class="section-header">
          <span class="section-title">维修步骤</span>
          <div class="section-operators">
            <el-input v-model="formData.repair_step_operator" placeholder="作业人" style="width: 120px; margin-right: 10px;" />
            <el-date-picker v-model="formData.repair_step_date" type="date" placeholder="日期" style="width: 140px;" value-format="YYYY-MM-DD" />
          </div>
        </div>
      </template>
      <el-table :data="formData.repair_steps" border style="width: 100%">
        <el-table-column type="index" label="步骤" width="80" />
        <el-table-column label="维修内容" min-width="300">
          <template #default="{ row }">
            <el-input v-model="row.content" type="textarea" :rows="2" placeholder="请输入维修内容" />
          </template>
        </el-table-column>
        <el-table-column label="使用物料" min-width="200">
          <template #default="{ row }">
            <el-input v-model="row.materials" placeholder="请输入使用物料" />
          </template>
        </el-table-column>
        <el-table-column label="结果" width="150">
          <template #default="{ row }">
            <el-radio-group v-model="row.result">
              <el-radio label="OK">OK</el-radio>
              <el-radio label="NG">NG</el-radio>
            </el-radio-group>
          </template>
        </el-table-column>
        <el-table-column label="备注" min-width="150">
          <template #default="{ row }">
            <el-input v-model="row.remark" placeholder="请输入备注" />
          </template>
        </el-table-column>
        <el-table-column label="操作" width="80">
          <template #default="{ $index }">
            <el-button type="danger" link @click="removeRepairStep($index)">删除</el-button>
          </template>
        </el-table-column>
      </el-table>
      <div class="table-actions">
        <el-button type="primary" link @click="addRepairStep">
          <el-icon><Plus /></el-icon>添加步骤
        </el-button>
      </div>
    </el-card>

    <!-- Product Check(维修前检测) -->
    <el-card class="section-card">
      <template #header>
        <div class="section-header">
          <span class="section-title">Product Check(维修前检测)</span>
          <div class="section-operators">
            <el-input v-model="formData.check_operator" placeholder="作业人" style="width: 120px; margin-right: 10px;" />
            <el-date-picker v-model="formData.check_date" type="date" placeholder="日期" style="width: 140px;" value-format="YYYY-MM-DD" />
          </div>
        </div>
      </template>
      <el-table :data="formData.check_items" border style="width: 100%">
        <el-table-column type="index" label="Item(项目)" width="80" />
        <el-table-column label="Check Item(检测项)" width="200">
          <template #default="{ row, $index }">
            <el-input v-model="row.check_item" placeholder="请输入检测项" />
          </template>
        </el-table-column>
        <el-table-column label="Result(结果)" width="150">
          <template #default="{ row }">
            <el-radio-group v-model="row.result">
              <el-radio label="OK">OK</el-radio>
              <el-radio label="NG">NG</el-radio>
            </el-radio-group>
          </template>
        </el-table-column>
        <el-table-column label="Remark(备注)">
          <template #default="{ row }">
            <el-input v-model="row.remark" placeholder="请输入备注" />
          </template>
        </el-table-column>
        <el-table-column label="操作" width="80">
          <template #default="{ $index }">
            <el-button type="danger" link @click="removeCheckItem($index)">删除</el-button>
          </template>
        </el-table-column>
      </el-table>
      <div class="table-actions">
        <el-button type="primary" link @click="addCheckItem">
          <el-icon><Plus /></el-icon>添加检测项
        </el-button>
      </div>
    </el-card>

    <!-- 物料清单 -->
    <el-card class="section-card">
      <template #header>
        <div class="section-header">
          <span class="section-title">物料清单</span>
          <div class="section-operators">
            <el-input v-model="formData.material_operator" placeholder="作业人" style="width: 120px; margin-right: 10px;" />
            <el-date-picker v-model="formData.material_date" type="date" placeholder="日期" style="width: 140px;" value-format="YYYY-MM-DD" />
          </div>
        </div>
      </template>
      <el-table :data="formData.material_items" border style="width: 100%">
        <el-table-column label="物料类别" width="180">
          <template #default="{ row }">
            <el-input v-model="row.category" placeholder="请选择或输入物料类别" />
          </template>
        </el-table-column>
        <el-table-column label="物料名称" width="200">
          <template #default="{ row }">
            <el-input v-model="row.name" placeholder="请选择或输入物料名称" />
          </template>
        </el-table-column>
        <el-table-column label="数量" width="100">
          <template #default="{ row }">
            <el-input-number v-model="row.quantity" :min="1" style="width: 80px;" />
          </template>
        </el-table-column>
        <el-table-column label="备注">
          <template #default="{ row }">
            <el-input v-model="row.remark" placeholder="请输入备注" />
          </template>
        </el-table-column>
        <el-table-column label="操作" width="80">
          <template #default="{ $index }">
            <el-button type="danger" link @click="removeMaterialItem($index)">删除</el-button>
          </template>
        </el-table-column>
      </el-table>
      <div class="table-actions">
        <el-button type="primary" link @click="addMaterialItem">
          <el-icon><Plus /></el-icon>添加物料
        </el-button>
      </div>
    </el-card>

    <!-- Final Test Item(最终测试项目) -->
    <el-card class="section-card">
      <template #header>
        <div class="section-header">
          <span class="section-title">Final Test Item(最终测试项目)</span>
          <div class="section-operators">
            <el-input v-model="formData.final_test_operator" placeholder="作业人" style="width: 120px; margin-right: 10px;" />
            <el-date-picker v-model="formData.final_test_date" type="date" placeholder="日期" style="width: 140px;" value-format="YYYY-MM-DD" />
          </div>
        </div>
      </template>
      <el-row :gutter="40">
        <el-col :span="8">
          <div class="test-item">
            <div class="test-label">运动测试</div>
            <el-radio-group v-model="formData.final_test_motion">
              <el-radio label="OK">OK</el-radio>
              <el-radio label="NG">NG</el-radio>
            </el-radio-group>
          </div>
        </el-col>
        <el-col :span="8">
          <div class="test-item">
            <div class="test-label">气动泄漏</div>
            <el-radio-group v-model="formData.final_test_pneumatic">
              <el-radio label="OK">OK</el-radio>
              <el-radio label="NG">NG</el-radio>
            </el-radio-group>
          </div>
        </el-col>
        <el-col :span="8">
          <div class="test-item">
            <div class="test-label">氦检</div>
            <el-radio-group v-model="formData.final_test_helium">
              <el-radio label="OK">OK</el-radio>
              <el-radio label="NG">NG</el-radio>
            </el-radio-group>
          </div>
        </el-col>
      </el-row>
    </el-card>

    <!-- 质保期和工程师信息 -->
    <el-card class="section-card">
      <template #header>
        <div class="section-header">
          <span class="section-title">质保期和工程师信息</span>
          <div class="section-operators">
            <el-input v-model="formData.warranty_operator" placeholder="作业人" style="width: 120px; margin-right: 10px;" />
            <el-date-picker v-model="formData.warranty_date" type="date" placeholder="日期" style="width: 140px;" value-format="YYYY-MM-DD" />
          </div>
        </div>
      </template>
      <el-row :gutter="20">
        <el-col :span="6">
          <el-form-item label="Product Warranty(质保期)">
            <el-input v-model="formData.product_warranty" placeholder="请输入质保期" />
          </el-form-item>
        </el-col>
        <el-col :span="6">
          <el-form-item label="维修工程师">
            <el-input v-model="formData.repair_engineer" placeholder="请输入维修工程师" />
          </el-form-item>
        </el-col>
        <el-col :span="6">
          <el-form-item label="审核人1">
            <el-input v-model="formData.reviewer_1" placeholder="请输入审核人1" />
          </el-form-item>
        </el-col>
        <el-col :span="6">
          <el-form-item label="审核人2">
            <el-input v-model="formData.reviewer_2" placeholder="请输入审核人2" />
          </el-form-item>
        </el-col>
      </el-row>
    </el-card>

    <!-- Test Data(测试数据) -->
    <el-card class="section-card">
      <template #header>
        <div class="section-header">
          <span class="section-title">Test Data(测试数据)</span>
          <div class="section-operators">
            <el-input v-model="formData.test_data_operator" placeholder="作业人" style="width: 120px; margin-right: 10px;" />
            <el-date-picker v-model="formData.test_data_date" type="date" placeholder="日期" style="width: 140px;" value-format="YYYY-MM-DD" />
          </div>
        </div>
      </template>
      <el-table :data="formData.test_data_items" border style="width: 100%">
        <el-table-column label="检查内容" width="200">
          <template #default="{ row }">
            <el-input v-model="row.item_name" placeholder="检查内容" />
          </template>
        </el-table-column>
        <el-table-column label="基准" width="200">
          <template #default="{ row }">
            <el-input v-model="row.standard" placeholder="请输入基准" />
          </template>
        </el-table-column>
        <el-table-column label="测试值" width="200">
          <template #default="{ row }">
            <el-input v-model="row.test_value" placeholder="请输入测试值" />
          </template>
        </el-table-column>
        <el-table-column label="判定" width="150">
          <template #default="{ row }">
            <el-radio-group v-model="row.result">
              <el-radio label="OK">OK</el-radio>
              <el-radio label="NG">NG</el-radio>
            </el-radio-group>
          </template>
        </el-table-column>
        <el-table-column label="操作" width="80">
          <template #default="{ $index }">
            <el-button type="danger" link @click="removeTestDataItem($index)">删除</el-button>
          </template>
        </el-table-column>
      </el-table>
      <div class="table-actions">
        <el-button type="primary" link @click="addTestDataItem">
          <el-icon><Plus /></el-icon>添加测试项
        </el-button>
      </div>
    </el-card>

    <!-- Attachment(附件) -->
    <el-card class="section-card">
      <template #header>
        <div class="section-header">
          <span class="section-title">Attachment(附件)</span>
          <div class="section-operators">
            <el-input v-model="formData.attachment_operator" placeholder="作业人" style="width: 120px; margin-right: 10px;" />
            <el-date-picker v-model="formData.attachment_date" type="date" placeholder="日期" style="width: 140px;" value-format="YYYY-MM-DD" />
          </div>
        </div>
      </template>
      <div class="attachment-section">
        <div class="attachment-label">Product Picture(产品图片)</div>
        <el-upload
          class="upload-box"
          drag
          action="#"
          :auto-upload="false"
          :on-change="(file: any) => handleFileChange(file, 'product')"
          :file-list="productImages"
          list-type="picture-card"
        >
          <el-icon class="upload-icon"><Plus /></el-icon>
          <div class="upload-text">上传图片</div>
        </el-upload>
      </div>
    </el-card>

    <!-- Packaging(包装) -->
    <el-card class="section-card">
      <template #header>
        <div class="section-header">
          <span class="section-title">Packaging(包装)</span>
          <div class="section-operators">
            <el-input v-model="formData.packaging_operator" placeholder="作业人" style="width: 120px; margin-right: 10px;" />
            <el-date-picker v-model="formData.packaging_date" type="date" placeholder="日期" style="width: 140px;" value-format="YYYY-MM-DD" />
          </div>
        </div>
      </template>
      <div class="attachment-section">
        <div class="attachment-label">Packaging Picture(包装图片)</div>
        <el-upload
          class="upload-box"
          drag
          action="#"
          :auto-upload="false"
          :on-change="(file: any) => handleFileChange(file, 'packaging')"
          :file-list="packagingImages"
          list-type="picture-card"
        >
          <el-icon class="upload-icon"><Plus /></el-icon>
          <div class="upload-text">上传图片</div>
        </el-upload>
      </div>
    </el-card>

    <!-- Shipment(发货) -->
    <el-card class="section-card">
      <template #header>
        <div class="section-header">
          <span class="section-title">Shipment(发货)</span>
          <div class="section-operators">
            <el-input v-model="formData.shipment_tracking_no" placeholder="快递单号" style="width: 150px; margin-right: 10px;" />
            <el-input v-model="formData.shipment_operator" placeholder="作业人" style="width: 120px; margin-right: 10px;" />
            <el-date-picker v-model="formData.shipment_date" type="date" placeholder="日期" style="width: 140px;" value-format="YYYY-MM-DD" />
          </div>
        </div>
      </template>
      <div class="attachment-section">
        <div class="attachment-label">Shipment Picture(发货图片)</div>
        <el-upload
          class="upload-box"
          drag
          action="#"
          :auto-upload="false"
          :on-change="(file: any) => handleFileChange(file, 'shipment')"
          list-type="picture-card"
        >
          <el-icon class="upload-icon"><Plus /></el-icon>
          <div class="upload-text">上传图片</div>
        </el-upload>
      </div>
    </el-card>
  </div>
</template>

<script setup lang="ts">
import { ref, reactive, onMounted } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { ElMessage, ElMessageBox } from 'element-plus'
import { DocumentChecked, Printer, Plus } from '@element-plus/icons-vue'
import { getRepairRecord, updateRepairRecord, searchValveBySn } from '@/api/repairRecords'

const route = useRoute()
const router = useRouter()

// 当前步骤
const currentStep = ref(1)

// 表单数据接口
interface FormData {
  // 基本信息
  abn_sn: string
  customer_sn: string
  po_no: string
  current_step: string

  // 产品信息
  part_no: string
  description: string
  model_no: string
  fault_description: string
  service_category: string

  // 维修前准备
  prepare_items: any[]
  prepare_operator: string
  prepare_date: string

  // 维修步骤
  repair_steps: any[]
  repair_step_operator: string
  repair_step_date: string

  // 检测项
  check_items: any[]
  check_operator: string
  check_date: string

  // 物料清单
  material_items: any[]
  material_operator: string
  material_date: string

  // 最终测试
  final_test_motion: string
  final_test_pneumatic: string
  final_test_helium: string
  final_test_operator: string
  final_test_date: string

  // 质保信息
  product_warranty: string
  repair_engineer: string
  reviewer_1: string
  reviewer_2: string
  warranty_operator: string
  warranty_date: string

  // 测试数据
  test_data_items: any[]
  test_data_operator: string
  test_data_date: string

  // 附件
  attachment_operator: string
  attachment_date: string

  // 包装
  packaging_operator: string
  packaging_date: string

  // 发货
  shipment_tracking_no: string
  shipment_operator: string
  shipment_date: string
}

// 表单数据
const formData = reactive<FormData>({
  // 基本信息
  abn_sn: '',
  customer_sn: '',
  po_no: '',
  current_step: '',
  
  // 产品信息
  part_no: '',
  description: '',
  model_no: '',
  fault_description: '',
  service_category: 'NormalRepair',
  
  // 维修前准备
  prepare_items: [] as any[],
  prepare_operator: '',
  prepare_date: '',
  
  // 维修步骤
  repair_steps: [] as any[],
  repair_step_operator: '',
  repair_step_date: '',
  
  // 检测项
  check_items: [
    { item_no: 1, check_item: '运动测试', result: '', remark: '' },
    { item_no: 2, check_item: '气动泄漏', result: '', remark: '' },
    { item_no: 3, check_item: '氦检', result: '', remark: '' }
  ] as any[],
  check_operator: '',
  check_date: '',
  
  // 物料清单
  material_items: [] as any[],
  material_operator: '',
  material_date: '',
  
  // 最终测试
  final_test_motion: '',
  final_test_pneumatic: '',
  final_test_helium: '',
  final_test_operator: '',
  final_test_date: '',
  
  // 质保信息
  product_warranty: '',
  repair_engineer: '',
  reviewer_1: '',
  reviewer_2: '',
  warranty_operator: '',
  warranty_date: '',
  
  // 测试数据
  test_data_items: [
    { item_name: '空气压降(60sec)', standard: '', test_value: '', result: '' },
    { item_name: 'Internal Leak Test', standard: '', test_value: '', result: '' },
    { item_name: 'External Leak Test', standard: '', test_value: '', result: '' }
  ] as any[],
  test_data_operator: '',
  test_data_date: '',
  
  // 附件
  attachment_operator: '',
  attachment_date: '',
  
  // 包装
  packaging_operator: '',
  packaging_date: '',
  
  // 发货
  shipment_tracking_no: '',
  shipment_operator: '',
  shipment_date: ''
})

// 附件列表
const productImages = ref<any[]>([])
const packagingImages = ref<any[]>([])

// 阀门ID
const valveId = ref<number | null>(null)

// 初始化
onMounted(() => {
  const id = route.query.valveId
  if (id) {
    valveId.value = Number(id)
    loadRepairRecord(Number(id))
  }
})

// 加载维修记录
const loadRepairRecord = async (id: number) => {
  try {
    const res = await getRepairRecord(id)
    if (res.data.code === 200) {
      const data = res.data.data
      // 填充表单数据
      Object.assign(formData, data)
      
      // 处理检测项
      if (data.check_items && data.check_items.length > 0) {
        formData.check_items = data.check_items
      }
      
      // 处理物料清单
      if (data.material_items) {
        formData.material_items = data.material_items
      }
      
      // 处理测试数据
      if (data.test_data_items && data.test_data_items.length > 0) {
        formData.test_data_items = data.test_data_items
      }
      
      // 处理附件
      if (data.attachments) {
        productImages.value = data.attachments
          .filter((a: any) => a.type === 'product')
          .map((a: any) => ({ name: a.file_name, url: a.file_path }))
        packagingImages.value = data.attachments
          .filter((a: any) => a.type === 'packaging')
          .map((a: any) => ({ name: a.file_name, url: a.file_path }))
      }
    }
  } catch (error) {
    ElMessage.error('加载维修记录失败')
  }
}

// 扫码输入SN
const handleScanSN = async () => {
  const sn = formData.abn_sn.trim()
  if (!sn) {
    ElMessage.warning('请输入艾宝尼SN')
    return
  }

  try {
    ElMessage.info('正在查询阀门信息...')
    const valve = await searchValveBySn(sn)
    // 设置阀门ID
    valveId.value = valve.id
    // 填充阀门基本信息
    formData.customer_sn = valve.customer_sn || ''
    formData.po_no = valve.po_no || ''
    formData.part_no = valve.part_no || ''
    formData.description = valve.description || ''
    formData.model_no = valve.model_no || ''
    formData.fault_description = valve.fault_description || ''
    formData.service_category = valve.service_category || 'NormalRepair'
    formData.current_step = valve.current_step || ''

    ElMessage.success('阀门信息加载成功')
  } catch (error: any) {
    // 查询失败，清除相关信息
    valveId.value = null
    formData.customer_sn = ''
    formData.po_no = ''
    // 错误消息已经在 request.ts 拦截器中显示
    // 这里只需要处理特殊情况
    if (!error.message || error.message === '请求失败') {
      ElMessage.error('查询阀门信息失败')
    }
  }
}

// 添加准备项
const addPrepareItem = () => {
  formData.prepare_items.push({
    item_name: '',
    requirement: '',
    result: '',
    remark: ''
  })
}

// 删除准备项
const removePrepareItem = (index: number) => {
  formData.prepare_items.splice(index, 1)
}

// 添加维修步骤
const addRepairStep = () => {
  formData.repair_steps.push({
    content: '',
    materials: '',
    result: '',
    remark: ''
  })
}

// 删除维修步骤
const removeRepairStep = (index: number) => {
  formData.repair_steps.splice(index, 1)
}

// 添加检测项
const addCheckItem = () => {
  formData.check_items.push({
    item_no: formData.check_items.length + 1,
    check_item: '',
    result: '',
    remark: ''
  })
}

// 删除检测项
const removeCheckItem = (index: number) => {
  formData.check_items.splice(index, 1)
  // 重新编号
  formData.check_items.forEach((item, idx) => {
    item.item_no = idx + 1
  })
}

// 添加物料项
const addMaterialItem = () => {
  formData.material_items.push({
    category: '',
    name: '',
    quantity: 1,
    remark: ''
  })
}

// 删除物料项
const removeMaterialItem = (index: number) => {
  formData.material_items.splice(index, 1)
}

// 添加测试数据项
const addTestDataItem = () => {
  formData.test_data_items.push({
    item_name: '',
    standard: '',
    test_value: '',
    result: ''
  })
}

// 删除测试数据项
const removeTestDataItem = (index: number) => {
  formData.test_data_items.splice(index, 1)
}

// 文件上传
const handleFileChange = (file: any, type: string) => {
  // TODO: 实现文件上传
  console.log('File changed:', file, type)
}

// 上一步
const prevStep = () => {
  if (currentStep.value > 1) {
    currentStep.value--
  }
}

// 下一步
const nextStep = () => {
  if (currentStep.value < 3) {
    currentStep.value++
  }
}

// 保存
const handleSave = async () => {
  // 如果没有阀门ID，但有SN，尝试先查询阀门
  if (!valveId.value && formData.abn_sn) {
    try {
      const valve = await searchValveBySn(formData.abn_sn.trim())
      valveId.value = valve.id
    } catch (error) {
      // 查询失败，继续检查
    }
  }

  if (!valveId.value) {
    ElMessage.warning('请先选择阀门或输入有效的艾宝尼SN')
    return
  }

  try {
    await updateRepairRecord(valveId.value, formData)
    ElMessage.success('保存成功')
  } catch (error) {
    ElMessage.error('保存失败')
  }
}

// 打印
const handlePrint = () => {
  window.print()
}
</script>

<style scoped lang="scss">
.repair-record {
  padding: 20px;
  background-color: #0d1b2a;
  min-height: 100vh;
  color: #fff;
}

.page-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 20px;
  
  h2 {
    margin: 0;
    font-size: 20px;
    color: #fff;
  }
  
  .header-actions {
    display: flex;
    gap: 10px;
  }
}

.section-card {
  margin-bottom: 20px;
  background-color: #1b2838;
  border: 1px solid #2d3d4f;
  
  :deep(.el-card__header) {
    background-color: #243447;
    border-bottom: 1px solid #2d3d4f;
    padding: 12px 20px;
  }
  
  :deep(.el-card__body) {
    padding: 20px;
  }
}

.section-title {
  font-size: 16px;
  font-weight: 500;
  color: #fff;
}

.section-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.section-operators {
  display: flex;
  align-items: center;
}

.step-navigation {
  display: flex;
  justify-content: center;
  align-items: center;
  gap: 20px;
  margin-bottom: 20px;
  padding: 15px;
  background-color: #1b2838;
  border-radius: 4px;
  
  .step-info {
    color: #fff;
    font-size: 14px;
  }
}

.table-actions {
  margin-top: 10px;
  text-align: center;
}

.test-item {
  display: flex;
  align-items: center;
  gap: 20px;
  padding: 10px;
  
  .test-label {
    color: #fff;
    font-size: 14px;
    min-width: 80px;
  }
}

.attachment-section {
  .attachment-label {
    color: #fff;
    font-size: 14px;
    margin-bottom: 10px;
  }
}

.upload-box {
  :deep(.el-upload-dragger) {
    background-color: #243447;
    border: 1px dashed #409eff;
    width: 150px;
    height: 150px;
    
    &:hover {
      border-color: #66b1ff;
    }
  }
  
  .upload-icon {
    font-size: 28px;
    color: #409eff;
    margin-bottom: 10px;
  }
  
  .upload-text {
    color: #409eff;
    font-size: 14px;
  }
}

// 表单样式
:deep(.el-form-item__label) {
  color: #fff;
}

:deep(.el-input__wrapper) {
  background-color: #243447;
}

:deep(.el-input__inner) {
  background-color: transparent;
  color: #fff;
}

:deep(.el-textarea__inner) {
  background-color: #243447;
  color: #fff;
}

:deep(.el-radio) {
  color: #fff;
}

:deep(.el-table) {
  background-color: transparent;
  
  th.el-table__cell {
    background-color: #243447;
    color: #fff;
  }
  
  td.el-table__cell {
    background-color: #1b2838;
    color: #fff;
  }
}

// 打印样式
@media print {
  .page-header,
  .step-navigation,
  .table-actions,
  .el-button {
    display: none !important;
  }
  
  .repair-record {
    background-color: #fff;
    color: #000;
  }
  
  .section-card {
    background-color: #fff;
    border: 1px solid #ccc;
    page-break-inside: avoid;
  }
}
</style>
