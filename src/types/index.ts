export type ScreenType = 'start' | 'login' | 'settings' | 'laser-treatment' | 'system-info'

export type FitzpatrickSkinType = 'I' | 'II' | 'III' | 'IV' | 'V' | 'VI'

export type HairColor = 'grey-white' | 'red' | 'blonde' | 'brown' | 'dark-brown' | 'black'

export type HairType = 'thin' | 'medium' | 'thick'

export type TreatmentMode = 'auto' | 'semi-auto' | 'manual'

export type LaserRunState = 'standby' | 'ready'

export interface User {
  name: string
  email: string
  role: string
  licenseExpiration: string
}

export interface CalibrationData {
  laserPower: number
  opticalScan: number
  temperature: string
}

export interface LaserParameters {
  nm808: number
  nm980: number
  nm1064: number
  pulseWidth: number
}

export interface SystemStatus {
  connected: boolean
  laserModuleTemp: number
  vacuumLock: boolean
  target: boolean
  targetedFollicles: number
}

export interface HardwareDetails {
  efLaserSerial: string
  pcSerial: string
}

export interface SoftwareDetails {
  firmwareVersion: string
  guiVersion: string
}

export interface ErrorState {
  show: boolean
  message: string
  title: string
}
