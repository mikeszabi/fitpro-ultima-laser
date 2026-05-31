import QtQuick
import QtQuick.Controls
import QtQuick.Layouts
import QtQuick.Window
import "components"
import "screens"

ApplicationWindow {
    id: root
    readonly property int designWidth: 1080
    readonly property int designHeight: 1920
    readonly property real fitScale: Math.min(width / designWidth, height / designHeight)

    width: wideScreenMode ? 1920 : designWidth
    height: wideScreenMode ? 1080 : designHeight
    visible: true
    visibility: windowedMode ? Window.Windowed : Window.FullScreen
    title: "FitPro Ultima Laser"
    color: "#071016"

    FontLoader {
        id: hurme
        source: "../assets/fonts/HurmeGeometricSans2-Regular.otf"
    }

    Image {
        anchors.fill: parent
        source: "../assets/images/Background-2.png"
        fillMode: Image.PreserveAspectCrop
    }

    Rectangle {
        anchors.fill: parent
        color: "#15000000"
    }

    Item {
        id: appSurface
        width: designWidth
        height: designHeight
        anchors.centerIn: parent
        scale: wideScreenMode ? fitScale : 1
        transformOrigin: Item.Center
        clip: true

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
    }

    Component { id: startScreen; StartScreen {} }
    Component { id: loginScreen; LoginScreen {} }
    Component { id: settingsScreen; SettingsScreen {} }
    Component { id: laserTreatmentScreen; LaserTreatmentScreen {} }
    Component { id: systemInfoScreen; SystemInfoScreen {} }
}
