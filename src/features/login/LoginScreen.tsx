import { useState } from 'react'
import { useTranslation } from 'react-i18next'
import { useAppDispatch } from '@/store/hooks'
import { setCurrentScreen } from '@/store/slices/uiSlice'
import { loginSuccess, setLoading } from '@/store/slices/authSlice'
import { showError } from '@/store/slices/systemSlice'
import { authService } from '@/services/authService'
import InfoButton from '@/components/common/InfoButton'
import './LoginScreen.scss'

const LoginScreen: React.FC = () => {
  const { t } = useTranslation()
  const dispatch = useAppDispatch()
  const [email, setEmail] = useState('')
  const [password, setPassword] = useState('')
  const [showPassword, setShowPassword] = useState(false)

  const handleLogin = async (e: React.FormEvent) => {
    e.preventDefault()
    e.stopPropagation()
    
    if (!email || !password) {
      dispatch(showError({
        title: t('error.authFailed'),
        message: t('error.authFailedMessage'),
      }))
      return
    }

    try {
      dispatch(setLoading(true))
      const user = await authService.login(email, password)
      dispatch(loginSuccess(user))
      dispatch(setCurrentScreen('settings'))
    } catch (error) {
      dispatch(showError({
        title: t('error.authFailed'),
        message: t('error.authFailedMessage'),
      }))
    } finally {
      dispatch(setLoading(false))
    }
  }

  return (
    <div className="login-screen">
      <div className="login-screen__background" />
      <InfoButton />
      
      <div className="login-screen__content">
        <div className="login-screen__text">
          <img 
            src="/assets/ULTIMA.png" 
            alt="ULTIMA" 
            className="login-screen__text-image"
          />
          <span className="login-screen__laser">{t('login.subtitle')}</span>
        </div>
        
        <p className="login-screen__description">{t('login.description')}</p>
        
        <form className="login-screen__form" onSubmit={handleLogin}>
          <div className="login-screen__input-group">
            <input
              type="text"
              className="login-screen__input"
              placeholder={t('login.email')}
              value={email}
              onChange={(e) => setEmail(e.target.value)}
              onKeyDown={(e) => {
                if (e.key === 'Enter') {
                  e.preventDefault()
                }
              }}
              autoComplete="email"
              inputMode="email"
            />
          </div>
          
          <div className="login-screen__input-group">
            <input
              type={showPassword ? 'text' : 'password'}
              className="login-screen__input"
              placeholder={t('login.password')}
              value={password}
              onChange={(e) => setPassword(e.target.value)}
              onKeyDown={(e) => {
                if (e.key === 'Enter') {
                  e.preventDefault()
                }
              }}
            />
            <button
              type="button"
              className="login-screen__password-toggle"
              onClick={() => setShowPassword(!showPassword)}
            >
              {showPassword ? (
                <svg width="20" height="20" viewBox="0 0 20 20" fill="none">
                  <path d="M2 10s3-6 8-6 8 6 8 6-3 6-8 6-8-6-8-6z" stroke="currentColor" strokeWidth="2" />
                  <circle cx="10" cy="10" r="3" stroke="currentColor" strokeWidth="2" />
                </svg>
              ) : (
                <svg width="20" height="20" viewBox="0 0 20 20" fill="none">
                  <path d="M2 10s3-6 8-6 8 6 8 6-3 6-8 6-8-6-8-6z" stroke="currentColor" strokeWidth="2" />
                  <circle cx="10" cy="10" r="3" stroke="currentColor" strokeWidth="2" />
                  <line x1="2" y1="2" x2="18" y2="18" stroke="currentColor" strokeWidth="2" />
                </svg>
              )}
            </button>
          </div>
          
          <button type="submit" className="login-screen__button">
            {t('login.loginButton')}
          </button>
        </form>
      </div>
    </div>
  )
}

export default LoginScreen
