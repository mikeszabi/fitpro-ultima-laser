import { useTranslation } from 'react-i18next'
import { useAppDispatch } from '@/store/hooks'
import { setShowGUIUpdateModal, setShowGUIUpdateLoading } from '@/store/slices/uiSlice'
import { useState, useEffect } from 'react'
import './GUIUpdateModal.scss'

const GUIUpdateModal: React.FC = () => {
  const { t } = useTranslation()
  const dispatch = useAppDispatch()
  const [updateAvailable, setUpdateAvailable] = useState<boolean>(false)
  const [isChecking, setIsChecking] = useState<boolean>(true)

  useEffect(() => {
    // Check for GUI updates when modal opens
    const checkForUpdates = async () => {
      try {
        // TODO: Replace with actual API call to check for updates
        // const response = await fetch('/api/gui/check-update')
        // const data = await response.json()
        // setUpdateAvailable(data.updateAvailable)
        
        // Mock implementation - simulate API call
        await new Promise(resolve => setTimeout(resolve, 500))
        
        // Mock: For now, assume update is available
        // In production, this should compare current version with latest version
        const currentVersion = '1.10.15'
        const latestVersion = '1.10.16'
        setUpdateAvailable(latestVersion > currentVersion)
      } catch (error) {
        console.error('Failed to check for updates:', error)
        setUpdateAvailable(false)
      } finally {
        setIsChecking(false)
      }
    }

    checkForUpdates()
  }, [])

  const handleYes = () => {
    dispatch(setShowGUIUpdateModal(false))
    dispatch(setShowGUIUpdateLoading(true))
  }

  const handleNo = () => {
    dispatch(setShowGUIUpdateModal(false))
  }

  const handleOk = () => {
    dispatch(setShowGUIUpdateModal(false))
  }

  if (isChecking) {
    return (
      <div className="gui-update-modal-overlay">
        <div className="gui-update-modal">
          <h2 className="gui-update-modal__title">{t('guiUpdate.modal.title')}</h2>
          <div className="gui-update-modal__divider" />
          <p className="gui-update-modal__message">Checking for updates...</p>
        </div>
      </div>
    )
  }

  return (
    <div className="gui-update-modal-overlay">
      <div className="gui-update-modal">
        <h2 className="gui-update-modal__title">{t('guiUpdate.modal.title')}</h2>
        <div className="gui-update-modal__divider" />
        
        {updateAvailable ? (
          <>
            <p 
              className="gui-update-modal__message" 
              dangerouslySetInnerHTML={{ __html: t('guiUpdate.modal.message') }}
            />
            <div className="gui-update-modal__buttons">
              <button className="gui-update-modal__button" onClick={handleYes}>
                {t('common.yes')}
              </button>
              <button className="gui-update-modal__button" onClick={handleNo}>
                {t('common.no')}
              </button>
            </div>
          </>
        ) : (
          <>
            <p className="gui-update-modal__message">
              {t('guiUpdate.modal.upToDate')}
            </p>
            <div className="gui-update-modal__buttons">
              <button className="gui-update-modal__button" onClick={handleOk}>
                {t('common.ok')}
              </button>
            </div>
          </>
        )}
      </div>
    </div>
  )
}

export default GUIUpdateModal
