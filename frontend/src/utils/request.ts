import axios from 'axios'
import type { AxiosInstance, AxiosResponse } from 'axios'
import { ElMessage } from 'element-plus'
import router from '@/router'
import { useUserStore } from '@/stores'

// 1. 创建实例
const instance: AxiosInstance = axios.create({
  baseURL: import.meta.env.VITE_API_BASE_URL || '',
  timeout: 10000,
})

// 2. 请求拦截器
instance.interceptors.request.use(
  (config) => {
    const userStore = useUserStore()
    if (userStore.token) {
      config.headers.Authorization = `Bearer ${userStore.token}`
    }
    return config
  },
  (err) => Promise.reject(err),
)

// 3. 响应拦截器
instance.interceptors.response.use(
  (res: AxiosResponse) => {
    // 业务成功，只返回 data 部分
    if (res.data.code === 200) {
      return res.data.data
    }
    // 业务失败，弹提示并 reject
    ElMessage.error(res.data.msg || '服务异常')
    return Promise.reject(res.data)
  },
  (err) => {
    // 401 未登录，跳登录页
    if (err.response?.status === 401) {
      router.push('/login')
    }
    ElMessage.error(err.response?.data?.msg || '请求失败')
    return Promise.reject(err)
  },
)

// 4. 统一导出
export default instance
export { instance as request }
