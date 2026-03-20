import request from './request'

// 订单数据类型
export interface Order {
  id: number
  po_no: string
  receive_date: string
  finish_date: string
  repair_status: string
  customer_name: string
  contact_phone: string
  email: string
  address: string
  remark: string
  valves?: Valve[]
  created_at?: string
  updated_at?: string
}

// 阀门数据类型
export interface Valve {
  id: number
  customer_sn: string
  abn_sn: string
  part_no: string
  description: string
  model_no: string
  fault_description: string
  current_step: string
  service_category: string
}

// 获取订单列表
export const getOrders = (params?: {
  search_type?: string
  keyword?: string
  start_date?: string
  end_date?: string
  page?: number
  per_page?: number
}) => {
  return request.get('/orders/', { params }) as Promise<{ items: Order[]; total: number }>
}

// 获取单个订单
export const getOrder = (id: number) => {
  return request.get(`/orders/${id}`) as Promise<Order>
}

// 创建订单
export const createOrder = (data: any) => {
  return request.post('/orders/', data)
}

// 更新订单
export const updateOrder = (id: number, data: any) => {
  return request.put(`/orders/${id}`, data)
}

// 删除订单
export const deleteOrder = (id: number) => {
  return request.delete(`/orders/${id}`)
}

// ========== 阀门相关接口 ==========

// 为订单添加阀门
export const createValve = (orderId: number, data: any) => {
  return request.post(`/orders/${orderId}/valves`, data) as Promise<Valve>
}

// 更新阀门信息
export const updateValve = (orderId: number, valveId: number, data: any) => {
  return request.put(`/orders/${orderId}/valves/${valveId}`, data)
}

// 删除阀门
export const deleteValve = (orderId: number, valveId: number) => {
  return request.delete(`/orders/${orderId}/valves/${valveId}`)
}
