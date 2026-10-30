// 用户接口
import request from '@/utils/request'

export function register(data: unknown[]) {
  return request.post('/user/register', data)
}
