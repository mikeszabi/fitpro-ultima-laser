import { useAppDispatch } from '@/store/hooks'
import { setCurrentScreen } from '@/store/slices/uiSlice'
import './InfoButton.scss'

const InfoButton: React.FC = () => {
  const dispatch = useAppDispatch()

  const handleClick = () => {
    dispatch(setCurrentScreen('system-info'))
  }

  return (
    <button className="info-button" onClick={handleClick}>
      <div className="info-button__circle">
        <span className="info-button__text">i</span>
      </div>
    </button>
  )
}

export default InfoButton
