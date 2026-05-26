import QtQuick

Rectangle {
    id: root
    property string label: ""
    property bool active: false

    height: 48
    radius: 24
    color: active ? "#1f7f6f" : "#2a3034"
    border.color: active ? "#7bf2df" : "#69777a"
    border.width: 1

    Text {
        anchors.centerIn: parent
        text: root.label
        color: "#f4fffd"
        font.pixelSize: 18
        font.bold: true
    }
}
