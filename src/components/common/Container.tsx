import './Container.scss'

interface ContainerProps {
  children: React.ReactNode
  title?: string
  className?: string
}

const Container: React.FC<ContainerProps> = ({ children, title, className = '' }) => {
  return (
    <div className={`container ${className}`}>
      {title && <h3 className="container__title">{title}</h3>}
      <div className="container__content">{children}</div>
    </div>
  )
}

export default Container
