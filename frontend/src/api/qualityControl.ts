import request from './request'

// ========== 质量检查记录 ==========

// 获取质量检查记录列表
export function getInspectionList(params: {
  keyword?: string
  result?: string
  page?: number
  per_page?: number
}) {
  return request({
    url: '/quality-control/inspection',
    method: 'get',
    params
  })
}

// 获取单条质量检查记录详情
export function getInspectionDetail(id: number) {
  return request({
    url: `/quality-control/inspection/${id}`,
    method: 'get'
  })
}

// 新增质量检查记录
export function createInspection(data: {
  plan_id: string
  product_code: string
  inspect_time: string
  result: string
  remark?: string
  defects?: Array<{ type: string; description?: string; quantity: string }>
}) {
  return request({
    url: '/quality-control/inspection',
    method: 'post',
    data
  })
}

// 更新质量检查记录
export function updateInspection(id: number, data: any) {
  return request({
    url: `/quality-control/inspection/${id}`,
    method: 'put',
    data
  })
}

// 删除质量检查记录
export function deleteInspection(id: number) {
  return request({
    url: `/quality-control/inspection/${id}`,
    method: 'delete'
  })
}

// ========== 维修工单 ==========

// 获取维修工单列表
export function getWorkorderList(params: {
  keyword?: string
  status?: string
  page?: number
  per_page?: number
}) {
  return request({
    url: '/quality-control/workorder',
    method: 'get',
    params
  })
}

// 新增维修工单
export function createWorkorder(data: {
  product_code: string
  product_name: string
  quantity: number
  plan_start: string
  plan_end: string
  status: string
  actual_start?: string
  actual_end?: string
}) {
  return request({
    url: '/quality-control/workorder',
    method: 'post',
    data
  })
}

// 更新维修工单
export function updateWorkorder(id: number, data: any) {
  return request({
    url: `/quality-control/workorder/${id}`,
    method: 'put',
    data
  })
}

// 删除维修工单
export function deleteWorkorder(id: number) {
  return request({
    url: `/quality-control/workorder/${id}`,
    method: 'delete'
  })
}
