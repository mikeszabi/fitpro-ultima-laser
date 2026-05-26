import QtQuick
import QtQuick.Controls

Button {
    id: control
    property color accent: "#ff7a1a"
    property color danger: "#dc4f5d"

    implicitHeight: 72
    font.pixelSize: 25
    font.bold: false
    flat: true

    contentItem: Text {
        text: control.text
        color: control.enabled ? "#f6fbfa" : "#7d8d8d"
        font: control.font
        horizontalAlignment: Text.AlignHCenter
        verticalAlignment: Text.AlignVCenter
        elide: Text.ElideRight
    }

    background: Rectangle {
        radius: height / 2
        color: control.down ? "#22ffffff" : "transparent"
        opacity: control.enabled ? 1.0 : 0.45
        border.width: 3
        border.color: control.accent
    }
}
