# MES阀门维修管理系统 - 项目提示词

## 项目概述
这是一个基于 **Vue3 + Element Plus + Flask** 的阀门维修管理系统(MES)，用于管理阀门维修的全流程业务。

## 技术栈

### 前端
- **框架**: Vue 3 (Composition API + `<script setup>`)
- **UI组件库**: Element Plus
- **路由**: Vue Router
- **状态管理**: Pinia
- **HTTP客户端**: Axios（配置响应拦截器统一处理错误）
- **构建工具**: Vite
- **语言**: TypeScript

### 后端
- **框架**: Flask (Python)
- **ORM**: Flask-SQLAlchemy
- **数据库**: SQLite (开发) / MySQL (生产)
- **跨域**: Flask-CORS
- **API格式**: 统一返回 `{code, message, data}`

## 项目结构

```
aibaoni/
├── frontend/                 # Vue3前端项目
│   ├── src/
│   │   ├── api/             # API接口封装
│   │   │   ├── request.ts   # Axios配置（含响应拦截器）
│   │   │   ├── orders.ts    # 订单相关API
│   │   │   └── repairRecords.ts  # 维修记录API
│   │   ├── views/           # 页面组件
│   │   │   ├── orders/
│   │   │   │   ├── OrderList.vue      # 订单列表
│   │   │   │   ├── CreateOrder.vue    # 新建订单
│   │   │   │   ├── OrderDetail.vue    # 订单详情
│   │   │   │   └── EditOrder.vue      # 编辑订单
│   │   │   └── repair/
│   │   │       ├── RepairRecord.vue   # 维修过程记录单
│   │   │       └── RepairHistory.vue  # 阀门维修履历
│   │   ├── layouts/         # 布局组件
│   │   │   └── MainLayout.vue
│   │   ├── router/          # 路由配置
│   │   └── main.ts
│   └── package.json
├── backend/                  # Flask后端项目
│   ├── app/
│   │   ├── __init__.py      # Flask应用初始化
│   │   ├── models.py        # 数据库模型
│   │   └── routes/          # API路由
│   │       ├── orders.py    # 订单相关接口
│   │       └── repair_records.py  # 维修记录接口
│   ├── instance/
│   │   └── valve_repair.db  # SQLite数据库
│   ├── venv/                # Python虚拟环境
│   ├── run.py               # 启动入口
│   └── requirements.txt
└── pic/                      # 界面截图参考
```

## 功能模块

### 1. 客户订单系统 ✅
- 订单列表（分页、搜索、多条件筛选）
- 新建订单（多区块表单：基本信息、阀门清单、维修方案、费用明细）
- 订单详情（只读展示）
- 编辑订单（可修改）
- 删除订单（级联删除关联阀门）

### 2. 维修过程记录 ✅
- 维修过程记录单（RepairRecord.vue）
- **SN扫码查询**: 输入艾宝尼SN自动查询阀门信息
- **信息自动填充**: Customer SN、PO No.、Part No.、Description、Model No.、故障描述等
- **查询失败处理**: SN不存在时清空已填充的Customer SN和PO No.
- 多区块表单：
  - 基本信息（艾宝尼SN、Customer SN、PO No.、当前步骤）
  - 产品信息（Part No.、Description、Model No.、故障描述、服务类型）
  - 维修前准备（动态表格）
  - 维修步骤（动态表格）
  - Product Check（检测项）
  - 物料清单
  - Final Test Item（最终测试）
  - 质保期和工程师信息
  - Test Data（测试数据）
  - Attachment（附件上传）
  - Packaging（包装）
  - Shipment（发货）

### 待开发模块
- 阀门维修履历（查询页面）
- 仓储管理
- 质量检查记录管理
- 维修质量管理
- 设备记录维护
- 用户管理

## 数据库模型

### Order (订单)
- po_no: 订单号
- receive_date: 收货日期
- finish_date: 完成日期
- repair_status: 维修状态
- customer_name: 客户姓名
- contact_phone: 联系电话
- email: 电子邮箱
- address: 联系地址
- remark: 备注

### Valve (阀门)
- order_id: 关联订单
- customer_sn: 客户序列号
- abn_sn: 艾宝尼序列号（支持SN扫码查询）
- part_no: 料号
- description: 产品描述
- model_no: 型号
- fault_description: 故障描述
- current_step: 当前维修进程
- service_category: 服务类型(NormalRepair/Warranty)

### RepairRecord (维修过程记录)
- valve_id: 关联阀门（唯一）
- current_step: 当前步骤
- prepare_operator/prepare_date: 维修前准备
- repair_step_operator/repair_step_date: 维修步骤
- check_operator/check_date: 检测信息
- material_operator/material_date: 物料信息
- final_test_motion/pneumatic/helium: 最终测试
- product_warranty/repair_engineer/reviewer: 质保信息
- test_data_operator/test_data_date: 测试数据
- attachment_operator/attachment_date: 附件
- packaging_operator/packaging_date: 包装
- shipment_tracking_no/shipment_operator/shipment_date: 发货

### 子表模型
- PrepareItem: 维修前准备项
- RepairStep: 维修步骤
- CheckItem: 检测项
- MaterialItem: 物料项
- TestDataItem: 测试数据项
- Attachment: 附件

## API接口

### 订单接口
- `GET /api/orders/` - 订单列表（支持分页、搜索）
- `GET /api/orders/:id` - 订单详情
- `POST /api/orders/` - 创建订单
- `PUT /api/orders/:id` - 更新订单
- `DELETE /api/orders/:id` - 删除订单

### 阀门接口
- `GET /api/valves/search?sn=xxx` - 通过SN查询阀门（SN扫码核心接口）
- `POST /api/orders/:id/valves` - 添加阀门
- `PUT /api/orders/:id/valves/:valve_id` - 更新阀门
- `DELETE /api/orders/:id/valves/:valve_id` - 删除阀门

### 维修记录接口
- `GET /api/valves/:valve_id/record` - 获取维修记录
- `PUT /api/valves/:valve_id/record` - 更新维修记录
- `POST /api/valves/:valve_id/check-items` - 添加检测项
- `POST /api/valves/:valve_id/material-items` - 添加物料项
- `POST /api/valves/:valve_id/attachments` - 上传附件

## 核心功能实现

### SN扫码查询功能
**前端流程**:
1. 在艾宝尼SN输入框输入值，按回车触发 `handleScanSN`
2. 调用 `searchValveBySn(sn)` API
3. 成功：填充阀门信息到表单（Customer SN、PO No.、Part No.等）
4. 失败（404）：显示"未找到该SN对应的阀门"，清空Customer SN和PO No.

**后端实现**:
- 路由: `GET /api/valves/search`
- 查询: `Valve.query.filter((Valve.abn_sn == sn) | (Valve.customer_sn == sn)).first()`
- 返回: 阀门基本信息 + 关联订单的PO号

### Axios响应拦截器
```typescript
// 统一处理后端返回的业务错误
if (error.response?.data?.message) {
  ElMessage.error(error.response.data.message)
  return Promise.reject(new Error(error.response.data.message))
}
```

## 开发规范

### 前端规范
- 使用 Composition API + `<script setup>` 语法
- 组件名使用 PascalCase
- API请求统一封装在 api/ 目录，使用 TypeScript 类型定义
- 页面组件放在 views/ 目录，按功能模块组织
- 使用 Element Plus 组件库，表单使用 `el-form-item`
- 动态表格使用 `el-table` + `v-for`
- 错误处理：API错误在 request.ts 拦截器中统一显示

### 后端规范
- 使用蓝图(Blueprint)组织路由
- 模型定义在 models.py，使用 SQLAlchemy ORM
- API返回统一格式: `{code: 200|404|500, message: string, data: object}`
- 使用 try-except 处理异常，返回统一错误格式
- 路由顺序：精确匹配路由放在参数路由之前（避免404）

## 启动命令

### 前端
```bash
cd frontend
npm run dev          # 开发服务器 http://localhost:5173
```

### 后端
```bash
cd backend
source venv/bin/activate
python run.py        # Flask服务器 http://localhost:5001
```

## 注意事项

1. **端口占用**: Flask默认5000端口可能被占用，使用5001
2. **跨域配置**: 后端已配置CORS允许前端访问
3. **日期格式**: 前后端统一使用 YYYY-MM-DD 格式
4. **数据验证**: 前端必填项: 订单号、收货日期、客户姓名、联系电话
5. **数据库迁移**: 模型变更后需手动更新数据库表结构（SQLite不支持自动迁移）
6. **SN查询**: 支持艾宝尼SN和客户SN两种方式查询

## 开发策略

采用**边开发前端边开发对应后端接口**的迭代方式：
1. 完成一个模块的前端界面
2. 同步开发该模块的后端API
3. 联调测试
4. 进入下一个模块

## 当前状态

- ✅ 客户订单系统：完整CRUD功能
- ✅ 维修过程记录：SN扫码查询、信息自动填充、多区块表单
- 🔄 阀门维修履历：待开发
- ⏳ 其他模块：待开发
