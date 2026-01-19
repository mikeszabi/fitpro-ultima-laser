import { LaserParameters } from '@/types'

const delay = (ms: number) => new Promise((resolve) => setTimeout(resolve, ms))

export const hardwareService = {
  /**
   * Mock command to update laser parameters
   */
  async updateLaserParameter(param: keyof LaserParameters, value: number): Promise<void> {
    await delay(100)

    // Simulate 5% failure rate
    if (Math.random() < 0.05) {
      throw new Error('Failed to update laser parameter')
    }

    // Mock success
    console.log(`Hardware: Updated ${param} to ${value}`)
  },

  /**
   * Mock command to set treatment mode
   */
  async setTreatmentMode(mode: string): Promise<void> {
    await delay(100)

    if (Math.random() < 0.05) {
      throw new Error('Failed to set treatment mode')
    }

    console.log(`Hardware: Set treatment mode to ${mode}`)
  },

  /**
   * Mock command to update run state
   */
  async setRunState(state: string): Promise<void> {
    await delay(150)

    if (Math.random() < 0.05) {
      throw new Error('Failed to set run state')
    }

    console.log(`Hardware: Set run state to ${state}`)
  },

  /**
   * Mock heartbeat/ping to check connection
   */
  async ping(): Promise<boolean> {
    await delay(50)

    // Simulate 95% success rate
    return Math.random() > 0.05
  },

  /**
   * Mock get system status
   */
  async getSystemStatus(): Promise<{
    laserModuleTemp: number
    vacuumLock: boolean
    target: boolean
    targetedFollicles: number
  }> {
    await delay(100)

    return {
      laserModuleTemp: 21 + Math.random() * 2, // 21-23°C
      vacuumLock: Math.random() > 0.5,
      target: Math.random() > 0.5,
      targetedFollicles: Math.floor(Math.random() * 10),
    }
  },
}
