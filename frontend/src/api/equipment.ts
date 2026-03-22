import request from './request'

// ========== 设备维护记录 ==========

// 获取设备维护记录列表
export function getEquipmentMaintenanceList(params: {
  status?: string
  page?: number
  per_page?: number
}) {
  return request({
    url: '/equipment/maintenance',
    method: 'get',
    params
  })
}

// 新增设备维护记录
export function createEquipmentMaintenance(data: {
  equipment_id: string
  equipment_name: string
  maintenance_type: string
  plan_time: string
  actual_time?: string
  status: string
  remark?: string
}) {
  return request({
    url: '/equipment/maintenance',
    method: 'post',
    data
  })
}

// 更新设备维护记录
export function updateEquipmentMaintenance(id: number, data: any) {
  return request({
    url: `/equipment/maintenance/${id}`,
    method: 'put',
    data
  })
}

// 删除设备维护记录
export function deleteEquipmentMaintenance(id: number) {
  return request({
    url: `/equipment/maintenance/${id}`,
    method: 'delete'
  })
}
