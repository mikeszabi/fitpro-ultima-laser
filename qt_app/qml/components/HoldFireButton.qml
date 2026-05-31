import QtQuick
import QtQuick.Controls

Button {
    id: control
    property int holdMs: 1200
    property color accent: "#ff9b00"
    signal armedTriggered()

    text: holdTimer.running ? "HOLD" : "FIRE"
    implicitHeight: 92
    font.pixelSize: 38
    font.bold: false
    flat: true

    onPressed: {
        if (enabled) {
            holdProgress.width = 0
            holdTimer.restart()
            progressAnimation.restart()
        }
    }

    onReleased: cancelHold()
    onCanceled: cancelHold()

    function cancelHold() {
        holdTimer.stop()
        progressAnimation.stop()
        holdProgress.width = 0
    }

    Timer {
        id: holdTimer
        interval: control.holdMs
        repeat: false
        onTriggered: {
            progressAnimation.stop()
            holdProgress.width = control.width
            control.armedTriggered()
        }
    }

    background: Rectangle {
        id: bg
        radius: height / 2
        color: control.down ? "#33210a" : "transparent"
        opacity: control.enabled ? 1.0 : 0.62
        border.width: 3
        border.color: control.accent

        Rectangle {
            id: holdProgress
            anchors.left: parent.left
            anchors.top: parent.top
            anchors.bottom: parent.bottom
            width: 0
            radius: 8
            color: "#66ffffff"
        }

        NumberAnimation {
            id: progressAnimation
            target: holdProgress
            property: "width"
            from: 0
            to: bg.width
            duration: control.holdMs
        }
    }

    contentItem: Text {
        text: control.text
        color: "#ffffff"
        font: control.font
        horizontalAlignment: Text.AlignHCenter
        verticalAlignment: Text.AlignVCenter
    }
}
