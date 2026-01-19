import { useTranslation } from 'react-i18next'
import { useAppDispatch } from '@/store/hooks'
import { setCurrentScreen } from '@/store/slices/uiSlice'
import './StartScreen.scss'

const StartScreen: React.FC = () => {
  const { t } = useTranslation()
  const dispatch = useAppDispatch()

  const handleGetStarted = () => {
    dispatch(setCurrentScreen('login'))
  }

  return (
    <div className="start-screen">
      <div className="start-screen__background" />
      <div className="start-screen__content">
        <div className="start-screen__logo">
          <img 
            src="/assets/Ultima-logo.png" 
            alt="Ultima Logo" 
            className="start-screen__logo-image"
          />
        </div>
        <div className="start-screen__text">
          <img 
            src="/assets/ULTIMA.png" 
            alt="ULTIMA" 
            className="start-screen__text-image"
          />
          <span className="start-screen__laser">LASER</span>
          <button className="start-screen__button" onClick={handleGetStarted}>
            {t('start.getStarted')}
          </button>
        </div>
      </div>
    </div>
  )
}

export default StartScreen
