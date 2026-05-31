import QtQuick
import "../components"

Item {
    anchors.fill: parent

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

    AppButton {
        x: 604
        y: 852
        width: 300
        height: 60
        text: "GUI version check"
        accent: "#6c96ff"
        onClicked: appController.syncBackend()
    }
}
