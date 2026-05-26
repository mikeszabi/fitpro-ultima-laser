import QtQuick
import QtQuick.Controls
import QtQuick.Layouts

Rectangle {
    id: root
    property string label: ""
    property int value: 0
    property int step: 1
    property color fillColor: "#ff4d0b"
    signal changed(int value)

    width: 120
    height: 430
    color: "transparent"

    ColumnLayout {
        anchors.fill: parent
        spacing: 8

        Text {
            Layout.fillWidth: true
            text: root.label
            color: "#ffffff"
            font.pixelSize: 17
            font.bold: true
            horizontalAlignment: Text.AlignHCenter
        }

        Button {
            Layout.alignment: Qt.AlignHCenter
            Layout.preferredWidth: 72
            Layout.preferredHeight: 52
            text: "+"
            font.pixelSize: 30
            font.bold: true
            onClicked: root.changed(Math.min(100, root.value + root.step))
        }

        Rectangle {
            Layout.alignment: Qt.AlignHCenter
            Layout.preferredWidth: 78
            Layout.preferredHeight: 260
            radius: 20
            color: "#10111b"
            border.color: "#33ffffff"
            border.width: 1
            clip: true

            Rectangle {
                anchors.left: parent.left
                anchors.right: parent.right
                anchors.bottom: parent.bottom
                height: parent.height * root.value / 100
                color: root.fillColor
            }

            MouseArea {
                anchors.fill: parent
                onClicked: function(mouse) {
                    var nextValue = Math.round((1 - mouse.y / height) * 100)
                    root.changed(Math.max(0, Math.min(100, nextValue)))
                }
            }
        }

        Rectangle {
            Layout.alignment: Qt.AlignHCenter
            Layout.preferredWidth: 78
            Layout.preferredHeight: 31
            radius: 8
            color: "#060606"

            Text {
                anchors.centerIn: parent
                text: root.value + "%"
                color: "#ffffff"
                font.pixelSize: 16
            }
        }

        Button {
            Layout.alignment: Qt.AlignHCenter
            Layout.preferredWidth: 72
            Layout.preferredHeight: 52
            text: "-"
            font.pixelSize: 30
            font.bold: true
            onClicked: root.changed(Math.max(0, root.value - root.step))
        }
    }
}
