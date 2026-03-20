# MES阀门维修管理系统 - 项目提示词

## 项目概述
这是一个基于 **Vue3 + Element Plus + Flask** 的阀门维修管理系统(MES)，用于管理阀门维修的全流程业务。

## 技术栈

### 前端
- **框架**: Vue 3 (Composition API)
- **UI组件库**: Element Plus
- **路由**: Vue Router
- **状态管理**: Pinia
- **HTTP客户端**: Axios
- **构建工具**: Vite

### 后端
- **框架**: Flask (Python)
- **ORM**: Flask-SQLAlchemy
- **数据库**: SQLite (开发) / MySQL (生产)
- **序列化**: Flask-Marshmallow
- **跨域**: Flask-CORS

## 项目结构

```
aibaoni/
├── frontend/                 # Vue3前端项目
│   ├── src/
│   │   ├── api/             # API接口封装
│   │   │   ├── request.ts   # Axios配置
│   │   │   └── orders.ts    # 订单相关API
│   │   ├── views/           # 页面组件
│   │   │   └── orders/
│   │   │       ├── OrderList.vue      # 订单列表
│   │   │       ├── CreateOrder.vue    # 新建订单
│   │   │       ├── OrderDetail.vue    # 订单详情
│   │   │       └── EditOrder.vue      # 编辑订单
│   │   ├── layouts/         # 布局组件
│   │   │   └── MainLayout.vue
│   │   ├── router/          # 路由配置
│   │   └── main.ts
│   └── package.json
├── backend/                  # Flask后端项目
│   ├── app/
│   │   ├── __init__.py      # Flask应用初始化
│   │   ├── models.py        # 数据库模型
│   │   ├── schemas.py       # Marshmallow序列化
│   │   └── routes/          # API路由
│   │       └── orders.py    # 订单相关接口
│   ├── venv/                # Python虚拟环境
│   ├── run.py               # 启动入口
│   └── requirements.txt
└── pic/                      # 界面截图参考
```

## 功能模块

### 1. 客户订单系统 ✅
- 订单列表（分页、搜索）
- 新建订单（多区块表单）
- 订单详情（只读展示）
- 编辑订单（可修改）

### 待开发模块
- 维修过程记录
- 阀门维修履历
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
- abn_sn: 艾宝尼序列号
- part_no: 料号
- description: 产品描述
- model_no: 型号
- fault_description: 故障描述
- current_step: 当前维修进程
- service_category: 服务类型(NormalRepair/Warranty)

### RepairPlan (维修方案)
- order_id: 关联订单
- project: 维修项目
- method: 维修方式
- duration: 预计时长
- confirmed: 客户确认

### FeeItem (费用明细)
- order_id: 关联订单
- type: 费用类型
- description: 项目说明
- price: 单价
- quantity: 数量
- warranty: 保修(月)

## API接口

### 订单接口
- `GET /api/orders/` - 订单列表
- `GET /api/orders/:id` - 订单详情
- `POST /api/orders/` - 创建订单
- `PUT /api/orders/:id` - 更新订单
- `DELETE /api/orders/:id` - 删除订单

### 阀门接口
- `POST /api/orders/:id/valves` - 添加阀门
- `PUT /api/orders/:id/valves/:valve_id` - 更新阀门
- `DELETE /api/orders/:id/valves/:valve_id` - 删除阀门

## 开发规范

### 前端规范
- 使用 Composition API
- 组件名使用 PascalCase
- API请求统一封装在 api/ 目录
- 页面组件放在 views/ 目录
- 使用 Element Plus 组件库

### 后端规范
- 使用蓝图(Blueprint)组织路由
- 模型定义在 models.py
- 序列化使用 Marshmallow
- API返回统一格式: `{code, message, data}`
- 使用 try-except 处理异常

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

## 开发策略

采用**边开发前端边开发对应后端接口**的迭代方式：
1. 完成一个模块的前端界面
2. 同步开发该模块的后端API
3. 联调测试
4. 进入下一个模块

## 当前状态

客户订单系统模块已完成前后端开发，包含完整的CRUD功能。
