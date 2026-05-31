import QtQuick
import QtQuick.Controls

Button {
    id: control
    text: "< BACK"
    width: 112
    height: 44
    flat: true
    font.pixelSize: 20
    font.bold: false

    contentItem: Text {
        text: control.text
        color: "#ffffff"
        font: control.font
        horizontalAlignment: Text.AlignLeft
        verticalAlignment: Text.AlignVCenter
    }

    background: Rectangle {
        color: "transparent"
    }
}
