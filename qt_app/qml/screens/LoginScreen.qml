import QtQuick
import QtQuick.Controls
import "../components"

Item {
    anchors.fill: parent

    BackButton {
        x: 32
        y: 30
        onClicked: appController.navigate("start")
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

    Image {
        x: 198
        y: 318
        width: 690
        height: 240
        source: "../../assets/images/ULTIMA.png"
        fillMode: Image.PreserveAspectFit
    }

    Text {
        x: 756
        y: 474
        text: "LASER"
        color: "#ffffff"
        font.pixelSize: 50
    }

    Text {
        anchors.horizontalCenter: parent.horizontalCenter
        y: 542
        text: "Please login with your ULTIMA Academy account."
        color: "#ffffff"
        font.pixelSize: 24
    }

    component LoginField: TextField {
        width: 530
        height: 62
        color: "#ffffff"
        placeholderTextColor: "#ffffff"
        font.pixelSize: 16
        leftPadding: 28
        rightPadding: 36
        background: Rectangle {
            radius: height / 2
            color: "transparent"
            border.color: "#ff7045"
            border.width: 5
        }
    }

    LoginField {
        x: 274
        y: 604
        placeholderText: "E-mail address"
    }

    LoginField {
        x: 274
        y: 690
        placeholderText: "Password"
        echoMode: TextInput.Password
        Text {
            anchors.right: parent.right
            anchors.rightMargin: 18
            anchors.verticalCenter: parent.verticalCenter
            text: "o"
            color: "#ffffff"
            font.pixelSize: 19
        }
    }

    AppButton {
        x: 274
        y: 826
        width: 530
        height: 62
        text: "Login"
        onClicked: appController.navigate("laser-treatment")
    }
}
