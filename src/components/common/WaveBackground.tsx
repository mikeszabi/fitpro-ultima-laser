import './WaveBackground.scss'

const WaveBackground: React.FC = () => {
  return (
    <div className="wave-background">
      <div className="wave-background__wave wave-background__wave--1"></div>
      <div className="wave-background__wave wave-background__wave--2"></div>
      <div className="wave-background__gradient"></div>
    </div>
  )
}

export default WaveBackground
