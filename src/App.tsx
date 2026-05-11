import { useEffect, useState } from 'react'
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
  const [viewportScale, setViewportScale] = useState(1)

  useEffect(() => {
    // Start heartbeat monitoring
    // dispatch(startHeartbeat())
  }, [dispatch])

  useEffect(() => {
    const updateViewportScale = () => {
      const scale = Math.min(window.innerWidth / 1080, window.innerHeight / 1920)
      setViewportScale(scale)
    }

    updateViewportScale()
    window.addEventListener('resize', updateViewportScale)

    return () => {
      window.removeEventListener('resize', updateViewportScale)
    }
  }, [])

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
      <div
        className="app__viewport"
        style={{ transform: `scale(${viewportScale})` }}
      >
        {renderScreen()}
        {showGUIUpdateModal && <GUIUpdateModal />}
        <ErrorModal />
      </div>
    </div>
  )
}

export default App
