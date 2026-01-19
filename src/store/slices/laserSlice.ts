import { createSlice, PayloadAction } from '@reduxjs/toolkit'
import { TreatmentMode, LaserRunState, LaserParameters } from '@/types'

interface LaserState {
  runState: LaserRunState
  treatmentMode: TreatmentMode
  parameters: LaserParameters
  totalOutputPower: number
}

const initialState: LaserState = {
  runState: 'standby',
  treatmentMode: 'semi-auto',
  parameters: {
    nm808: 12,
    nm980: 12,
    nm1064: 12,
    pulseWidth: 12,
  },
  totalOutputPower: 0,
}

const laserSlice = createSlice({
  name: 'laser',
  initialState,
  reducers: {
    setRunState: (state, action: PayloadAction<LaserRunState>) => {
      state.runState = action.payload
    },
    setTreatmentMode: (state, action: PayloadAction<TreatmentMode>) => {
      state.treatmentMode = action.payload
    },
    updateParameter: (
      state,
      action: PayloadAction<{ param: keyof LaserParameters; value: number }>
    ) => {
      state.parameters[action.payload.param] = action.payload.value
    },
    setTotalOutputPower: (state, action: PayloadAction<number>) => {
      state.totalOutputPower = action.payload
    },
  },
})

export const { setRunState, setTreatmentMode, updateParameter, setTotalOutputPower } =
  laserSlice.actions

export default laserSlice.reducer
