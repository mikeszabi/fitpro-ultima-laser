import { createSlice, PayloadAction } from '@reduxjs/toolkit'
import { FitzpatrickSkinType, HairColor, HairType, CalibrationData } from '@/types'

interface SettingsState {
  calibration: CalibrationData
  skinType: FitzpatrickSkinType | null
  hairColor: HairColor | null
  hairType: HairType | null
  language: 'en' | 'hu'
  wifiNetwork: string
  bluetoothStatus: string
}

const initialState: SettingsState = {
  calibration: {
    laserPower: 80,
    opticalScan: 0,
    temperature: 'OK',
  },
  skinType: null,
  hairColor: null,
  hairType: null,
  language: 'en',
  wifiNetwork: 'Factory',
  bluetoothStatus: 'On',
}

const settingsSlice = createSlice({
  name: 'settings',
  initialState,
  reducers: {
    setSkinType: (state, action: PayloadAction<FitzpatrickSkinType>) => {
      state.skinType = action.payload
    },
    setHairColor: (state, action: PayloadAction<HairColor>) => {
      state.hairColor = action.payload
    },
    setHairType: (state, action: PayloadAction<HairType>) => {
      state.hairType = action.payload
    },
    setLanguage: (state, action: PayloadAction<'en' | 'hu'>) => {
      state.language = action.payload
    },
    setWifiNetwork: (state, action: PayloadAction<string>) => {
      state.wifiNetwork = action.payload
    },
    setBluetoothStatus: (state, action: PayloadAction<string>) => {
      state.bluetoothStatus = action.payload
    },
    updateCalibration: (state, action: PayloadAction<Partial<CalibrationData>>) => {
      state.calibration = { ...state.calibration, ...action.payload }
    },
  },
})

export const {
  setSkinType,
  setHairColor,
  setHairType,
  setLanguage,
  setWifiNetwork,
  setBluetoothStatus,
  updateCalibration,
} = settingsSlice.actions

export default settingsSlice.reducer
