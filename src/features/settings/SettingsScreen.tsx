import { useState } from 'react'
import { useTranslation } from 'react-i18next'
import { useAppDispatch } from '@/store/hooks'
import { setCurrentScreen } from '@/store/slices/uiSlice'
import { setSkinType, setHairColor, setHairType, updateCalibration } from '@/store/slices/settingsSlice'
import BackButton from '@/components/common/BackButton'
import InfoButton from '@/components/common/InfoButton'
import './SettingsScreen.scss'

const SettingsScreen: React.FC = () => {
  const { t } = useTranslation()
  const dispatch = useAppDispatch()
  
  const [step, setStep] = useState<'calibration' | 'settings'>('calibration')
  const [laserPower] = useState(80)
  const [opticalScan] = useState(0)
  const [selectedSkinType, setSelectedSkinType] = useState(3)
  const [selectedHairColor, setSelectedHairColor] = useState('dark-brown')
  const [selectedHairType, setSelectedHairType] = useState('medium')
  const [temperature] = useState(21)

  const handleStart = () => {
    // Save settings to Redux store
    dispatch(setSkinType(`${selectedSkinType === 1 ? 'I' : selectedSkinType === 2 ? 'II' : selectedSkinType === 3 ? 'III' : selectedSkinType === 4 ? 'IV' : selectedSkinType === 5 ? 'V' : 'VI'}` as any))
    dispatch(setHairColor(selectedHairColor as any))
    dispatch(setHairType(selectedHairType as any))
    dispatch(updateCalibration({ laserPower, opticalScan, temperature: 'OK' }))
    
    dispatch(setCurrentScreen('laser-treatment'))
  }

  const skinTypes = [
    { id: 1, label: t('settings.skinType.type1'), color: '#f4d0b0' },
    { id: 2, label: t('settings.skinType.type2'), color: '#e9b590' },
    { id: 3, label: t('settings.skinType.type3'), color: '#d49e7c' },
    { id: 4, label: t('settings.skinType.type4'), color: '#bb7750' },
    { id: 5, label: t('settings.skinType.type5'), color: '#a55d2b' },
    { id: 6, label: t('settings.skinType.type6'), color: '#3d1f1d' },
  ]

  const hairColors = [
    { id: 'grey-white', label: t('settings.hairColor.greyWhite'), image: '/assets/haircolors/n.png', disabled: true },
    { id: 'red', label: t('settings.hairColor.red'), image: '/assets/haircolors/h.png', disabled: true },
    { id: 'blonde', label: t('settings.hairColor.blonde'), image: '/assets/haircolors/dd.png', disabled: false },
    { id: 'brown', label: t('settings.hairColor.brown'), image: '/assets/haircolors/vv.png', disabled: false },
    { id: 'dark-brown', label: t('settings.hairColor.darkBrown'), image: '/assets/haircolors/e.png', disabled: false },
    { id: 'black', label: t('settings.hairColor.black'), image: '/assets/haircolors/hf.png', disabled: false },
  ]

  const hairTypes = [
    { id: 'thin', label: t('settings.hairType.thin'), image: '/assets/hairtypes/thin.png' },
    { id: 'medium', label: t('settings.hairType.medium'), image: '/assets/hairtypes/medium.png' },
    { id: 'thick', label: t('settings.hairType.thick'), image: '/assets/hairtypes/thick.png' },
  ]

  return (
    <div className="settings-screen">
      <div className="settings-screen__background" />
      <InfoButton />
      <BackButton />
      
      <div className={`settings-screen__content settings-screen__content--${step}`}>
        <div className="settings-screen__calibration">
          <h2 className="settings-screen__calibration-title">{t('settings.calibration.title')}</h2>
          <img 
            src="/assets/calibration-device.png" 
            alt="Calibration Device" 
            className="settings-screen__calibration-device"
          />
          {step === 'calibration' ? (
            <div className="settings-screen__calibration-controls">
              <div className="settings-screen__slider-group">
                <div className="settings-screen__slider-container">
                  <span className="settings-screen__slider-label">{t('settings.calibration.laserPower')}</span>
                  <div className="settings-screen__slider-fill" style={{ width: `${laserPower}%` }} />
                </div>
                <span className="settings-screen__slider-value">{laserPower}%</span>
              </div>
              <div className="settings-screen__slider-group">
                <div className="settings-screen__slider-container">
                  <span className="settings-screen__slider-label">{t('settings.calibration.opticalScan')}</span>
                  <div className="settings-screen__slider-fill settings-screen__slider-fill--inactive" style={{ width: `${opticalScan}%` }} />
                </div>
                <span className="settings-screen__slider-value">{opticalScan}%</span>
              </div>
              <div className="settings-screen__temperature">
                {t('settings.calibration.temperature')} <span className="settings-screen__temperature-ok">OK</span>
              </div>
            </div>
          ) : (
            <div className="settings-screen__recalibration">
              <button className="settings-screen__recalibration-button" onClick={() => setStep('calibration')}>
                Recalibration
              </button>
              <div className="settings-screen__temperature">
                {t('settings.calibration.temperature')} <span className="settings-screen__temperature-ok">OK</span>
              </div>
            </div>
          )}
        </div>

        <h1 className="settings-screen__title">{t('settings.title')}</h1>

        {step === 'calibration' ? (
          <div className="settings-screen__optical-section">
            <h3 className="settings-screen__section-title">Optical Calibration</h3>
            <img src="/assets/scan-target.webp" alt="Optical calibration target" className="settings-screen__scan-target" />
          </div>
        ) : (
          <>
            <div className="settings-screen__section">
              <h3 className="settings-screen__section-title">Skin Type</h3>
              <div className="settings-screen__skin-types">
                {skinTypes.map((type) => (
                  <div
                    key={type.id}
                    className={`settings-screen__skin-type ${selectedSkinType === type.id ? 'settings-screen__skin-type--selected' : ''}`}
                    onClick={() => setSelectedSkinType(type.id)}
                  >
                    <div className="settings-screen__skin-type-circle" style={{ backgroundColor: type.color }} />
                    <span className="settings-screen__skin-type-label">{type.label}</span>
                  </div>
                ))}
              </div>
            </div>

            <div className="settings-screen__section">
              <h3 className="settings-screen__section-title">{t('settings.hairColor.title')}</h3>
              <div className="settings-screen__hair-colors">
                {hairColors.map((color) => (
                  <div
                    key={color.id}
                    className={`settings-screen__hair-color ${selectedHairColor === color.id ? 'settings-screen__hair-color--selected' : ''} ${color.disabled ? 'settings-screen__hair-color--disabled' : ''}`}
                    onClick={() => !color.disabled && setSelectedHairColor(color.id)}
                  >
                    <div className="settings-screen__hair-color-circle">
                      <img src={color.image} alt={color.label} className="settings-screen__hair-color-image" />
                      {color.disabled && <div className="settings-screen__hair-color-blocked" />}
                    </div>
                    <span className="settings-screen__hair-color-label">{color.label}</span>
                  </div>
                ))}
              </div>
            </div>

            <div className="settings-screen__section">
              <h3 className="settings-screen__section-title">{t('settings.hairType.title')}</h3>
              <div className="settings-screen__hair-types">
                {hairTypes.map((type) => (
                  <div
                    key={type.id}
                    className={`settings-screen__hair-type ${selectedHairType === type.id ? 'settings-screen__hair-type--selected' : ''}`}
                    onClick={() => setSelectedHairType(type.id)}
                  >
                    <div className="settings-screen__hair-type-icon">
                      <img src={type.image} alt={type.label} className="settings-screen__hair-type-image" />
                    </div>
                    <span className="settings-screen__hair-type-label">{type.label}</span>
                  </div>
                ))}
              </div>
            </div>
          </>
        )}

        <div className="settings-screen__laser-temp">
          {t('settings.laserModuleTemp')}: <span className="settings-screen__laser-temp-value">{temperature}°C</span>
        </div>

        <button className={`settings-screen__start-button settings-screen__start-button--${step}`} onClick={step === 'calibration' ? () => setStep('settings') : handleStart}>
          {step === 'calibration' ? 'Start calibration' : 'Start treatment'}
        </button>
      </div>
    </div>
  )
}

export default SettingsScreen
