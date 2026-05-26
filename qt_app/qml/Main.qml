import QtQuick
import QtQuick.Controls
import QtQuick.Layouts
import QtQuick.Window
import "components"
import "screens"

ApplicationWindow {
    id: root
    width: 1080
    height: 1920
    visible: true
    visibility: windowedMode ? Window.Windowed : Window.FullScreen
    title: "FitPro Ultima Laser"
    color: "#071016"

    FontLoader {
        id: hurme
        source: "../../public/fonts/HurmeGeometricSans2-Regular.otf"
    }

    Image {
        anchors.fill: parent
        source: "../../public/assets/ultima-wave-bg.webp"
        fillMode: Image.PreserveAspectCrop
    }

    Rectangle {
        anchors.fill: parent
        color: "#33000000"
    }

    Loader {
        id: screenLoader
        anchors.fill: parent
        sourceComponent: {
            switch (appController.screen) {
            case "login": return loginScreen
            case "settings": return settingsScreen
            case "laser-treatment": return laserTreatmentScreen
            case "system-info": return systemInfoScreen
            default: return startScreen
            }
        }
    }

    ErrorDialog {
        anchors.fill: parent
        titleText: appController.errorTitle
        messageText: appController.errorMessage
        visible: appController.errorMessage.length > 0
        onAccepted: appController.clearError()
    }

    Component { id: startScreen; StartScreen {} }
    Component { id: loginScreen; LoginScreen {} }
    Component { id: settingsScreen; SettingsScreen {} }
    Component { id: laserTreatmentScreen; LaserTreatmentScreen {} }
    Component { id: systemInfoScreen; SystemInfoScreen {} }
}
