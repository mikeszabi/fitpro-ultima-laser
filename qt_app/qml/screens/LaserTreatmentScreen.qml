import QtQuick
import QtQuick.Controls
import QtQuick.Layouts
import "../components"

Item {
    anchors.fill: parent

    Timer {
        interval: 2500
        running: true
        repeat: true
        onTriggered: appController.syncBackend()
    }

    Timer {
        interval: 500
        running: true
        repeat: true
        onTriggered: appController.refreshCameraFrame()
    }

    ColumnLayout {
        width: 954
        height: parent.height - 78
        anchors.horizontalCenter: parent.horizontalCenter
        anchors.top: parent.top
        anchors.topMargin: 78
        spacing: 0

        RowLayout {
            Layout.fillWidth: true
            Layout.preferredHeight: 56

            BackButton { onClicked: appController.navigate("start") }

            Text {
                Layout.fillWidth: true
                text: "Laser Treatment"
                color: "#ffffff"
                font.pixelSize: 40
                font.bold: false
                horizontalAlignment: Text.AlignHCenter
            }

            AppButton {
                Layout.preferredWidth: 140
                Layout.preferredHeight: 62
                text: "Sync"
                accent: "#ffffff"
                enabled: !appController.busy
                onClicked: appController.syncBackend()
            }
        }

        RowLayout {
            Layout.fillWidth: true
            Layout.topMargin: 32
            Layout.bottomMargin: 42
            spacing: 80

            Text { text: "FP skin type"; color: "#ffffff"; font.pixelSize: 25; Layout.fillWidth: true; horizontalAlignment: Text.AlignHCenter }
            Text { text: "Hair color"; color: "#ffffff"; font.pixelSize: 25; Layout.fillWidth: true; horizontalAlignment: Text.AlignHCenter }
            Text { text: "Hair type"; color: "#ffffff"; font.pixelSize: 25; Layout.fillWidth: true; horizontalAlignment: Text.AlignHCenter }
        }

        Rectangle {
            Layout.fillWidth: true
            Layout.preferredHeight: 616
            radius: 39
            color: "#7a000000"
            border.color: "#ffffff"
            border.width: 3

            ColumnLayout {
                anchors.fill: parent
                anchors.leftMargin: 48
                anchors.rightMargin: 48
                anchors.topMargin: 10
                anchors.bottomMargin: 24
                spacing: 18

                Text {
                    Layout.fillWidth: true
                    text: "Output Performance"
                    color: "#ffffff"
                    font.pixelSize: 40
                    horizontalAlignment: Text.AlignHCenter
                }

                RowLayout {
                    Layout.fillWidth: true
                    Layout.fillHeight: true
                    spacing: 28

                    ColumnLayout {
                        Layout.preferredWidth: 54
                        Layout.fillHeight: true
                        Text { text: "100"; color: "#ffffff"; font.pixelSize: 20 }
                        Item { Layout.fillHeight: true }
                        Text { text: "80"; color: "#ffffff"; font.pixelSize: 20 }
                        Item { Layout.fillHeight: true }
                        Text { text: "60"; color: "#ffffff"; font.pixelSize: 20 }
                        Item { Layout.fillHeight: true }
                        Text { text: "40"; color: "#ffffff"; font.pixelSize: 20 }
                        Item { Layout.fillHeight: true }
                        Text { text: "20"; color: "#ffffff"; font.pixelSize: 20 }
                        Item { Layout.fillHeight: true }
                        Text { text: "0"; color: "#ffffff"; font.pixelSize: 20 }
                    }

                    PowerControl {
                        label: "808 nm"
                        value: appController.p808
                        fillColor: "#a00000"
                        onChanged: function(value) { appController.setPower("p808", value) }
                    }

                    PowerControl {
                        label: "980 nm"
                        value: appController.p980
                        fillColor: "#f1060b"
                        onChanged: function(value) { appController.setPower("p980", value) }
                    }

                    PowerControl {
                        label: "1064 nm"
                        value: appController.p1064
                        fillColor: "#ff4d0b"
                        onChanged: function(value) { appController.setPower("p1064", value) }
                    }

                    ColumnLayout {
                        Layout.fillWidth: true
                        Layout.fillHeight: true
                        spacing: 16

                        Text {
                            Layout.fillWidth: true
                            text: "P.WIDTH: " + appController.pulseWidth + " ms"
                            color: "#ffffff"
                            font.pixelSize: 24
                            horizontalAlignment: Text.AlignHCenter
                        }

                        Slider {
                            Layout.fillWidth: true
                            from: 1
                            to: 300
                            stepSize: 1
                            value: appController.pulseWidth
                            onMoved: appController.setPulseWidth(Math.round(value))
                        }

                        RowLayout {
                            Layout.fillWidth: true
                            AppButton { Layout.fillWidth: true; text: "-5"; accent: "#ffffff"; onClicked: appController.setPulseWidth(appController.pulseWidth - 5) }
                            AppButton { Layout.fillWidth: true; text: "+5"; accent: "#ffffff"; onClicked: appController.setPulseWidth(appController.pulseWidth + 5) }
                        }

                        Item { Layout.fillHeight: true }

                        Text {
                            Layout.fillWidth: true
                            text: "Red Dot"
                            color: "#ffffff"
                            font.pixelSize: 20
                            horizontalAlignment: Text.AlignHCenter
                        }

                        AppButton {
                            Layout.alignment: Qt.AlignHCenter
                            Layout.preferredWidth: 150
                            Layout.preferredHeight: 48
                            text: appController.redDot ? "ON" : "OFF"
                            accent: "#ffffff"
                            enabled: !appController.busy
                            onClicked: appController.setRedDot(!appController.redDot)
                        }
                    }

                    PowerControl {
                        label: "Total"
                        value: Math.min(100, appController.totalPower)
                        fillColor: "#4f86ff"
                        onChanged: function(_) {}
                    }
                }

                RowLayout {
                    Layout.fillWidth: true
                    Text {
                        Layout.fillWidth: true
                        text: "Total Output Power"
                        color: "#ffffff"
                        font.pixelSize: 30
                        horizontalAlignment: Text.AlignRight
                    }
                    Text {
                        Layout.preferredWidth: 180
                        text: appController.totalPower + "%"
                        color: "#ffffff"
                        font.pixelSize: 30
                    }
                }
            }
        }

        Rectangle {
            Layout.fillWidth: true
            Layout.topMargin: 40
            Layout.preferredHeight: 205
            radius: 39
            color: "#7a000000"
            border.color: "#ffffff"
            border.width: 3

            ColumnLayout {
                anchors.fill: parent
                anchors.topMargin: 8
                spacing: 18

                Text {
                    Layout.fillWidth: true
                    text: "Treatment Mode"
                    color: "#ffffff"
                    font.pixelSize: 40
                    horizontalAlignment: Text.AlignHCenter
                }

                RowLayout {
                    Layout.alignment: Qt.AlignHCenter
                    spacing: 110

                    ModeButton {
                        text: "Auto"
                        active: appController.treatmentMode === "auto"
                        onClicked: appController.setTreatmentMode("auto")
                    }
                    ModeButton {
                        text: "Semi\nAuto"
                        active: appController.treatmentMode === "semi-auto"
                        onClicked: appController.setTreatmentMode("semi-auto")
                    }
                    ModeButton {
                        text: "Manual"
                        active: appController.treatmentMode === "manual"
                        onClicked: appController.setTreatmentMode("manual")
                    }
                }
            }
        }

        Text {
            Layout.fillWidth: true
            Layout.topMargin: 20
            text: "LASER MODULE TEMP  <span style='color:#06CC1A'>21 C</span>"
            textFormat: Text.RichText
            color: "#ffffff"
            font.pixelSize: 30
            horizontalAlignment: Text.AlignHCenter
        }

        AppButton {
            Layout.alignment: Qt.AlignHCenter
            Layout.topMargin: 14
            Layout.bottomMargin: 20
            Layout.preferredWidth: 430
            Layout.preferredHeight: 72
            text: appController.laserReady ? "READY" : "Standby"
            accent: appController.laserReady ? "#ffffff" : "#ff7a1a"
            enabled: !appController.busy
            onClicked: appController.setLaserReady(!appController.laserReady)
        }

        Rectangle {
            Layout.fillWidth: true
            Layout.preferredHeight: 580
            radius: 39
            color: "#7a000000"
            border.color: appController.laserReady ? "#ff7a1a" : "#ffffff"
            border.width: 3
            clip: true

            RowLayout {
                anchors.fill: parent
                anchors.rightMargin: 52
                spacing: 28

                Rectangle {
                    Layout.preferredWidth: 580
                    Layout.preferredHeight: 580
                    radius: 290
                    color: "#66000000"
                    border.width: 5
                    border.color: appController.laserReady ? "#ff7a1a" : "#ffffff"
                    clip: true

                    Image {
                        anchors.fill: parent
                        source: appController.cameraFrameUrl
                        fillMode: Image.PreserveAspectCrop
                        cache: false
                    }
                }

                ColumnLayout {
                    Layout.fillWidth: true
                    Layout.fillHeight: true
                    Layout.topMargin: 42
                    Layout.bottomMargin: 28
                    spacing: 12

                    RowLayout {
                        Layout.fillWidth: true
                        Text { text: "Vacuum"; color: "#ffffff"; font.pixelSize: 27; Layout.fillWidth: true }
                        AppButton {
                            Layout.preferredWidth: 92
                            Layout.preferredHeight: 42
                            text: appController.vacuumEnabled ? "ON" : "OFF"
                            accent: "#ffffff"
                            onClicked: appController.setVacuumEnabled(!appController.vacuumEnabled)
                        }
                    }

                    RowLayout {
                        Layout.fillWidth: true
                        Text { text: "Confidence"; color: "#ffffff"; font.pixelSize: 24; Layout.fillWidth: true }
                        Text { text: appController.confidence.toFixed(2); color: "#ffffff"; font.pixelSize: 24 }
                    }

                    Slider {
                        Layout.fillWidth: true
                        from: 0.01
                        to: 1
                        stepSize: 0.01
                        value: appController.confidence
                        onMoved: appController.setConfidence(value)
                    }

                    AppButton {
                        Layout.alignment: Qt.AlignHCenter
                        Layout.preferredWidth: 220
                        Layout.preferredHeight: 62
                        text: "Targets"
                        accent: "#ffffff"
                        enabled: !appController.busy
                        onClicked: appController.captureAndLoadTargets()
                    }

                    HoldFireButton {
                        Layout.alignment: Qt.AlignHCenter
                        Layout.preferredWidth: 220
                        enabled: !appController.busy && appController.laserReady
                        onArmedTriggered: appController.fire()
                    }

                    AppButton {
                        Layout.alignment: Qt.AlignHCenter
                        Layout.preferredWidth: 220
                        Layout.preferredHeight: 72
                        text: "STOP"
                        accent: "#ff0033"
                        enabled: !appController.busy
                        onClicked: appController.stop()
                    }

                    Item { Layout.fillHeight: true }

                    ColumnLayout {
                        Layout.fillWidth: true
                        spacing: 2

                        Text {
                            Layout.fillWidth: true
                            text: "TARGET"
                            color: "#ffffff"
                            font.pixelSize: 30
                            horizontalAlignment: Text.AlignHCenter
                        }

                        Text {
                            Layout.fillWidth: true
                            text: appController.target ? "OK" : "NO"
                            color: appController.target ? "#06CC1A" : "#ff0033"
                            font.pixelSize: 30
                            horizontalAlignment: Text.AlignHCenter
                        }

                        Text {
                            Layout.fillWidth: true
                            text: "TARGETED FOLLICLES"
                            color: "#ffffff"
                            font.pixelSize: 22
                            horizontalAlignment: Text.AlignHCenter
                        }

                        Text {
                            Layout.fillWidth: true
                            text: appController.targetedFollicles
                            color: "#ffffff"
                            font.pixelSize: 24
                            horizontalAlignment: Text.AlignHCenter
                        }

                        Text {
                            Layout.fillWidth: true
                            text: appController.apiStatus
                            color: "#c8ffffff"
                            font.pixelSize: 16
                            horizontalAlignment: Text.AlignHCenter
                            elide: Text.ElideRight
                        }
                    }
                }
            }
        }
    }
}
