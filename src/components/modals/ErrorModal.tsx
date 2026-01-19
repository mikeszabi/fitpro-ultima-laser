import { useAppDispatch, useAppSelector } from '@/store/hooks'
import { hideError } from '@/store/slices/systemSlice'
import './ErrorModal.scss'

const ErrorModal: React.FC = () => {
  const dispatch = useAppDispatch()
  const { show, title, message } = useAppSelector((state) => state.system.error)

  if (!show) return null

  const handleClose = () => {
    dispatch(hideError())
  }

  return (
    <div className="error-modal-overlay" onClick={handleClose}>
      <div className="error-modal" onClick={(e) => e.stopPropagation()}>
        <div className="error-modal__header">
          <h2>{title}</h2>
        </div>
        <div className="error-modal__body">
          <p>{message}</p>
        </div>
        <div className="error-modal__footer">
          <button className="error-modal__button" onClick={handleClose}>
            OK
          </button>
        </div>
      </div>
    </div>
  )
}

export default ErrorModal
