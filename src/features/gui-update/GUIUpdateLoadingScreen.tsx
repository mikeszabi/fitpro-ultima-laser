import { useEffect } from 'react'
import { useAppDispatch, useAppSelector } from '@/store/hooks'
import { setGUIUpdateProgress, setShowGUIUpdateLoading, setCurrentScreen } from '@/store/slices/uiSlice'
import { configService } from '@/services/configService'
import './GUIUpdateLoadingScreen.scss'

const GUIUpdateLoadingScreen: React.FC = () => {
  const dispatch = useAppDispatch()
  const progress = useAppSelector((state) => state.ui.guiUpdateProgress)

  useEffect(() => {
    const startUpdate = async () => {
      await configService.downloadGUIUpdate((progress) => {
        dispatch(setGUIUpdateProgress(progress))
      })

      // After completion, return to system info
      setTimeout(() => {
        dispatch(setShowGUIUpdateLoading(false))
        dispatch(setCurrentScreen('system-info'))
      }, 500)
    }

    startUpdate()
  }, [dispatch])

  return (
    <div className="gui-update-loading">
      <div className="gui-update-loading__background" />
      <div className="gui-update-loading__content">
        <div className="gui-update-loading__logo">
          <img 
            src="/assets/ULTIMA.png" 
            alt="ULTIMA" 
            className="gui-update-loading__logo-image"
          />
          <span className="gui-update-loading__laser">LASER</span>
        </div>
        <div className="gui-update-loading__progress-section">
          <div className="gui-update-loading__progress-header">
            <span className="gui-update-loading__progress-label">NEW GUI LOADING</span>
            <span className="gui-update-loading__progress-text">{progress}%</span>
          </div>
          <div className="gui-update-loading__progress-bar">
            <div
              className="gui-update-loading__progress-fill"
              style={{ width: `${progress}%` }}
            />
          </div>
        </div>
      </div>
    </div>
  )
}

export default GUIUpdateLoadingScreen
