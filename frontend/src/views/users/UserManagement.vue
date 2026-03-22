<template>
  <div class="user-management">
    <!-- 页面标题 -->
    <div class="page-header">
      <h2>用户管理</h2>
    </div>

    <!-- 用户查询区域 -->
    <div class="search-section">
      <div class="section-title">用户查询</div>
      <div class="search-form">
        <el-input
          v-model="searchUsername"
          placeholder="请输入用户名"
          clearable
          style="width: 240px;"
          @keyup.enter="handleSearch"
        />
        <el-button type="primary" @click="handleSearch">查询用户</el-button>
        <el-button @click="handleSearchAll">查询所有用户</el-button>
        <el-button @click="handleReset">清空</el-button>
      </div>
    </div>

    <!-- 用户列表 -->
    <div class="list-section">
      <div class="list-header">
        <span class="list-title">用户列表</span>
        <el-button type="primary" @click="handleNewUser">
          <el-icon><Plus /></el-icon>新建用户
        </el-button>
      </div>
      <el-table :data="userList" style="width: 100%;" class="data-table" v-loading="loading">
        <el-table-column prop="username" label="用户名" min-width="140" />
        <el-table-column prop="chinese_name" label="中文名" min-width="120" />
        <el-table-column prop="role" label="角色" min-width="120">
          <template #default="{ row }">
            <el-tag :type="roleTagType(row.role)" size="small">
              {{ roleLabel(row.role) }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="email" label="邮箱" min-width="180" />
        <el-table-column prop="created_at" label="创建时间" min-width="160" />
        <el-table-column prop="updated_at" label="修改时间" min-width="160" />
        <el-table-column label="操作" width="140" fixed="right">
          <template #default="{ row }">
            <el-button type="primary" link size="small" @click="handleEditUser(row)">编辑</el-button>
            <el-button type="danger" link size="small" @click="handleDeleteUser(row)">删除</el-button>
          </template>
        </el-table-column>
      </el-table>

      <!-- 空状态提示 -->
      <div v-if="!loading && userList.length === 0" class="empty-tip">
        请输入用户名查询用户信息
      </div>
    </div>

    <!-- 新增/编辑弹窗 -->
    <el-dialog
      v-model="dialogVisible"
      :title="dialogTitle"
      width="550px"
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
            <el-form-item label="用户名" prop="username">
              <el-input v-model="form.username" placeholder="请输入用户名" :disabled="isEdit" />
            </el-form-item>
          </el-col>
          <el-col :span="12">
            <el-form-item label="中文名" prop="chinese_name">
              <el-input v-model="form.chinese_name" placeholder="请输入中文名" />
            </el-form-item>
          </el-col>
        </el-row>
        <el-row :gutter="20">
          <el-col :span="12">
            <el-form-item label="角色" prop="role">
              <el-select v-model="form.role" placeholder="请选择角色" style="width: 100%;">
                <el-option label="管理员" value="admin" />
                <el-option label="工程师" value="engineer" />
                <el-option label="操作员" value="operator" />
              </el-select>
            </el-form-item>
          </el-col>
          <el-col :span="12">
            <el-form-item label="邮箱" prop="email">
              <el-input v-model="form.email" placeholder="请输入邮箱" />
            </el-form-item>
          </el-col>
        </el-row>
        <el-form-item v-if="!isEdit" label="密码" prop="password" :rules="isEdit ? [] : rules.password">
          <el-input v-model="form.password" type="password" placeholder="请输入密码" show-password />
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="dialogVisible = false">取消</el-button>
        <el-button type="primary" @click="handleSaveUser">确定</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup lang="ts">
import { ref, reactive, onMounted } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import { Plus } from '@element-plus/icons-vue'
import { getUserList, createUser, updateUser, deleteUser } from '../../api/users'

// ========== 搜索 ==========
const searchUsername = ref('')
const loading = ref(false)

// ========== 数据列表 ==========
interface User {
  id: number
  username: string
  chinese_name: string
  role: 'admin' | 'engineer' | 'operator'
  email: string
  created_at?: string
  updated_at?: string
}

const userList = ref<User[]>([])

// ========== 弹窗和表单 ==========
const dialogVisible = ref(false)
const dialogTitle = ref('新增用户')
const formRef = ref()
const isEdit = ref(false)
const currentId = ref<number | null>(null)

const form = reactive({
  username: '',
  chinese_name: '',
  role: 'operator' as 'admin' | 'engineer' | 'operator',
  email: '',
  password: ''
})

const rules = {
  username: [{ required: true, message: '请输入用户名', trigger: 'blur' }],
  chinese_name: [{ required: true, message: '请输入中文名', trigger: 'blur' }],
  role: [{ required: true, message: '请选择角色', trigger: 'change' }],
  email: [
    { required: true, message: '请输入邮箱', trigger: 'blur' },
    { type: 'email', message: '请输入正确的邮箱格式', trigger: 'blur' }
  ],
  password: [{ required: true, message: '请输入密码', trigger: 'blur' }]
}

// ========== 角色映射 ==========
const roleLabel = (role: string) => {
  const map: Record<string, string> = {
    admin: '管理员',
    engineer: '工程师',
    operator: '操作员'
  }
  return map[role] || role
}

const roleTagType = (role: string): any => {
  const map: Record<string, any> = {
    admin: 'danger',
    engineer: 'warning',
    operator: 'info'
  }
  return map[role] || 'info'
}

// ========== 方法 ==========
const loadData = async (showAll: boolean = false) => {
  loading.value = true
  try {
    const data = await getUserList({
      username: showAll ? undefined : searchUsername.value || undefined,
      page: 1,
      per_page: 100
    }) as any
    userList.value = data.items || []
  } catch (error: any) {
    ElMessage.error(error.message || '获取用户列表失败')
  } finally {
    loading.value = false
  }
}

const handleSearch = () => {
  if (!searchUsername.value.trim()) {
    ElMessage.warning('请输入用户名')
    return
  }
  loadData(false)
}

const handleSearchAll = () => {
  searchUsername.value = ''
  loadData(true)
}

const handleReset = () => {
  searchUsername.value = ''
  userList.value = []
}

const handleNewUser = () => {
  isEdit.value = false
  currentId.value = null
  dialogTitle.value = '新增用户'
  Object.assign(form, {
    username: '',
    chinese_name: '',
    role: 'operator',
    email: '',
    password: ''
  })
  dialogVisible.value = true
}

const handleEditUser = (row: User) => {
  isEdit.value = true
  currentId.value = row.id
  dialogTitle.value = '编辑用户'
  Object.assign(form, {
    username: row.username,
    chinese_name: row.chinese_name,
    role: row.role,
    email: row.email,
    password: ''
  })
  dialogVisible.value = true
}

const handleSaveUser = async () => {
  if (!formRef.value) return
  try {
    await formRef.value.validate()

    if (isEdit.value && currentId.value) {
      // 编辑
      await updateUser(currentId.value, {
        chinese_name: form.chinese_name,
        role: form.role,
        email: form.email,
        password: form.password
      })
      ElMessage.success('更新成功')
    } else {
      // 新增
      await createUser({
        username: form.username,
        chinese_name: form.chinese_name,
        role: form.role,
        email: form.email,
        password: form.password
      })
      ElMessage.success('新增成功')
    }

    dialogVisible.value = false
    loadData(true) // 重新加载数据
  } catch (error: any) {
    ElMessage.error(error.message || '保存失败')
  }
}

const handleDeleteUser = async (row: User) => {
  try {
    await ElMessageBox.confirm(`确认删除用户 "${row.username}"？`, '提示', {
      confirmButtonText: '确定',
      cancelButtonText: '取消',
      type: 'warning'
    })
    await deleteUser(row.id)
    ElMessage.success('删除成功')
    loadData(true) // 重新加载数据
  } catch (error: any) {
    if (error !== 'cancel') {
      ElMessage.error(error.message || '删除失败')
    }
  }
}

// ========== 初始化 ==========
onMounted(() => {
  // 默认不加载数据，等待用户查询
})
</script>

<style scoped lang="scss">
.user-management {
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

// 查询区域
.search-section {
  background-color: #1a1a1a;
  border: 1px solid #2d2d2d;
  border-radius: 6px;
  margin-bottom: 20px;
  overflow: hidden;
}

.section-title {
  padding: 16px 24px;
  font-size: 16px;
  font-weight: 500;
  color: #fff;
  border-bottom: 1px solid #2d2d2d;
  background-color: #1a1a1a;
}

.search-form {
  display: flex;
  align-items: center;
  gap: 12px;
  padding: 20px 24px;
}

// 列表区域
.list-section {
  background-color: #1a1a1a;
  border: 1px solid #2d2d2d;
  border-radius: 6px;
  overflow: hidden;
}

.list-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 16px 24px;
  border-bottom: 1px solid #2d2d2d;
  background-color: #1a1a1a;
}

.list-title {
  font-size: 16px;
  font-weight: 500;
  color: #fff;
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

.empty-tip {
  text-align: center;
  padding: 60px 20px;
  color: #666;
  font-size: 14px;
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
  .el-select .el-input__wrapper {
    background-color: #111;
    box-shadow: 0 0 0 1px #333 inset;
  }
  .el-input__inner {
    color: #fff;
    &::placeholder { color: #555; }
  }
}
</style>
