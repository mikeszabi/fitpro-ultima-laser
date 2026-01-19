import { useEffect } from 'react'
import { useAppDispatch, useAppSelector } from './store/hooks'
// import { startHeartbeat } from './store/slices/systemSlice'
import StartScreen from './features/start/StartScreen'
import LoginScreen from './features/login/LoginScreen'
import SettingsScreen from './features/settings/SettingsScreen'
import LaserTreatmentScreen from './features/laser-treatment/LaserTreatmentScreen'
import SystemInfoScreen from './features/system-info/SystemInfoScreen'
import GUIUpdateModal from './components/modals/GUIUpdateModal'
import GUIUpdateLoadingScreen from './features/gui-update/GUIUpdateLoadingScreen'
import ErrorModal from './components/modals/ErrorModal'
import './App.scss'

function App() {
  const dispatch = useAppDispatch()
  const currentScreen = useAppSelector((state) => state.ui.currentScreen)
  const showGUIUpdateModal = useAppSelector((state) => state.ui.showGUIUpdateModal)
  const showGUIUpdateLoading = useAppSelector((state) => state.ui.showGUIUpdateLoading)

  useEffect(() => {
    // Start heartbeat monitoring
    // dispatch(startHeartbeat())
  }, [dispatch])

  const renderScreen = () => {
    if (showGUIUpdateLoading) {
      return <GUIUpdateLoadingScreen />
    }

    switch (currentScreen) {
      case 'start':
        return <StartScreen />
      case 'login':
        return <LoginScreen />
      case 'settings':
        return <SettingsScreen />
      case 'laser-treatment':
        return <LaserTreatmentScreen />
      case 'system-info':
        return <SystemInfoScreen />
      default:
        return <StartScreen />
    }
  }

  return (
    <div className="app">
      {renderScreen()}
      {showGUIUpdateModal && <GUIUpdateModal />}
      <ErrorModal />
    </div>
  )
}

export default App
