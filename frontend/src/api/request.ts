import axios from 'axios'
import { ElMessage } from 'element-plus'

// 创建 axios 实例
// 使用 Vite 环境变量，开发时走 localhost:5001，生产环境走相对路径
const request = axios.create({
  baseURL: import.meta.env.VITE_API_BASE_URL || '/api',
  timeout: 10000,
  headers: {
    'Content-Type': 'application/json'
  }
})

// 请求拦截器
request.interceptors.request.use(
  (config) => {
    // 可以在这里添加 token 等
    return config
  },
  (error) => {
    return Promise.reject(error)
  }
)

// 响应拦截器
request.interceptors.response.use(
  (response) => {
    const { code, message, data } = response.data

    if (code === 200) {
      return data
    } else {
      ElMessage.error(message || '请求失败')
      return Promise.reject(new Error(message))
    }
  },
  (error) => {
    // 处理后端返回的业务错误（HTTP 状态码非 200，但包含业务错误信息）
    if (error.response?.data?.message) {
      ElMessage.error(error.response.data.message)
      return Promise.reject(new Error(error.response.data.message))
    }
    ElMessage.error(error.message || '网络错误')
    return Promise.reject(error)
  }
)

export default request
