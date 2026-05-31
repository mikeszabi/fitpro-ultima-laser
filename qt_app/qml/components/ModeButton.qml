import QtQuick
import QtQuick.Controls

Button {
    id: control
    property bool active: false

    width: 112
    height: 112
    flat: true
    font.pixelSize: 25
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
        color: control.active ? "#88b56d5f" : "transparent"
        border.width: control.active ? 7 : 3
        border.color: "#ffffff"
    }
}
