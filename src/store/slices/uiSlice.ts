import { createSlice, PayloadAction } from '@reduxjs/toolkit'
import { ScreenType } from '@/types'

interface UIState {
  currentScreen: ScreenType
  navigationHistory: ScreenType[]
  showGUIUpdateModal: boolean
  showGUIUpdateLoading: boolean
  guiUpdateProgress: number
}

const initialState: UIState = {
  currentScreen: 'start',
  navigationHistory: [],
  showGUIUpdateModal: false,
  showGUIUpdateLoading: false,
  guiUpdateProgress: 0,
}

const uiSlice = createSlice({
  name: 'ui',
  initialState,
  reducers: {
    setCurrentScreen: (state, action: PayloadAction<ScreenType>) => {
      if (state.currentScreen !== action.payload) {
        state.navigationHistory.push(state.currentScreen)
        state.currentScreen = action.payload
      }
    },
    goBack: (state) => {
      if (state.navigationHistory.length > 0) {
        state.currentScreen = state.navigationHistory.pop()!
      }
    },
    setShowGUIUpdateModal: (state, action: PayloadAction<boolean>) => {
      state.showGUIUpdateModal = action.payload
    },
    setShowGUIUpdateLoading: (state, action: PayloadAction<boolean>) => {
      state.showGUIUpdateLoading = action.payload
      if (action.payload) {
        state.guiUpdateProgress = 0
      }
    },
    setGUIUpdateProgress: (state, action: PayloadAction<number>) => {
      state.guiUpdateProgress = action.payload
    },
  },
})

export const {
  setCurrentScreen,
  goBack,
  setShowGUIUpdateModal,
  setShowGUIUpdateLoading,
  setGUIUpdateProgress,
} = uiSlice.actions

export default uiSlice.reducer
