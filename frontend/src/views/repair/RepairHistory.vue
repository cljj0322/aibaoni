<template>
  <div class="repair-history">
    <!-- 页面标题 -->
    <div class="page-header">
      <h2>阀门维修履历</h2>
    </div>

    <!-- 查询条件 -->
    <el-card class="search-card">
      <el-radio-group v-model="searchType" class="search-type">
        <el-radio label="customer_sn">按客户SN查询</el-radio>
        <el-radio label="abn_sn">按艾宝尼查询</el-radio>
      </el-radio-group>
      <el-input 
        v-model="searchKeyword" 
        :placeholder="searchType === 'customer_sn' ? '请输入客户SN' : '请输入艾宝尼SN'"
        style="width: 250px; margin-left: 15px;"
      />
      <el-button type="primary" style="margin-left: 10px;" @click="handleSearch">查询</el-button>
      <el-button style="margin-left: 10px;" @click="handleReset">重置</el-button>
    </el-card>

    <!-- 阀门列表 -->
    <el-card class="table-card">
      <el-table 
        :data="valveList" 
        border 
        style="width: 100%"
        highlight-current-row
        @row-click="handleRowClick"
      >
        <el-table-column type="index" label="序号" width="60" />
        <el-table-column prop="combined_sn" label="组合序列号" min-width="150" />
        <el-table-column prop="customer_sn" label="客户序列号" min-width="120" />
        <el-table-column prop="abn_sn" label="艾宝尼序列号" min-width="120" />
        <el-table-column prop="po_no" label="PO号" min-width="100" />
        <el-table-column prop="repair_status" label="维修状态" min-width="100">
          <template #default="{ row }">
            <el-tag :type="getStatusType(row.repair_status)">
              {{ getStatusText(row.repair_status) }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="current_step" label="当前维修步骤" min-width="150" />
      </el-table>
      <div class="pagination-wrapper">
        <span class="total-text">共 {{ total }} 个SN</span>
        <el-pagination
          v-model:current-page="currentPage"
          v-model:page-size="pageSize"
          :page-sizes="[10, 20, 50]"
          layout="sizes, prev, pager, next"
          :total="total"
          @size-change="handleSizeChange"
          @current-change="handlePageChange"
        />
      </div>
    </el-card>

    <!-- 维修前检测查询 -->
    <el-card class="section-card">
      <template #header>
        <div class="section-header">
          <span class="section-title">维修前检测查询</span>
          <div class="section-filter">
            <el-input v-model="filterCombinedSn1" placeholder="请输入组合序列号" style="width: 180px;" />
            <el-select v-model="filterType1" placeholder="请选择" style="width: 120px; margin-left: 10px;">
              <el-option label="全部" value="" />
              <el-option label="OK" value="OK" />
              <el-option label="NG" value="NG" />
            </el-select>
          </div>
        </div>
      </template>
      <el-table :data="checkItemsData" border style="width: 100%">
        <el-table-column type="index" label="Item(项目)" width="90" />
        <el-table-column prop="check_item" label="Check Item(检测项)" min-width="150" />
        <el-table-column label="Result(结果)" width="120">
          <template #default="{ row }">
            <span :class="row.result === 'OK' ? 'result-ok' : 'result-ng'">{{ row.result }}</span>
          </template>
        </el-table-column>
        <el-table-column prop="remark" label="Remark(备注)" min-width="200" />
      </el-table>
      <div class="operator-info">
        <div class="info-row">
          <span class="info-label">作业人</span>
          <el-input v-model="checkOperator" style="width: 150px;" disabled />
        </div>
        <div class="info-row">
          <span class="info-label">日期</span>
          <el-date-picker v-model="checkDate" type="date" style="width: 150px;" disabled />
        </div>
      </div>
    </el-card>

    <!-- 维修前准备查询 -->
    <el-card class="section-card">
      <template #header>
        <div class="section-header">
          <span class="section-title">维修前准备查询</span>
          <div class="section-filter">
            <el-input v-model="filterCombinedSn2" placeholder="请输入组合序列号" style="width: 180px;" />
            <el-select v-model="filterType2" placeholder="请选择" style="width: 120px; margin-left: 10px;">
              <el-option label="全部" value="" />
            </el-select>
          </div>
        </div>
      </template>
      <div class="checkbox-group">
        <div class="checkbox-row">
          <span class="row-label">故障现象:</span>
          <el-checkbox-group v-model="faultPhenomenon" disabled>
            <el-checkbox label="内漏">内漏</el-checkbox>
            <el-checkbox label="外漏">外漏</el-checkbox>
            <el-checkbox label="CDA漏气">CDA漏气</el-checkbox>
            <el-checkbox label="运动卡顿">运动卡顿</el-checkbox>
            <el-checkbox label="HUNTING">HUNTING</el-checkbox>
            <el-checkbox label="开关闭合失败">开关闭合失败</el-checkbox>
          </el-checkbox-group>
        </div>
        <div class="checkbox-row">
          <span class="row-label">工具准备:</span>
          <el-checkbox-group v-model="toolsReady" disabled>
            <el-checkbox label="内六角">内六角</el-checkbox>
            <el-checkbox label="扳手">扳手</el-checkbox>
            <el-checkbox label="螺丝刀">螺丝刀</el-checkbox>
            <el-checkbox label="密封圈挑针">密封圈挑针</el-checkbox>
            <el-checkbox label="紧固胶">紧固胶</el-checkbox>
            <el-checkbox label="润滑脂">润滑脂</el-checkbox>
          </el-checkbox-group>
        </div>
        <div class="checkbox-row">
          <span class="row-label">更换件确认:</span>
          <el-checkbox-group v-model="replacementParts" disabled>
            <el-checkbox label="FKM密封圈">FKM密封圈</el-checkbox>
            <el-checkbox label="FFKM密封圈">FFKM密封圈</el-checkbox>
            <el-checkbox label="PACKING">PACKING</el-checkbox>
            <el-checkbox label="波纹管">波纹管</el-checkbox>
            <el-checkbox label="弹簧">弹簧</el-checkbox>
            <el-checkbox label="轴承">轴承</el-checkbox>
            <el-checkbox label="密封门板">密封门板</el-checkbox>
            <el-checkbox label="钢珠">钢珠</el-checkbox>
            <el-checkbox label="马达">马达</el-checkbox>
            <el-checkbox label="螺丝">螺丝</el-checkbox>
            <el-checkbox label="气管接头">气管接头</el-checkbox>
            <el-checkbox label="卡簧">卡簧</el-checkbox>
            <el-checkbox label="定制加工件">定制加工件</el-checkbox>
          </el-checkbox-group>
        </div>
      </div>
      <div class="operator-info">
        <div class="info-row">
          <span class="info-label">作业人</span>
          <el-input v-model="prepareOperator" style="width: 150px;" disabled />
        </div>
        <div class="info-row">
          <span class="info-label">日期</span>
          <el-date-picker v-model="prepareDate" type="date" style="width: 150px;" disabled />
        </div>
      </div>
    </el-card>

    <!-- 维修步骤查询 -->
    <el-card class="section-card">
      <template #header>
        <div class="section-header">
          <span class="section-title">维修步骤查询</span>
          <div class="section-filter">
            <el-input v-model="filterCombinedSn3" placeholder="请输入组合序列号" style="width: 180px;" />
            <el-select v-model="filterType3" placeholder="请选择" style="width: 120px; margin-left: 10px;">
              <el-option label="全部" value="" />
            </el-select>
          </div>
        </div>
      </template>
      <div class="checkbox-group">
        <div class="checkbox-row">
          <span class="row-label">拆卸步骤:</span>
          <el-checkbox-group v-model="disassemblySteps" disabled>
            <el-checkbox label="隔离与拆卸">隔离与拆卸</el-checkbox>
            <el-checkbox label="分解阀门">分解阀门</el-checkbox>
            <el-checkbox label="外包清洗">外包清洗</el-checkbox>
            <el-checkbox label="内部简单表面处理">内部简单表面处理</el-checkbox>
          </el-checkbox-group>
        </div>
        <div class="checkbox-row">
          <span class="row-label">重组安装步骤:</span>
          <el-radio-group v-model="reassemblyResult" disabled>
            <el-radio label="按顺序组装">按顺序组装</el-radio>
            <el-radio label="OK">OK</el-radio>
            <el-radio label="NG">NG</el-radio>
          </el-radio-group>
        </div>
      </div>
      <div class="operator-info">
        <div class="info-row">
          <span class="info-label">作业人</span>
          <el-input v-model="repairStepOperator" style="width: 150px;" disabled />
        </div>
        <div class="info-row">
          <span class="info-label">日期</span>
          <el-date-picker v-model="repairStepDate" type="date" style="width: 150px;" disabled />
        </div>
      </div>
    </el-card>

    <!-- 最终测试项目查询 -->
    <el-card class="section-card">
      <template #header>
        <div class="section-header">
          <span class="section-title">最终测试项目查询</span>
          <div class="section-filter">
            <el-input v-model="filterCombinedSn4" placeholder="请输入组合序列号" style="width: 180px;" />
            <el-select v-model="filterType4" placeholder="请选择" style="width: 120px; margin-left: 10px;">
              <el-option label="全部" value="" />
            </el-select>
          </div>
        </div>
      </template>
      <div class="test-results">
        <div class="test-row">
          <span class="test-label">运动测试:</span>
          <el-radio-group v-model="finalTestMotion" disabled>
            <el-radio label="OK">OK</el-radio>
            <el-radio label="NG">NG</el-radio>
          </el-radio-group>
        </div>
        <div class="test-row">
          <span class="test-label">气动泄漏:</span>
          <el-radio-group v-model="finalTestPneumatic" disabled>
            <el-radio label="OK">OK</el-radio>
            <el-radio label="NG">NG</el-radio>
          </el-radio-group>
        </div>
        <div class="test-row">
          <span class="test-label">氦检:</span>
          <el-radio-group v-model="finalTestHelium" disabled>
            <el-radio label="OK">OK</el-radio>
            <el-radio label="NG">NG</el-radio>
          </el-radio-group>
        </div>
      </div>
      <div class="operator-info">
        <div class="info-row">
          <span class="info-label">作业人</span>
          <el-input v-model="finalTestOperator" style="width: 150px;" disabled />
        </div>
        <div class="info-row">
          <span class="info-label">日期</span>
          <el-date-picker v-model="finalTestDate" type="date" style="width: 150px;" disabled />
        </div>
      </div>
    </el-card>

    <!-- 质保期和工程师信息查询 -->
    <el-card class="section-card">
      <template #header>
        <div class="section-header">
          <span class="section-title">质保期和工程师信息查询</span>
          <div class="section-filter">
            <el-input v-model="filterCombinedSn5" placeholder="请输入组合序列号" style="width: 180px;" />
            <el-select v-model="filterType5" placeholder="请选择" style="width: 120px; margin-left: 10px;">
              <el-option label="全部" value="" />
            </el-select>
          </div>
        </div>
      </template>
      <div class="warranty-info">
        <div class="info-row-inline">
          <span class="info-label">Product Warranty(质保期):</span>
          <el-input v-model="productWarranty" style="width: 150px;" disabled />
          <span class="info-label" style="margin-left: 30px;">维修工程师:</span>
          <el-input v-model="repairEngineer" style="width: 150px;" disabled />
          <span class="info-label" style="margin-left: 30px;">审核人1:</span>
          <el-input v-model="reviewer1" style="width: 150px;" disabled />
          <span class="info-label" style="margin-left: 30px;">审核人2:</span>
          <el-input v-model="reviewer2" style="width: 150px;" disabled />
        </div>
      </div>
      <div class="operator-info">
        <div class="info-row">
          <span class="info-label">作业人</span>
          <el-input v-model="warrantyOperator" style="width: 150px;" disabled />
        </div>
        <div class="info-row">
          <span class="info-label">日期</span>
          <el-date-picker v-model="warrantyDate" type="date" style="width: 150px;" disabled />
        </div>
      </div>
    </el-card>

    <!-- Test Data(测试数据)查询 -->
    <el-card class="section-card">
      <template #header>
        <div class="section-header">
          <span class="section-title">Test Data(测试数据)查询</span>
          <div class="section-filter">
            <el-input v-model="filterCombinedSn6" placeholder="请输入组合序列号" style="width: 180px;" />
            <el-select v-model="filterType6" placeholder="请选择" style="width: 120px; margin-left: 10px;">
              <el-option label="全部" value="" />
            </el-select>
          </div>
        </div>
      </template>
      <el-table :data="testDataItems" border style="width: 100%">
        <el-table-column prop="item_name" label="检查内容" min-width="150" />
        <el-table-column prop="standard" label="基准" min-width="150">
          <template #default="{ row }">
            <el-input v-model="row.standard" placeholder="请输入基准" disabled />
          </template>
        </el-table-column>
        <el-table-column prop="test_value" label="测试值" min-width="150">
          <template #default="{ row }">
            <el-input v-model="row.test_value" placeholder="请输入测试值" disabled />
          </template>
        </el-table-column>
        <el-table-column label="判定" width="100">
          <template #default="{ row }">
            <el-radio-group v-model="row.result" disabled>
              <el-radio label="OK">OK</el-radio>
              <el-radio label="NG">NG</el-radio>
            </el-radio-group>
          </template>
        </el-table-column>
      </el-table>
      <div class="operator-info">
        <div class="info-row">
          <span class="info-label">作业人</span>
          <el-input v-model="testDataOperator" style="width: 150px;" disabled />
        </div>
        <div class="info-row">
          <span class="info-label">日期</span>
          <el-date-picker v-model="testDataDate" type="date" style="width: 150px;" disabled />
        </div>
      </div>
    </el-card>

    <!-- 物料清单查询 -->
    <el-card class="section-card">
      <template #header>
        <div class="section-header">
          <span class="section-title">物料清单查询</span>
          <div class="section-filter">
            <el-input v-model="filterCombinedSn7" placeholder="请输入组合序列号" style="width: 180px;" />
            <el-select v-model="filterType7" placeholder="请选择" style="width: 120px; margin-left: 10px;">
              <el-option label="全部" value="" />
            </el-select>
          </div>
        </div>
      </template>
      <el-table :data="materialItems" border style="width: 100%">
        <el-table-column prop="category" label="物料类别" min-width="150" />
        <el-table-column prop="name" label="物料品类" min-width="150" />
        <el-table-column prop="quantity" label="数量" width="100" />
        <el-table-column prop="remark" label="备注" min-width="200" />
      </el-table>
      <div class="operator-info">
        <div class="info-row">
          <span class="info-label">作业人</span>
          <el-input v-model="materialOperator" style="width: 150px;" disabled />
        </div>
        <div class="info-row">
          <span class="info-label">日期</span>
          <el-date-picker v-model="materialDate" type="date" style="width: 150px;" disabled />
        </div>
      </div>
    </el-card>

    <!-- 附件图片查询 -->
    <el-card class="section-card">
      <template #header>
        <div class="section-header">
          <span class="section-title">附件图片查询</span>
          <div class="section-filter">
            <el-input v-model="filterCombinedSn8" placeholder="请输入组合序列号" style="width: 180px;" />
            <el-button type="danger" style="margin-left: 10px;">删除附件图片</el-button>
          </div>
        </div>
      </template>
      <div class="image-gallery">
        <div v-for="(img, index) in attachmentImages" :key="index" class="image-item">
          <el-image 
            :src="img" 
            :preview-src-list="attachmentImages"
            fit="cover"
            style="width: 120px; height: 120px;"
          />
        </div>
        <div v-if="attachmentImages.length === 0" class="no-image">暂无附件图片</div>
      </div>
    </el-card>

    <!-- 包装图片查询 -->
    <el-card class="section-card">
      <template #header>
        <div class="section-header">
          <span class="section-title">包装图片查询</span>
          <div class="section-filter">
            <el-input v-model="filterCombinedSn9" placeholder="请输入组合序列号" style="width: 180px;" />
            <el-button type="danger" style="margin-left: 10px;">删除包装图片</el-button>
          </div>
        </div>
      </template>
      <div class="image-gallery">
        <div v-for="(img, index) in packagingImages" :key="index" class="image-item">
          <el-image 
            :src="img" 
            :preview-src-list="packagingImages"
            fit="cover"
            style="width: 120px; height: 120px;"
          />
        </div>
        <div v-if="packagingImages.length === 0" class="no-image">暂无包装图片</div>
      </div>
    </el-card>

    <!-- 发货图片查询 -->
    <el-card class="section-card">
      <template #header>
        <div class="section-header">
          <span class="section-title">发货图片查询</span>
          <div class="section-filter">
            <el-input v-model="filterCombinedSn10" placeholder="请输入组合序列号" style="width: 180px;" />
            <el-button type="danger" style="margin-left: 10px;">删除发货图片</el-button>
          </div>
        </div>
      </template>
      <div class="image-gallery">
        <div v-for="(img, index) in shipmentImages" :key="index" class="image-item">
          <el-image 
            :src="img" 
            :preview-src-list="shipmentImages"
            fit="cover"
            style="width: 120px; height: 120px;"
          />
        </div>
        <div v-if="shipmentImages.length === 0" class="no-image">暂无发货图片</div>
      </div>
    </el-card>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { ElMessage } from 'element-plus'
import { searchValvesList, getRepairRecord } from '../../api/repairRecords'

// 搜索条件
const searchType = ref('customer_sn')
const searchKeyword = ref('')

// 分页
const currentPage = ref(1)
const pageSize = ref(10)
const total = ref(0)

// 阀门列表
const valveList = ref<any[]>([])
const selectedValve = ref<any>(null)

// 筛选条件
const filterCombinedSn1 = ref('')
const filterType1 = ref('')
const filterCombinedSn2 = ref('')
const filterType2 = ref('')
const filterCombinedSn3 = ref('')
const filterType3 = ref('')
const filterCombinedSn4 = ref('')
const filterType4 = ref('')
const filterCombinedSn5 = ref('')
const filterType5 = ref('')
const filterCombinedSn6 = ref('')
const filterType6 = ref('')
const filterCombinedSn7 = ref('')
const filterType7 = ref('')
const filterCombinedSn8 = ref('')
const filterCombinedSn9 = ref('')
const filterCombinedSn10 = ref('')

// 检测数据
const checkItemsData = ref([
  { item_no: 1, check_item: '运动测试', result: '', remark: '' },
  { item_no: 2, check_item: '气动泄漏', result: '', remark: '' },
  { item_no: 3, check_item: '氦检', result: '', remark: '' }
])
const checkOperator = ref('')
const checkDate = ref('')

// 维修前准备
const faultPhenomenon = ref<string[]>([])
const toolsReady = ref<string[]>([])
const replacementParts = ref<string[]>([])
const prepareOperator = ref('')
const prepareDate = ref('')

// 维修步骤
const disassemblySteps = ref<string[]>([])
const reassemblyResult = ref('')
const repairStepOperator = ref('')
const repairStepDate = ref('')

// 最终测试
const finalTestMotion = ref('')
const finalTestPneumatic = ref('')
const finalTestHelium = ref('')
const finalTestOperator = ref('')
const finalTestDate = ref('')

// 质保信息
const productWarranty = ref('')
const repairEngineer = ref('')
const reviewer1 = ref('')
const reviewer2 = ref('')
const warrantyOperator = ref('')
const warrantyDate = ref('')

// 图片数据
const attachmentImages = ref<string[]>([])
const packagingImages = ref<string[]>([])
const shipmentImages = ref<string[]>([])

// 测试数据
const testDataItems = ref([
  { item_name: '空气压降(60sec)', standard: '', test_value: '', result: '' },
  { item_name: 'Internal Leak Test', standard: '', test_value: '', result: '' },
  { item_name: 'External Leak Test', standard: '', test_value: '', result: '' }
])
const testDataOperator = ref('')
const testDataDate = ref('')

// 物料清单
const materialItems = ref<any[]>([])
const materialOperator = ref('')
const materialDate = ref('')

// 状态映射
const getStatusType = (status: string) => {
  const map: Record<string, string> = {
    'not_started': 'info',
    'in_progress': 'warning',
    'completed': 'success'
  }
  return map[status] || 'info'
}

const getStatusText = (status: string) => {
  const map: Record<string, string> = {
    'not_started': '未开始',
    'in_progress': '维修中',
    'completed': '已完成'
  }
  return map[status] || status
}

// 搜索阀门
const handleSearch = async () => {
  if (!searchKeyword.value.trim()) {
    ElMessage.warning('请输入搜索关键词')
    return
  }

  try {
    const response = await searchValvesList({
      sn: searchKeyword.value.trim(),
      search_type: searchType.value,
      page: currentPage.value,
      per_page: pageSize.value
    })

    valveList.value = response.list || []
    total.value = response.total || 0

    // 自动加载第一条记录的详细信息
    if (valveList.value.length > 0) {
      await handleRowClick(valveList.value[0])
    } else {
      ElMessage.info('未找到匹配的阀门记录')
      clearAllData()
    }
  } catch (error: any) {
    valveList.value = []
    total.value = 0
    clearAllData()
  }
}

// 点击行加载详细数据
const handleRowClick = async (row: any) => {
  selectedValve.value = row
  try {
    const record = await getRepairRecord(row.id)
    fillRecordData(record)
  } catch (error) {
    // 如果没有维修记录，清空数据
    clearAllData()
  }
}

// 填充维修记录数据
const fillRecordData = (record: any) => {
  if (!record) {
    clearAllData()
    return
  }

  // 检测数据
  checkItemsData.value = record.check_items?.length > 0
    ? record.check_items.map((item: any, index: number) => ({
        item_no: index + 1,
        check_item: item.item_name,
        result: item.result || '',
        remark: item.remark || ''
      }))
    : [
        { item_no: 1, check_item: '运动测试', result: '', remark: '' },
        { item_no: 2, check_item: '气动泄漏', result: '', remark: '' },
        { item_no: 3, check_item: '氦检', result: '', remark: '' }
      ]
  checkOperator.value = record.check_operator || ''
  checkDate.value = record.check_date || ''

  // 维修前准备
  faultPhenomenon.value = record.fault_phenomenon || []
  toolsReady.value = record.tools_ready || []
  replacementParts.value = record.replacement_parts || []
  prepareOperator.value = record.prepare_operator || ''
  prepareDate.value = record.prepare_date || ''

  // 维修步骤
  disassemblySteps.value = record.disassembly_steps || []
  reassemblyResult.value = record.reassembly_result || ''
  repairStepOperator.value = record.repair_step_operator || ''
  repairStepDate.value = record.repair_step_date || ''

  // 最终测试
  finalTestMotion.value = record.final_test_motion || ''
  finalTestPneumatic.value = record.final_test_pneumatic || ''
  finalTestHelium.value = record.final_test_helium || ''
  finalTestOperator.value = record.final_test_operator || ''
  finalTestDate.value = record.final_test_date || ''

  // 质保信息
  productWarranty.value = record.product_warranty || ''
  repairEngineer.value = record.repair_engineer || ''
  reviewer1.value = record.reviewer_1 || ''
  reviewer2.value = record.reviewer_2 || ''
  warrantyOperator.value = record.warranty_operator || ''
  warrantyDate.value = record.warranty_date || ''

  // 测试数据
  testDataItems.value = record.test_data_items?.length > 0
    ? record.test_data_items
    : [
        { item_name: '空气压降(60sec)', standard: '', test_value: '', result: '' },
        { item_name: 'Internal Leak Test', standard: '', test_value: '', result: '' },
        { item_name: 'External Leak Test', standard: '', test_value: '', result: '' }
      ]
  testDataOperator.value = record.test_data_operator || ''
  testDataDate.value = record.test_data_date || ''

  // 物料清单
  materialItems.value = record.material_items || []
  materialOperator.value = record.material_operator || ''
  materialDate.value = record.material_date || ''

  // 图片数据
  attachmentImages.value = record.attachments?.map((a: any) => a.file_path) || []
  packagingImages.value = record.packaging_images || []
  shipmentImages.value = record.shipment_images || []
}

// 清空所有数据
const clearAllData = () => {
  // 检测数据
  checkItemsData.value = [
    { item_no: 1, check_item: '运动测试', result: '', remark: '' },
    { item_no: 2, check_item: '气动泄漏', result: '', remark: '' },
    { item_no: 3, check_item: '氦检', result: '', remark: '' }
  ]
  checkOperator.value = ''
  checkDate.value = ''

  // 维修前准备
  faultPhenomenon.value = []
  toolsReady.value = []
  replacementParts.value = []
  prepareOperator.value = ''
  prepareDate.value = ''

  // 维修步骤
  disassemblySteps.value = []
  reassemblyResult.value = ''
  repairStepOperator.value = ''
  repairStepDate.value = ''

  // 最终测试
  finalTestMotion.value = ''
  finalTestPneumatic.value = ''
  finalTestHelium.value = ''
  finalTestOperator.value = ''
  finalTestDate.value = ''

  // 质保信息
  productWarranty.value = ''
  repairEngineer.value = ''
  reviewer1.value = ''
  reviewer2.value = ''
  warrantyOperator.value = ''
  warrantyDate.value = ''

  // 测试数据
  testDataItems.value = [
    { item_name: '空气压降(60sec)', standard: '', test_value: '', result: '' },
    { item_name: 'Internal Leak Test', standard: '', test_value: '', result: '' },
    { item_name: 'External Leak Test', standard: '', test_value: '', result: '' }
  ]
  testDataOperator.value = ''
  testDataDate.value = ''

  // 物料清单
  materialItems.value = []
  materialOperator.value = ''
  materialDate.value = ''

  // 图片数据
  attachmentImages.value = []
  packagingImages.value = []
  shipmentImages.value = []
}

// 重置
const handleReset = () => {
  searchKeyword.value = ''
  searchType.value = 'customer_sn'
  valveList.value = []
  total.value = 0
  selectedValve.value = null
  clearAllData()
}

// 分页
const handleSizeChange = (val: number) => {
  pageSize.value = val
  handleSearch()
}

const handlePageChange = (val: number) => {
  currentPage.value = val
  handleSearch()
}

// 初始化
onMounted(() => {
  // 页面加载时不自动查询
})
</script>

<style scoped lang="scss">
.repair-history {
  padding: 20px;
  background-color: #0d1b2a;
  min-height: 100vh;
  color: #fff;
}

.page-header {
  margin-bottom: 20px;
  
  h2 {
    margin: 0;
    font-size: 20px;
    color: #fff;
  }
}

.search-card {
  margin-bottom: 20px;
  background-color: #1b2838;
  border: 1px solid #2d3d4f;
  
  :deep(.el-card__body) {
    padding: 15px 20px;
  }
  
  .search-type {
    .el-radio {
      color: #fff;
    }
  }
}

.table-card {
  margin-bottom: 20px;
  background-color: #1b2838;
  border: 1px solid #2d3d4f;
  
  :deep(.el-card__body) {
    padding: 15px;
  }
}

.pagination-wrapper {
  display: flex;
  justify-content: flex-end;
  align-items: center;
  margin-top: 15px;
  gap: 15px;
  
  .total-text {
    color: #fff;
    font-size: 14px;
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

.section-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.section-title {
  font-size: 16px;
  font-weight: 500;
  color: #fff;
}

.section-filter {
  display: flex;
  align-items: center;
}

.result-ok {
  color: #67c23a;
}

.result-ng {
  color: #f56c6c;
}

.operator-info {
  display: flex;
  flex-direction: column;
  gap: 10px;
  margin-top: 15px;
  padding-top: 15px;
  border-top: 1px solid #2d3d4f;
  
  .info-row {
    display: flex;
    align-items: center;
    gap: 10px;
    
    .info-label {
      color: #fff;
      font-size: 14px;
      min-width: 60px;
    }
  }
}

.checkbox-group {
  display: flex;
  flex-direction: column;
  gap: 15px;
  
  .checkbox-row {
    display: flex;
    align-items: flex-start;
    gap: 15px;
    
    .row-label {
      color: #fff;
      font-size: 14px;
      min-width: 100px;
      white-space: nowrap;
    }
    
    :deep(.el-checkbox) {
      color: #fff;
      margin-right: 20px;
    }
    
    :deep(.el-radio) {
      color: #fff;
      margin-right: 20px;
    }
  }
}

.test-results {
  display: flex;
  gap: 40px;
  
  .test-row {
    display: flex;
    align-items: center;
    gap: 15px;
    
    .test-label {
      color: #fff;
      font-size: 14px;
    }
    
    :deep(.el-radio) {
      color: #fff;
    }
  }
}

.warranty-info {
  .info-row-inline {
    display: flex;
    align-items: center;
    flex-wrap: wrap;
    gap: 10px;
    
    .info-label {
      color: #fff;
      font-size: 14px;
    }
  }
}

.image-gallery {
  min-height: 100px;
  display: flex;
  gap: 15px;
  flex-wrap: wrap;

  .image-item {
    border-radius: 4px;
    overflow: hidden;
    border: 1px solid #2d3d4f;
  }

  .no-image {
    color: #909399;
    font-size: 14px;
    padding: 40px;
    text-align: center;
    width: 100%;
  }
}

// 表格样式
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

// 表单样式
:deep(.el-input__wrapper) {
  background-color: #243447;
}

:deep(.el-input__inner) {
  background-color: transparent;
  color: #fff;
}

:deep(.el-radio) {
  color: #fff;
}

:deep(.el-checkbox) {
  color: #fff;
}
</style>
