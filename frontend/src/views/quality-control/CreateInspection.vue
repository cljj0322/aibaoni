<template>
  <div class="create-inspection">
    <!-- 标题区 -->
    <div class="section-card">
      <div class="section-title-bar">新建质量检查记录</div>

      <el-form
        ref="formRef"
        :model="form"
        :rules="rules"
        label-position="top"
        class="inspection-form"
      >
        <!-- 生产计划ID -->
        <el-form-item label="生产计划ID" prop="plan_id" class="required-label">
          <el-input v-model="form.plan_id" placeholder="" />
        </el-form-item>

        <!-- 产品代码 -->
        <el-form-item label="产品代码" prop="product_code" class="required-label">
          <el-input v-model="form.product_code" placeholder="" />
        </el-form-item>

        <!-- 检查时间 -->
        <el-form-item label="检查时间" prop="inspect_time" class="required-label">
          <el-date-picker
            v-model="form.inspect_time"
            type="datetime"
            placeholder="Select date"
            format="YYYY-MM-DD HH:mm"
            value-format="YYYY-MM-DD HH:mm"
            style="width: 100%;"
          />
        </el-form-item>

        <!-- 检查结果 -->
        <el-form-item label="检查结果" prop="result" class="required-label">
          <el-input v-model="form.result" placeholder="" />
        </el-form-item>

        <!-- 缺陷列表 -->
        <div class="defect-block">
          <div class="defect-block-title">缺陷列表</div>

          <div v-for="(defect, index) in form.defects" :key="index" class="defect-row-group">
            <!-- 缺陷类型 -->
            <el-form-item
              label="缺陷类型"
              :prop="`defects.${index}.type`"
              :rules="[{ required: true, message: '请输入缺陷类型', trigger: 'blur' }]"
              class="required-label"
            >
              <el-input v-model="defect.type" placeholder="" />
            </el-form-item>

            <!-- 描述 -->
            <el-form-item label="描述" :prop="`defects.${index}.description`">
              <el-input v-model="defect.description" placeholder="" />
            </el-form-item>

            <!-- 数量 -->
            <el-form-item
              label="数量"
              :prop="`defects.${index}.quantity`"
              :rules="[{ required: true, message: '请输入数量', trigger: 'blur' }]"
              class="required-label"
            >
              <el-input v-model="defect.quantity" placeholder="" />
            </el-form-item>

            <!-- 删除行（多行时显示） -->
            <div v-if="form.defects.length > 1" class="defect-row-delete">
              <el-button type="danger" link size="small" @click="removeDefect(index)">
                <el-icon><Delete /></el-icon> 删除
              </el-button>
            </div>
          </div>

          <!-- 添加缺陷按钮 -->
          <el-button class="add-defect-btn" @click="addDefect">添加缺陷</el-button>
        </div>

        <!-- 底部按钮 -->
        <div class="form-actions">
          <el-button type="primary" @click="handleSubmit">提交</el-button>
          <el-button @click="handleCancel">取消</el-button>
        </div>
      </el-form>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, reactive } from 'vue'
import { useRouter } from 'vue-router'
import { ElMessage } from 'element-plus'
import { Delete } from '@element-plus/icons-vue'
import { createInspection } from '../../api/qualityControl'

const router = useRouter()
const formRef = ref()

const form = reactive({
  plan_id: '',
  product_code: '',
  inspect_time: '',
  result: '',
  defects: [
    { type: '', description: '', quantity: '' }
  ]
})

const rules = {
  plan_id: [{ required: true, message: '请输入生产计划ID', trigger: 'blur' }],
  product_code: [{ required: true, message: '请输入产品代码', trigger: 'blur' }],
  inspect_time: [{ required: true, message: '请选择检查时间', trigger: 'change' }],
  result: [{ required: true, message: '请输入检查结果', trigger: 'blur' }]
}

const addDefect = () => {
  form.defects.push({ type: '', description: '', quantity: '' })
}

const removeDefect = (index: number) => {
  form.defects.splice(index, 1)
}

const handleSubmit = async () => {
  if (!formRef.value) return
  try {
    await formRef.value.validate()
    await createInspection({
      plan_id: form.plan_id,
      product_code: form.product_code,
      inspect_time: form.inspect_time,
      result: form.result,
      defects: form.defects.map(d => ({ ...d, quantity: String(d.quantity) }))
    })
    ElMessage.success('新建质量检查记录成功')
    router.push('/quality-control')
  } catch {
    // 验证失败，不处理
  }
}

const handleCancel = () => {
  router.push('/quality-control')
}
</script>

<style scoped lang="scss">
.create-inspection {
  padding: 20px;
  background-color: #0d1b2a;
  min-height: 100vh;
  color: #fff;
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

.inspection-form {
  padding: 24px;

  :deep(.el-form-item) {
    margin-bottom: 20px;
  }

  :deep(.el-form-item__label) {
    color: #fff;
    font-size: 14px;
    padding-bottom: 6px;
    line-height: 1.4;
  }

  // 必填红星放在label前面（和截图一致）
  :deep(.required-label .el-form-item__label::before) {
    content: '* ';
    color: #f56c6c;
  }

  :deep(.el-input__wrapper) {
    background-color: #111;
    box-shadow: 0 0 0 1px #333 inset;
    border-radius: 4px;
  }

  :deep(.el-input__inner) {
    color: #fff;
    font-size: 14px;
    &::placeholder { color: transparent; }
  }

  :deep(.el-date-editor .el-input__wrapper) {
    background-color: #111;
    box-shadow: 0 0 0 1px #333 inset;
  }

  :deep(.el-date-editor .el-input__inner) {
    color: #888;
  }

  :deep(.el-date-editor .el-input__prefix) {
    display: none;
  }

  :deep(.el-date-editor .el-input__suffix .el-icon) {
    color: #666;
  }
}

// 缺陷列表区块
.defect-block {
  background-color: #111;
  border: 1px solid #2d2d2d;
  border-radius: 4px;
  padding: 16px 20px 20px;
  margin-bottom: 24px;
}

.defect-block-title {
  font-size: 14px;
  font-weight: 500;
  color: #fff;
  margin-bottom: 16px;
  padding-bottom: 10px;
  border-bottom: 1px solid #2d2d2d;
}

.defect-row-group {
  border-bottom: 1px dashed #2d2d2d;
  padding-bottom: 12px;
  margin-bottom: 12px;

  &:last-of-type {
    border-bottom: none;
    margin-bottom: 0;
    padding-bottom: 0;
  }
}

.defect-row-delete {
  display: flex;
  justify-content: flex-end;
  margin-top: -8px;
  margin-bottom: 4px;
}

.add-defect-btn {
  margin-top: 14px;
  background-color: #1e3a52;
  border-color: #2d5a7a;
  color: #a0c4e0;
  font-size: 13px;

  &:hover {
    background-color: #254a6a;
    border-color: #3a7aaa;
    color: #fff;
  }
}

// 底部操作区
.form-actions {
  display: flex;
  gap: 12px;
  padding-top: 8px;
  border-top: 1px solid #2d2d2d;
  margin-top: 8px;
}
</style>
