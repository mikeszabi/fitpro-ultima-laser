import QtQuick
import QtQuick.Controls
import "../components"

Item {
    anchors.fill: parent
    
    property bool logsVisible: false

    component FitText: Text {
        color: "#ffffff"
        elide: Text.ElideRight
        wrapMode: Text.NoWrap
        verticalAlignment: Text.AlignVCenter
    }

    Image {
        anchors.fill: parent
        source: "../../assets/images/xd-new/abstract-wave-bg.jpg"
        fillMode: Image.PreserveAspectCrop
    }

    Rectangle {
        anchors.fill: parent
        color: "#26000000"
    }

    Timer {
        interval: 2500
        running: true
        repeat: true
        onTriggered: appController.syncBackend()
    }

    Timer {
        interval: 750
        running: true
        repeat: true
        onTriggered: appController.refreshCameraFrame()
    }

    Component.onCompleted: {
        appController.initializeTreatmentPage()
        appController.refreshCameraFrame()
    }

    Component.onDestruction: appController.stopTreatmentCameraStream()

    BackButton {
        x: 32
        y: 30
        onClicked: appController.navigate("settings")
    }

    Rectangle {
        x: 1010
        y: 28
        width: 38
        height: 38
        radius: 19
        color: "transparent"
        border.color: "#ffffff"
        Text { anchors.centerIn: parent; text: "i"; color: "#ffffff"; font.pixelSize: 24 }
        MouseArea { anchors.fill: parent; onClicked: appController.navigate("system-info") }
    }

    FitText {
        anchors.horizontalCenter: parent.horizontalCenter
        y: 80
        width: 520
        height: 48
        text: "Laser Treatment"
        font.pixelSize: 40
        horizontalAlignment: Text.AlignHCenter
    }

    Row {
        x: 76
        y: 164
        width: 844
        height: 44
        spacing: 18

        FitText { width: 238; height: 44; text: "Skin type: III."; font.pixelSize: 30; horizontalAlignment: Text.AlignHCenter }
        FitText { width: 314; height: 44; text: "Hair color: Dark Brown"; font.pixelSize: 30; horizontalAlignment: Text.AlignHCenter }
        FitText { width: 238; height: 44; text: "Hair type: Medium"; font.pixelSize: 30; horizontalAlignment: Text.AlignHCenter }
    }

    component Panel: Rectangle {
        color: "#18000000"
        radius: 39
        border.color: "#ffffff"
        border.width: 3
    }

    Panel {
        id: outputPanel
        x: 58
        y: 246
        width: 952
        height: 620
        readonly property int powerRulerLabelX: 94
        readonly property int powerRulerTickX: 162
        readonly property int pulseRulerTickX: pulseSlider.x + pulseSlider.width + 10
        readonly property int pulseRulerLabelX: pulseRulerTickX + 30

        FitText {
            anchors.horizontalCenter: parent.horizontalCenter
            y: -2
            width: 520
            height: 48
            text: "Output Performance"
            font.pixelSize: 40
            horizontalAlignment: Text.AlignHCenter
        }

        FitText {
            x: outputPanel.powerRulerLabelX
            y: p808Slider.y + p808Slider.scaleTop - height / 2
            width: 52
            height: 24
            text: "15W"
            font.pixelSize: 20
            horizontalAlignment: Text.AlignRight
        }
        FitText {
            x: outputPanel.powerRulerLabelX
            y: p808Slider.y + p808Slider.scaleTop + p808Slider.scaleHeight - height / 2
            width: 52
            height: 24
            text: "0W"
            font.pixelSize: 20
            horizontalAlignment: Text.AlignRight
        }

        Repeater {
            model: 17
            Rectangle {
                x: outputPanel.powerRulerTickX
                y: p808Slider.y + p808Slider.scaleTop - height / 2 + index * (p808Slider.scaleHeight / 16)
                width: index % 4 === 0 ? 24 : 14
                height: 2
                color: "#cfd5db"
            }
        }

        PowerControl {
            id: p808Slider
            x: 188
            y: 92
            label: "808 nm"
            value: appController.p808Watts
            minValue: 0
            maxValue: 15
            step: 0.5
            fillColor: "#9b0000"
            offZoneEndValue: 1
            bottomText: appController.p808Watts.toFixed(1) + "W"
            onChanged: function(value) { appController.setPower("p808", value) }
        }

        PowerControl {
            x: 326
            y: 92
            label: "980 nm"
            value: appController.p980Watts
            minValue: 0
            maxValue: 15
            step: 0.5
            fillColor: "#f00012"
            offZoneEndValue: 1
            bottomText: appController.p980Watts.toFixed(1) + "W"
            onChanged: function(value) { appController.setPower("p980", value) }
        }

        PowerControl {
            x: 464
            y: 92
            label: "1064 nm"
            value: appController.p1064Watts
            minValue: 0
            maxValue: 15
            step: 0.5
            fillColor: "#ff4a12"
            offZoneEndValue: 1
            bottomText: appController.p1064Watts.toFixed(1) + "W"
            onChanged: function(value) { appController.setPower("p1064", value) }
        }

        FitText {
            x: outputPanel.pulseRulerLabelX
            y: pulseSlider.y + pulseSlider.scaleTop - height / 2
            width: 70
            height: 24
            text: "100ms"
            font.pixelSize: 20
            horizontalAlignment: Text.AlignLeft
        }
        FitText {
            x: outputPanel.pulseRulerLabelX
            y: pulseSlider.y + pulseSlider.scaleTop + pulseSlider.scaleHeight - height / 2
            width: 70
            height: 24
            text: "10ms"
            font.pixelSize: 20
            horizontalAlignment: Text.AlignLeft
        }

        Repeater {
            model: 11
            Rectangle {
                x: outputPanel.pulseRulerTickX
                y: pulseSlider.y + pulseSlider.scaleTop - height / 2 + index * (pulseSlider.scaleHeight / 10)
                width: index % 5 === 0 ? 22 : 12
                height: 2
                color: "#cfd5db"
            }
        }

        PowerControl {
            id: pulseSlider
            x: 700
            y: 92
            label: "P.WIDTH"
            value: Math.min(100, Math.max(10, Math.round(appController.pulseWidth)))
            minValue: 10
            maxValue: 100
            fillColor: "#4f86ff"
            bottomText: Math.min(100, appController.pulseWidth) + "ms"
            onChanged: function(value) { appController.setPulseWidth(value) }
        }

        AppButton {
            x: 658
            y: 526
            width: 214
            height: 58
            text: appController.settingsDirty ? "Apply settings" : "Settings OK"
            accent: appController.settingsDirty ? "#ff9300" : "#00d723"
            textColor: accent
            enabled: !appController.busy
            onClicked: appController.applyLaserSettings()
        }

        FitText {
            x: 126
            y: 550
            width: 500
            height: 38
            text: "Total Output Power: " + appController.totalPower.toFixed(1) + " W        J/cm2"
            font.pixelSize: 30
            horizontalAlignment: Text.AlignHCenter
        }
    }

    Panel {
        x: 62
        y: 904
        width: 956
        height: 206

        FitText {
            anchors.horizontalCenter: parent.horizontalCenter
            y: -2
            width: 420
            height: 46
            text: "Treatment Mode"
            font.pixelSize: 40
            horizontalAlignment: Text.AlignHCenter
        }

        ModeButton {
            x: 170
            y: 60
            text: "Auto"
            active: appController.treatmentMode === "auto"
            enabled: !appController.busy
            onClicked: appController.setTreatmentMode("auto")
        }
        ModeButton {
            x: 422
            y: 60
            text: "Semi\nAuto"
            active: appController.treatmentMode === "semi-auto"
            enabled: !appController.busy
            onClicked: appController.setTreatmentMode("semi-auto")
        }
        ModeButton {
            x: 674
            y: 60
            text: "Manual"
            active: appController.treatmentMode === "manual"
            enabled: !appController.busy
            onClicked: appController.setTreatmentMode("manual")
        }
    }

    FitText {
        anchors.horizontalCenter: parent.horizontalCenter
        y: 1130
        width: 620
        height: 42
        text: "LASER MODULE TEMP: <span style='color:#00d723'>" + appController.laserTemp + "</span>"
        textFormat: Text.RichText
        font.pixelSize: 30
        horizontalAlignment: Text.AlignHCenter
    }

    AppButton {
        x: 186
        y: 1180
        width: 320
        height: 72
        text: appController.laserReady ? "DISARM" : "ARM"
        accent: "#ffffff"
        enabled: !appController.busy
        onClicked: appController.toggleArm()
    }

    AppButton {
        x: 574
        y: 1180
        width: 320
        height: 72
        text: "Emergency Stop"
        accent: "#dc4f5d"
        textColor: "#dc4f5d"
        borderWidth: 4
        onClicked: appController.emergencyStop()
    }

    Panel {
        x: 62
        y: 1274
        width: 956
        height: 582
        border.color: appController.laserReady ? "#ff9300" : "#ffffff"

        Rectangle {
            x: 4
            y: 4
            width: 572
            height: 572
            radius: 286
            color: "#1a000000"
            clip: true

            Image {
                anchors.fill: parent
                anchors.margins: 7
                source: appController.cameraFrameUrl !== "" ? appController.cameraFrameUrl : "../../assets/images/xd-new/scan-target.png"
                asynchronous: true
                retainWhileLoading: true
                cache: false
                fillMode: Image.PreserveAspectCrop
            }

            Rectangle {
                anchors.fill: parent
                radius: parent.radius
                color: "transparent"
                border.width: 4
                border.color: "#ff9300"
            }
        }

        FitText { x: 604; y: 44; width: 350; height: 34; text: appController.apiStatus; font.pixelSize: 18; horizontalAlignment: Text.AlignHCenter }

        AppButton {
            x: 610
            y: 92
            width: 150
            height: 58
            text: "Detect"
            accent: "#ff9300"
            textColor: "#ff9300"
            visible: appController.treatmentMode !== "auto"
            enabled: !appController.busy
            onClicked: appController.detectTargets()
        }

        HoldFireButton {
            x: 784
            y: 78
            width: 160
            height: 84
            enabled: !appController.busy && appController.loadedTargetCount > 0
            visible: appController.treatmentMode === "semi-auto"
            onArmedTriggered: appController.fire()
        }

        FitText {
            x: 784
            y: 168
            width: 160
            height: 18
            text: "Hold 1.2s"
            font.pixelSize: 12
            color: "#ff9300"
            visible: appController.treatmentMode === "semi-auto"
            horizontalAlignment: Text.AlignHCenter
        }

        AppButton {
            x: 784
            y: 92
            width: 160
            height: 58
            text: "Next"
            accent: "#ff9300"
            textColor: "#ff9300"
            visible: appController.treatmentMode === "manual"
            enabled: !appController.busy && appController.loadedTargetCount > 0
            onClicked: appController.nextTarget()
        }

        FitText { x: 610; y: 178; width: 228; height: 44; text: "VACUUM LOCK:"; font.pixelSize: 25; horizontalAlignment: Text.AlignRight }
        Rectangle {
            x: 846
            y: 178
            width: 98
            height: 38
            radius: 19
            color: "#19191f"
            border.color: "#ffffff"
            border.width: 1
            Rectangle {
                x: appController.vacuumEnabled ? 0 : 49
                width: 49
                height: parent.height
                radius: 19
                color: appController.vacuumEnabled ? "#ff7045" : "#22222a"
            }
            FitText { x: 7; width: 42; height: parent.height; text: "ON"; font.pixelSize: 16; horizontalAlignment: Text.AlignHCenter }
            FitText { x: 49; width: 49; height: parent.height; text: "OFF"; font.pixelSize: 16; horizontalAlignment: Text.AlignHCenter }
            MouseArea { anchors.fill: parent; enabled: !appController.busy; onClicked: appController.toggleVacuum() }
        }

        FitText {
            x: 610
            y: 244
            width: 334
            height: 42
            text: "CONFIDENCE: " + appController.confidence.toFixed(3)
            font.pixelSize: 25
            horizontalAlignment: Text.AlignHCenter
        }
        Slider {
            x: 664
            y: 292
            width: 230
            from: 0
            to: 1
            stepSize: 0.005
            value: appController.confidence
            live: false
            onMoved: appController.setConfidence(value)
        }

        AppButton {
            x: 610
            y: 344
            width: 158
            height: 54
            text: appController.detectionEnabled ? "Detection Off" : "Detection On"
            accent: appController.detectionEnabled ? "#ff7045" : "#ffffff"
            enabled: !appController.busy
            onClicked: appController.toggleDetection()
        }
        AppButton {
            x: 786
            y: 344
            width: 158
            height: 54
            text: appController.overlayEnabled ? "Overlay Off" : "Overlay On"
            accent: appController.overlayEnabled ? "#ff7045" : "#ffffff"
            enabled: !appController.busy
            onClicked: appController.toggleOverlay()
        }

        AppButton {
            x: 610
            y: 412
            width: 158
            height: 54
            text: "Check States"
            accent: "#ffffff"
            enabled: !appController.busy
            onClicked: appController.checkStates()
        }
        AppButton {
            x: 786
            y: 412
            width: 158
            height: 54
            text: "Cleanup"
            accent: "#ffffff"
            enabled: !appController.busy
            onClicked: appController.cleanupStates()
        }

        FitText {
            x: 610
            y: 490
            width: 334
            height: 34
            text: "TARGET: <span style='color:" + (appController.target ? "#00d723" : "#dc4f5d") + "'>" + (appController.target ? "OK" : "NO") + "</span>"
            textFormat: Text.RichText
            font.pixelSize: 25
            horizontalAlignment: Text.AlignHCenter
        }
        FitText {
            x: 610
            y: 524
            width: 334
            height: 24
            text: "APP: " + appController.appState + "    TARGETS: " + appController.loadedTargetCount
            font.pixelSize: 15
            horizontalAlignment: Text.AlignHCenter
        }
        FitText {
            x: 610
            y: 548
            width: 334
            height: 24
            text: "TARGET STATE: " + appController.targetState
            font.pixelSize: 15
            horizontalAlignment: Text.AlignHCenter
        }
        FitText {
            x: 610
            y: 570
            width: 334
            height: 18
            text: appController.treatmentLogHead
            font.pixelSize: 12
            horizontalAlignment: Text.AlignHCenter
        }
    }

    // Logs toggle button
    AppButton {
        x: 186
        y: 8
        width: 200
        height: 44
        text: logsVisible ? "Hide Logs" : "Show Logs"
        accent: logsVisible ? "#ff7045" : "#ffffff"
        enabled: true
        onClicked: logsVisible = !logsVisible
    }

    // Logs panel (top-anchored, expands downward)
    Rectangle {
        x: 62
        y: 56
        width: 956
        height: logsVisible ? 350 : 0
        radius: 12
        color: "#18000000"
        border.color: "#ffffff"
        border.width: 2
        clip: true
        visible: height > 0
        z: 100

        Behavior on height {
            NumberAnimation { duration: 200 }
        }

        FitText {
            anchors.horizontalCenter: parent.horizontalCenter
            y: 10
            width: 420
            height: 28
            text: "Treatment Log"
            font.pixelSize: 20
            horizontalAlignment: Text.AlignHCenter
        }

        Rectangle {
            x: 12
            y: 45
            width: parent.width - 24
            height: parent.height - 57
            color: "#0c0c0c"
            border.color: "#3a3a3a"
            border.width: 1
            radius: 6

            TextEdit {
                anchors.fill: parent
                anchors.margins: 6
                text: appController.treatmentLog
                color: "#d2dde1"
                font.family: "Courier"
                font.pixelSize: 10
                readOnly: true
                wrapMode: TextEdit.Wrap
                selectByMouse: true
                topPadding: 6
                bottomPadding: 6
                leftPadding: 6
                rightPadding: 6
            }

            ScrollBar {
                anchors.right: parent.right
                anchors.top: parent.top
                anchors.bottom: parent.bottom
                anchors.rightMargin: 2
                anchors.topMargin: 2
                anchors.bottomMargin: 2
                width: 10
            }
        }
    }
}
