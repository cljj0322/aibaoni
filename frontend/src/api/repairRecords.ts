import request from './request'

// 阀门数据类型
export interface Valve {
  id: number
  order_id: number
  po_no: string
  abn_sn: string
  customer_sn: string
  part_no: string
  description: string
  model_no: string
  fault_description: string
  service_category: string
  current_step: string
}

// 通过SN查询阀门
export function searchValveBySn(sn: string): Promise<Valve> {
  return request({
    url: '/valves/search',
    method: 'get',
    params: { sn }
  }) as Promise<Valve>
}

// 获取阀门维修记录
export function getRepairRecord(valveId: number) {
  return request({
    url: `/valves/${valveId}/record`,
    method: 'get'
  })
}

// 更新阀门维修记录
export function updateRepairRecord(valveId: number, data: any) {
  return request({
    url: `/valves/${valveId}/record`,
    method: 'put',
    data
  })
}

// 添加检测项
export function addCheckItem(valveId: number, data: any) {
  return request({
    url: `/valves/${valveId}/check-items`,
    method: 'post',
    data
  })
}

// 添加物料项
export function addMaterialItem(valveId: number, data: any) {
  return request({
    url: `/valves/${valveId}/material-items`,
    method: 'post',
    data
  })
}

// 上传附件
export function uploadAttachment(valveId: number, file: File, type: string) {
  const formData = new FormData()
  formData.append('file', file)
  formData.append('type', type)

  return request({
    url: `/valves/${valveId}/attachments`,
    method: 'post',
    data: formData,
    headers: {
      'Content-Type': 'multipart/form-data'
    }
  })
}

// 删除附件
export function deleteAttachment(attachmentId: number) {
  return request({
    url: `/attachments/${attachmentId}`,
    method: 'delete'
  })
}
