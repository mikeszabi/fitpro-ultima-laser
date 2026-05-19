import { useCallback, useEffect, useRef, useState } from 'react'
import type { ReactNode } from 'react'
import { useTranslation } from 'react-i18next'
import { useAppDispatch, useAppSelector } from '@/store/hooks'
import { showError } from '@/store/slices/systemSlice'
import BackButton from '@/components/common/BackButton'
import { hairKillerApi } from '@/services/hairKillerApi'
import type { TreatmentMode } from '@/types'
import './LaserTreatmentScreen.scss'

type LaserRunState = 'standby' | 'ready'

const SEQUENCE_POLL_MS = 250
const MIN_SEQUENCE_CLEANUP_WAIT_MS = 5000
const MAX_SEQUENCE_CLEANUP_WAIT_MS = 45000

const stringifyBackendValue = (value: unknown) => (
  Array.isArray(value) ? value.join(' ') : String(value || '')
)

const LaserTreatmentScreen: React.FC = () => {
  const { t } = useTranslation()
  const dispatch = useAppDispatch()
  const settings = useAppSelector((state) => state.settings)

  const [treatmentMode, setTreatmentMode] = useState<TreatmentMode>('semi-auto')
  const [laserState, setLaserState] = useState<LaserRunState>('standby')
  const [laserTemp] = useState(21)
  const [vacuumEnabled, setVacuumEnabled] = useState(false)
  const [vacuumLock, setVacuumLock] = useState(false)
  const [redDot, setRedDot] = useState(false)
  const [target, setTarget] = useState(false)
  const [confidence, setConfidence] = useState(0.1)
  const [targetedFollicles, setTargetedFollicles] = useState(0)
  const [loadedTargetCount, setLoadedTargetCount] = useState(0)
  const [nm808Power, setNm808Power] = useState(12)
  const [nm980Power, setNm980Power] = useState(12)
  const [nm1064Power, setNm1064Power] = useState(12)
  const [pulseWidth, setPulseWidth] = useState(80)
  const [apiStatus, setApiStatus] = useState('Backend: checking')
  const [isBusy, setIsBusy] = useState(false)
  const settingsLoadedRef = useRef(false)

  const totalOutputPower = nm808Power + nm980Power + nm1064Power

  const showBackendError = useCallback((title: string, error: unknown) => {
    const message = error instanceof Error ? error.message : 'Unknown backend error'
    setApiStatus(message)
    dispatch(showError({ title, message }))
  }, [dispatch])

  const runBackendAction = useCallback(async (
    label: string,
    action: () => Promise<void>,
  ) => {
    setIsBusy(true)
    setApiStatus(`${label}...`)

    try {
      await action()
      setApiStatus(`${label}: OK`)
    } catch (error) {
      showBackendError(label, error)
    } finally {
      setIsBusy(false)
    }
  }, [showBackendError])

  const syncBackendState = useCallback(async () => {
    try {
      const [health, laserSettings, detectionStatus, stats] = await Promise.all([
        hairKillerApi.health(),
        hairKillerApi.getLaserSettings(),
        hairKillerApi.getDetectionStatus(),
        hairKillerApi.getStats(),
      ])

      setLaserState('standby')
      setNm808Power(laserSettings.power.p808)
      setNm980Power(laserSettings.power.p980)
      setNm1064Power(laserSettings.power.p1064)
      setPulseWidth(laserSettings.pulse_ms)
      setConfidence(detectionStatus.conf)
      setRedDot(detectionStatus.red_dot || stats.red_dot_enabled)
      setTarget(stats.detection_count > 0 || stats.detected_points > 0 || laserSettings.targets_count > 0)
      setTargetedFollicles(laserSettings.targets_count || stats.detected_points || stats.detection_count)
      setLoadedTargetCount(laserSettings.targets_count)
      setApiStatus(health.ok ? 'Backend: connected' : 'Backend: not ready')
      settingsLoadedRef.current = true
    } catch (error) {
      showBackendError('Backend connection', error)
    }

  }, [showBackendError])

  useEffect(() => {
    syncBackendState()
    // Semi-auto temporarily runs without the backend vacuum safety check.
    hairKillerApi.setVacuumCheckEnabled(false)
      .catch((error) => showBackendError('Vacuum check', error))

    const statsInterval = window.setInterval(async () => {
      try {
        const stats = await hairKillerApi.getStats()

        setTarget(stats.detection_count > 0 || stats.detected_points > 0)
        setTargetedFollicles(stats.detected_points || stats.detection_count)
        setRedDot(stats.red_dot_enabled)
      } catch {
        setApiStatus('Backend: polling failed')
      }
    }, 2500)

    const detectionEvents = new EventSource(`${hairKillerApi.baseUrl}/sse/detection`)
    detectionEvents.onmessage = (event) => {
      try {
        const data = JSON.parse(event.data) as { count?: number }
        const count = data.count || 0
        setTarget(count > 0)
        setTargetedFollicles(count)
      } catch {
        // Ignore malformed SSE payloads; the polling loop still keeps state fresh.
      }
    }

    return () => {
      window.clearInterval(statsInterval)
      detectionEvents.close()
    }
  }, [syncBackendState])

  useEffect(() => {
    if (!settingsLoadedRef.current) return

    const handle = window.setTimeout(() => {
      hairKillerApi.updateLaserSettings({
        armed: laserState === 'ready',
        p808: nm808Power,
        p980: nm980Power,
        p1064: nm1064Power,
        pulse_ms: pulseWidth,
        reload_targets: false,
      }).catch((error) => showBackendError('Laser settings', error))
    }, 350)

    return () => window.clearTimeout(handle)
  }, [laserState, nm808Power, nm980Power, nm1064Power, pulseWidth, showBackendError])

  const captureAndLoadTargets = useCallback(async () => {
    const capture = await hairKillerApi.captureDetections()
    setTarget(capture.captured > 0)
    setTargetedFollicles(capture.captured)

    if (capture.captured === 0) {
      await hairKillerApi.clearTargets()
      await hairKillerApi.showTargets(false)
      setLoadedTargetCount(0)
      return 0
    }

    const targets = await hairKillerApi.updateTargets()
    await hairKillerApi.showTargets(true)
    setTargetedFollicles(targets.targets_count)
    setLoadedTargetCount(targets.targets_count)
    return targets.targets_count
  }, [])

  const fireLoadedSequence = useCallback(async () => {
    if (treatmentMode === 'manual') {
      await hairKillerApi.setSequenceMode('manual')
      await hairKillerApi.stepSequence()
      return
    }

    await hairKillerApi.setSequenceMode('auto')
    await hairKillerApi.startSequence()
  }, [treatmentMode])

  const cleanupFinishedSequence = useCallback(async () => {
    try {
      await hairKillerApi.stopSequence()
    } finally {
      await hairKillerApi.clearAppError()
    }
  }, [])

  const waitForSequenceDone = useCallback(async (startedAt: number, targetsCount: number) => {
    const waitMs = Math.min(
      MAX_SEQUENCE_CLEANUP_WAIT_MS,
      Math.max(MIN_SEQUENCE_CLEANUP_WAIT_MS, targetsCount * (pulseWidth + 250) + 3000),
    )
    const deadline = Date.now() + waitMs

    while (Date.now() < deadline) {
      const status = await hairKillerApi.getSequenceStatus()
      const stateText = stringifyBackendValue(status.state).toUpperCase()
      const lastEvent = status.events?.find((event) => (
        typeof event.timestamp === 'number' && event.timestamp >= startedAt - SEQUENCE_POLL_MS
      ))
      const eventText = `${lastEvent?.status || ''} ${lastEvent?.message || ''}`.toUpperCase()

      if (
        lastEvent ||
        stateText.includes('COMPLETED') ||
        stateText.includes('ERROR') ||
        eventText.includes('TARGET_SEQ_FINISHED')
      ) {
        return
      }

      await new Promise((resolve) => window.setTimeout(resolve, SEQUENCE_POLL_MS))
    }
  }, [pulseWidth])

  const fireLoadedSequenceAndCleanup = useCallback(async (targetsCount: number) => {
    const startedAt = Date.now()

    try {
      await fireLoadedSequence()
      await waitForSequenceDone(startedAt, targetsCount)
    } finally {
      await cleanupFinishedSequence()
    }
  }, [cleanupFinishedSequence, fireLoadedSequence, waitForSequenceDone])

  const handleArmToggle = () => {
    const nextReady = laserState === 'standby'

    runBackendAction(nextReady ? 'Arm laser' : 'Disarm laser', async () => {
      if (nextReady) {
        await hairKillerApi.setDetectionEnabled(true)
      }
      await hairKillerApi.updateLaserSettings({
        armed: nextReady,
        p808: nm808Power,
        p980: nm980Power,
        p1064: nm1064Power,
        pulse_ms: pulseWidth,
        reload_targets: true,
      })
      setLaserState(nextReady ? 'ready' : 'standby')
    })
  }

  const handleModeChange = (mode: TreatmentMode) => {
    setTreatmentMode(mode)

    runBackendAction('Treatment mode', async () => {
      await hairKillerApi.setDetectionEnabled(true)
      // Vacuum checks are temporarily disabled for semi-auto so it can run without vacuum.
      await hairKillerApi.setVacuumCheckEnabled(mode === 'auto')
      await hairKillerApi.setSequenceMode(mode)

      if (mode === 'semi-auto') {
        await cleanupFinishedSequence()
        await captureAndLoadTargets()
      }

      if (mode !== 'auto') {
        setVacuumLock(false)
      }
    })
  }

  const handleVacuumEnabledChange = (enabled: boolean) => {
    runBackendAction('Vacuum', async () => {
      await hairKillerApi.setVacuumEnabled(enabled)
      setVacuumEnabled(enabled)
      if (!enabled) setVacuumLock(false)
    })
  }

  const handleVacuumLockChange = (locked: boolean) => {
    runBackendAction('Vacuum lock', async () => {
      setVacuumLock(locked)
      await hairKillerApi.setDetectionEnabled(true)

      if (!locked || treatmentMode === 'manual') {
        return
      }

      const targetsCount = await captureAndLoadTargets()
      if (treatmentMode === 'auto' && targetsCount > 0) {
        await fireLoadedSequenceAndCleanup(targetsCount)
      }
    })
  }

  const handleRedDotChange = (enabled: boolean) => {
    runBackendAction('Red dot', async () => {
      const response = await hairKillerApi.setRedDot(enabled)
      setRedDot(response.enabled)
    })
  }

  const handleConfidenceChange = (value: number) => {
    const normalizedValue = Number((value / 100).toFixed(2))
    setConfidence(normalizedValue)
    hairKillerApi.setDetectionConfidence(normalizedValue)
      .then((response) => setConfidence(response.conf))
      .catch((error) => showBackendError('Detection sensitivity', error))
  }

  const handleFire = () => {
    runBackendAction('Fire', async () => {
      if (laserState !== 'ready') {
        await hairKillerApi.updateLaserSettings({
          armed: true,
          p808: nm808Power,
          p980: nm980Power,
          p1064: nm1064Power,
          pulse_ms: pulseWidth,
          reload_targets: false,
        })
        setLaserState('ready')
      }

      if (treatmentMode === 'manual') {
        let targetsCount = loadedTargetCount
        if (targetsCount === 0) {
          targetsCount = await captureAndLoadTargets()
        }
        if (targetsCount === 0) return
        await fireLoadedSequenceAndCleanup(targetsCount)
        return
      }

      const targetsCount = treatmentMode === 'semi-auto'
        ? await captureAndLoadTargets()
        : loadedTargetCount || await captureAndLoadTargets()

      if (targetsCount === 0) return
      await fireLoadedSequenceAndCleanup(targetsCount)
    })
  }

  const getSkinTypeLabel = () => settings.skinType || 'III'
  const getHairColorLabel = () => {
    const colorMap: Record<string, string> = {
      'grey-white': t('settings.hairColor.greyWhite'),
      red: t('settings.hairColor.red'),
      blonde: t('settings.hairColor.blonde'),
      brown: t('settings.hairColor.brown'),
      'dark-brown': t('settings.hairColor.darkBrown'),
      black: t('settings.hairColor.black')
    }
    return settings.hairColor ? colorMap[settings.hairColor] : t('settings.hairColor.darkBrown')
  }

  const getHairTypeLabel = () => {
    const hairTypeMap: Record<string, string> = {
      thin: t('settings.hairType.thin'),
      medium: t('settings.hairType.medium'),
      thick: t('settings.hairType.thick')
    }
    return settings.hairType ? hairTypeMap[settings.hairType] : t('settings.hairType.medium')
  }

  const calculateBarValue = (
    clientY: number,
    element: HTMLDivElement,
    minValue: number,
    maxValue: number
  ) => {
    const rect = element.getBoundingClientRect()
    const position = 1 - ((clientY - rect.top) / rect.height)
    const value = minValue + position * (maxValue - minValue)

    return Math.max(minValue, Math.min(maxValue, Math.round(value)))
  }

  const updateBarFromPointer = (
    event: React.PointerEvent<HTMLDivElement>,
    setter: (value: number) => void,
    minValue: number,
    maxValue: number
  ) => {
    setter(calculateBarValue(event.clientY, event.currentTarget, minValue, maxValue))
  }

  const startBarDrag = (
    event: React.PointerEvent<HTMLDivElement>,
    setter: (value: number) => void,
    minValue: number,
    maxValue: number
  ) => {
    event.currentTarget.setPointerCapture(event.pointerId)
    updateBarFromPointer(event, setter, minValue, maxValue)
  }

  const bars = [
    { label: '808 nm', value: nm808Power, setValue: setNm808Power, min: 0, max: 100, unit: '%', color: 'claret' },
    { label: '980 nm', value: nm980Power, setValue: setNm980Power, min: 0, max: 100, unit: '%', color: 'red' },
    { label: '1064 nm', value: nm1064Power, setValue: setNm1064Power, min: 0, max: 100, unit: '%', color: 'orange' },
  ]

  const modeLabels: Record<TreatmentMode, ReactNode> = {
    auto: t('laserTreatment.treatmentMode.auto'),
    'semi-auto': <>Semi<br />Auto</>,
    manual: t('laserTreatment.treatmentMode.manual'),
  }

  return (
    <div className="laser-treatment-screen">
      <div className="laser-treatment-screen__background" />
      <BackButton />

      <div className="laser-treatment-screen__content">
        <h1 className="laser-treatment-screen__title">{t('laserTreatment.title')}</h1>

        <div className="laser-treatment-screen__settings-row">
          <span>Skin type: {getSkinTypeLabel()}.</span>
          <span>{t('laserTreatment.hairColor')}: {getHairColorLabel()}</span>
          <span>{t('laserTreatment.hairType')}: {getHairTypeLabel()}</span>
        </div>

        <section className="laser-treatment-screen__output-performance">
          <h2 className="laser-treatment-screen__section-title">{t('laserTreatment.outputPerformance.title')}</h2>
          <div className="laser-treatment-screen__performance-grid">
            <div className="laser-treatment-screen__scale laser-treatment-screen__scale--left">
              <span>100%</span>
              <span>0%</span>
            </div>

            {bars.map((bar) => (
              <div className="laser-treatment-screen__bar-container" key={bar.label}>
                <div className="laser-treatment-screen__bar-label">{bar.label}</div>
                <div
                  className="laser-treatment-screen__bar"
                  role="slider"
                  aria-label={`${bar.label} power`}
                  aria-valuemin={bar.min}
                  aria-valuemax={bar.max}
                  aria-valuenow={bar.value}
                  tabIndex={0}
                  onPointerDown={(event) => startBarDrag(event, bar.setValue, bar.min, bar.max)}
                  onPointerMove={(event) => {
                    if (event.currentTarget.hasPointerCapture(event.pointerId)) {
                      updateBarFromPointer(event, bar.setValue, bar.min, bar.max)
                    }
                  }}
                  onKeyDown={(event) => {
                    if (event.key === 'ArrowUp') bar.setValue(Math.min(bar.max, bar.value + 1))
                    if (event.key === 'ArrowDown') bar.setValue(Math.max(bar.min, bar.value - 1))
                  }}
                >
                  <div className={`laser-treatment-screen__bar-fill laser-treatment-screen__bar-fill--${bar.color}`} style={{ height: `${(bar.value / bar.max) * 100}%` }} />
                </div>
                <div className="laser-treatment-screen__bar-value">{bar.value}{bar.unit}</div>
              </div>
            ))}

            <div className="laser-treatment-screen__red-dot">
              <span>RED DOT</span>
              <div className="laser-treatment-screen__segmented">
                <button className={redDot ? 'is-active' : ''} onClick={() => handleRedDotChange(true)}>ON</button>
                <button className={!redDot ? 'is-active' : ''} onClick={() => handleRedDotChange(false)}>OFF</button>
              </div>
            </div>

            <div className="laser-treatment-screen__bar-container laser-treatment-screen__bar-container--pulse">
              <div className="laser-treatment-screen__bar-label">P.WIDTH</div>
              <div
                className="laser-treatment-screen__bar"
                role="slider"
                aria-label="Pulse width"
                aria-valuemin={10}
                aria-valuemax={1000}
                aria-valuenow={pulseWidth}
                tabIndex={0}
                onPointerDown={(event) => startBarDrag(event, setPulseWidth, 10, 1000)}
                onPointerMove={(event) => {
                  if (event.currentTarget.hasPointerCapture(event.pointerId)) {
                    updateBarFromPointer(event, setPulseWidth, 10, 1000)
                  }
                }}
                onKeyDown={(event) => {
                  if (event.key === 'ArrowUp') setPulseWidth(Math.min(1000, pulseWidth + 10))
                  if (event.key === 'ArrowDown') setPulseWidth(Math.max(10, pulseWidth - 10))
                }}
              >
                <div className="laser-treatment-screen__bar-fill laser-treatment-screen__bar-fill--blue" style={{ height: `${((pulseWidth - 10) / 990) * 100}%` }} />
              </div>
              <div className="laser-treatment-screen__bar-value">{pulseWidth}ms</div>
            </div>

            <div className="laser-treatment-screen__scale laser-treatment-screen__scale--right">
              <span>1000ms</span>
              <span>10ms</span>
            </div>
          </div>
          <div className="laser-treatment-screen__total-power">
            <span>{t('laserTreatment.outputPerformance.totalOutputPower')}:</span>
            <span>{totalOutputPower}%</span>
          </div>
        </section>

        <section className="laser-treatment-screen__treatment-mode">
          <h2 className="laser-treatment-screen__section-title">{t('laserTreatment.treatmentMode.title')}</h2>
          <div className="laser-treatment-screen__mode-buttons">
            {(['auto', 'semi-auto', 'manual'] as TreatmentMode[]).map((mode) => (
              <button
                key={mode}
                className={`laser-treatment-screen__mode-button ${treatmentMode === mode ? 'laser-treatment-screen__mode-button--active' : ''}`}
                onClick={() => handleModeChange(mode)}
              >
                <span>{modeLabels[mode]}</span>
              </button>
            ))}
          </div>
        </section>

        <div className="laser-treatment-screen__laser-temp">
          {t('laserTreatment.laserModuleTemp')}: <span>{laserTemp.toFixed(1)}°C</span>
        </div>

        <button className={`laser-treatment-screen__arm-button laser-treatment-screen__arm-button--${laserState}`} onClick={handleArmToggle} disabled={isBusy}>
          {laserState === 'standby' ? 'ARM' : 'DISARM'}
        </button>

        <section className={`laser-treatment-screen__camera-section ${laserState === 'ready' ? 'laser-treatment-screen__camera-section--ready' : ''}`}>
          <div className="laser-treatment-screen__camera-container">
            <img src={hairKillerApi.getFrameUrl()} alt="Treatment camera stream" className="laser-treatment-screen__camera-feed" />
          </div>

          <div className="laser-treatment-screen__status-panel">
            <div className="laser-treatment-screen__toggle-row">
              <span>VACUUM:</span>
              <div className="laser-treatment-screen__segmented laser-treatment-screen__segmented--small">
                <button className={vacuumEnabled ? 'is-active' : ''} onClick={() => handleVacuumEnabledChange(true)}>ON</button>
                <button className={!vacuumEnabled ? 'is-active' : ''} onClick={() => handleVacuumEnabledChange(false)}>OFF</button>
              </div>
            </div>
            <div className="laser-treatment-screen__toggle-row">
              <span>{t('laserTreatment.vacuumLock')}:</span>
              <div className="laser-treatment-screen__segmented laser-treatment-screen__segmented--small">
                <button className={vacuumLock ? 'is-active' : ''} onClick={() => handleVacuumLockChange(true)}>ON</button>
                <button className={!vacuumLock ? 'is-active' : ''} onClick={() => handleVacuumLockChange(false)}>OFF</button>
              </div>
            </div>
            <label className="laser-treatment-screen__confidence">
              <span>SENSITIVITY: {confidence.toFixed(2)}</span>
              <input type="range" min="1" max="100" value={Math.round(confidence * 100)} onChange={(event) => handleConfidenceChange(Number(event.target.value))} />
            </label>
            <button className="laser-treatment-screen__fire-button" onClick={handleFire} disabled={isBusy}>FIRE</button>
            <div className="laser-treatment-screen__target-state">
              <span>{t('laserTreatment.target')}: <strong className={target ? 'is-ok' : 'is-no'}>{target ? 'OK' : 'NO'}</strong></span>
              <small>{t('laserTreatment.targetedFollicles')}: {targetedFollicles}</small>
              <small className="laser-treatment-screen__api-status">{apiStatus}</small>
            </div>
          </div>
        </section>
      </div>
    </div>
  )
}

export default LaserTreatmentScreen
