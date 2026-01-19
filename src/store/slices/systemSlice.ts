import { createSlice, PayloadAction } from '@reduxjs/toolkit'
import { SystemStatus, HardwareDetails, SoftwareDetails, ErrorState } from '@/types'
import { AppDispatch } from '../index'

interface SystemState {
  status: SystemStatus
  hardware: HardwareDetails
  software: SoftwareDetails
  error: ErrorState
  heartbeatInterval: number | null
}

const initialState: SystemState = {
  status: {
    connected: true,
    laserModuleTemp: 21,
    vacuumLock: false,
    target: false,
    targetedFollicles: 0,
  },
  hardware: {
    efLaserSerial: '22300005',
    pcSerial: '931190061110058',
  },
  software: {
    firmwareVersion: '31',
    guiVersion: '1.10.3',
  },
  error: {
    show: false,
    message: '',
    title: '',
  },
  heartbeatInterval: null,
}

const systemSlice = createSlice({
  name: 'system',
  initialState,
  reducers: {
    updateSystemStatus: (state, action: PayloadAction<Partial<SystemStatus>>) => {
      state.status = { ...state.status, ...action.payload }
    },
    setConnected: (state, action: PayloadAction<boolean>) => {
      state.status.connected = action.payload
    },
    showError: (state, action: PayloadAction<{ title: string; message: string }>) => {
      state.error = {
        show: true,
        title: action.payload.title,
        message: action.payload.message,
      }
    },
    hideError: (state) => {
      state.error.show = false
    },
    setHeartbeatInterval: (state, action: PayloadAction<number | null>) => {
      state.heartbeatInterval = action.payload
    },
  },
})

export const { updateSystemStatus, setConnected, showError, hideError, setHeartbeatInterval } =
  systemSlice.actions

// Thunk for heartbeat monitoring
export const startHeartbeat = () => (dispatch: AppDispatch) => {
  const interval = window.setInterval(() => {
    // Simulate heartbeat check
    const isConnected = Math.random() > 0.05 // 95% success rate
    dispatch(setConnected(isConnected))
    
    if (!isConnected) {
      dispatch(
        showError({
          title: 'Connection Lost',
          message: 'Unable to communicate with the hardware backend.',
        })
      )
    }
  }, 5000) // Check every 5 seconds

  dispatch(setHeartbeatInterval(interval))
}

export default systemSlice.reducer
