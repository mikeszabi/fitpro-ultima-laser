from __future__ import annotations

import argparse
import os
import sys
from pathlib import Path

from PySide6.QtCore import Qt, QUrl
from PySide6.QtGui import QGuiApplication
from PySide6.QtQml import QQmlApplicationEngine

from api_client import ApiClient
from app_controller import AppController


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="FitPro Ultima Laser native kiosk")
    parser.add_argument("--windowed", action="store_true", help="Run in a development window")
    parser.add_argument(
        "--wide-screen",
        action="store_true",
        help="Scale the portrait kiosk UI so the full frontend fits on a wide display",
    )
    parser.add_argument(
        "--api-base-url",
        default=os.environ.get("FITPRO_API_BASE_URL"),
        help="FastAPI backend base URL",
    )
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    QGuiApplication.setAttribute(Qt.AA_SynthesizeMouseForUnhandledTouchEvents, True)
    QGuiApplication.setAttribute(Qt.AA_SynthesizeTouchForUnhandledMouseEvents, True)

    app = QGuiApplication(sys.argv)
    app.setApplicationName("FitPro Ultima Laser")
    app.setOrganizationName("FitPro")

    qml_dir = Path(__file__).resolve().parent / "qml"
    api = ApiClient(base_url=args.api_base_url) if args.api_base_url else ApiClient()
    controller = AppController(api)

    engine = QQmlApplicationEngine()
    engine.rootContext().setContextProperty("appController", controller)
    engine.rootContext().setContextProperty("windowedMode", args.windowed)
    engine.rootContext().setContextProperty("wideScreenMode", args.wide_screen)
    engine.addImportPath(str(qml_dir))
    engine.load(QUrl.fromLocalFile(str(qml_dir / "Main.qml")))

    if not engine.rootObjects():
        return 1

    return app.exec()


if __name__ == "__main__":
    raise SystemExit(main())
