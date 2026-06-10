import QtQuick
import "../components"

Item {
    anchors.fill: parent

    Image {
        anchors.fill: parent
        source: "../../assets/images/xd-new/abstract-wave-bg.jpg"
        sourceSize.width: 1080
        sourceSize.height: 1920
        fillMode: Image.PreserveAspectCrop
    }

    Rectangle {
        anchors.fill: parent
        color: "#33000000"
    }

    Image {
        x: 204
        y: 249
        width: 673
        height: 787
        source: "../../assets/images/xd-new/ultima-u-mark.png"
        sourceSize.width: 673
        sourceSize.height: 787
        fillMode: Image.PreserveAspectFit
    }

    Image {
        x: 204
        y: 1252
        width: 673
        height: 252
        source: "../../assets/images/xd-new/ultima-wordmark.png"
        fillMode: Image.PreserveAspectFit
    }

    Text {
        x: 804
        y: 1447
        text: "LASER"
        color: "#ffffff"
        font.pixelSize: 60
    }

    AppButton {
        x: 356
        y: 1469
        width: 368
        height: 71
        text: "Get started"
        borderWidth: 5
        font.pixelSize: 22
        onClicked: appController.navigate("login")
    }
}
