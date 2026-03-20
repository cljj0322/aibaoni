import request from './request'

// ========== 库存管理 ==========

// 获取库存列表
export function getInventoryList(params: {
  search_type?: string
  keyword?: string
  page?: number
  per_page?: number
}) {
  return request({
    url: '/warehouse/inventory',
    method: 'get',
    params
  })
}

// 新增库存
export function createInventory(data: any) {
  return request({
    url: '/warehouse/inventory',
    method: 'post',
    data
  })
}

// 更新库存
export function updateInventory(id: number, data: any) {
  return request({
    url: `/warehouse/inventory/${id}`,
    method: 'put',
    data
  })
}

// 删除库存
export function deleteInventory(id: number) {
  return request({
    url: `/warehouse/inventory/${id}`,
    method: 'delete'
  })
}

// 入库
export function inboundInventory(id: number, data: { quantity: number; remark?: string; operator?: string }) {
  return request({
    url: `/warehouse/inventory/${id}/inbound`,
    method: 'post',
    data
  })
}

// 出库
export function outboundInventory(id: number, data: { quantity: number; remark?: string; operator?: string }) {
  return request({
    url: `/warehouse/inventory/${id}/outbound`,
    method: 'post',
    data
  })
}

// ========== 物料编码管理 ==========

// 获取物料编码列表
export function getMaterialList(params: {
  keyword?: string
  page?: number
  per_page?: number
}) {
  return request({
    url: '/warehouse/materials',
    method: 'get',
    params
  })
}

// 新增物料编码
export function createMaterial(data: any) {
  return request({
    url: '/warehouse/materials',
    method: 'post',
    data
  })
}

// 更新物料编码
export function updateMaterial(id: number, data: any) {
  return request({
    url: `/warehouse/materials/${id}`,
    method: 'put',
    data
  })
}

// 删除物料编码
export function deleteMaterial(id: number) {
  return request({
    url: `/warehouse/materials/${id}`,
    method: 'delete'
  })
}
