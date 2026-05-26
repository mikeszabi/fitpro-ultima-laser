import QtQuick
import QtQuick.Controls

Item {
    id: root
    property string titleText: ""
    property string messageText: ""
    signal accepted()

    Rectangle {
        anchors.fill: parent
        color: "#b0000000"
        visible: root.visible
    }

    Rectangle {
        width: Math.min(parent.width - 96, 760)
        height: 320
        anchors.centerIn: parent
        radius: 8
        color: "#111b20"
        border.color: "#dc4f5d"
        border.width: 2

        Column {
            anchors.fill: parent
            anchors.margins: 34
            spacing: 24

            Text {
                width: parent.width
                text: root.titleText || "Error"
                color: "#ffffff"
                font.pixelSize: 32
                font.bold: true
                wrapMode: Text.WordWrap
            }

            Text {
                width: parent.width
                text: root.messageText
                color: "#d8e4e3"
                font.pixelSize: 22
                wrapMode: Text.WordWrap
            }

            AppButton {
                width: 180
                text: "OK"
                anchors.horizontalCenter: parent.horizontalCenter
                onClicked: root.accepted()
            }
        }
    }
}
