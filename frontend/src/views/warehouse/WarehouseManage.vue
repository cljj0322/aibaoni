<template>
  <div class="warehouse-manage">
    <!-- 页面标题 -->
    <div class="page-header">
      <h2>仓储管理</h2>
    </div>

    <!-- 标签页 -->
    <el-tabs v-model="activeTab" class="warehouse-tabs">
      <!-- 库存管理 -->
      <el-tab-pane label="库存管理" name="inventory">
        <!-- 搜索区域 -->
        <div class="search-area">
          <el-radio-group v-model="searchType" class="search-type">
            <el-radio label="code">按编码查询</el-radio>
            <el-radio label="exact">精确查询(编码@批次)</el-radio>
          </el-radio-group>
          <el-input 
            v-model="searchKeyword" 
            placeholder="请输入编码"
            style="width: 250px; margin-left: 15px;"
          />
          <el-button type="primary" style="margin-left: 10px;" @click="handleSearch">
            <el-icon><Search /></el-icon>查询
          </el-button>
          <el-button style="margin-left: 10px;" @click="handleRefresh">
            <el-icon><Refresh /></el-icon>刷新
          </el-button>
          <el-button 
            :type="showAddForm ? 'info' : 'primary'" 
            style="margin-left: 10px;" 
            @click="toggleAddForm"
          >
            <el-icon><Plus /></el-icon>{{ showAddForm ? '关闭新增' : '新增库存' }}
          </el-button>
        </div>

        <!-- 新增库存表单区域 -->
        <div v-show="showAddForm" class="add-form-section">
          <div class="add-form-header">
            <span class="add-form-title">新增库存</span>
            <el-button link @click="toggleAddForm">
              <el-icon><Close /></el-icon>关闭
            </el-button>
          </div>
          <el-form 
            ref="inventoryFormRef"
            :model="inventoryForm" 
            :rules="inventoryRules"
            label-width="90px"
            class="inventory-form"
          >
            <!-- 第一行：编码、批次号、品目名 -->
            <el-row :gutter="20">
              <el-col :span="8">
                <el-form-item label="编码" prop="code">
                  <el-input v-model="inventoryForm.code" placeholder="请输入编码" />
                </el-form-item>
              </el-col>
              <el-col :span="8">
                <el-form-item label="批次号" prop="batch">
                  <el-input v-model="inventoryForm.batch" placeholder="请输入批次号" />
                </el-form-item>
              </el-col>
              <el-col :span="8">
                <el-form-item label="品目名" prop="name">
                  <el-input v-model="inventoryForm.name" placeholder="请输入品目名" />
                </el-form-item>
              </el-col>
            </el-row>
            
            <!-- 第二行：规格信息、材质、材质分类 -->
            <el-row :gutter="20">
              <el-col :span="8">
                <el-form-item label="规格信息" prop="spec">
                  <el-input v-model="inventoryForm.spec" placeholder="请输入规格信息" />
                </el-form-item>
              </el-col>
              <el-col :span="8">
                <el-form-item label="材质" prop="material">
                  <el-input v-model="inventoryForm.material" placeholder="请输入材质" />
                </el-form-item>
              </el-col>
              <el-col :span="8">
                <el-form-item label="材质分类" prop="material_category">
                  <el-input v-model="inventoryForm.material_category" placeholder="请输入材质分类" />
                </el-form-item>
              </el-col>
            </el-row>
            
            <!-- 第三行：颜色、库别、单位 -->
            <el-row :gutter="20">
              <el-col :span="8">
                <el-form-item label="颜色" prop="color">
                  <el-input v-model="inventoryForm.color" placeholder="请输入颜色" />
                </el-form-item>
              </el-col>
              <el-col :span="8">
                <el-form-item label="库别" prop="warehouse">
                  <el-input v-model="inventoryForm.warehouse" placeholder="请输入库别" />
                </el-form-item>
              </el-col>
              <el-col :span="8">
                <el-form-item label="单位" prop="unit">
                  <el-input v-model="inventoryForm.unit" placeholder="请输入单位" />
                </el-form-item>
              </el-col>
            </el-row>
            
            <!-- 第四行：产地、品类、现有库存 -->
            <el-row :gutter="20">
              <el-col :span="8">
                <el-form-item label="产地" prop="origin">
                  <el-input v-model="inventoryForm.origin" placeholder="请输入产地" />
                </el-form-item>
              </el-col>
              <el-col :span="8">
                <el-form-item label="品类" prop="category">
                  <el-input v-model="inventoryForm.category" placeholder="请输入品类" />
                </el-form-item>
              </el-col>
              <el-col :span="8">
                <el-form-item label="现有库存" prop="stock">
                  <el-input-number 
                    v-model="inventoryForm.stock" 
                    :min="0" 
                    style="width: 100%;" 
                    placeholder="请输入现有库存"
                  />
                </el-form-item>
              </el-col>
            </el-row>
            
            <!-- 按钮行 -->
            <el-row>
              <el-col :span="24">
                <div class="add-form-actions">
                  <el-button type="primary" @click="handleSaveInventory">提交</el-button>
                  <el-button @click="handleResetInventoryForm">重置</el-button>
                </div>
              </el-col>
            </el-row>
          </el-form>
        </div>

        <!-- 库存表格 -->
        <el-table :data="inventoryList" border style="width: 100%" class="data-table">
          <el-table-column type="index" label="ID" width="50" />
          <el-table-column prop="code" label="编码" min-width="120" />
          <el-table-column prop="name" label="品目名" min-width="150" />
          <el-table-column prop="spec" label="规格信息" min-width="120" />
          <el-table-column prop="material" label="材质" width="80" />
          <el-table-column prop="material_category" label="材质分类" width="100" />
          <el-table-column prop="color" label="颜色" width="80" />
          <el-table-column prop="warehouse" label="库别" width="60" />
          <el-table-column prop="unit" label="单位" width="60" />
          <el-table-column prop="origin" label="产地" width="80" />
          <el-table-column prop="category" label="品类" width="80" />
          <el-table-column prop="stock" label="现有库存" width="90" />
          <el-table-column prop="batch" label="批次" width="100" />
          <el-table-column label="操作" width="200" fixed="right">
            <template #default="{ row }">
              <el-button type="primary" link @click="handleInbound(row)">
                <el-icon><Plus /></el-icon>入库
              </el-button>
              <el-button type="warning" link @click="handleOutbound(row)">
                <el-icon><Minus /></el-icon>出库
              </el-button>
              <el-button type="danger" link @click="handleDelete(row)">
                <el-icon><Delete /></el-icon>删
              </el-button>
            </template>
          </el-table-column>
        </el-table>

        <!-- 分页 -->
        <div class="pagination-wrapper">
          <el-pagination
            v-model:current-page="currentPage"
            v-model:page-size="pageSize"
            :page-sizes="[10, 20, 50, 100]"
            layout="total, sizes, prev, pager, next"
            :total="total"
            @size-change="handleSizeChange"
            @current-change="handlePageChange"
          />
        </div>
      </el-tab-pane>

      <!-- 物料编码管理 -->
      <el-tab-pane label="物料编码管理" name="material">
        <!-- 搜索区域 -->
        <div class="search-area">
          <el-input 
            v-model="materialSearchKeyword" 
            placeholder="请输入物料编码或名称"
            style="width: 300px;"
          />
          <el-button type="primary" style="margin-left: 10px;" @click="handleMaterialSearch">
            <el-icon><Search /></el-icon>查询
          </el-button>
          <el-button style="margin-left: 10px;" @click="handleMaterialRefresh">
            <el-icon><Refresh /></el-icon>刷新
          </el-button>
          <el-button type="primary" style="margin-left: 10px;" @click="handleAddMaterial">
            <el-icon><Plus /></el-icon>新增物料
          </el-button>
        </div>

        <!-- 物料表格 -->
        <el-table :data="materialList" border style="width: 100%" class="data-table">
          <el-table-column type="index" label="序号" width="60" />
          <el-table-column prop="material_code" label="物料编码" min-width="120" />
          <el-table-column prop="material_name" label="物料名称" min-width="150" />
          <el-table-column prop="specification" label="规格型号" min-width="120" />
          <el-table-column prop="category" label="分类" width="100" />
          <el-table-column prop="unit" label="单位" width="80" />
          <el-table-column prop="brand" label="品牌" width="100" />
          <el-table-column prop="supplier" label="供应商" min-width="120" />
          <el-table-column prop="remark" label="备注" min-width="150" />
          <el-table-column label="操作" width="150" fixed="right">
            <template #default="{ row }">
              <el-button type="primary" link @click="handleEditMaterial(row)">编辑</el-button>
              <el-button type="danger" link @click="handleDeleteMaterial(row)">删除</el-button>
            </template>
          </el-table-column>
        </el-table>

        <!-- 分页 -->
        <div class="pagination-wrapper">
          <el-pagination
            v-model:current-page="materialPage"
            v-model:page-size="materialPageSize"
            :page-sizes="[10, 20, 50, 100]"
            layout="total, sizes, prev, pager, next"
            :total="materialTotal"
            @size-change="handleMaterialSizeChange"
            @current-change="handleMaterialPageChange"
          />
        </div>
      </el-tab-pane>
    </el-tabs>

    <!-- 入库弹窗 -->
    <el-dialog
      v-model="inboundDialogVisible"
      title="入库"
      width="400px"
    >
      <el-form :model="inboundForm" label-width="80px">
        <el-form-item label="物料编码">
          <el-input v-model="inboundForm.code" disabled />
        </el-form-item>
        <el-form-item label="品目名">
          <el-input v-model="inboundForm.name" disabled />
        </el-form-item>
        <el-form-item label="入库数量">
          <el-input-number v-model="inboundForm.quantity" :min="1" style="width: 100%;" />
        </el-form-item>
        <el-form-item label="备注">
          <el-input v-model="inboundForm.remark" type="textarea" :rows="2" />
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="inboundDialogVisible = false">取消</el-button>
        <el-button type="primary" @click="handleConfirmInbound">确定</el-button>
      </template>
    </el-dialog>

    <!-- 出库弹窗 -->
    <el-dialog
      v-model="outboundDialogVisible"
      title="出库"
      width="400px"
    >
      <el-form :model="outboundForm" label-width="80px">
        <el-form-item label="物料编码">
          <el-input v-model="outboundForm.code" disabled />
        </el-form-item>
        <el-form-item label="品目名">
          <el-input v-model="outboundForm.name" disabled />
        </el-form-item>
        <el-form-item label="出库数量">
          <el-input-number v-model="outboundForm.quantity" :min="1" style="width: 100%;" />
        </el-form-item>
        <el-form-item label="备注">
          <el-input v-model="outboundForm.remark" type="textarea" :rows="2" />
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="outboundDialogVisible = false">取消</el-button>
        <el-button type="primary" @click="handleConfirmOutbound">确定</el-button>
      </template>
    </el-dialog>

    <!-- 新增/编辑物料弹窗 -->
    <el-dialog
      v-model="materialDialogVisible"
      :title="materialDialogTitle"
      width="600px"
    >
      <el-form :model="materialForm" label-width="100px">
        <el-form-item label="物料编码">
          <el-input v-model="materialForm.material_code" placeholder="请输入物料编码" />
        </el-form-item>
        <el-form-item label="物料名称">
          <el-input v-model="materialForm.material_name" placeholder="请输入物料名称" />
        </el-form-item>
        <el-form-item label="规格型号">
          <el-input v-model="materialForm.specification" placeholder="请输入规格型号" />
        </el-form-item>
        <el-row :gutter="20">
          <el-col :span="12">
            <el-form-item label="分类">
              <el-input v-model="materialForm.category" placeholder="请输入分类" />
            </el-form-item>
          </el-col>
          <el-col :span="12">
            <el-form-item label="单位">
              <el-input v-model="materialForm.unit" placeholder="请输入单位" />
            </el-form-item>
          </el-col>
        </el-row>
        <el-row :gutter="20">
          <el-col :span="12">
            <el-form-item label="品牌">
              <el-input v-model="materialForm.brand" placeholder="请输入品牌" />
            </el-form-item>
          </el-col>
          <el-col :span="12">
            <el-form-item label="供应商">
              <el-input v-model="materialForm.supplier" placeholder="请输入供应商" />
            </el-form-item>
          </el-col>
        </el-row>
        <el-form-item label="备注">
          <el-input v-model="materialForm.remark" type="textarea" :rows="3" placeholder="请输入备注" />
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="materialDialogVisible = false">取消</el-button>
        <el-button type="primary" @click="handleSaveMaterial">确定</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup lang="ts">
import { ref, reactive, onMounted } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import { Search, Refresh, Plus, Minus, Delete, Close } from '@element-plus/icons-vue'
import {
  getInventoryList,
  createInventory,
  updateInventory,
  deleteInventory,
  inboundInventory,
  outboundInventory,
  getMaterialList,
  createMaterial,
  updateMaterial,
  deleteMaterial
} from '@/api/warehouse'

// 当前标签页
const activeTab = ref('inventory')

// ========== 库存管理 ==========
const searchType = ref('code')
const searchKeyword = ref('')
const currentPage = ref(1)
const pageSize = ref(10)
const total = ref(0)
const inventoryList = ref<any[]>([])

// 显示新增表单
const showAddForm = ref(false)

// 切换新增表单显示
const toggleAddForm = () => {
  showAddForm.value = !showAddForm.value
  if (showAddForm.value) {
    handleResetInventoryForm()
  }
}

// 库存弹窗
const inventoryDialogVisible = ref(false)
const inventoryDialogTitle = ref('新增库存')
const inventoryFormRef = ref<any>(null)
const inventoryForm = reactive({
  id: null as number | null,
  code: '',
  name: '',
  spec: '',
  material: '',
  material_category: '',
  color: '',
  warehouse: 'A',
  unit: '',
  origin: '',
  category: '',
  stock: 0,
  batch: ''
})

// 表单验证规则
const inventoryRules = {
  code: [{ required: true, message: '请输入编码', trigger: 'blur' }],
  batch: [{ required: true, message: '请输入批次号', trigger: 'blur' }],
  name: [{ required: true, message: '请输入品目名', trigger: 'blur' }],
  stock: [{ required: true, message: '请输入现有库存', trigger: 'blur' }]
}

// 入库弹窗
const inboundDialogVisible = ref(false)
const inboundForm = reactive({
  id: null as number | null,
  code: '',
  name: '',
  quantity: 1,
  remark: ''
})

// 出库弹窗
const outboundDialogVisible = ref(false)
const outboundForm = reactive({
  id: null as number | null,
  code: '',
  name: '',
  quantity: 1,
  remark: ''
})

// ========== 物料编码管理 ==========
const materialSearchKeyword = ref('')
const materialPage = ref(1)
const materialPageSize = ref(10)
const materialTotal = ref(0)
const materialList = ref<any[]>([])

// 物料弹窗
const materialDialogVisible = ref(false)
const materialDialogTitle = ref('新增物料')
const materialForm = reactive({
  id: null as number | null,
  material_code: '',
  material_name: '',
  specification: '',
  category: '',
  unit: '',
  brand: '',
  supplier: '',
  remark: ''
})

// 搜索库存
const handleSearch = async () => {
  try {
    const data = await getInventoryList({
      search_type: searchType.value,
      keyword: searchKeyword.value,
      page: currentPage.value,
      per_page: pageSize.value
    }) as any
    inventoryList.value = data.items || []
    total.value = data.total || 0
  } catch (error) {
    ElMessage.error('获取库存列表失败')
  }
}

// 刷新库存
const handleRefresh = async () => {
  console.log('刷新按钮被点击')
  searchKeyword.value = ''
  searchType.value = 'code'
  currentPage.value = 1
  console.log('准备调用handleSearch，参数：', {
    search_type: searchType.value,
    keyword: searchKeyword.value,
    page: currentPage.value,
    per_page: pageSize.value
  })
  await handleSearch()
  console.log('handleSearch调用完成')
}

// 新增库存
const handleAddInventory = () => {
  inventoryDialogTitle.value = '新增库存'
  Object.assign(inventoryForm, {
    id: null,
    code: '',
    name: '',
    spec: '',
    material: '',
    material_category: '',
    color: '',
    warehouse: 'A',
    unit: '',
    origin: '',
    category: '',
    stock: 0,
    batch: ''
  })
  inventoryDialogVisible.value = true
}

// 重置表单
const handleResetInventoryForm = () => {
  if (inventoryFormRef.value) {
    inventoryFormRef.value.resetFields()
  }
  Object.assign(inventoryForm, {
    id: null,
    code: '',
    name: '',
    spec: '',
    material: '',
    material_category: '',
    color: '',
    warehouse: 'A',
    unit: '',
    origin: '',
    category: '',
    stock: 0,
    batch: ''
  })
}

// 保存库存
const handleSaveInventory = async () => {
  if (!inventoryFormRef.value) return

  try {
    await inventoryFormRef.value.validate()

    if (inventoryForm.id) {
      // 更新
      await updateInventory(inventoryForm.id, inventoryForm)
      ElMessage.success('更新成功')
    } else {
      // 新增
      await createInventory(inventoryForm)
      ElMessage.success('新增成功')
    }
    showAddForm.value = false
    await handleSearch()
  } catch (error: any) {
    if (error.message) {
      ElMessage.error(error.message)
    } else {
      ElMessage.error('保存失败')
    }
  }
}

// 入库
const handleInbound = (row: any) => {
  inboundForm.id = row.id
  inboundForm.code = row.code
  inboundForm.name = row.name
  inboundForm.quantity = 1
  inboundForm.remark = ''
  inboundDialogVisible.value = true
}

// 确认入库
const handleConfirmInbound = async () => {
  try {
    if (!inboundForm.id) return
    await inboundInventory(inboundForm.id, {
      quantity: inboundForm.quantity,
      remark: inboundForm.remark
    })
    ElMessage.success('入库成功')
    inboundDialogVisible.value = false
    await handleSearch()
  } catch (error) {
    ElMessage.error('入库失败')
  }
}

// 出库
const handleOutbound = (row: any) => {
  outboundForm.id = row.id
  outboundForm.code = row.code
  outboundForm.name = row.name
  outboundForm.quantity = 1
  outboundForm.remark = ''
  outboundDialogVisible.value = true
}

// 确认出库
const handleConfirmOutbound = async () => {
  try {
    if (!outboundForm.id) return
    await outboundInventory(outboundForm.id, {
      quantity: outboundForm.quantity,
      remark: outboundForm.remark
    })
    ElMessage.success('出库成功')
    outboundDialogVisible.value = false
    await handleSearch()
  } catch (error) {
    ElMessage.error('出库失败')
  }
}

// 删除库存
const handleDelete = (row: any) => {
  ElMessageBox.confirm('确认删除该库存记录？', '提示', {
    confirmButtonText: '确定',
    cancelButtonText: '取消',
    type: 'warning'
  }).then(async () => {
    try {
      await deleteInventory(row.id)
      ElMessage.success('删除成功')
      await handleSearch()
    } catch (error) {
      ElMessage.error('删除失败')
    }
  })
}

// 分页
const handleSizeChange = async (val: number) => {
  pageSize.value = val
  await handleSearch()
}

const handlePageChange = async (val: number) => {
  currentPage.value = val
  await handleSearch()
}

// ========== 物料编码管理 ==========
const handleMaterialSearch = async () => {
  try {
    const data = await getMaterialList({
      keyword: materialSearchKeyword.value,
      page: materialPage.value,
      per_page: materialPageSize.value
    }) as any
    materialList.value = data.items || []
    materialTotal.value = data.total || 0
  } catch (error) {
    ElMessage.error('获取物料列表失败')
  }
}

const handleMaterialRefresh = () => {
  materialSearchKeyword.value = ''
  materialPage.value = 1
  handleMaterialSearch()
}

const handleAddMaterial = () => {
  materialDialogTitle.value = '新增物料'
  Object.assign(materialForm, {
    id: null,
    material_code: '',
    material_name: '',
    specification: '',
    category: '',
    unit: '',
    brand: '',
    supplier: '',
    remark: ''
  })
  materialDialogVisible.value = true
}

const handleEditMaterial = (row: any) => {
  materialDialogTitle.value = '编辑物料'
  Object.assign(materialForm, row)
  materialDialogVisible.value = true
}

const handleSaveMaterial = async () => {
  try {
    if (materialForm.id) {
      // 更新
      const res = await updateMaterial(materialForm.id, materialForm)
      if (res.data.code === 200) {
        ElMessage.success('更新成功')
      }
    } else {
      // 新增
      const res = await createMaterial(materialForm)
      if (res.data.code === 200) {
        ElMessage.success('新增成功')
      }
    }
    materialDialogVisible.value = false
    handleMaterialSearch()
  } catch (error) {
    ElMessage.error('保存失败')
  }
}

const handleDeleteMaterial = (row: any) => {
  ElMessageBox.confirm('确认删除该物料？', '提示', {
    confirmButtonText: '确定',
    cancelButtonText: '取消',
    type: 'warning'
  }).then(async () => {
    try {
      const res = await deleteMaterial(row.id)
      if (res.data.code === 200) {
        ElMessage.success('删除成功')
        handleMaterialSearch()
      } else {
        ElMessage.error(res.data.message || '删除失败')
      }
    } catch (error) {
      ElMessage.error('删除失败')
    }
  })
}

const handleMaterialSizeChange = (val: number) => {
  materialPageSize.value = val
  handleMaterialSearch()
}

const handleMaterialPageChange = (val: number) => {
  materialPage.value = val
  handleMaterialSearch()
}

// 初始化
onMounted(async () => {
  await handleSearch()
  await handleMaterialSearch()
})
</script>

<style scoped lang="scss">
.warehouse-manage {
  padding: 20px;
  background-color: #0d1b2a;
  min-height: 100vh;
  color: #fff;
}

.page-header {
  margin-bottom: 20px;
  
  h2 {
    margin: 0;
    font-size: 24px;
    color: #fff;
  }
}

.warehouse-tabs {
  :deep(.el-tabs__header) {
    margin-bottom: 20px;
  }
  
  :deep(.el-tabs__nav-wrap::after) {
    background-color: #2d3d4f;
  }
  
  :deep(.el-tabs__item) {
    color: #bfcbd9;
    font-size: 15px;
    
    &.is-active {
      color: #409eff;
    }
    
    &:hover {
      color: #409eff;
    }
  }
  
  :deep(.el-tabs__active-bar) {
    background-color: #409eff;
  }
}

.search-area {
  display: flex;
  align-items: center;
  margin-bottom: 20px;
  padding: 15px;
  background-color: #1b2838;
  border-radius: 4px;
  
  .search-type {
    .el-radio {
      color: #fff;
    }
  }
}

// 新增表单区域
.add-form-section {
  margin-bottom: 20px;
  background-color: #1b2838;
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
  font-size: 16px;
  font-weight: 500;
  color: #fff;
}

.add-form-actions {
  display: flex;
  justify-content: flex-start;
  gap: 10px;
  padding: 15px 20px;
  border-top: 1px solid #2d3d4f;
  margin-top: 10px;
}

// 库存表单样式
.inventory-form {
  padding: 20px;
  
  .el-form-item {
    margin-bottom: 18px;
  }
  
  .el-form-item__label {
    color: #fff;
    font-size: 14px;
  }
  
  .el-input__wrapper {
    background-color: #243447;
    box-shadow: 0 0 0 1px #2d3d4f inset;
  }
  
  .el-input__inner {
    background-color: transparent;
    color: #fff;
    
    &::placeholder {
      color: #606266;
    }
  }
  
  .el-input-number {
    .el-input__wrapper {
      background-color: #243447;
    }
    
    .el-input-number__decrease,
    .el-input-number__increase {
      background-color: #2d3d4f;
      border-color: #2d3d4f;
      color: #fff;
      
      &:hover {
        color: #409eff;
      }
    }
  }
}

.data-table {
  background-color: #1b2838;
  
  :deep(.el-table__header-wrapper) {
    th.el-table__cell {
      background-color: #243447;
      color: #fff;
      font-weight: 500;
    }
  }
  
  :deep(.el-table__body-wrapper) {
    td.el-table__cell {
      background-color: #1b2838;
      color: #fff;
    }
  }
  
  :deep(.el-table--border) {
    border-color: #2d3d4f;
  }
  
  :deep(.el-table--border .el-table__cell) {
    border-color: #2d3d4f;
  }
}

.pagination-wrapper {
  display: flex;
  justify-content: flex-end;
  margin-top: 20px;
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

:deep(.el-dialog) {
  background-color: #1b2838;
  
  .el-dialog__title {
    color: #fff;
  }
  
  .el-form-item__label {
    color: #fff;
  }
  
  .el-dialog__header {
    border-bottom: 1px solid #2d3d4f;
    margin-right: 0;
    padding: 15px 20px;
  }
  
  .el-dialog__body {
    padding: 20px;
  }
  
  .el-dialog__footer {
    border-top: 1px solid #2d3d4f;
    padding: 15px 20px;
  }
}

// 库存弹窗表单样式
:deep(.inventory-form) {
  .el-form-item {
    margin-bottom: 18px;
  }
  
  .el-form-item__label {
    color: #fff;
    font-size: 14px;
  }
  
  .el-input__wrapper {
    background-color: #243447;
    box-shadow: 0 0 0 1px #2d3d4f inset;
  }
  
  .el-input__inner {
    background-color: transparent;
    color: #fff;
    
    &::placeholder {
      color: #606266;
    }
  }
  
  .el-input-number {
    .el-input__wrapper {
      background-color: #243447;
    }
    
    .el-input-number__decrease,
    .el-input-number__increase {
      background-color: #2d3d4f;
      border-color: #2d3d4f;
      color: #fff;
      
      &:hover {
        color: #409eff;
      }
    }
  }
}
</style>
