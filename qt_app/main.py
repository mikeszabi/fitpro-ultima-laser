from __future__ import annotations

import argparse
import faulthandler
import logging
import os
import signal
import sys
from pathlib import Path

from PySide6.QtCore import QCoreApplication, QEventLoop, QTimer, Qt, QtMsgType, QUrl, qInstallMessageHandler
from PySide6.QtGui import QGuiApplication
from PySide6.QtQml import QQmlApplicationEngine

from api_client import ApiClient
from app_controller import AppController


LOG = logging.getLogger(__name__)


def configure_logging() -> None:
    level_name = os.environ.get("FITPRO_QT_LOG_LEVEL", "INFO").upper()
    level = getattr(logging, level_name, logging.INFO)
    logging.basicConfig(
        level=level,
        format="%(asctime)s.%(msecs)03d %(levelname)s [%(threadName)s] %(name)s: %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S",
        stream=sys.stderr,
        force=True,
    )

    faulthandler.enable()
    if hasattr(signal, "SIGUSR1"):
        faulthandler.register(signal.SIGUSR1, all_threads=True)

    def handle_exception(exc_type, exc_value, exc_traceback) -> None:
        if issubclass(exc_type, KeyboardInterrupt):
            sys.__excepthook__(exc_type, exc_value, exc_traceback)
            return
        logging.getLogger(__name__).critical(
            "Unhandled exception", exc_info=(exc_type, exc_value, exc_traceback)
        )

    sys.excepthook = handle_exception


def install_qt_message_handler() -> None:
    qt_logger = logging.getLogger("qt")
    levels = {
        QtMsgType.QtDebugMsg: logging.DEBUG,
        QtMsgType.QtInfoMsg: logging.INFO,
        QtMsgType.QtWarningMsg: logging.WARNING,
        QtMsgType.QtCriticalMsg: logging.ERROR,
        QtMsgType.QtFatalMsg: logging.CRITICAL,
    }

    def handler(message_type, context, message) -> None:
        location = ""
        if context.file:
            location = f" ({context.file}:{context.line})"
        qt_logger.log(levels.get(message_type, logging.INFO), "%s%s", message, location)

    qInstallMessageHandler(handler)


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


def install_input_event_pump(interval_ms: int) -> QTimer | None:
    if interval_ms <= 0:
        LOG.info("Qt input event pump disabled")
        return None

    active = False
    timer = QTimer()
    timer.setInterval(interval_ms)
    timer.setTimerType(Qt.PreciseTimer)

    def pump_events() -> None:
        nonlocal active
        if active:
            return
        active = True
        try:
            QCoreApplication.processEvents(QEventLoop.AllEvents, 1)
        finally:
            active = False

    timer.timeout.connect(pump_events)
    timer.start()
    LOG.info("Qt input event pump enabled every %sms", interval_ms)
    return timer


def main() -> int:
    configure_logging()
    install_qt_message_handler()
    os.environ.setdefault("QT_XCB_NO_XI2", "1")
    args = parse_args()
    LOG.info(
        "Starting FitPro Qt app windowed=%s wide_screen=%s api_base=%s qt_qpa=%s qt_xcb_no_xi2=%s",
        args.windowed,
        args.wide_screen,
        args.api_base_url or os.environ.get("FITPRO_API_BASE_URL") or "default",
        os.environ.get("QT_QPA_PLATFORM", ""),
        os.environ.get("QT_XCB_NO_XI2", ""),
    )
    QGuiApplication.setAttribute(Qt.AA_SynthesizeMouseForUnhandledTouchEvents, True)
    QGuiApplication.setAttribute(Qt.AA_SynthesizeTouchForUnhandledMouseEvents, True)

    app = QGuiApplication(sys.argv)
    app.setApplicationName("FitPro Ultima Laser")
    app.setOrganizationName("FitPro")

    qml_dir = Path(__file__).resolve().parent / "qml"
    api = ApiClient(base_url=args.api_base_url) if args.api_base_url else ApiClient()
    controller = AppController(api)
    app.aboutToQuit.connect(controller.stopStateSynchronization)
    LOG.info("Qt app using API base URL: %s", api.base_url)

    engine = QQmlApplicationEngine()
    engine.rootContext().setContextProperty("appController", controller)
    engine.rootContext().setContextProperty("windowedMode", args.windowed)
    engine.rootContext().setContextProperty("wideScreenMode", args.wide_screen)
    engine.addImportPath(str(qml_dir))
    LOG.info("Loading QML from %s", qml_dir / "Main.qml")
    engine.load(QUrl.fromLocalFile(str(qml_dir / "Main.qml")))

    if not engine.rootObjects():
        LOG.error("QML engine did not create a root object")
        return 1

    heartbeat_ms = max(1000, int(os.environ.get("FITPRO_QT_HEARTBEAT_MS", "10000")))
    heartbeat = QTimer()
    heartbeat.setInterval(heartbeat_ms)
    heartbeat.timeout.connect(controller.logHeartbeat)
    heartbeat.start()
    LOG.info("Heartbeat logging enabled every %sms", heartbeat_ms)

    # Qt already owns the event loop. The old nested 50 ms processEvents pump can
    # introduce re-entrancy and input/render jitter, so it is opt-in for debugging.
    input_pump_ms = int(os.environ.get("FITPRO_QT_INPUT_PUMP_MS", "0"))
    input_pump = install_input_event_pump(input_pump_ms)

    exit_code = app.exec()
    if input_pump is not None:
        input_pump.stop()
    LOG.info("Qt app exiting with code %s", exit_code)
    return exit_code


if __name__ == "__main__":
    raise SystemExit(main())
