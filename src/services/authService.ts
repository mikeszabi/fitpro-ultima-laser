import { User } from '@/types'

const delay = (ms: number) => new Promise((resolve) => setTimeout(resolve, ms))

export const authService = {
  /**
   * Mock login - simulates Supabase authentication
   */
  async login(email: string, password: string): Promise<User> {
    await delay(800) // Simulate network delay

    // Mock validation - accept any email/password for demo
    if (!email || !password) {
      throw new Error('Email and password are required')
    }

    // Return mock user data
    return {
      name: 'Judit Pinter',
      email: email,
      role: 'Operator',
      licenseExpiration: 'XX Day(s)',
    }
  },

  /**
   * Mock logout
   */
  async logout(): Promise<void> {
    await delay(300)
    // Clear any stored session data
  },
}
