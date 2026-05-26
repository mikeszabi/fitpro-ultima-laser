import QtQuick
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
            BackButton { onClicked: appController.navigate("settings") }
            Text {
                text: "SYSTEM INFO"
                color: "#ffffff"
                font.pixelSize: 40
                font.bold: true
                Layout.fillWidth: true
                horizontalAlignment: Text.AlignHCenter
            }
            Item { width: 76; height: 76 }
        }

        Rectangle {
            Layout.fillWidth: true
            height: 280
            radius: 8
            color: "#10191d"
            border.color: "#355055"

            Column {
                anchors.fill: parent
                anchors.margins: 28
                spacing: 18

                Text { text: "Backend"; color: "#ffffff"; font.pixelSize: 28; font.bold: true }
                Text { text: appController.apiStatus; color: "#d8e4e3"; font.pixelSize: 22; wrapMode: Text.WordWrap; width: parent.width }
                Text { text: "API: " + appController.cameraFrameUrl.replace("/frame/current?t=", ""); color: "#8fa6a6"; font.pixelSize: 18; width: parent.width; elide: Text.ElideRight }
            }
        }

        AppButton {
            Layout.preferredWidth: 280
            text: "Refresh"
            onClicked: appController.syncBackend()
        }

        Item { Layout.fillHeight: true }
    }
}
