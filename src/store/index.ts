import { configureStore } from '@reduxjs/toolkit'
import uiReducer from './slices/uiSlice'
import authReducer from './slices/authSlice'
import settingsReducer from './slices/settingsSlice'
import laserReducer from './slices/laserSlice'
import systemReducer from './slices/systemSlice'

export const store = configureStore({
  reducer: {
    ui: uiReducer,
    auth: authReducer,
    settings: settingsReducer,
    laser: laserReducer,
    system: systemReducer,
  },
})

export type RootState = ReturnType<typeof store.getState>
export type AppDispatch = typeof store.dispatch
