import { create } from 'zustand'
import { persist } from 'zustand/middleware'
import { supabase } from '@/lib/supabase'
import { User } from '@/types'

interface AuthState {
  user: User | null
  isAuthenticated: boolean
  isLoading: boolean
  login: (email: string, password: string) => Promise<void>
  register: (email: string, password: string, fullName: string) => Promise<void>
  logout: () => Promise<void>
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
          const { data: authData, error: authError } = await supabase.auth.signInWithPassword({
            email,
            password,
          })

          if (authError) throw authError

          if (authData.user) {
            const { data: userData, error: userError } = await supabase
              .from('users')
              .select('*')
              .eq('id', authData.user.id)
              .maybeSingle()

            if (userError) throw userError

            if (userData) {
              set({
                user: userData as User,
                isAuthenticated: true,
                isLoading: false,
              })
            }
          }
        } catch (error) {
          set({ isLoading: false })
          throw error
        }
      },

      register: async (email: string, password: string, fullName: string) => {
        set({ isLoading: true })
        try {
          const { data: authData, error: authError } = await supabase.auth.signUp({
            email,
            password,
          })

          if (authError) throw authError

          if (authData.user) {
            const { error: insertError } = await supabase.from('users').insert({
              id: authData.user.id,
              email,
              full_name: fullName,
              is_active: true,
              is_verified: false,
              subscription_tier: 'basic',
              subscription_status: 'active',
              forecast_credits_remaining: 50,
            })

            if (insertError) throw insertError

            await useAuthStore.getState().login(email, password)
          }
        } catch (error) {
          set({ isLoading: false })
          throw error
        }
      },

      logout: async () => {
        await supabase.auth.signOut()
        set({
          user: null,
          isAuthenticated: false,
        })
      },

      fetchUser: async () => {
        try {
          const { data: { user: authUser } } = await supabase.auth.getUser()

          if (authUser) {
            const { data: userData, error } = await supabase
              .from('users')
              .select('*')
              .eq('id', authUser.id)
              .maybeSingle()

            if (!error && userData) {
              set({
                user: userData as User,
                isAuthenticated: true,
              })
            } else {
              set({
                user: null,
                isAuthenticated: false,
              })
            }
          } else {
            set({
              user: null,
              isAuthenticated: false,
            })
          }
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
