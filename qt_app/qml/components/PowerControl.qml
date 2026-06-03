import QtQuick

Item {
    id: root
    property string label: ""
    property real value: 0
    property real minValue: 0
    property real maxValue: 100
    property real step: 1
    property color fillColor: "#ff4d0b"
    property color offZoneColor: "#6f747c"
    property int offZoneEndValue: minValue
    property string bottomText: value.toString()
    readonly property real scaleTop: (label.length > 0 ? topLabel.implicitHeight : 0) + 12
    readonly property real scaleHeight: 358
    readonly property real fillRatio: maxValue === minValue ? 0 : Math.max(0, Math.min(1, (value - minValue) / (maxValue - minValue)))
    readonly property real offZoneRatio: maxValue === minValue ? 0 : Math.max(0, Math.min(1, (offZoneEndValue - minValue) / (maxValue - minValue)))
    signal changed(real value)

    width: 88
    height: 430

    Text {
        id: topLabel
        anchors.horizontalCenter: parent.horizontalCenter
        anchors.top: parent.top
        visible: root.label.length > 0
        height: visible ? implicitHeight : 0
        text: root.label
        color: "#ffffff"
        font.pixelSize: 20
        horizontalAlignment: Text.AlignHCenter
    }

    Rectangle {
        id: track
        anchors.horizontalCenter: parent.horizontalCenter
        anchors.top: topLabel.bottom
        anchors.topMargin: 12
        width: 78
        height: root.scaleHeight
        radius: 18
        color: "#111219"
        border.color: "#05060a"
        border.width: 3
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
            anchors.bottom: valueReadout.top
            height: (parent.height - valueReadout.height) * root.offZoneRatio
            visible: root.offZoneRatio > 0
            color: root.offZoneColor
        }

        Rectangle {
            anchors.fill: parent
            radius: parent.radius
            color: "transparent"
            border.width: 1
            border.color: "#2f3442"
        }

        Rectangle {
            id: valueReadout
            anchors.left: parent.left
            anchors.right: parent.right
            anchors.bottom: parent.bottom
            height: 34
            color: "#050506"

            Text {
                anchors.centerIn: parent
                text: root.bottomText
                color: "#ffffff"
                font.pixelSize: 16
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
