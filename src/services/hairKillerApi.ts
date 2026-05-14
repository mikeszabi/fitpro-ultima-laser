import type { TreatmentMode } from '@/types'

const DEFAULT_API_BASE_URL = 'http://localhost:8000'

const getApiBaseUrl = () => {
  const configuredUrl = import.meta.env.VITE_HK_API_BASE_URL as string | undefined
  return (configuredUrl || DEFAULT_API_BASE_URL).replace(/\/$/, '')
}

type QueryValue = string | number | boolean

interface StatsResponse {
  detection_enabled: boolean
  detection_count: number
  red_dot_enabled: boolean
  detected_points: number
  walking: boolean
}

interface DetectionStatusResponse {
  detection_enabled: boolean
  conf: number
  red_dot: boolean
}

interface CaptureResponse {
  captured: number
  points: number[][]
}

interface LaserSettingsResponse {
  armed: boolean
  power: {
    p808: number
    p980: number
    p1064: number
  }
  pulse_ms: number
  targets_count: number
}

interface LaserTempResponse {
  temp: number | string
}

interface SensorValuesResponse {
  values: {
    laserTemp_C?: number | string
  }
  raw: string[]
}

interface SequenceStatusResponse {
  state?: string | string[]
  mode?: string | string[]
  last_error?: string | string[]
  target_count: number
  show_target_points_overlay: boolean
  events?: {
    status?: string
    message?: string
    timestamp?: number
  }[]
}

const buildUrl = (path: string, query?: Record<string, QueryValue>) => {
  const url = new URL(`${getApiBaseUrl()}${path}`)

  Object.entries(query || {}).forEach(([key, value]) => {
    url.searchParams.set(key, String(value))
  })

  return url.toString()
}

const readErrorMessage = async (response: Response) => {
  try {
    const data = await response.json()
    return data?.error || response.statusText
  } catch {
    return response.statusText
  }
}

const request = async <T>(
  path: string,
  options: RequestInit = {},
  query?: Record<string, QueryValue>
): Promise<T> => {
  const response = await fetch(buildUrl(path, query), options)

  if (!response.ok) {
    throw new Error(await readErrorMessage(response))
  }

  return response.json() as Promise<T>
}

const post = <T>(path: string, query?: Record<string, QueryValue>) =>
  request<T>(path, { method: 'POST' }, query)

const postJson = <T>(path: string, body: Record<string, unknown>) =>
  request<T>(path, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(body),
  })

const toSequenceMode = (mode: TreatmentMode) => (mode === 'manual' ? 'manual' : 'auto')

export const hairKillerApi = {
  get baseUrl() {
    return getApiBaseUrl()
  },

  getFrameUrl() {
    return `${getApiBaseUrl()}/frame/current`
  },

  health() {
    return request<{ ok: boolean }>('/health')
  },

  getStats() {
    return request<StatsResponse>('/stats')
  },

  getDetectionStatus() {
    return request<DetectionStatusResponse>('/detection/status')
  },

  setDetectionEnabled(enabled: boolean) {
    return post<DetectionStatusResponse>('/detection/toggle', { enabled })
  },

  setDetectionConfidence(conf: number) {
    return post<{ conf: number }>('/detection/conf', { conf })
  },

  captureDetections() {
    return post<CaptureResponse>('/detection/capture')
  },

  clearPoints() {
    return post<{ status: string }>('/points/clear')
  },

  updateTargets() {
    return post<{ targets_count: number; detected_count: number }>('/seq/update_targets')
  },

  clearTargets() {
    return post<{ targets_count: number }>('/seq/clear_targets')
  },

  showTargets(enabled: boolean) {
    return post<SequenceStatusResponse>('/seq/show_targets', { enabled })
  },

  setSequenceMode(mode: TreatmentMode) {
    return post<{ mode: string }>('/seq/mode', { mode: toSequenceMode(mode) })
  },

  startSequence() {
    return post<{ targets_count: number }>('/seq/start')
  },

  stepSequence() {
    return post<{ targets_count: number }>('/seq/step')
  },

  getSequenceStatus() {
    return request<SequenceStatusResponse>('/seq/status')
  },

  fireWalk() {
    return post<{ targets_count: number; status: string }>('/fire/walk')
  },

  stopSequence() {
    return post<{ targets_count: number }>('/seq/stop')
  },

  clearAppError() {
    return post<{ response: string[] }>('/app/clear_error')
  },

  armLaser(enabled: boolean) {
    return post<{ enabled?: boolean }>(enabled ? '/laser/arm' : '/laser/disarm')
  },

  updateLaserSettings(settings: {
    armed: boolean
    p808: number
    p980: number
    p1064: number
    pulse_ms: number
    reload_targets?: boolean
  }) {
    return postJson<LaserSettingsResponse>('/laser/settings', {
      reload_targets: true,
      ...settings,
    })
  },

  getLaserSettings() {
    return request<LaserSettingsResponse>('/laser/settings')
  },

  getLaserTemp() {
    return request<LaserTempResponse>('/laser/temp')
  },

  getSensorValues() {
    return request<SensorValuesResponse>('/sensors/values')
  },

  async getLaserTempSafe() {
    try {
      const sensors = await this.getSensorValues()
      const sensorTemp = Number(sensors.values.laserTemp_C)

      if (Number.isFinite(sensorTemp)) {
        return sensorTemp
      }
    } catch {
      // Fall back to the legacy temp endpoint below.
    }

    const response = await this.getLaserTemp()
    const temp = Number(response.temp)

    if (!Number.isFinite(temp)) {
      throw new Error('Laser temperature unavailable')
    }

    return temp
  },

  setRedDot(enabled: boolean) {
    return post<{ enabled: boolean }>('/laser/red_dot', { enabled })
  },

  fireLaser(durationMs: number) {
    return post<{ duration_ms: number }>('/laser/fire', { duration_ms: durationMs })
  },

  setVacuumEnabled(enabled: boolean) {
    return postJson<{ response: string[]; command: string }>('/app/raw_command', {
      command: `APP_SET_VACUUM_EN ${enabled ? 1 : 0}`,
    })
  },

  setVacuumCheckEnabled(enabled: boolean) {
    return postJson<{ response: string[]; command: string }>('/app/raw_command', {
      command: `APP_SET_CHECK_VACUUM ${enabled ? 1 : 0}`,
    })
  },
}
