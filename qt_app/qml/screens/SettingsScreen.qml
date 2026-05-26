import QtQuick
import QtQuick.Controls
import QtQuick.Layouts
import "../components"

Item {
    anchors.fill: parent

    ColumnLayout {
        anchors.fill: parent
        anchors.margins: 56
        spacing: 24

        RowLayout {
            Layout.fillWidth: true
            BackButton { onClicked: appController.navigate("start") }
            Text {
                text: "SETTINGS"
                color: "#ffffff"
                font.pixelSize: 42
                font.bold: true
                Layout.fillWidth: true
                horizontalAlignment: Text.AlignHCenter
            }
            Item { width: 76; height: 76 }
        }

        GroupBox {
            title: "Treatment profile"
            Layout.fillWidth: true
            label: Text { text: "Treatment profile"; color: "#ffffff"; font.pixelSize: 22; font.bold: true }

            ColumnLayout {
                anchors.fill: parent
                spacing: 16

                ComboBox {
                    Layout.fillWidth: true
                    model: ["FP I", "FP II", "FP III", "FP IV", "FP V", "FP VI"]
                    font.pixelSize: 22
                }

                ComboBox {
                    Layout.fillWidth: true
                    model: ["Grey/White", "Red", "Blonde", "Brown", "Dark Brown", "Black"]
                    font.pixelSize: 22
                }

                ComboBox {
                    Layout.fillWidth: true
                    model: ["Thin", "Medium", "Thick"]
                    font.pixelSize: 22
                }
            }
        }

        AppButton {
            Layout.preferredWidth: 360
            text: "System info"
            accent: "#2d5964"
            onClicked: appController.navigate("system-info")
        }

        AppButton {
            Layout.preferredWidth: 360
            text: "Treatment"
            onClicked: appController.navigate("laser-treatment")
        }

        Item { Layout.fillHeight: true }
    }
}
