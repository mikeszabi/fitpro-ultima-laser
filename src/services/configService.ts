const delay = (ms: number) => new Promise((resolve) => setTimeout(resolve, ms))

export const configService = {
  /**
   * Mock save configuration to Supabase
   */
  async saveConfiguration(config: Record<string, unknown>): Promise<void> {
    await delay(300)

    if (Math.random() < 0.05) {
      throw new Error('Failed to save configuration')
    }

    console.log('Config saved:', config)
  },

  /**
   * Mock load configuration from Supabase
   */
  async loadConfiguration(): Promise<Record<string, unknown> | null> {
    await delay(300)

    // Return null for first-time users
    return null
  },

  /**
   * Mock GUI version check
   */
  async checkGUIVersion(): Promise<{ hasUpdate: boolean; version: string }> {
    await delay(500)

    // Simulate update available
    return {
      hasUpdate: true,
      version: 'V1.10.16',
    }
  },

  /**
   * Mock GUI update download
   */
  async downloadGUIUpdate(
    onProgress: (progress: number) => void
  ): Promise<void> {
    const totalSteps = 100
    
    for (let i = 0; i <= totalSteps; i++) {
      await delay(50) // Simulate download time
      onProgress(i)
    }
  },
}
