import { defineStore } from 'pinia'
import { ref } from 'vue'

export const useUserStore = defineStore(
  'user',
  () => {
    const user = ref()
    const token = ref()
    const setToken = (newToken: string) => {
      token.value = newToken
    }
    return { user, token, setToken }
  },
  {
    persist: true,
  },
)
