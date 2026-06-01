import QtQuick
import QtQuick.Controls
import "../components"

Item {
    anchors.fill: parent

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
            value: appController.p808
            minValue: 0
            maxValue: 15
            fillColor: "#9b0000"
            offZoneEndValue: 1
            bottomText: appController.p808 + "W"
            onChanged: function(value) { appController.setPower("p808", value) }
        }

        PowerControl {
            x: 326
            y: 92
            label: "980 nm"
            value: appController.p980
            minValue: 0
            maxValue: 15
            fillColor: "#f00012"
            offZoneEndValue: 1
            bottomText: appController.p980 + "W"
            onChanged: function(value) { appController.setPower("p980", value) }
        }

        PowerControl {
            x: 464
            y: 92
            label: "1064 nm"
            value: appController.p1064
            minValue: 0
            maxValue: 15
            fillColor: "#ff4a12"
            offZoneEndValue: 1
            bottomText: appController.p1064 + "W"
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
            bottomText: appController.pulseWidth + "ms"
            onChanged: function(value) { appController.setPulseWidth(value) }
        }

        FitText {
            anchors.horizontalCenter: parent.horizontalCenter
            y: 550
            width: 720
            height: 38
            text: "Total Output Power: " + appController.totalPower + " W        J/cm2"
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
            onClicked: appController.setTreatmentMode("auto")
        }
        ModeButton {
            x: 422
            y: 60
            text: "Semi\nAuto"
            active: appController.treatmentMode === "semi-auto"
            onClicked: appController.setTreatmentMode("semi-auto")
        }
        ModeButton {
            x: 674
            y: 60
            text: "Manual"
            active: appController.treatmentMode === "manual"
            onClicked: appController.setTreatmentMode("manual")
        }
    }

    FitText {
        anchors.horizontalCenter: parent.horizontalCenter
        y: 1130
        width: 520
        height: 42
        text: "LASER MODULE TEMP: <span style='color:#00d723'>21°C</span>"
        textFormat: Text.RichText
        font.pixelSize: 30
        horizontalAlignment: Text.AlignHCenter
    }

    AppButton {
        anchors.horizontalCenter: parent.horizontalCenter
        y: 1180
        width: 430
        height: 72
        text: appController.laserReady ? "DISARM" : "ARM"
        accent: "#ffffff"
        onClicked: appController.setLaserReady(!appController.laserReady)
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

        FitText { x: 610; y: 94; width: 228; height: 44; text: "VACUUM LOCK:"; font.pixelSize: 25; horizontalAlignment: Text.AlignRight }
        Rectangle {
            x: 846
            y: 94
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
            MouseArea { anchors.fill: parent; onClicked: appController.setVacuumEnabled(!appController.vacuumEnabled) }
        }

        FitText {
            x: 610
            y: 172
            width: 334
            height: 42
            text: "CONFIDENCE: " + appController.confidence.toFixed(2)
            font.pixelSize: 25
            horizontalAlignment: Text.AlignHCenter
        }
        Slider {
            x: 664
            y: 226
            width: 230
            from: 0.01
            to: 1
            stepSize: 0.01
            value: appController.confidence
            onMoved: appController.setConfidence(value)
        }

        HoldFireButton {
            x: 668
            y: 316
            width: 220
            height: 92
            enabled: !appController.busy && appController.laserReady
            onArmedTriggered: appController.fire()
        }

        FitText {
            x: 610
            y: 500
            width: 334
            height: 40
            text: "TARGET: <span style='color:#00d723'>" + (appController.target ? "OK" : "NO") + "</span>"
            textFormat: Text.RichText
            font.pixelSize: 25
            horizontalAlignment: Text.AlignHCenter
        }
        FitText {
            x: 610
            y: 540
            width: 334
            height: 30
            text: "TARGETED FOLLICLES: " + appController.targetedFollicles
            font.pixelSize: 17
            horizontalAlignment: Text.AlignHCenter
        }
    }
}
