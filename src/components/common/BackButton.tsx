import { useTranslation } from 'react-i18next'
import { useAppDispatch } from '@/store/hooks'
import { goBack } from '@/store/slices/uiSlice'
import './BackButton.scss'

const BackButton: React.FC = () => {
  const { t } = useTranslation()
  const dispatch = useAppDispatch()

  const handleClick = () => {
    console.log('I"m clicked!')
    dispatch(goBack())
  }

  return (
    <button className="back-button" onClick={handleClick}>
      <svg width="30" height="30" viewBox="0 0 24 24" fill="none">
        <path
          d="M15 18L9 12L15 6"
          stroke="currentColor"
          strokeWidth="2"
          strokeLinecap="round"
          strokeLinejoin="round"
        />
      </svg>
      {t('common.back')}
    </button>
  )
}

export default BackButton
