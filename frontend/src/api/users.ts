import request from './request'

// ========== 用户管理 ==========

// 获取用户列表
export function getUserList(params: {
  username?: string
  page?: number
  per_page?: number
}) {
  return request({
    url: '/users',
    method: 'get',
    params
  })
}

// 新增用户
export function createUser(data: {
  username: string
  chinese_name: string
  role: string
  email: string
  password: string
}) {
  return request({
    url: '/users',
    method: 'post',
    data
  })
}

// 更新用户
export function updateUser(id: number, data: any) {
  return request({
    url: `/users/${id}`,
    method: 'put',
    data
  })
}

// 删除用户
export function deleteUser(id: number) {
  return request({
    url: `/users/${id}`,
    method: 'delete'
  })
}
