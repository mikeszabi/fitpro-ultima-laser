import QtQuick
import "../components"

Item {
    anchors.fill: parent

    Image {
        anchors.fill: parent
        source: "../../assets/images/Background.png"
        fillMode: Image.PreserveAspectCrop
    }

    Rectangle {
        anchors.fill: parent
        color: "#33000000"
    }

    Item {
        x: 204
        y: 184
        width: 672
        height: 866

        Image {
            id: uMark
            anchors.horizontalCenter: parent.horizontalCenter
            y: 0
            width: 672
            height: 672
            source: "../../assets/images/Ultima-logo.png"
            fillMode: Image.PreserveAspectFit
        }

        Image {
            anchors.horizontalCenter: parent.horizontalCenter
            y: 710
            width: 650
            height: 166
            source: "../../assets/images/ULTIMA.png"
            fillMode: Image.PreserveAspectFit
        }

        Text {
            x: 720
            y: 813
            text: "LASER"
            color: "#ffffff"
            font.pixelSize: 51
        }

        AppButton {
            anchors.horizontalCenter: parent.horizontalCenter
            y: 891
            width: 366
            height: 72
            text: "Get started"
            onClicked: appController.navigate("login")
        }
    }
}
