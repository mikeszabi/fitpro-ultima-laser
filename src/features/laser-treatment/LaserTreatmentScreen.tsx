import { useState, useRef, useEffect } from 'react'
import { useTranslation } from 'react-i18next'
import { useAppSelector } from '@/store/hooks'
import BackButton from '@/components/common/BackButton'
import './LaserTreatmentScreen.scss'

type TreatmentMode = 'auto' | 'semi-auto' | 'manual'
type LaserRunState = 'standby' | 'ready'

const LaserTreatmentScreen: React.FC = () => {
  const { t } = useTranslation()
  const settings = useAppSelector((state) => state.settings)
  
  const [treatmentMode, setTreatmentMode] = useState<TreatmentMode>('semi-auto')
  const [laserState, setLaserState] = useState<LaserRunState>('standby')
  const [isAdjusting, setIsAdjusting] = useState(false)
  const [laserTemp, setLaserTemp] = useState(21)
  const [vacuumLock, setVacuumLock] = useState(false)
  const [target, setTarget] = useState(false)
  const [targetedFollicles, setTargetedFollicles] = useState(0)
  
  // Output performance values (calculated from settings)
  const [nm808Power, setNm808Power] = useState(12)
  const [nm980Power, setNm980Power] = useState(12)
  const [nm1064Power, setNm1064Power] = useState(12)
  const [pulseWidth, setPulseWidth] = useState(10)
  
  // Camera
  const videoRef = useRef<HTMLVideoElement>(null)
  const [cameraActive, setCameraActive] = useState(false)

  // TODO remove when backend is ready
  useEffect(() => {
    setLaserTemp(21)
  }, [])

  const handleStandbyToggle = () => {
    if (laserState === 'standby') {
      setLaserState('ready')
      setCameraActive(true)
      setVacuumLock(true)
      setTarget(true)
      setTargetedFollicles(6)
    } else {
      setLaserState('standby')
      setCameraActive(false)
      setVacuumLock(false)
      setTarget(false)
      setTargetedFollicles(0)
    }
  }

  // Mock camera activation
  useEffect(() => {
    if (cameraActive && videoRef.current) {
      navigator.mediaDevices
        .getUserMedia({ video: true })
        .then((stream) => {
          if (videoRef.current) {
            videoRef.current.srcObject = stream
          }
        })
        .catch((err) => {
          console.error('Camera access error:', err)
        })
    } else if (!cameraActive && videoRef.current && videoRef.current.srcObject) {
      const stream = videoRef.current.srcObject as MediaStream
      stream.getTracks().forEach((track) => track.stop())
      videoRef.current.srcObject = null
    }
  }, [cameraActive])

  const getSkinTypeLabel = () => {
    if (!settings.skinType) return t('settings.skinType.type3')
    const skinTypeMap: Record<string, string> = {
      'I': t('settings.skinType.type1'),
      'II': t('settings.skinType.type2'),
      'III': t('settings.skinType.type3'),
      'IV': t('settings.skinType.type4'),
      'V': t('settings.skinType.type5'),
      'VI': t('settings.skinType.type6')
    }
    return skinTypeMap[settings.skinType] || t('settings.skinType.type3')
  }

  const getHairColorLabel = () => {
    if (!settings.hairColor) return t('settings.hairColor.darkBrown')
    const colorMap: Record<string, string> = {
      'blonde': t('settings.hairColor.blonde'),
      'brown': t('settings.hairColor.brown'),
      'dark-brown': t('settings.hairColor.darkBrown'),
      'black': t('settings.hairColor.black'),
      'red': t('settings.hairColor.red'),
      'grey-white': t('settings.hairColor.greyWhite')
    }
    return colorMap[settings.hairColor] || t('settings.hairColor.darkBrown')
  }

  const getHairTypeLabel = () => {
    if (!settings.hairType) return t('settings.hairType.medium')
    const hairTypeMap: Record<string, string> = {
      'thin': t('settings.hairType.thin'),
      'medium': t('settings.hairType.medium'),
      'thick': t('settings.hairType.thick')
    }
    return hairTypeMap[settings.hairType] || t('settings.hairType.medium')
  }

  const totalOutputPower = nm808Power + nm980Power + nm1064Power

  // Common function to calculate bar value from position
  const calculateBarValue = (
    clientY: number,
    rect: DOMRect,
    minValue: number,
    maxValue: number
  ): number => {
    const clickY = clientY - rect.top
    const percentage = 1 - (clickY / rect.height) // Invert because bars fill from bottom
    return Math.max(minValue, Math.min(maxValue, Math.round(percentage * (maxValue - minValue) + minValue)))
  }

  // Handle bar click
  const handleBarClick = (
    e: React.MouseEvent<HTMLDivElement>,
    setter: (value: number) => void,
    minValue: number,
    maxValue: number
  ) => {
    const rect = e.currentTarget.getBoundingClientRect()
    const newValue = calculateBarValue(e.clientY, rect, minValue, maxValue)
    setter(newValue)
    setIsAdjusting(true)
  }

  // Handle touch start
  const handleBarTouchStart = (
    e: React.TouchEvent<HTMLDivElement>,
    setter: (value: number) => void,
    minValue: number,
    maxValue: number
  ) => {
    e.preventDefault()
    const rect = e.currentTarget.getBoundingClientRect()
    const newValue = calculateBarValue(e.touches[0].clientY, rect, minValue, maxValue)
    setter(newValue)
    setIsAdjusting(true)
  }

  // Handle touch move (swipe gesture)
  const handleBarTouchMove = (
    e: React.TouchEvent<HTMLDivElement>,
    setter: (value: number) => void,
    minValue: number,
    maxValue: number
  ) => {
    e.preventDefault()
    const rect = e.currentTarget.getBoundingClientRect()
    const newValue = calculateBarValue(e.touches[0].clientY, rect, minValue, maxValue)
    setter(newValue)
  }

  return (
    <div className="laser-treatment-screen">
      <div className="laser-treatment-screen__background" />
      <BackButton />
      
      <div className="laser-treatment-screen__content">
        <h1 className="laser-treatment-screen__title">{t('laserTreatment.title')}</h1>
        
        {/* Settings Display Row */}
        <div className="laser-treatment-screen__settings-row">
          <div className="laser-treatment-screen__setting">
            <span className="laser-treatment-screen__setting-label">{t('laserTreatment.fpSkinType')}:</span>
            {isAdjusting ? (
              <img src="/assets/ss.png" alt="Adjusting" className="laser-treatment-screen__setting-icon" />
            ) : (
              <span className="laser-treatment-screen__setting-value">{getSkinTypeLabel()}</span>
            )}
          </div>
          <div className="laser-treatment-screen__setting">
            <span className="laser-treatment-screen__setting-label">{t('laserTreatment.hairColor')}:</span>
            {isAdjusting ? (
              <img src="/assets/ss.png" alt="Adjusting" className="laser-treatment-screen__setting-icon" />
            ) : (
              <span className="laser-treatment-screen__setting-value">{getHairColorLabel()}</span>
            )}
          </div>
          <div className="laser-treatment-screen__setting">
            <span className="laser-treatment-screen__setting-label">{t('laserTreatment.hairType')}:</span>
            {isAdjusting ? (
              <img src="/assets/ss.png" alt="Adjusting" className="laser-treatment-screen__setting-icon" />
            ) : (
              <span className="laser-treatment-screen__setting-value">{getHairTypeLabel()}</span>
            )}
          </div>
        </div>

        {/* Output Performance Section */}
        <div className="laser-treatment-screen__output-performance">
          <h3 className="laser-treatment-screen__section-title">{t('laserTreatment.outputPerformance.title')}</h3>
          
          <div className="laser-treatment-screen__performance-content">
            {/* Laser bars - Two groups */}
            <div className="laser-treatment-screen__laser-bars">
              {/* Left group: 808nm, 980nm, 1064nm */}

              <div className="laser-treatment-screen__laser-group">
                {/* Left scale with labels */}
                <div className="laser-treatment-screen__scale-container laser-treatment-screen__scale-container--left">
                  <div className="laser-treatment-screen__scale-labels">
                    <div className="laser-treatment-screen__scale-label laser-treatment-screen__scale-label--top">15W</div>
                    <div className="laser-treatment-screen__scale-label laser-treatment-screen__scale-label--bottom">0W</div>
                  </div>
                  <img 
                    src="/assets/merosav-2.png" 
                    alt="Scale" 
                    className="laser-treatment-screen__scale laser-treatment-screen__scale--left"
                  />
                </div>
                  {/* 808 nm */}
                  <div className="laser-treatment-screen__bar-container laser-treatment-screen__scale-container--margin-right">
                    <div className="laser-treatment-screen__bar-label">808 nm</div>
                    <div 
                      className="laser-treatment-screen__bar-wrapper"
                      onClick={(e) => handleBarClick(e, setNm808Power, 0, 15)}
                      onTouchStart={(e) => handleBarTouchStart(e, setNm808Power, 0, 15)}
                      onTouchMove={(e) => handleBarTouchMove(e, setNm808Power, 0, 15)}
                    >
                      <div className="laser-treatment-screen__bar">
                        <div 
                          className="laser-treatment-screen__bar-fill laser-treatment-screen__bar-fill--claret"
                          style={{ height: `${(nm808Power / 15) * 100}%` }}
                        />
                      </div>
                    </div>
                    <div className="laser-treatment-screen__bar-value">{nm808Power}W</div>
                  </div>
                {/* </div> */}

                {/* 980 nm */}
                <div className="laser-treatment-screen__bar-container laser-treatment-screen__scale-container--margin-right">
                  <div className="laser-treatment-screen__bar-label">980 nm</div>
                  <div 
                    className="laser-treatment-screen__bar-wrapper"
                    onClick={(e) => handleBarClick(e, setNm980Power, 0, 15)}
                    onTouchStart={(e) => handleBarTouchStart(e, setNm980Power, 0, 15)}
                    onTouchMove={(e) => handleBarTouchMove(e, setNm980Power, 0, 15)}
                  >
                    <div className="laser-treatment-screen__bar">
                      <div 
                        className="laser-treatment-screen__bar-fill laser-treatment-screen__bar-fill--red"
                        style={{ height: `${(nm980Power / 15) * 100}%` }}
                      />
                    </div>
                  </div>
                  <div className="laser-treatment-screen__bar-value">{nm980Power}W</div>
                </div>

                {/* 1064 nm */}
                <div className="laser-treatment-screen__bar-container laser-treatment-screen__scale-container--margin-right">
                  <div className="laser-treatment-screen__bar-label">1064 nm</div>
                  <div 
                    className="laser-treatment-screen__bar-wrapper"
                    onClick={(e) => handleBarClick(e, setNm1064Power, 0, 15)}
                    onTouchStart={(e) => handleBarTouchStart(e, setNm1064Power, 0, 15)}
                    onTouchMove={(e) => handleBarTouchMove(e, setNm1064Power, 0, 15)}
                  >
                    <div className="laser-treatment-screen__bar">
                      <div 
                        className="laser-treatment-screen__bar-fill laser-treatment-screen__bar-fill--orange"
                        style={{ height: `${(nm1064Power / 15) * 100}%` }}
                      />
                    </div>
                  </div>
                  <div className="laser-treatment-screen__bar-value">{nm1064Power}W</div>
                </div>
              </div>

              {/* Right group: P.WIDTH */}
              <div className="laser-treatment-screen__laser-group">
                {/* Pulse Width */}
                <div className="laser-treatment-screen__bar-container">
                  <div className="laser-treatment-screen__bar-label">P.WIDTH</div>
                  <div 
                    className="laser-treatment-screen__bar-wrapper"
                    onClick={(e) => handleBarClick(e, setPulseWidth, 10, 110)}
                    onTouchStart={(e) => handleBarTouchStart(e, setPulseWidth, 10, 110)}
                    onTouchMove={(e) => handleBarTouchMove(e, setPulseWidth, 10, 110)}
                  >
                    <div className="laser-treatment-screen__bar">
                      <div 
                        className="laser-treatment-screen__bar-fill laser-treatment-screen__bar-fill--blue"
                        style={{ height: `${(pulseWidth - 10)}%` }}
                      />
                    </div>
                  </div>
                  <div className="laser-treatment-screen__bar-value">{pulseWidth}W</div>
                </div>
                
                {/* Right scale with labels (mirrored) */}
                <div className="laser-treatment-screen__scale-container laser-treatment-screen__scale-container--right">
                  <img
                    src="/assets/merosav-2.png" 
                    alt="Scale" 
                    className="laser-treatment-screen__scale laser-treatment-screen__scale--right"
                  />
                  <div className="laser-treatment-screen__scale-labels">
                    <div className="laser-treatment-screen__scale-label laser-treatment-screen__scale-label--top">110ms</div>
                    <div className="laser-treatment-screen__scale-label laser-treatment-screen__scale-label--bottom">10ms</div>
                  </div>
                </div>
              </div>
            </div>

            {/* Total Output Power */}
            <div className="laser-treatment-screen__total-power">
              <span className="laser-treatment-screen__total-power-label">{t('laserTreatment.outputPerformance.totalOutputPower')}:</span>
              <span className="laser-treatment-screen__total-power-value">{totalOutputPower} J/cm2</span>
            </div>
          </div>
        </div>

        {/* Treatment Mode Section */}
        <div className="laser-treatment-screen__treatment-mode">
          <h3 style={{marginBottom: 0}} className="laser-treatment-screen__section-title">{t('laserTreatment.treatmentMode.title')}</h3>
          
          <div className="laser-treatment-screen__mode-buttons">
            <button
              className={`laser-treatment-screen__mode-button ${
                treatmentMode === 'auto' ? 'laser-treatment-screen__mode-button--active' : ''
              }`}
              onClick={() => setTreatmentMode('auto')}
            >
              <span>{t('laserTreatment.treatmentMode.auto')}</span>
            </button>
            <button
              className={`laser-treatment-screen__mode-button ${
                treatmentMode === 'semi-auto' ? 'laser-treatment-screen__mode-button--active' : ''
              }`}
              onClick={() => setTreatmentMode('semi-auto')}
            >
              <span dangerouslySetInnerHTML={{ __html: t('laserTreatment.treatmentMode.semiAuto').replace(' ', '<br/>') }} />
            </button>
            <button
              className={`laser-treatment-screen__mode-button ${
                treatmentMode === 'manual' ? 'laser-treatment-screen__mode-button--active' : ''
              }`}
              onClick={() => setTreatmentMode('manual')}
            >
              <span>{t('laserTreatment.treatmentMode.manual')}</span>
            </button>
          </div>
        </div>

        {/* Laser Module Temperature */}
        <div className="laser-treatment-screen__laser-temp">
          <span className="laser-treatment-screen__laser-temp-label">{t('laserTreatment.laserModuleTemp')}:</span>
          <span className="laser-treatment-screen__laser-temp-value">{laserTemp}°C</span>
        </div>

        {/* Standby/Ready Button */}
        <button
          className={`laser-treatment-screen__standby-button ${
            laserState === 'ready' ? 'laser-treatment-screen__standby-button--ready' : ''
          }`}
          onClick={handleStandbyToggle}
        >
          {laserState === 'standby' ? t('laserTreatment.standby') : t('laserTreatment.ready')}
        </button>

        {/* Camera and Status Section */}
        <div className="laser-treatment-screen__camera-section">
          <div className="laser-treatment-screen__camera-container">
            {cameraActive ? (
              <video
                ref={videoRef}
                autoPlay
                playsInline
                className="laser-treatment-screen__camera-feed"
              />
            ) : (
              <div className="laser-treatment-screen__camera-placeholder" />
            )}
          </div>

          <div className="laser-treatment-screen__status">
            <div className="laser-treatment-screen__status-item">
              <span className="laser-treatment-screen__status-label">{t('laserTreatment.vacuumLock')}:</span>
              <span className={`laser-treatment-screen__status-value ${
                vacuumLock ? 'laser-treatment-screen__status-value--ok' : 'laser-treatment-screen__status-value--no'
              }`}>
                {vacuumLock ? t('laserTreatment.status.ok') : t('laserTreatment.status.no')}
              </span>
            </div>
            <div className="laser-treatment-screen__status-item">
              <span className="laser-treatment-screen__status-label">{t('laserTreatment.target')}:</span>
              <span className={`laser-treatment-screen__status-value ${
                target ? 'laser-treatment-screen__status-value--ok' : 'laser-treatment-screen__status-value--no'
              }`}>
                {target ? t('laserTreatment.status.ok') : t('laserTreatment.status.no')}
              </span>
            </div>
          </div>

          <div className="laser-treatment-screen__follicles">
            <span className="laser-treatment-screen__follicles-label">{t('laserTreatment.targetedFollicles')}:</span>
            <span className="laser-treatment-screen__follicles-value">{targetedFollicles}</span>
          </div>
        </div>
      </div>
    </div>
  )
}

export default LaserTreatmentScreen
