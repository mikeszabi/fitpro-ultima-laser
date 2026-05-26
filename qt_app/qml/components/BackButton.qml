import QtQuick
import QtQuick.Controls

Button {
    id: control
    text: "<"
    width: 76
    height: 76
    flat: true
    font.pixelSize: 34
    font.bold: true

    contentItem: Text {
        text: control.text
        color: "#ecfffb"
        font: control.font
        horizontalAlignment: Text.AlignHCenter
        verticalAlignment: Text.AlignVCenter
    }

    background: Rectangle {
        radius: 38
        color: control.down ? "#1a5551" : "#123b39"
        border.color: "#72d8cc"
        border.width: 1
    }
}
