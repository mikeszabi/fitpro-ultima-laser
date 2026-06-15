import QtQuick
import QtQuick.Controls
import "../components"

Item {
    id: root
    anchors.fill: parent

    function statusColor(status) {
        if (status === "OK") return "#62d27c"
        if (status === "WARN") return "#f3bc55"
        if (status === "FAIL") return "#ff6b6b"
        return "#aeb8bd"
    }

    function restartBackend() {
        appController.restartBackend(sudoPassword.text)
        sudoPassword.text = ""
    }

    Image {
        anchors.fill: parent
        source: "../../assets/images/xd-new/abstract-wave-bg.jpg"
        sourceSize.width: 1080
        sourceSize.height: 1920
        fillMode: Image.PreserveAspectCrop
    }

    Rectangle {
        anchors.fill: parent
        color: "#44000000"
    }

    BackButton {
        x: 32
        y: 30
        onClicked: appController.navigate("system-info")
    }

    Text {
        anchors.horizontalCenter: parent.horizontalCenter
        y: 66
        text: "HW/SW TEST"
        color: "#ffffff"
        font.pixelSize: 34
    }

    Rectangle {
        x: 74
        y: 138
        width: 932
        height: 384
        radius: 24
        color: "#22000000"
        border.color: "#72a0ff"
        border.width: 2

        Text {
            x: 34
            y: 28
            text: "Backend control"
            color: "#72a0ff"
            font.pixelSize: 28
        }

        Text {
            x: 34
            y: 82
            width: 528
            text: "Service: hairkiller-backend.service"
            color: "#ffffff"
            font.pixelSize: 20
        }

        TextField {
            id: sudoPassword
            x: 34
            y: 126
            width: 450
            height: 58
            color: "#ffffff"
            placeholderText: "Sudo password"
            placeholderTextColor: "#aeb8bd"
            echoMode: TextInput.Password
            font.pixelSize: 18
            leftPadding: 22
            rightPadding: 22
            background: Rectangle {
                radius: height / 2
                color: "#05000000"
                border.color: "#ff7045"
                border.width: 3
            }
            onAccepted: root.restartBackend()
        }

        AppButton {
            id: restartButton
            x: 600
            y: 120
            width: 260
            height: 64
            text: appController.busy ? "Working..." : "Restart backend"
            accent: "#ff7045"
            textColor: "#ff7045"
            enabled: !appController.busy
            onClicked: root.restartBackend()
        }

        Rectangle {
            x: 34
            y: 214
            width: 864
            height: 144
            radius: 12
            color: "#4a0d1116"
            border.color: "#33414a"

            Text {
                anchors.fill: parent
                anchors.margins: 18
                text: appController.backendRestartOutput
                color: "#d9e1e5"
                font.pixelSize: 17
                wrapMode: Text.Wrap
                elide: Text.ElideRight
            }
        }
    }

    Rectangle {
        x: 74
        y: 554
        width: 932
        height: 1194
        radius: 24
        color: "#22000000"
        border.color: "#ffffff"
        border.width: 2

        Text {
            x: 34
            y: 26
            text: "Full backend test"
            color: "#ffffff"
            font.pixelSize: 28
        }

        CheckBox {
            id: skipModelLoad
            x: 34
            y: 78
            width: 330
            height: 48
            text: "Skip YOLO model load"
            checked: false
            font.pixelSize: 18
            indicator.width: 28
            indicator.height: 28
            contentItem: Text {
                text: skipModelLoad.text
                color: "#ffffff"
                font: skipModelLoad.font
                verticalAlignment: Text.AlignVCenter
                leftPadding: skipModelLoad.indicator.width + skipModelLoad.spacing
            }
        }

        AppButton {
            x: 600
            y: 70
            width: 260
            height: 64
            text: appController.busy ? "Running..." : "Run full test"
            accent: "#72a0ff"
            enabled: !appController.busy
            onClicked: appController.runFullBackendCheck(skipModelLoad.checked)
        }

        Text {
            x: 34
            y: 154
            width: 864
            text: appController.diagnosticSummary
            color: appController.diagnosticSummary.indexOf("FAIL") >= 0 ? "#ff6b6b" : "#62d27c"
            font.pixelSize: 21
            wrapMode: Text.Wrap
        }

        Text {
            x: 34
            y: 194
            width: 864
            text: appController.diagnosticLastRun.length > 0 ? "Last run: " + appController.diagnosticLastRun : "Last run: never"
            color: "#aeb8bd"
            font.pixelSize: 16
        }

        Rectangle {
            x: 34
            y: 238
            width: 864
            height: 604
            radius: 12
            color: "#4a0d1116"
            border.color: "#33414a"
            clip: true

            ListView {
                id: checksList
                anchors.fill: parent
                anchors.margins: 12
                spacing: 8
                model: appController.diagnosticChecks
                boundsBehavior: Flickable.StopAtBounds

                header: Row {
                    width: checksList.width
                    height: 32
                    spacing: 12

                    Text { width: 94; text: "STATUS"; color: "#aeb8bd"; font.pixelSize: 13; font.bold: true }
                    Text { width: 258; text: "CHECK"; color: "#aeb8bd"; font.pixelSize: 13; font.bold: true }
                    Text { width: checksList.width - 388; text: "DETAILS"; color: "#aeb8bd"; font.pixelSize: 13; font.bold: true }
                }

                delegate: Rectangle {
                    width: checksList.width
                    height: Math.max(58, detailText.implicitHeight + 24)
                    radius: 8
                    color: "#24191f24"
                    border.color: "#28343a"

                    Rectangle {
                        x: 10
                        anchors.verticalCenter: parent.verticalCenter
                        width: 72
                        height: 30
                        radius: 15
                        color: root.statusColor(modelData.status)

                        Text {
                            anchors.centerIn: parent
                            text: modelData.status
                            color: "#071016"
                            font.pixelSize: 13
                            font.bold: true
                        }
                    }

                    Text {
                        x: 104
                        y: 12
                        width: 246
                        text: modelData.name
                        color: "#ffffff"
                        font.pixelSize: 16
                        wrapMode: Text.Wrap
                    }

                    Text {
                        id: detailText
                        x: 374
                        y: 12
                        width: parent.width - 390
                        text: modelData.message
                        color: "#d9e1e5"
                        font.pixelSize: 15
                        wrapMode: Text.Wrap
                    }
                }

                Text {
                    anchors.centerIn: parent
                    text: appController.busy ? "Checking..." : "No checks yet."
                    color: "#aeb8bd"
                    font.pixelSize: 22
                    visible: checksList.count === 0
                }
            }
        }

        Text {
            x: 34
            y: 876
            text: "Raw output"
            color: "#aeb8bd"
            font.pixelSize: 18
        }

        Rectangle {
            x: 34
            y: 914
            width: 864
            height: 236
            radius: 12
            color: "#62101214"
            border.color: "#33414a"
            clip: true

            Flickable {
                anchors.fill: parent
                anchors.margins: 16
                contentWidth: rawOutput.width
                contentHeight: rawOutput.implicitHeight
                boundsBehavior: Flickable.StopAtBounds

                Text {
                    id: rawOutput
                    width: 832
                    text: appController.diagnosticRawOutput.length > 0 ? appController.diagnosticRawOutput : "No raw output."
                    color: "#d9e1e5"
                    font.family: "monospace"
                    font.pixelSize: 14
                    wrapMode: Text.Wrap
                }
            }
        }
    }
}
