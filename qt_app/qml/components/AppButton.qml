import QtQuick
import QtQuick.Controls

Button {
    id: control
    property color accent: "#ffffff"
    property color danger: "#dc4f5d"
    property color textColor: "#ffffff"

    implicitHeight: 58
    font.pixelSize: 18
    font.bold: false
    flat: true

    contentItem: Text {
        text: control.text
        color: control.enabled ? control.textColor : "#7d8d8d"
        font: control.font
        horizontalAlignment: Text.AlignHCenter
        verticalAlignment: Text.AlignVCenter
        elide: Text.ElideRight
    }

    background: Rectangle {
        radius: height / 2
        color: control.down ? "#26ffffff" : "transparent"
        opacity: control.enabled ? 1.0 : 0.45
        border.width: 4
        border.color: control.accent
        clip: true

        Rectangle {
            width: parent.width * 0.38
            height: parent.height
            radius: parent.radius
            opacity: control.down ? 0.72 : 0.58
            gradient: Gradient {
                GradientStop { position: 0.0; color: "#f2ffffff" }
                GradientStop { position: 1.0; color: "#00ffffff" }
            }
        }
    }
}
