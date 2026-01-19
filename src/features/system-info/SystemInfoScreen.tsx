import { useState, useEffect } from 'react'
import { useTranslation } from 'react-i18next'
import { useAppDispatch, useAppSelector } from '@/store/hooks'
import { setCurrentScreen } from '@/store/slices/uiSlice'
import { setShowGUIUpdateModal } from '@/store/slices/uiSlice'
import { logout } from '@/store/slices/authSlice'
import BackButton from '@/components/common/BackButton'
import InfoButton from '@/components/common/InfoButton'
import './SystemInfoScreen.scss'

interface SystemData {
  user: {
    name: string
    expirationTime: string
  }
  settings: {
    language: string
    wifiNetwork: string
    bluetooth: string
  }
  hardware: {
    efLaserSerial: string
    pcSerial: string
  }
  software: {
    firmwareVersion: string
    guiVersion: string
  }
}

const SystemInfoScreen: React.FC = () => {
  const { t, i18n } = useTranslation()
  const dispatch = useAppDispatch()
  
  // Get authenticated user from Redux store
  const { user, isAuthenticated } = useAppSelector((state) => state.auth)

  // Mock data - will be fetched from backend
  const [systemData, setSystemData] = useState<SystemData>({
    user: {
      name: 'Judit Pinter',
      expirationTime: 'XX Day(s)'
    },
    settings: {
      language: 'English',
      wifiNetwork: 'Factory',
      bluetooth: 'On'
    },
    hardware: {
      efLaserSerial: '22300005',
      pcSerial: '93100061110058'
    },
    software: {
      firmwareVersion: '31',
      guiVersion: '1.10.3'
    }
  })

  // Fetch system data from backend
  useEffect(() => {
    // TODO: Fetch from backend
    // const fetchSystemData = async () => {
    //   const data = await hardwareService.getSystemInfo()
    //   setSystemData(data)
    // }
    // fetchSystemData()
  }, [])

  const handleLogout = () => {
    dispatch(logout())
    dispatch(setCurrentScreen('login'))
  }

  const handleGUIVersionCheck = () => {
    dispatch(setShowGUIUpdateModal(true))
  }

  const handleLanguageClick = () => {
    // Toggle language or open language selector
    const newLang = i18n.language === 'en' ? 'hu' : 'en'
    i18n.changeLanguage(newLang)
    setSystemData(prev => ({
      ...prev,
      settings: {
        ...prev.settings,
        language: newLang === 'en' ? 'English' : 'Magyar'
      }
    }))
  }

  const handleWifiClick = () => {
    // Open wifi settings
    console.log('Open wifi settings')
  }

  const handleBluetoothClick = () => {
    // Toggle bluetooth
    console.log('Toggle bluetooth')
  }

  return (
    <div className="system-info-screen">
      <div className="system-info-screen__background" />
      <BackButton />
      <InfoButton />
      
      <div className="system-info-screen__content">
        <h1 className="system-info-screen__title">{t('systemInfo.title')}</h1>
        
        <div className="system-info-screen__columns">
          {/* Left Column - User Details & Settings */}
          <div className="system-info-screen__left-column">
            {/* User Details - Only show if user is authenticated */}
            {isAuthenticated && user && (
              <div className="system-info-screen__section system-info-screen__section--user-details">
                <h2 className="system-info-screen__section-title system-info-screen__section-title--orange">
                  {t('systemInfo.userDetails.title')}
                </h2>
                
                <div className="system-info-screen__user-info">
                  <div className="system-info-screen__user-avatar">
                    <img src="/assets/people.png" alt="User" />
                  </div>
                  <div className="system-info-screen__user-details">
                    <div className="system-info-screen__user-name">{user.name}</div>
                    <div className="system-info-screen__user-expiration">
                      {t('systemInfo.userDetails.expiration')}: {user.licenseExpiration}
                    </div>
                  </div>
                </div>

                <button className="system-info-screen__logout-button" onClick={handleLogout}>
                  {t('common.logout')}
                </button>
              </div>
            )}

            {/* Settings */}
            <div className="system-info-screen__section system-info-screen__section--settings">
              <h2 className="system-info-screen__section-title system-info-screen__section-title--orange">
                {t('systemInfo.settings.title')}
              </h2>
              
              <div className="system-info-screen__settings-list">
                <div className="system-info-screen__setting-item" onClick={handleLanguageClick}>
                  <div className="system-info-screen__setting-row">
                    <span className="system-info-screen__setting-label">{t('systemInfo.settings.language')}</span>
                    <img src="/assets/settings-solid.png" alt="Settings" className="system-info-screen__setting-icon" />
                  </div>
                  <div className="system-info-screen__setting-value system-info-screen__setting-value--orange">
                    {systemData.settings.language}
                  </div>
                </div>

                <div className="system-info-screen__setting-item" onClick={handleWifiClick}>
                  <div className="system-info-screen__setting-row">
                    <span className="system-info-screen__setting-label">{t('systemInfo.settings.wifiNetwork')}</span>
                    <img src="/assets/settings-solid.png" alt="Settings" className="system-info-screen__setting-icon" />
                  </div>
                  <div className="system-info-screen__setting-value system-info-screen__setting-value--orange">
                    {systemData.settings.wifiNetwork}
                  </div>
                </div>

                <div className="system-info-screen__setting-item" onClick={handleBluetoothClick}>
                  <div className="system-info-screen__setting-row">
                    <span className="system-info-screen__setting-label">{t('systemInfo.settings.bluetooth')}</span>
                    <img src="/assets/settings-solid.png" alt="Settings" className="system-info-screen__setting-icon" />
                  </div>
                  <div className="system-info-screen__setting-value system-info-screen__setting-value--orange">
                    {systemData.settings.bluetooth}
                  </div>
                </div>
              </div>
            </div>
          </div>

          {/* Divider with gradient line */}
          <div className="system-info-screen__divider">
            <div className="system-info-screen__divider-line" />
          </div>

          {/* Right Column - Hardware & Software Details */}
          <div className="system-info-screen__right-column">
            {/* Hardware Details */}
            <div className="system-info-screen__section system-info-screen__section--hardware-details">
              <h2 className="system-info-screen__section-title system-info-screen__section-title--blue">
                {t('systemInfo.hardwareDetails.title')}
              </h2>
              
              <div className="system-info-screen__details-list">
                <div className="system-info-screen__detail-item">
                  <span className="system-info-screen__detail-label">{t('systemInfo.hardwareDetails.efLaserSerial')}:</span>
                  <span className="system-info-screen__detail-value">{systemData.hardware.efLaserSerial}</span>
                </div>
                <div className="system-info-screen__detail-item">
                  <span className="system-info-screen__detail-label">{t('systemInfo.hardwareDetails.pcSerial')}:</span>
                  <span className="system-info-screen__detail-value">{systemData.hardware.pcSerial}</span>
                </div>
              </div>
            </div>

            {/* Software Details */}
            <div className="system-info-screen__section system-info-screen__section--software-details">
              <h2 className="system-info-screen__section-title system-info-screen__section-title--blue">
                {t('systemInfo.softwareDetails.title')}
              </h2>
              
              <div className="system-info-screen__details-list">
                <div className="system-info-screen__detail-item">
                  <span className="system-info-screen__detail-label">{t('systemInfo.softwareDetails.firmwareVersion')}</span>
                  <span className="system-info-screen__detail-value">{systemData.software.firmwareVersion}</span>
                </div>
                <div className="system-info-screen__detail-item">
                  <span className="system-info-screen__detail-label">{t('systemInfo.softwareDetails.guiVersion')}</span>
                  <span className="system-info-screen__detail-value">{systemData.software.guiVersion}</span>
                </div>
              </div>

              <button className="system-info-screen__version-check-button" onClick={handleGUIVersionCheck}>
                {t('systemInfo.softwareDetails.guiVersionCheck')}
              </button>
            </div>
          </div>
        </div>
      </div>
    </div>
  )
}

export default SystemInfoScreen
