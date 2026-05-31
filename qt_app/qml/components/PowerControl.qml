import QtQuick

Item {
    id: root
    property string label: ""
    property int value: 0
    property int minValue: 0
    property int maxValue: 100
    property int step: 1
    property color fillColor: "#ff4d0b"
    property string bottomText: value.toString()
    readonly property real scaleTop: (label.length > 0 ? topLabel.implicitHeight : 0) + 12
    readonly property real scaleHeight: 282
    readonly property real fillRatio: maxValue === minValue ? 0 : Math.max(0, Math.min(1, (value - minValue) / (maxValue - minValue)))
    signal changed(int value)

    width: 86
    height: 390

    Text {
        id: topLabel
        anchors.horizontalCenter: parent.horizontalCenter
        anchors.top: parent.top
        visible: root.label.length > 0
        height: visible ? implicitHeight : 0
        text: root.label
        color: "#ffffff"
        font.pixelSize: 16
        horizontalAlignment: Text.AlignHCenter
    }

    Rectangle {
        id: track
        anchors.horizontalCenter: parent.horizontalCenter
        anchors.top: topLabel.bottom
        anchors.topMargin: 12
        width: 76
        height: root.scaleHeight
        radius: 17
        color: "#11131e"
        border.color: "#273041"
        border.width: 2
        clip: true

        Rectangle {
            anchors.left: parent.left
            anchors.right: parent.right
            anchors.bottom: parent.bottom
            height: parent.height * root.fillRatio
            color: root.fillColor
        }

        Rectangle {
            anchors.left: parent.left
            anchors.right: parent.right
            anchors.bottom: parent.bottom
            height: 32
            color: "#050506"

            Text {
                anchors.centerIn: parent
                text: root.bottomText
                color: "#ffffff"
                font.pixelSize: 15
            }
        }

        MouseArea {
            anchors.fill: parent
            onClicked: function(mouse) {
                var rawValue = root.minValue + (1 - mouse.y / height) * (root.maxValue - root.minValue)
                var steppedValue = Math.round(rawValue / root.step) * root.step
                root.changed(Math.max(root.minValue, Math.min(root.maxValue, steppedValue)))
            }
        }
    }
}
