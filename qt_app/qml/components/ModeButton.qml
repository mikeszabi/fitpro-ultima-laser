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
        color: control.active ? "#8fb56d5f" : "#09000000"
        border.width: control.active ? 7 : 3
        border.color: "#ffffff"

        Rectangle {
            anchors.fill: parent
            anchors.margins: 4
            radius: width / 2
            visible: control.active
            color: "transparent"
            border.width: 2
            border.color: "#ffc1b5"
        }
    }
}
