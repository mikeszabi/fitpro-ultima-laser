import QtQuick
import QtQuick.Controls

Button {
    id: control
    property bool active: false

    width: 115
    height: 115
    flat: true
    font.pixelSize: 28
    font.bold: false

    contentItem: Text {
        text: control.text
        color: "#ffffff"
        font: control.font
        horizontalAlignment: Text.AlignHCenter
        verticalAlignment: Text.AlignVCenter
        wrapMode: Text.WordWrap
    }

    background: Rectangle {
        radius: width / 2
        color: control.active ? "#55fa7e4e" : "transparent"
        border.width: control.active ? 5 : 3
        border.color: "#ffffff"
    }
}
