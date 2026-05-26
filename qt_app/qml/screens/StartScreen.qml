import QtQuick
import QtQuick.Layouts
import "../components"

Item {
    anchors.fill: parent

    Image {
        anchors.fill: parent
        source: "../../../public/assets/Background.png"
        fillMode: Image.PreserveAspectCrop
        opacity: 0.35
    }

    ColumnLayout {
        anchors.fill: parent
        anchors.margins: 92
        spacing: 32

        Item { Layout.fillHeight: true }

        Image {
            source: "../../../public/assets/ULTIMA.png"
            Layout.alignment: Qt.AlignHCenter
            Layout.preferredWidth: 560
            Layout.preferredHeight: 220
            fillMode: Image.PreserveAspectFit
        }

        Text {
            Layout.fillWidth: true
            text: "LASER"
            color: "#f6fffd"
            font.pixelSize: 72
            font.bold: true
            horizontalAlignment: Text.AlignHCenter
        }

        Item { Layout.preferredHeight: 180 }

        AppButton {
            Layout.alignment: Qt.AlignHCenter
            Layout.preferredWidth: 360
            text: "Get started"
            onClicked: appController.navigate("laser-treatment")
        }

        AppButton {
            Layout.alignment: Qt.AlignHCenter
            Layout.preferredWidth: 360
            text: "Settings"
            accent: "#2d5964"
            onClicked: appController.navigate("settings")
        }

        Item { Layout.fillHeight: true }
    }
}
