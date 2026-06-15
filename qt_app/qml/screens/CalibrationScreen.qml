pragma ComponentBehavior: Bound

import QtQuick
import QtQuick.Controls
import "../components"

Item {
    id: root
    anchors.fill: parent
    property bool hsvInspectMode: false
    property bool hsvLimitsVisible: false

    component FitText: Text {
        color: "#ffffff"
        elide: Text.ElideRight
        wrapMode: Text.NoWrap
        verticalAlignment: Text.AlignVCenter
    }

    component Panel: Rectangle {
        color: "#18000000"
        radius: 28
        border.color: "#ffffff"
        border.width: 3
    }

    component InfoLine: FitText {
        width: parent ? parent.width - 40 : 200
        height: 28
        font.pixelSize: 18
    }

    component NumberField: TextInput {
        id: field
        property int numericValue: 0
        width: 110
        height: 48
        text: String(numericValue)
        color: "#ffffff"
        font.pixelSize: 22
        horizontalAlignment: TextInput.AlignHCenter
        verticalAlignment: TextInput.AlignVCenter
        validator: IntValidator { bottom: 0; top: 4095 }
        selectByMouse: true
        Rectangle {
            anchors.fill: parent
            z: -1
            radius: 8
            color: "#18000000"
            border.color: "#86ffffff"
            border.width: 1
        }
    }

    component HsvRow: Item {
        id: hsvRow
        property string label: ""
        property string rangeName: "1"
        property string boundName: "lower"
        property int channel: 0
        property var values: [0, 0, 0]
        property int maximumValue: channel === 0 ? 180 : 255
        width: 392
        height: 44

        FitText {
            x: 0
            width: 82
            height: parent.height
            text: hsvRow.label
            font.pixelSize: 16
        }
        Slider {
            id: slider
            x: 84
            y: 2
            width: 240
            height: 40
            from: 0
            to: hsvRow.maximumValue
            stepSize: 1
            live: false
            value: hsvRow.values[hsvRow.channel]
            onMoved: appController.setHsvChannel(hsvRow.rangeName, hsvRow.boundName, hsvRow.channel, Math.round(value))
        }
        FitText {
            x: 330
            width: 60
            height: parent.height
            text: Math.round(slider.value)
            color: "#ffcf4a"
            font.pixelSize: 18
            horizontalAlignment: Text.AlignRight
        }
    }

    Image {
        anchors.fill: parent
        source: "../../assets/images/xd-new/abstract-wave-bg.jpg"
        sourceSize.width: 1080
        sourceSize.height: 1920
        fillMode: Image.PreserveAspectCrop
    }

    Rectangle { anchors.fill: parent; color: "#26000000" }

    Timer {
        interval: 250
        running: true
        repeat: true
        onTriggered: appController.refreshCameraFrame()
    }

    Timer {
        interval: 450
        running: true
        repeat: true
        onTriggered: appController.refreshCalibrationTelemetry()
    }

    Component.onCompleted: {
        appController.initializeCalibrationPage()
        appController.refreshCameraFrame()
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
        text: "Calibration"
        font.pixelSize: 40
        horizontalAlignment: Text.AlignHCenter
    }

    Panel {
        id: cameraPanel
        x: 58
        y: 144
        width: 964
        height: 582
        border.color: appController.calibrationDetectionEnabled ? "#ff0876" : "#ffffff"

        Rectangle {
            id: cameraFrame
            x: 18
            y: 18
            width: 560
            height: 546
            radius: 22
            color: "#1a000000"
            clip: true

            Image {
                id: liveImage
                anchors.fill: parent
                anchors.margins: 8
                source: appController.cameraFrameUrl !== "" ? appController.cameraFrameUrl : "../../assets/images/xd-new/scan-target.png"
                asynchronous: true
                retainWhileLoading: true
                cache: false
                fillMode: Image.PreserveAspectFit
            }

            Rectangle {
                anchors.fill: parent
                radius: parent.radius
                color: "transparent"
                border.width: 3
                border.color: "#ffffff"
            }

            MouseArea {
                anchors.fill: liveImage
                cursorShape: root.hsvInspectMode ? Qt.CrossCursor : Qt.PointingHandCursor
                onClicked: function(mouse) {
                    if (liveImage.paintedWidth <= 0 || liveImage.paintedHeight <= 0 || liveImage.sourceSize.width <= 0 || liveImage.sourceSize.height <= 0)
                        return
                    const imageLeft = (liveImage.width - liveImage.paintedWidth) / 2
                    const imageTop = (liveImage.height - liveImage.paintedHeight) / 2
                    const localX = mouse.x - imageLeft
                    const localY = mouse.y - imageTop
                    if (localX < 0 || localY < 0 || localX > liveImage.paintedWidth || localY > liveImage.paintedHeight)
                        return
                    const imgX = Math.round(localX * liveImage.sourceSize.width / liveImage.paintedWidth)
                    const imgY = Math.round(localY * liveImage.sourceSize.height / liveImage.paintedHeight)
                    appController.handleCalibrationImageClick(imgX, imgY, root.hsvInspectMode)
                }
            }
        }

        FitText {
            x: 612
            y: 28
            width: 300
            height: 38
            text: "Red Dot Detection"
            font.pixelSize: 28
            horizontalAlignment: Text.AlignHCenter
        }

        AppButton {
            x: 620
            y: 86
            width: 150
            height: 54
            text: appController.calibrationDetectionEnabled ? "Detection Off" : "Detection On"
            accent: appController.calibrationDetectionEnabled ? "#ff0876" : "#ffffff"
            textColor: accent
            enabled: !appController.busy
            onClicked: appController.setCalibrationDetection(!appController.calibrationDetectionEnabled)
        }
        AppButton {
            x: 790
            y: 86
            width: 150
            height: 54
            text: appController.maskOverlayEnabled ? "Mask Off" : "Mask On"
            accent: appController.maskOverlayEnabled ? "#ff0876" : "#ffffff"
            textColor: accent
            enabled: !appController.busy
            onClicked: appController.setMaskOverlay(!appController.maskOverlayEnabled)
        }
        AppButton {
            x: 620
            y: 156
            width: 320
            height: 54
            text: root.hsvInspectMode ? "HSV Inspect On" : "HSV Inspect Off"
            accent: root.hsvInspectMode ? "#ffcf4a" : "#ffffff"
            textColor: accent
            onClicked: root.hsvInspectMode = !root.hsvInspectMode
        }
        AppButton {
            x: 620
            y: 220
            width: 320
            height: 58
            text: "DISABLE CALIBRATION MODE"
            accent: "#dc4f5d"
            textColor: "#dc4f5d"
            borderWidth: 4
            enabled: !appController.busy
            onClicked: {
                root.hsvInspectMode = false
                appController.disableCalibrationMode()
            }
        }

        InfoLine { x: 620; y: 302; text: "Dot in image: X=" + appController.dotImageX + "  Y=" + appController.dotImageY }
        InfoLine { x: 620; y: 332; text: "Click image: X=" + appController.clickedImageX + "  Y=" + appController.clickedImageY }
        InfoLine { x: 620; y: 362; text: "Clicked HSV: " + appController.hsvClickValue }
        InfoLine { x: 620; y: 392; text: "Clicked RGB: " + appController.rgbClickValue }
        InfoLine { x: 620; y: 422; text: "Target galvo: X=" + appController.targetGalvoX + "  Y=" + appController.targetGalvoY }
        InfoLine { x: 620; y: 452; text: "Move result: " + appController.moveResult }
        InfoLine { x: 620; y: 492; text: "Galvo position: X=" + appController.galvoX + "  Y=" + appController.galvoY }
        InfoLine { x: 620; y: 522; text: "Homography: " + appController.homographyStatus }
    }

    ScrollView {
        x: 58
        y: 752
        width: 964
        height: 1098
        clip: true

        Item {
            width: 924
            height: collectionPanel.y + collectionPanel.height + 24

            Panel {
                id: hsvPanel
                x: 0
                y: 0
                width: 924
                height: root.hsvLimitsVisible ? 420 : 86
                clip: true

                FitText {
                    x: 34
                    y: 20
                    width: 420
                    height: 38
                    text: "HSV Limits"
                    font.pixelSize: 30
                    horizontalAlignment: Text.AlignLeft
                }
                AppButton {
                    x: 708
                    y: 14
                    width: 170
                    height: 54
                    text: root.hsvLimitsVisible ? "Hide" : "Show"
                    accent: root.hsvLimitsVisible ? "#ff0876" : "#ffffff"
                    textColor: accent
                    onClicked: root.hsvLimitsVisible = !root.hsvLimitsVisible
                }
                FitText { x: 34; y: 70; width: 360; height: 30; text: "Range 1: Low Hue Red"; font.pixelSize: 20; visible: root.hsvLimitsVisible }
                HsvRow { x: 34; y: 106; label: "Lower H"; rangeName: "1"; boundName: "lower"; channel: 0; values: appController.hsvLower1; visible: root.hsvLimitsVisible }
                HsvRow { x: 34; y: 150; label: "Lower S"; rangeName: "1"; boundName: "lower"; channel: 1; values: appController.hsvLower1; visible: root.hsvLimitsVisible }
                HsvRow { x: 34; y: 194; label: "Lower V"; rangeName: "1"; boundName: "lower"; channel: 2; values: appController.hsvLower1; visible: root.hsvLimitsVisible }
                HsvRow { x: 34; y: 250; label: "Upper H"; rangeName: "1"; boundName: "upper"; channel: 0; values: appController.hsvUpper1; visible: root.hsvLimitsVisible }
                HsvRow { x: 34; y: 294; label: "Upper S"; rangeName: "1"; boundName: "upper"; channel: 1; values: appController.hsvUpper1; visible: root.hsvLimitsVisible }
                HsvRow { x: 34; y: 338; label: "Upper V"; rangeName: "1"; boundName: "upper"; channel: 2; values: appController.hsvUpper1; visible: root.hsvLimitsVisible }

                FitText { x: 498; y: 70; width: 360; height: 30; text: "Range 2: High Hue Red"; font.pixelSize: 20; visible: root.hsvLimitsVisible }
                HsvRow { x: 498; y: 106; label: "Lower H"; rangeName: "2"; boundName: "lower"; channel: 0; values: appController.hsvLower2; visible: root.hsvLimitsVisible }
                HsvRow { x: 498; y: 150; label: "Lower S"; rangeName: "2"; boundName: "lower"; channel: 1; values: appController.hsvLower2; visible: root.hsvLimitsVisible }
                HsvRow { x: 498; y: 194; label: "Lower V"; rangeName: "2"; boundName: "lower"; channel: 2; values: appController.hsvLower2; visible: root.hsvLimitsVisible }
                HsvRow { x: 498; y: 250; label: "Upper H"; rangeName: "2"; boundName: "upper"; channel: 0; values: appController.hsvUpper2; visible: root.hsvLimitsVisible }
                HsvRow { x: 498; y: 294; label: "Upper S"; rangeName: "2"; boundName: "upper"; channel: 1; values: appController.hsvUpper2; visible: root.hsvLimitsVisible }
                HsvRow { x: 498; y: 338; label: "Upper V"; rangeName: "2"; boundName: "upper"; channel: 2; values: appController.hsvUpper2; visible: root.hsvLimitsVisible }
            }

            Panel {
                id: laserPanel
                x: 0
                y: hsvPanel.y + hsvPanel.height + 26
                width: 924
                height: 256

                FitText { anchors.horizontalCenter: parent.horizontalCenter; y: 20; width: 360; height: 38; text: "Laser Control"; font.pixelSize: 30; horizontalAlignment: Text.AlignHCenter }
                InfoLine { x: 42; y: 82; width: 360; text: "ARM: " + (appController.laserReady ? "ARMED" : "DISARMED"); color: appController.laserReady ? "#00d723" : "#dc4f5d" }
                InfoLine { x: 42; y: 120; width: 360; text: "RED DOT: " + (appController.redDot ? "ON" : "OFF"); color: appController.redDot ? "#00d723" : "#dc4f5d" }
                AppButton { x: 436; y: 78; width: 170; height: 58; text: "ARM"; accent: "#ffffff"; enabled: !appController.busy; onClicked: appController.setCalibrationLaserArm(true) }
                AppButton { x: 632; y: 78; width: 170; height: 58; text: "DISARM"; accent: "#dc4f5d"; textColor: "#dc4f5d"; enabled: !appController.busy; onClicked: appController.setCalibrationLaserArm(false) }
                AppButton { x: 436; y: 158; width: 170; height: 58; text: "Red Dot ON"; accent: "#ff0876"; textColor: "#ff0876"; enabled: !appController.busy; onClicked: appController.setCalibrationRedDot(true) }
                AppButton { x: 632; y: 158; width: 170; height: 58; text: "Red Dot OFF"; accent: "#ffffff"; enabled: !appController.busy; onClicked: appController.setCalibrationRedDot(false) }
            }

            Panel {
                id: galvoPanel
                x: 0
                y: laserPanel.y + laserPanel.height + 26
                width: 924
                height: 294

                FitText { anchors.horizontalCenter: parent.horizontalCenter; y: 20; width: 420; height: 38; text: "Direct Galvo Control"; font.pixelSize: 30; horizontalAlignment: Text.AlignHCenter }
                InfoLine { x: 42; y: 74; text: "Position: X=" + appController.galvoX + "  Y=" + appController.galvoY }
                FitText { x: 42; y: 126; width: 34; height: 48; text: "X"; font.pixelSize: 22 }
                NumberField { id: moveXField; x: 82; y: 126; numericValue: appController.moveX; onEditingFinished: appController.setMoveTarget(parseInt(text), appController.moveY) }
                FitText { x: 214; y: 126; width: 34; height: 48; text: "Y"; font.pixelSize: 22 }
                NumberField { id: moveYField; x: 254; y: 126; numericValue: appController.moveY; onEditingFinished: appController.setMoveTarget(appController.moveX, parseInt(text)) }
                AppButton { x: 394; y: 122; width: 150; height: 58; text: "Move"; accent: "#ff0876"; textColor: "#ff0876"; enabled: !appController.busy; onClicked: appController.moveGalvoToTarget() }
                FitText { x: 42; y: 212; width: 58; height: 48; text: "Step"; font.pixelSize: 22 }
                NumberField { x: 110; y: 212; width: 96; numericValue: appController.moveStep; onEditingFinished: appController.setMoveStep(parseInt(text)) }
                AppButton { x: 706; y: 76; width: 92; height: 52; text: "Up"; onClicked: appController.moveGalvoDirection("up") }
                AppButton { x: 706; y: 194; width: 92; height: 52; text: "Down"; onClicked: appController.moveGalvoDirection("down") }
                AppButton { x: 598; y: 136; width: 92; height: 52; text: "Left"; onClicked: appController.moveGalvoDirection("left") }
                AppButton { x: 814; y: 136; width: 92; height: 52; text: "Right"; onClicked: appController.moveGalvoDirection("right") }
            }

            Panel {
                id: collectionPanel
                x: 0
                y: galvoPanel.y + galvoPanel.height + 26
                width: 924
                height: 286

                FitText { anchors.horizontalCenter: parent.horizontalCenter; y: 20; width: 480; height: 38; text: "Calibration Collection"; font.pixelSize: 30; horizontalAlignment: Text.AlignHCenter }
                InfoLine { x: 42; y: 82; text: "Points stored: " + appController.storedCount }
                AppButton { x: 42; y: 142; width: 180; height: 60; text: "Start"; accent: "#ffffff"; enabled: !appController.busy; onClicked: appController.startCalibrationCollection() }
                AppButton { x: 250; y: 142; width: 180; height: 60; text: "Store Point"; accent: "#ff0876"; textColor: "#ff0876"; enabled: !appController.busy; onClicked: appController.storeCalibrationPoint() }
                AppButton { x: 458; y: 142; width: 300; height: 60; text: "Calculate & Save"; accent: "#ffcf4a"; textColor: "#ffcf4a"; enabled: !appController.busy; onClicked: appController.saveCalibration() }
                AppButton { x: 780; y: 142; width: 102; height: 60; text: "Reload"; accent: "#ffffff"; enabled: !appController.busy; onClicked: appController.reloadHomography() }
                InfoLine { x: 42; y: 226; text: "Status: " + appController.homographyStatus }
            }
        }
    }
}
