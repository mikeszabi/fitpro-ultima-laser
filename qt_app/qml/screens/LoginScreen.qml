import QtQuick
import QtQuick.Controls
import QtQuick.Layouts
import "../components"

Item {
    anchors.fill: parent

    ColumnLayout {
        anchors.fill: parent
        anchors.margins: 72
        spacing: 28

        BackButton {
            onClicked: appController.navigate("start")
        }

        Text {
            text: "ULTIMA LASER"
            color: "#ffffff"
            font.pixelSize: 56
            font.bold: true
        }

        Text {
            Layout.fillWidth: true
            text: "Please login with your ULTIMA Academy account."
            color: "#d6e3e1"
            font.pixelSize: 24
            wrapMode: Text.WordWrap
        }

        TextField {
            Layout.fillWidth: true
            placeholderText: "E-mail address"
            font.pixelSize: 24
        }

        TextField {
            Layout.fillWidth: true
            placeholderText: "Password"
            echoMode: TextInput.Password
            font.pixelSize: 24
        }

        AppButton {
            Layout.preferredWidth: 320
            text: "Login"
            onClicked: appController.navigate("laser-treatment")
        }

        Item { Layout.fillHeight: true }
    }
}
