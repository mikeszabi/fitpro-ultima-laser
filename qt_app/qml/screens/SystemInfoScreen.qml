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
        color: "#26000000"
    }

    BackButton {
        x: 32
        y: 30
        onClicked: appController.navigate("settings")
    }

    Text {
        anchors.horizontalCenter: parent.horizontalCenter
        y: 66
        text: "SYSTEM INFO"
        color: "#ffffff"
        font.pixelSize: 34
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
    }

    Rectangle {
        x: 540
        y: 240
        width: 2
        height: 800
        color: "#2c2f38"
    }

    Text { x: 168; y: 282; text: "USER DETAILS"; color: "#ff7045"; font.pixelSize: 34 }

    Rectangle {
        x: 168
        y: 348
        width: 96
        height: 96
        radius: 48
        gradient: Gradient {
            GradientStop { position: 0; color: "#ff8b59" }
            GradientStop { position: 1; color: "#3b170c" }
        }
        border.color: "#ffffff"
        Image {
            anchors.centerIn: parent
            width: 65
            height: 65
            source: "../../assets/images/people.png"
            fillMode: Image.PreserveAspectFit
        }
    }

    Text { x: 292; y: 374; text: "Judit Pintér"; color: "#ffffff"; font.pixelSize: 17; font.bold: true }
    Text { x: 292; y: 401; text: "Expiration time: XX Day(s)"; color: "#ffffff"; font.pixelSize: 16 }

    AppButton {
        x: 168
        y: 482
        width: 200
        height: 62
        text: "Logout"
    }

    Text { x: 168; y: 584; text: "SETTINGS"; color: "#ff7045"; font.pixelSize: 34 }

    Text { x: 168; y: 654; text: "Language"; color: "#ffffff"; font.pixelSize: 24 }
    Text { x: 168; y: 704; text: "English"; color: "#ff7045"; font.pixelSize: 14 }
    Text { x: 300; y: 642; text: "\u2699"; color: "#ffffff"; font.pixelSize: 36 }

    Text { x: 168; y: 746; text: "Wifi network"; color: "#ffffff"; font.pixelSize: 24 }
    Text { x: 168; y: 796; text: "Factory"; color: "#ff7045"; font.pixelSize: 14 }
    Text { x: 332; y: 734; text: "\u2699"; color: "#ffffff"; font.pixelSize: 36 }

    Text { x: 168; y: 838; text: "Bluetooth"; color: "#ffffff"; font.pixelSize: 24 }
    Text { x: 168; y: 888; text: "On"; color: "#ff7045"; font.pixelSize: 14 }
    Text { x: 332; y: 826; text: "\u2699"; color: "#ffffff"; font.pixelSize: 36 }

    Text { x: 604; y: 282; text: "HARDWARE DETAILS"; color: "#6394ff"; font.pixelSize: 34 }
    Text { x: 604; y: 364; text: "EF-LASER serial no.:"; color: "#ffffff"; font.pixelSize: 20 }
    Text { x: 604; y: 412; text: "22300005"; color: "#6394ff"; font.pixelSize: 14 }
    Text { x: 604; y: 456; text: "PC serial no.:"; color: "#ffffff"; font.pixelSize: 20 }
    Text { x: 604; y: 504; text: "93100061110058"; color: "#6394ff"; font.pixelSize: 14 }

    Text { x: 604; y: 580; text: "SOFTWARE DETAILS"; color: "#6394ff"; font.pixelSize: 34 }
    Text { x: 604; y: 652; text: "Firmware version"; color: "#ffffff"; font.pixelSize: 20 }
    Text { x: 604; y: 700; text: "31"; color: "#6394ff"; font.pixelSize: 14 }
    Text { x: 604; y: 744; text: "GUI version"; color: "#ffffff"; font.pixelSize: 20 }
    Text { x: 604; y: 792; text: "1.10.3"; color: "#6394ff"; font.pixelSize: 14 }

    Text { x: 604; y: 830; text: "Confidence range / default"; color: "#ffffff"; font.pixelSize: 20 }
    Text {
        x: 604
        y: 862
        text: appController.confidenceMinimum.toFixed(3) + " – "
              + appController.confidenceMaximum.toFixed(3) + " / "
              + appController.confidenceDefault.toFixed(3)
        color: "#6394ff"
        font.pixelSize: 14
    }

    AppButton {
        x: 604
        y: 910
        width: 300
        height: 60
        text: "GUI version check"
        accent: "#6c96ff"
        onClicked: appController.syncBackend()
    }

    AppButton {
        x: 604
        y: 994
        width: 300
        height: 60
        text: "HW/SW test"
        accent: "#ff7045"
        onClicked: appController.navigate("hw-sw-test")
    }
}
