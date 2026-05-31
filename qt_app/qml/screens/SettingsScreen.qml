pragma ComponentBehavior: Bound

import QtQuick
import "../components"

Item {
    id: root
    anchors.fill: parent
    property int selectedSkinType: 2
    property int selectedHairColor: 1
    property int selectedHairType: 1

    Image {
        anchors.fill: parent
        source: "../../assets/images/Background-1.png"
        fillMode: Image.PreserveAspectCrop
    }

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
        MouseArea { anchors.fill: parent; onClicked: appController.navigate("system-info") }
    }

    component Panel: Rectangle {
        color: "#8a000000"
        radius: 39
        border.color: "#ffffff"
        border.width: 3
    }

    Panel {
        x: 64
        y: 120
        width: 952
        height: 536

        Text {
            anchors.horizontalCenter: parent.horizontalCenter
            y: 38
            text: "CALIBRATION"
            color: "#ffffff"
            font.pixelSize: 36
        }

        Image {
            anchors.horizontalCenter: parent.horizontalCenter
            y: 108
            width: 260
            height: 132
            source: "../../assets/images/calibration-device.png"
            fillMode: Image.PreserveAspectFit
        }

        AppButton {
            anchors.horizontalCenter: parent.horizontalCenter
            y: 270
            width: 366
            height: 70
            text: "Recalibration"
            accent: "#ff0876"
            textColor: "#ff0876"
        }

        Text {
            anchors.horizontalCenter: parent.horizontalCenter
            y: 486
            text: "Temperature OK"
            color: "#ffffff"
            font.pixelSize: 20
        }
    }

    Text {
        anchors.horizontalCenter: parent.horizontalCenter
        y: 680
        text: "SETTINGS"
        color: "#ffffff"
        font.pixelSize: 36
    }

    Panel {
        x: 62
        y: 740
        width: 956
        height: 298

        Text { anchors.horizontalCenter: parent.horizontalCenter; y: 36; text: "Skin Type"; color: "#ffffff"; font.pixelSize: 36 }

        component SkinTypeOption: Item {
            id: skinTypeControl
            property int optionIndex: 0
            property string optionLabel: ""
            property color swatchColor: "#f2caa7"
            width: 150
            height: 160

            Rectangle {
                anchors.horizontalCenter: parent.horizontalCenter
                width: 126
                height: 126
                radius: 63
                color: skinTypeControl.swatchColor
                border.width: root.selectedSkinType === skinTypeControl.optionIndex ? 8 : 0
                border.color: "#ffffff"

                Rectangle {
                    anchors.fill: parent
                    anchors.margins: -12
                    radius: width / 2
                    color: "transparent"
                    border.width: root.selectedSkinType === skinTypeControl.optionIndex ? 4 : 0
                    border.color: "#ff7045"
                }
            }

            Text {
                anchors.horizontalCenter: parent.horizontalCenter
                y: 128
                text: skinTypeControl.optionLabel
                color: root.selectedSkinType === skinTypeControl.optionIndex ? "#ff7045" : "#ffffff"
                font.pixelSize: 32
            }

            MouseArea {
                anchors.fill: parent
                onClicked: root.selectedSkinType = skinTypeControl.optionIndex
            }
        }

        Row {
            x: 28
            y: 122
            width: 900
            height: 160
            spacing: 0

            SkinTypeOption { optionIndex: 0; optionLabel: "I."; swatchColor: "#f2caa7" }
            SkinTypeOption { optionIndex: 1; optionLabel: "II."; swatchColor: "#eeb58d" }
            SkinTypeOption { optionIndex: 2; optionLabel: "III."; swatchColor: "#d89a73" }
            SkinTypeOption { optionIndex: 3; optionLabel: "IV."; swatchColor: "#bf794c" }
            SkinTypeOption { optionIndex: 4; optionLabel: "V."; swatchColor: "#b66a2b" }
            SkinTypeOption { optionIndex: 5; optionLabel: "VI."; swatchColor: "#48211e" }
        }
    }

    Panel {
        x: 62
        y: 1054
        width: 956
        height: 294

        Text { anchors.horizontalCenter: parent.horizontalCenter; y: 34; text: "Hair color"; color: "#ffffff"; font.pixelSize: 34 }

        component HairColor: Item {
            id: hairColorControl
            property string img: ""
            property string label: ""
            property bool selected: false
            signal clicked()
            width: 150
            height: 180

            Rectangle {
                anchors.horizontalCenter: parent.horizontalCenter
                y: 40
                width: 108
                height: 118
                radius: 54
                color: "transparent"
                border.color: hairColorControl.selected ? "#ff7045" : "transparent"
                border.width: hairColorControl.selected ? 4 : 0
            }

            Image {
                anchors.horizontalCenter: parent.horizontalCenter
                y: 48
                width: 92
                height: 104
                source: hairColorControl.img
                fillMode: Image.PreserveAspectFit
            }

            Text {
                anchors.horizontalCenter: parent.horizontalCenter
                y: 160
                width: parent.width
                text: hairColorControl.label
                color: hairColorControl.selected ? "#ff7045" : "#ffffff"
                font.pixelSize: 18
                horizontalAlignment: Text.AlignHCenter
            }

            MouseArea {
                anchors.fill: parent
                onClicked: hairColorControl.clicked()
            }
        }

        Row {
            x: 28
            y: 70
            width: 900
            height: 188
            spacing: 0

            HairColor { img: "../../assets/images/haircolors/hf.png"; label: "Black"; selected: root.selectedHairColor === 0; onClicked: root.selectedHairColor = 0 }
            HairColor { img: "../../assets/images/haircolors/e.png"; label: "Dark Brown"; selected: root.selectedHairColor === 1; onClicked: root.selectedHairColor = 1 }
            HairColor { img: "../../assets/images/haircolors/vv.png"; label: "Brown"; selected: root.selectedHairColor === 2; onClicked: root.selectedHairColor = 2 }
            HairColor { img: "../../assets/images/haircolors/n.png"; label: "Grey/White"; selected: root.selectedHairColor === 3; onClicked: root.selectedHairColor = 3 }
            HairColor { img: "../../assets/images/haircolors/dd.png"; label: "Blonde"; selected: root.selectedHairColor === 4; onClicked: root.selectedHairColor = 4 }
            HairColor { img: "../../assets/images/haircolors/h.png"; label: "Red"; selected: root.selectedHairColor === 5; onClicked: root.selectedHairColor = 5 }
        }
    }

    Panel {
        x: 62
        y: 1370
        width: 956
        height: 290

        Text { anchors.horizontalCenter: parent.horizontalCenter; y: 34; text: "Hair Type"; color: "#ffffff"; font.pixelSize: 34 }

        component HairType: Item {
            id: hairTypeControl
            property string img: ""
            property string label: ""
            property bool selected: false
            signal clicked()
            width: 220
            height: 170

            Rectangle {
                anchors.horizontalCenter: parent.horizontalCenter
                y: 28
                width: 150
                height: 122
                radius: 22
                color: hairTypeControl.selected ? "#18ffffff" : "transparent"
                border.color: hairTypeControl.selected ? "#ff7045" : "transparent"
                border.width: hairTypeControl.selected ? 4 : 0
            }

            Image {
                anchors.horizontalCenter: parent.horizontalCenter
                y: 38
                width: 120
                height: 96
                source: hairTypeControl.img
                fillMode: Image.PreserveAspectFit
            }

            Text {
                anchors.horizontalCenter: parent.horizontalCenter
                y: 142
                text: hairTypeControl.label
                color: hairTypeControl.selected ? "#ff7045" : "#ffffff"
                font.pixelSize: 24
            }

            MouseArea {
                anchors.fill: parent
                onClicked: hairTypeControl.clicked()
            }
        }

        Row {
            x: 148
            y: 86
            width: 660
            height: 170
            spacing: 0

            HairType { img: "../../assets/images/hairtypes/thin.png"; label: "Thin"; selected: root.selectedHairType === 0; onClicked: root.selectedHairType = 0 }
            HairType { img: "../../assets/images/hairtypes/medium.png"; label: "Medium"; selected: root.selectedHairType === 1; onClicked: root.selectedHairType = 1 }
            HairType { img: "../../assets/images/hairtypes/thick.png"; label: "Thick"; selected: root.selectedHairType === 2; onClicked: root.selectedHairType = 2 }
        }
    }

    Text {
        anchors.horizontalCenter: parent.horizontalCenter
        y: 1692
        text: "LASER MODULE TEMP: <span style='color:#00d723'>21°C</span>"
        textFormat: Text.RichText
        color: "#ffffff"
        font.pixelSize: 24
    }

    AppButton {
        anchors.horizontalCenter: parent.horizontalCenter
        y: 1738
        width: 366
        height: 68
        text: "Start treatment"
        accent: "#ff7045"
        textColor: "#ff7045"
        onClicked: appController.navigate("laser-treatment")
    }
}
