import { create } from 'zustand'
import { persist } from 'zustand/middleware'
import apiClient from '@/lib/api-client'
import { User } from '@/types'

interface AuthState {
  user: User | null
  isAuthenticated: boolean
  isLoading: boolean
  login: (email: string, password: string) => Promise<void>
  register: (email: string, password: string, fullName: string) => Promise<void>
  logout: () => void
  fetchUser: () => Promise<void>
}

export const useAuthStore = create<AuthState>()(
  persist(
    (set) => ({
      user: null,
      isAuthenticated: false,
      isLoading: false,

      login: async (email: string, password: string) => {
        set({ isLoading: true })
        try {
          const response = await apiClient.post('/api/v1/auth/login', {
            email,
            password,
          })

          const { access_token, refresh_token } = response.data

          localStorage.setItem('access_token', access_token)
          localStorage.setItem('refresh_token', refresh_token)

          const userResponse = await apiClient.get('/api/v1/auth/me')

          set({
            user: userResponse.data,
            isAuthenticated: true,
            isLoading: false,
          })
        } catch (error) {
          set({ isLoading: false })
          throw error
        }
      },

      register: async (email: string, password: string, fullName: string) => {
        set({ isLoading: true })
        try {
          await apiClient.post('/api/v1/auth/register', {
            email,
            password,
            full_name: fullName,
          })

          await useAuthStore.getState().login(email, password)
        } catch (error) {
          set({ isLoading: false })
          throw error
        }
      },

      logout: () => {
        localStorage.removeItem('access_token')
        localStorage.removeItem('refresh_token')
        set({
          user: null,
          isAuthenticated: false,
        })
      },

      fetchUser: async () => {
        try {
          const response = await apiClient.get('/api/v1/auth/me')
          set({
            user: response.data,
            isAuthenticated: true,
          })
        } catch (error) {
          set({
            user: null,
            isAuthenticated: false,
          })
        }
      },
    }),
    {
      name: 'auth-storage',
      partialize: (state) => ({
        user: state.user,
        isAuthenticated: state.isAuthenticated,
      }),
    }
  )
)
