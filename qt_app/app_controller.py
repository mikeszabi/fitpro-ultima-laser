from __future__ import annotations

import os
import itertools
import logging
import subprocess
import tempfile
import threading
import time
from collections.abc import Callable
from pathlib import Path
from typing import Any

from PySide6.QtCore import QObject, Property, QRunnable, QThreadPool, Signal, Slot

from api_client import ApiClient
from app_config import ConfidenceConfig, load_confidence_config


LOG = logging.getLogger(__name__)
_WORKER_IDS = itertools.count(1)


class WorkerSignals(QObject):
    finished = Signal(object)
    failed = Signal(str)


class ApiWorker(QRunnable):
    def __init__(self, label: str, task: Callable[[], Any], quiet: bool = False) -> None:
        super().__init__()
        self.label = label
        self.task = task
        self.quiet = quiet
        self.worker_id = next(_WORKER_IDS)
        self.started_at = 0.0
        self.signals = WorkerSignals()

    def run(self) -> None:
        self.started_at = time.monotonic()
        if not self.quiet:
            LOG.info("task[%s] START %s", self.worker_id, self.label)
        else:
            LOG.debug("task[%s] START %s", self.worker_id, self.label)
        try:
            result = self.task()
            duration_ms = (time.monotonic() - self.started_at) * 1000
            if self.quiet:
                LOG.debug("task[%s] OK %s %.0fms", self.worker_id, self.label, duration_ms)
            else:
                LOG.info("task[%s] OK %s %.0fms", self.worker_id, self.label, duration_ms)
            if duration_ms >= 3000:
                LOG.warning("task[%s] SLOW %s %.0fms", self.worker_id, self.label, duration_ms)
            self.signals.finished.emit(result)
        except Exception as exc:
            duration_ms = (time.monotonic() - self.started_at) * 1000
            LOG.exception("task[%s] FAIL %s %.0fms: %s", self.worker_id, self.label, duration_ms, exc)
            self.signals.failed.emit(str(exc))


class AppController(QObject):
    screenChanged = Signal()
    apiStatusChanged = Signal()
    busyChanged = Signal()
    startupCheckChanged = Signal()
    laserStateChanged = Signal()
    powerChanged = Signal()
    pulseWidthChanged = Signal()
    redDotChanged = Signal()
    vacuumChanged = Signal()
    targetChanged = Signal()
    calibrationChanged = Signal()
    cameraFrameUrlChanged = Signal()
    errorChanged = Signal()
    diagnosticsChanged = Signal()
    _cameraFrameReady = Signal(str, object)
    _cameraFrameFailed = Signal(str, object)
    _taskFinished = Signal(str, object, object, bool, object)
    _taskFailed = Signal(str, str, bool, object)
    _streamLog = Signal(str)
    _stateSnapshot = Signal(object)
    _stateConnection = Signal(bool, str)

    def __init__(
        self,
        api: ApiClient | None = None,
        confidence_config: ConfidenceConfig | None = None,
    ) -> None:
        super().__init__()
        self._api = api or ApiClient()
        self._pool = QThreadPool.globalInstance()
        self._workers: list[ApiWorker] = []

        self._screen = "start"
        self._api_status = "Backend: checking"
        self._backend_ok = False
        self._busy = False
        self._busy_label = ""
        self._startup_backend_check_started = False
        self._startup_check_in_progress = False
        self._laser_ready: bool | None = None
        self._p808 = 20
        self._p980 = 25
        self._p1064 = 50
        self._pulse_width = 50
        self._red_dot = False
        self._vacuum_enabled: bool | None = None
        self._vacuum_lock: bool | None = None
        self._target = False
        self._targeted_follicles = 0
        self._loaded_target_count = -1
        self._confidence_config = confidence_config or load_confidence_config()
        self._confidence = self._confidence_config.default
        self._treatment_mode = "semi-auto"
        self._detection_enabled: bool | None = None
        self._overlay_enabled: bool | None = None
        self._app_state = "-"
        self._target_state = "-"
        self._target_error_clear: bool | None = None
        self._app_state_running: bool | None = None
        self._laser_temp = "-"
        self._calibration_detection_enabled = False
        self._mask_overlay_enabled = False
        self._dot_image_x = "-"
        self._dot_image_y = "-"
        self._hsv_click_x = "-"
        self._hsv_click_y = "-"
        self._hsv_click_value = "-"
        self._rgb_click_value = "-"
        self._galvo_x = "-"
        self._galvo_y = "-"
        self._move_x = 3000
        self._move_y = 3000
        self._move_step = 25
        self._stored_count = 0
        self._clicked_image_x = "-"
        self._clicked_image_y = "-"
        self._target_galvo_x = "-"
        self._target_galvo_y = "-"
        self._move_result = "-"
        self._homography_status = "not loaded"
        self._hsv_lower1 = [0, 50, 250]
        self._hsv_upper1 = [20, 240, 255]
        self._hsv_lower2 = [160, 50, 250]
        self._hsv_upper2 = [180, 240, 255]
        self._settings_dirty = True
        self._treatment_log = ""
        self._camera_frame_dir = Path(tempfile.gettempdir()) / "fitpro-ultima-laser"
        self._camera_frame_dir.mkdir(parents=True, exist_ok=True)
        self._camera_frame_slot = 0
        self._camera_refresh_in_flight = False
        self._calibration_telemetry_in_flight = False
        self._camera_frame_started_at = 0.0
        self._camera_frame_count = 0
        self._camera_skip_busy_count = 0
        self._camera_skip_in_flight_count = 0
        self._camera_skip_interval_count = 0
        self._last_camera_progress_log_at = 0.0
        self._camera_last_refresh_at = 0.0
        self._camera_min_refresh_interval = 0.25
        self._camera_last_error = ""
        self._camera_frame_url = ""
        self._backend_camera_error = ""
        self._backend_sync_error = ""
        self._sync_backend_in_flight = False
        self._state_revision = -1
        self._state_connected = False
        self._state_stream_stop = threading.Event()
        self._state_stream_thread: threading.Thread | None = None
        self._treatment_stream_stop: threading.Event | None = None
        self._treatment_stream_thread: threading.Thread | None = None
        self._diagnostic_checks: list[dict[str, str]] = []
        self._diagnostic_summary = "Not run yet"
        self._diagnostic_raw_output = ""
        self._diagnostic_last_run = ""
        self._backend_restart_output = "Backend restart has not been run."
        self._error_title = ""
        self._error_message = ""

        self._cameraFrameReady.connect(self._handle_camera_frame_ready)
        self._cameraFrameFailed.connect(self._handle_camera_frame_failed)
        self._taskFinished.connect(self._handle_task_finished)
        self._taskFailed.connect(self._handle_task_failed)
        self._streamLog.connect(self._append_log)
        self._stateSnapshot.connect(self._apply_treatment_status)
        self._stateConnection.connect(self._apply_state_connection)

    @Property(str, notify=screenChanged)
    def screen(self) -> str:
        return self._screen

    @Property(str, notify=apiStatusChanged)
    def apiStatus(self) -> str:
        return self._api_status

    @Property(bool, notify=busyChanged)
    def busy(self) -> bool:
        return self._busy

    @Property(str, notify=busyChanged)
    def busyLabel(self) -> str:
        return self._busy_label

    @Property(bool, notify=startupCheckChanged)
    def startupCheckInProgress(self) -> bool:
        return self._startup_check_in_progress

    @Property(bool, notify=laserStateChanged)
    def laserReady(self) -> bool:
        return self._laser_ready is True

    @Property(str, notify=laserStateChanged)
    def laserStateText(self) -> str:
        return self._format_boolean_state(self._laser_ready, "ARMED", "DISARMED")

    @Property(int, notify=powerChanged)
    def p808(self) -> int:
        return self._p808

    @Property(int, notify=powerChanged)
    def p980(self) -> int:
        return self._p980

    @Property(int, notify=powerChanged)
    def p1064(self) -> int:
        return self._p1064

    @Property(float, notify=powerChanged)
    def totalPower(self) -> float:
        return self.p808Watts + self.p980Watts + self.p1064Watts

    @Property(float, notify=powerChanged)
    def p808Watts(self) -> float:
        return self._percent_to_watts(self._p808)

    @Property(float, notify=powerChanged)
    def p980Watts(self) -> float:
        return self._percent_to_watts(self._p980)

    @Property(float, notify=powerChanged)
    def p1064Watts(self) -> float:
        return self._percent_to_watts(self._p1064)

    @Property(int, notify=pulseWidthChanged)
    def pulseWidth(self) -> int:
        return self._pulse_width

    @Property(bool, notify=redDotChanged)
    def redDot(self) -> bool:
        return self._red_dot

    @Property(bool, notify=vacuumChanged)
    def vacuumEnabled(self) -> bool:
        return self._vacuum_enabled is True

    @Property(str, notify=vacuumChanged)
    def vacuumStateText(self) -> str:
        return self._format_boolean_state(self._vacuum_enabled, "ON", "OFF")

    @Property(bool, notify=vacuumChanged)
    def vacuumLock(self) -> bool:
        return self._vacuum_lock is True

    @Property(bool, notify=targetChanged)
    def target(self) -> bool:
        return self._target

    @Property(int, notify=targetChanged)
    def targetedFollicles(self) -> int:
        return self._targeted_follicles

    @Property(int, notify=targetChanged)
    def loadedTargetCount(self) -> int:
        return self._loaded_target_count

    @Property(float, notify=targetChanged)
    def confidence(self) -> float:
        return self._confidence

    @Property(float, constant=True)
    def confidenceMinimum(self) -> float:
        return self._confidence_config.minimum

    @Property(float, constant=True)
    def confidenceMaximum(self) -> float:
        return self._confidence_config.maximum

    @Property(float, constant=True)
    def confidenceDefault(self) -> float:
        return self._confidence_config.default

    @Property(float, constant=True)
    def confidenceStep(self) -> float:
        return self._confidence_config.step

    @Property(str, notify=targetChanged)
    def treatmentMode(self) -> str:
        return self._treatment_mode

    @Property(bool, notify=targetChanged)
    def detectionEnabled(self) -> bool:
        return self._detection_enabled is True

    @Property(str, notify=targetChanged)
    def detectionStateText(self) -> str:
        return self._format_boolean_state(self._detection_enabled, "ON", "OFF")

    @Property(bool, notify=targetChanged)
    def overlayEnabled(self) -> bool:
        return self._overlay_enabled is True

    @Property(str, notify=targetChanged)
    def overlayStateText(self) -> str:
        return self._format_boolean_state(self._overlay_enabled, "ON", "OFF")

    @Property(str, notify=targetChanged)
    def loadedTargetText(self) -> str:
        return str(self._loaded_target_count) if self._loaded_target_count >= 0 else "UNKNOWN"

    @Property(str, notify=targetChanged)
    def appState(self) -> str:
        return self._app_state

    @Property(str, notify=targetChanged)
    def targetState(self) -> str:
        return self._target_state

    @Property(bool, notify=targetChanged)
    def targetErrorClear(self) -> bool:
        return self._target_error_clear

    @Property(bool, notify=targetChanged)
    def appStateRunning(self) -> bool:
        return self._app_state_running is True

    @Property(bool, notify=targetChanged)
    def stateConnected(self) -> bool:
        return self._state_connected

    @Property(bool, notify=targetChanged)
    def hardwareStateKnown(self) -> bool:
        return (
            self._laser_ready is not None
            and self._vacuum_enabled is not None
            and self._app_state_running is not None
            and self._target_error_clear is not None
            and self._target_state != "-"
            and self._loaded_target_count >= 0
        )

    @Property(str, notify=targetChanged)
    def laserTemp(self) -> str:
        return self._laser_temp

    @Property(bool, notify=calibrationChanged)
    def calibrationDetectionEnabled(self) -> bool:
        return self._calibration_detection_enabled

    @Property(bool, notify=calibrationChanged)
    def maskOverlayEnabled(self) -> bool:
        return self._mask_overlay_enabled

    @Property(str, notify=calibrationChanged)
    def dotImageX(self) -> str:
        return self._dot_image_x

    @Property(str, notify=calibrationChanged)
    def dotImageY(self) -> str:
        return self._dot_image_y

    @Property(str, notify=calibrationChanged)
    def hsvClickX(self) -> str:
        return self._hsv_click_x

    @Property(str, notify=calibrationChanged)
    def hsvClickY(self) -> str:
        return self._hsv_click_y

    @Property(str, notify=calibrationChanged)
    def hsvClickValue(self) -> str:
        return self._hsv_click_value

    @Property(str, notify=calibrationChanged)
    def rgbClickValue(self) -> str:
        return self._rgb_click_value

    @Property(str, notify=calibrationChanged)
    def galvoX(self) -> str:
        return self._galvo_x

    @Property(str, notify=calibrationChanged)
    def galvoY(self) -> str:
        return self._galvo_y

    @Property(int, notify=calibrationChanged)
    def moveX(self) -> int:
        return self._move_x

    @Property(int, notify=calibrationChanged)
    def moveY(self) -> int:
        return self._move_y

    @Property(int, notify=calibrationChanged)
    def moveStep(self) -> int:
        return self._move_step

    @Property(int, notify=calibrationChanged)
    def storedCount(self) -> int:
        return self._stored_count

    @Property(str, notify=calibrationChanged)
    def clickedImageX(self) -> str:
        return self._clicked_image_x

    @Property(str, notify=calibrationChanged)
    def clickedImageY(self) -> str:
        return self._clicked_image_y

    @Property(str, notify=calibrationChanged)
    def targetGalvoX(self) -> str:
        return self._target_galvo_x

    @Property(str, notify=calibrationChanged)
    def targetGalvoY(self) -> str:
        return self._target_galvo_y

    @Property(str, notify=calibrationChanged)
    def moveResult(self) -> str:
        return self._move_result

    @Property(str, notify=calibrationChanged)
    def homographyStatus(self) -> str:
        return self._homography_status

    @Property("QVariantList", notify=calibrationChanged)
    def hsvLower1(self) -> list[int]:
        return self._hsv_lower1

    @Property("QVariantList", notify=calibrationChanged)
    def hsvUpper1(self) -> list[int]:
        return self._hsv_upper1

    @Property("QVariantList", notify=calibrationChanged)
    def hsvLower2(self) -> list[int]:
        return self._hsv_lower2

    @Property("QVariantList", notify=calibrationChanged)
    def hsvUpper2(self) -> list[int]:
        return self._hsv_upper2

    @Property(bool, notify=targetChanged)
    def settingsDirty(self) -> bool:
        return self._settings_dirty

    @Property(str, notify=targetChanged)
    def treatmentLog(self) -> str:
        return self._treatment_log

    @Property(str, notify=targetChanged)
    def treatmentLogHead(self) -> str:
        return self._treatment_log.splitlines()[0] if self._treatment_log else ""

    @Property(bool, notify=targetChanged)
    def treatmentModeReady(self) -> bool:
        return (
            self._backend_ok
            and self._state_connected
            and self.hardwareStateKnown
            and self._app_state_running is True
            and self._is_ok_state(self._app_state)
            and self._is_ok_state(self._target_state)
        )

    @Property(bool, notify=targetChanged)
    def fireReady(self) -> bool:
        return (
            self.treatmentModeReady
            and self._laser_ready
            and self._vacuum_enabled
            and self._target_error_clear
            and not self._settings_dirty
            and self._loaded_target_count > 0
        )

    @Property(str, notify=cameraFrameUrlChanged)
    def cameraFrameUrl(self) -> str:
        return self._camera_frame_url

    @Property(str, notify=targetChanged)
    def liveCameraFrameUrl(self) -> str:
        return self._api.current_frame_url()

    @Property(str, notify=errorChanged)
    def errorTitle(self) -> str:
        return self._error_title

    @Property(str, notify=errorChanged)
    def errorMessage(self) -> str:
        return self._error_message

    @Property("QVariantList", notify=diagnosticsChanged)
    def diagnosticChecks(self) -> list[dict[str, str]]:
        return self._diagnostic_checks

    @Property(str, notify=diagnosticsChanged)
    def diagnosticSummary(self) -> str:
        return self._diagnostic_summary

    @Property(str, notify=diagnosticsChanged)
    def diagnosticRawOutput(self) -> str:
        return self._diagnostic_raw_output

    @Property(str, notify=diagnosticsChanged)
    def diagnosticLastRun(self) -> str:
        return self._diagnostic_last_run

    @Property(str, notify=diagnosticsChanged)
    def backendRestartOutput(self) -> str:
        return self._backend_restart_output

    @Slot(str)
    def navigate(self, screen: str) -> None:
        if self._screen == screen:
            LOG.info("Navigation ignored; already on screen=%s", screen)
            return
        previous_screen = self._screen
        LOG.info("Navigation %s -> %s", previous_screen, screen)
        if self._screen == "laser-treatment" and screen != "laser-treatment":
            self.stopTreatmentCameraStream()
        self._screen = screen
        self.screenChanged.emit()

    @Slot()
    def clearError(self) -> None:
        LOG.info("Clearing error dialog title=%r message=%r", self._error_title, self._error_message)
        self._error_title = ""
        self._error_message = ""
        self.errorChanged.emit()

    @Slot()
    def refreshCameraFrame(self) -> None:
        if self._screen not in {"laser-treatment", "calibration"}:
            return
        if self._busy:
            self._camera_skip_busy_count += 1
            self._log_camera_skips()
            return
        if self._camera_refresh_in_flight:
            self._camera_skip_in_flight_count += 1
            self._log_camera_skips()
            return
        now = time.monotonic()
        if now - self._camera_last_refresh_at < self._camera_min_refresh_interval:
            self._camera_skip_interval_count += 1
            return

        self._camera_refresh_in_flight = True
        self._camera_frame_started_at = now
        self._camera_last_refresh_at = now
        frame_number = self._camera_frame_count + 1
        if now - self._last_camera_progress_log_at > 5:
            LOG.info("camera[%s] START screen=%s overlay=%s targets=%s", frame_number, self._screen, self._overlay_enabled, self._loaded_target_count)
            self._last_camera_progress_log_at = now

        def task() -> str:
            timestamp = int(time.time() * 1000)
            if self._screen == "calibration" or self._overlay_enabled or self._loaded_target_count > 0:
                payload = self._api.current_frame_bytes(timestamp)
            else:
                payload = self._api.snapshot_bytes(timestamp)
            if not self._is_supported_image(payload):
                raise ValueError("Snapshot response is not a supported image")

            self._camera_frame_slot = 1 - self._camera_frame_slot
            frame_path = self._camera_frame_dir / f"camera-frame-{self._camera_frame_slot}.jpg"
            tmp_path = self._camera_frame_dir / f".camera-frame-{self._camera_frame_slot}.tmp"
            tmp_path.write_bytes(payload)
            os.replace(tmp_path, frame_path)
            return f"{frame_path.as_uri()}?t={timestamp}"

        worker = ApiWorker("Camera frame", task, quiet=True)
        self._workers.append(worker)
        worker.signals.finished.connect(
            lambda url, worker=worker: self._cameraFrameReady.emit(str(url), worker)
        )
        worker.signals.failed.connect(
            lambda message, worker=worker: self._cameraFrameFailed.emit(message, worker)
        )
        self._pool.start(worker)

    @Slot()
    def syncBackend(self) -> None:
        if self._sync_backend_in_flight:
            LOG.debug("Backend sync skipped; already in flight")
            return
        self._sync_backend_in_flight = True

        def task() -> dict[str, Any]:
            return {"health": self._api.health(), "state": self._api.treatment_app_status()}

        self._run("Backend sync", task, self._apply_backend_state, busy=False)

    @Slot()
    def initializeCalibrationPage(self) -> None:
        LOG.info("Initializing calibration page")
        def task() -> dict[str, Any]:
            detection = self._api.detection_status()
            hsv = self._api.detection_hsv()
            arm = self._api.laser_arm_enabled()
            red_dot = self._api.laser_red_dot_enabled()
            pos = self._api.mover_pos()
            return {
                "detection": detection,
                "hsv": hsv,
                "arm": arm,
                "red_dot": red_dot,
                "pos": pos,
            }

        self._run("Calibration init", task, self._apply_calibration_status, busy=False)

    @Slot()
    def refreshCalibrationTelemetry(self) -> None:
        if self._screen != "calibration":
            return
        if self._calibration_telemetry_in_flight:
            LOG.debug("Calibration telemetry skipped; already in flight")
            return
        self._calibration_telemetry_in_flight = True

        def task() -> dict[str, Any]:
            data: dict[str, Any] = {}
            try:
                data["dot"] = self._api.dot()
            except Exception as exc:
                data["dot_error"] = str(exc)
            try:
                data["pos"] = self._api.mover_pos()
            except Exception as exc:
                data["pos_error"] = str(exc)
            return data

        self._run("Calibration telemetry", task, self._apply_calibration_telemetry, busy=False)

    @Slot(bool)
    def setCalibrationDetection(self, enabled: bool) -> None:
        LOG.info("Calibration detection requested enabled=%s", enabled)
        self._run(
            "Calibration detection",
            lambda: self._api.set_calibration_detection_enabled(enabled),
            self._apply_calibration_detection,
        )

    @Slot(bool)
    def setMaskOverlay(self, enabled: bool) -> None:
        LOG.info("Mask overlay requested enabled=%s", enabled)
        self._run(
            "Mask overlay",
            lambda: self._api.set_mask_overlay_enabled(enabled),
            self._apply_mask_overlay,
        )

    @Slot()
    def disableCalibrationMode(self) -> None:
        LOG.info("Disable calibration mode requested")

        def task() -> dict[str, Any]:
            results: dict[str, Any] = {}
            results["mask"] = self._api.set_mask_overlay_enabled(False)
            results["detection"] = self._api.set_calibration_detection_enabled(False)
            results["red_dot"] = self._api.set_red_dot_enabled(False)
            results["arm"] = self._api.arm_laser(False)
            return results

        self._run("Disable calibration mode", task, self._apply_calibration_mode_disabled)

    @Slot(str, str, int, int)
    def setHsvChannel(self, range_name: str, bound_name: str, channel: int, value: int) -> None:
        LOG.info("HSV change range=%s bound=%s channel=%s value=%s", range_name, bound_name, channel, value)
        target = self._hsv_target(range_name, bound_name)
        if target is None or channel < 0 or channel > 2:
            return
        limit = 180 if channel == 0 else 255
        target[channel] = max(0, min(limit, int(value)))
        self.calibrationChanged.emit()

        values = self._hsv_payload()
        self._run("HSV limits", lambda: self._api.set_detection_hsv(values), self._apply_hsv_status, busy=False)

    @Slot(bool)
    def setCalibrationLaserArm(self, enabled: bool) -> None:
        LOG.info("Calibration laser arm requested enabled=%s", enabled)
        self._run("Laser arm" if enabled else "Laser disarm", lambda: self._api.arm_laser(enabled), lambda _: None)

    @Slot(bool)
    def setCalibrationRedDot(self, enabled: bool) -> None:
        LOG.info("Calibration red dot requested enabled=%s", enabled)
        self._run("Red dot", lambda: self._api.set_red_dot_enabled(enabled), lambda _: self._apply_red_dot(enabled))

    @Slot(int, int)
    def setMoveTarget(self, x: int, y: int) -> None:
        self._move_x = max(0, min(4095, int(x)))
        self._move_y = max(0, min(4095, int(y)))
        self.calibrationChanged.emit()

    @Slot(int)
    def setMoveStep(self, step: int) -> None:
        self._move_step = max(1, min(1000, int(step)))
        self.calibrationChanged.emit()

    @Slot()
    def moveGalvoToTarget(self) -> None:
        LOG.info("Galvo move requested x=%s y=%s", self._move_x, self._move_y)
        self._run(
            "Galvo move",
            lambda: self._api.mover_move(self._move_x, self._move_y),
            self._apply_galvo_move_result,
        )

    @Slot(str)
    def moveGalvoDirection(self, direction: str) -> None:
        if direction not in {"up", "down", "left", "right"}:
            LOG.warning("Ignoring invalid galvo direction=%s", direction)
            return
        LOG.info("Galvo direction requested direction=%s step=%s", direction, self._move_step)
        self._run(
            f"Galvo {direction}",
            lambda: self._api.mover_direction(direction, self._move_step),
            self._apply_galvo_move_result,
        )

    @Slot()
    def startCalibrationCollection(self) -> None:
        LOG.info("Calibration point collection start requested")
        self._run("Calibration start", self._api.calibration_start, self._apply_calibration_start)

    @Slot()
    def storeCalibrationPoint(self) -> None:
        LOG.info("Calibration store point requested")
        self._run("Store point", self._api.calibration_store, self._apply_calibration_store)

    @Slot()
    def saveCalibration(self) -> None:
        LOG.info("Calibration save requested stored_count=%s", self._stored_count)
        self._run("Save calibration", self._api.calibration_save, self._apply_calibration_save)

    @Slot()
    def reloadHomography(self) -> None:
        LOG.info("Homography reload requested")
        self._run("Reload homography", self._api.homography_reload, self._apply_homography_reload)

    @Slot(int, int, bool)
    def handleCalibrationImageClick(self, x: int, y: int, hsv_inspect: bool) -> None:
        LOG.info("Calibration image click x=%s y=%s hsv_inspect=%s", x, y, hsv_inspect)
        self._clicked_image_x = str(x)
        self._clicked_image_y = str(y)
        self.calibrationChanged.emit()
        if hsv_inspect:
            self._run(
                "HSV inspect",
                lambda: self._api.frame_hsv(x, y),
                self._apply_hsv_click,
                busy=False,
            )
            return
        self._run(
            "Image move",
            lambda: self._api.mover_move_image(x, y),
            self._apply_image_move,
        )

    @Slot(str)
    def restartBackend(self, sudo_password: str) -> None:
        if not sudo_password:
            self._backend_restart_output = "Enter the sudo password before restarting."
            self.diagnosticsChanged.emit()
            return

        def task() -> str:
            completed = subprocess.run(
                ["sudo", "-S", "-k", "-p", "", "systemctl", "restart", "hairkiller-backend.service"],
                input=f"{sudo_password}\n",
                capture_output=True,
                check=False,
                text=True,
                timeout=45.0,
            )
            output = "\n".join(
                part.strip()
                for part in (completed.stdout, completed.stderr)
                if part and part.strip()
            )
            if completed.returncode != 0:
                raise RuntimeError(output or f"systemctl exited with {completed.returncode}")
            self._api.wait_until_ready(timeout=35.0)
            return output or "Backend restarted and is reachable."

        self._run("Backend restart", task, self._apply_backend_restart_output)

    @Slot(bool)
    def runFullBackendCheck(self, skip_model_load: bool) -> None:
        self._diagnostic_checks = []
        self._diagnostic_summary = "Running..."
        self._diagnostic_raw_output = ""
        self._diagnostic_last_run = ""
        self.diagnosticsChanged.emit()

        self._run(
            "Full backend check",
            lambda: self._run_full_backend_check_task(skip_model_load),
            self._apply_full_backend_check,
        )

    @Slot()
    def runStartupBackendCheck(self) -> None:
        """Wait for backend health once per app start without running heavy diagnostics."""
        if self._startup_backend_check_started:
            return
        self._startup_backend_check_started = True
        self.startStateSynchronization()
        self._set_startup_check_in_progress(True)
        self._diagnostic_checks = []
        self._diagnostic_summary = "Waiting for backend readiness..."
        self._diagnostic_raw_output = ""
        self._diagnostic_last_run = ""
        self.diagnosticsChanged.emit()
        self._run(
            "Startup backend health check",
            lambda: self._api.wait_until_ready(timeout=20.0),
            self._apply_startup_health_check,
            busy=False,
        )

    @Slot(bool)
    def setLaserReady(self, enabled: bool) -> None:
        self._run(
            "Laser arm" if enabled else "Laser disarm",
            lambda: self._api.arm_laser(enabled),
            lambda _: None,
        )

    @Slot(str, float)
    def setPower(self, channel: str, value: float) -> None:
        value = self._watts_to_percent(value)
        if channel == "p808":
            self._p808 = value
        elif channel == "p980":
            self._p980 = value
        elif channel == "p1064":
            self._p1064 = value
        else:
            return

        self.powerChanged.emit()
        self._settings_dirty = True
        self.targetChanged.emit()

    @Slot(int)
    def setPulseWidth(self, value: int) -> None:
        self._pulse_width = max(10, min(1000, int(value)))
        self.pulseWidthChanged.emit()
        self._settings_dirty = True
        self.targetChanged.emit()

    @Slot(bool)
    def setRedDot(self, enabled: bool) -> None:
        self._run("Red dot", lambda: self._api.set_red_dot(enabled), lambda _: self._apply_red_dot(enabled))

    @Slot(bool)
    def setVacuumEnabled(self, enabled: bool) -> None:
        self._run(
            "Vacuum",
            lambda: self._api.set_vacuum_enabled(enabled),
            lambda _: None,
        )

    @Slot(str)
    def setTreatmentMode(self, mode: str) -> None:
        if mode not in {"auto", "semi-auto", "manual"}:
            return
        api_mode = self._mode_to_api(mode)

        self._run(
            f"Mode {mode.upper()}",
            lambda: self._api.set_treatment_app_mode(api_mode),
            lambda _: None,
        )

    @Slot(float)
    def setConfidence(self, confidence: float) -> None:
        confidence = self._clamp_confidence(confidence)

        def task() -> float:
            self._api.set_detection_confidence(confidence)
            return confidence

        self._run("Detection confidence", task, self._apply_confidence)

    def _clamp_confidence(self, confidence: float) -> float:
        config = self._confidence_config
        clamped = max(config.minimum, min(config.maximum, float(confidence)))
        steps = round((clamped - config.minimum) / config.step)
        snapped = round(config.minimum + steps * config.step, 10)
        return max(config.minimum, min(config.maximum, snapped))

    @Slot()
    def captureAndLoadTargets(self) -> None:
        self.detectTargets()

    @Slot()
    def applyLaserSettings(self) -> None:
        self._run("Laser settings", self._apply_settings_task, lambda _: None)

    @Slot()
    def initializeTreatmentPage(self) -> None:
        self.startStateSynchronization()

    @Slot()
    def startTreatmentCameraStream(self) -> None:
        self.stopTreatmentCameraStream()

    @Slot()
    def stopTreatmentCameraStream(self) -> None:
        if self._treatment_stream_stop is not None:
            self._treatment_stream_stop.set()
        self._treatment_stream_stop = None
        self._treatment_stream_thread = None

    @Slot()
    def detectTargets(self) -> None:
        def task() -> Any:
            if self._settings_dirty:
                self._apply_settings_task()
            return self._api.treatment_app_detect()

        self._run("Detect targets", task, lambda _: None)

    @Slot()
    def fire(self) -> None:
        def task() -> Any:
            if self._settings_dirty:
                self._apply_settings_task()
            return self._api.treatment_app_fire()

        self._run("Fire", task, lambda _: None)

    @Slot()
    def nextTarget(self) -> None:
        def task() -> Any:
            if self._settings_dirty:
                self._apply_settings_task()
            return self._api.treatment_app_next()

        self._run("Next target", task, lambda _: None)

    @Slot()
    def stop(self) -> None:
        def task() -> Any:
            try:
                return self._api.stop_sequence()
            finally:
                self._api.clear_app_error()

        self._run("Stop sequence", task, lambda _: None)

    @Slot()
    def emergencyStop(self) -> None:
        self._run("Emergency stop", self._api.treatment_app_emergency_stop, lambda _: None)

    @Slot()
    def cleanupStates(self) -> None:
        self._run("Cleanup states", self._api.startup_clean_state, self._verify_cleanup_result)

    @Slot()
    def checkStates(self) -> None:
        self._run("Check states", self._api.treatment_app_status, self._apply_treatment_status, busy=False)

    @Slot()
    def toggleArm(self) -> None:
        if self._laser_ready is not None:
            self.setLaserReady(not self._laser_ready)

    @Slot()
    def toggleVacuum(self) -> None:
        if self._vacuum_enabled is not None:
            self.setVacuumEnabled(not self._vacuum_enabled)

    @Slot()
    def toggleDetection(self) -> None:
        enabled = not self._detection_enabled
        self._run(
            "Detection on" if enabled else "Detection off",
            lambda: self._api.set_detection_enabled(enabled),
            lambda _: None,
        )

    @Slot()
    def toggleOverlay(self) -> None:
        enabled = not self._overlay_enabled
        self._run(
            "Live overlay on" if enabled else "Live overlay off",
            lambda: self._api.set_live_overlay_enabled(enabled),
            lambda _: None,
        )

    @Slot()
    def queryLaserTemp(self) -> None:
        def task() -> str:
            try:
                data = self._api.sensor_values()
                values = data.get("values", {}) if isinstance(data, dict) else {}
                if "laserTemp_C" in values:
                    return f"{values['laserTemp_C']} C"
            except Exception:
                pass
            data = self._api.laser_temp()
            temp = data.get("temp", "-") if isinstance(data, dict) else "-"
            return f"{temp} C"

        self._run("Laser temp", task, self._apply_laser_temp, busy=False)

    def _push_laser_settings(self) -> None:
        self._run(
            "Laser settings",
            lambda: self._api.update_laser_settings(
                self._laser_ready,
                self._p808,
                self._p980,
                self._p1064,
                self._pulse_width,
            ),
            lambda _: None,
            busy=False,
        )

    def _apply_settings_task(self) -> Any:
        result = self._api.treatment_app_settings(
            self._p808,
            self._p980,
            self._p1064,
            self._pulse_width,
        )
        self._settings_dirty = False
        return result

    def _run_full_backend_check_task(self, skip_model_load: bool) -> Any:
        self._api.wait_until_ready(timeout=20.0)
        return self._api.full_app_check(skip_model_load)

    def _run(
        self,
        label: str,
        task: Callable[[], Any],
        on_success: Callable[[Any], None],
        busy: bool = True,
    ) -> None:
        quiet = label in {"Backend sync", "Calibration telemetry"}
        LOG.info(
            "queue task label=%s busy=%s quiet=%s screen=%s workers=%s",
            label,
            busy,
            quiet,
            self._screen,
            len(self._workers),
        ) if not quiet else LOG.debug(
            "queue task label=%s busy=%s quiet=%s screen=%s workers=%s",
            label,
            busy,
            quiet,
            self._screen,
            len(self._workers),
        )
        if busy:
            self._set_busy(True, label)
        if not quiet:
            self._set_status(f"{label}...")
        worker = ApiWorker(label, task, quiet=quiet)
        self._workers.append(worker)
        worker.signals.finished.connect(
            lambda result, worker=worker: self._taskFinished.emit(label, result, on_success, busy, worker)
        )
        worker.signals.failed.connect(
            lambda message, worker=worker: self._taskFailed.emit(label, message, busy, worker)
        )
        self._pool.start(worker)

    @Slot(str, object)
    def _handle_camera_frame_ready(self, url: str, worker: object) -> None:
        duration_ms = (time.monotonic() - self._camera_frame_started_at) * 1000 if self._camera_frame_started_at else 0.0
        self._camera_refresh_in_flight = False
        self._camera_last_error = ""
        self._camera_frame_count += 1
        self._release_worker(worker)
        self._camera_frame_url = url
        if duration_ms >= 1000 or self._camera_frame_count % 20 == 0:
            LOG.info("camera[%s] OK %.0fms url=%s", self._camera_frame_count, duration_ms, url)
        if duration_ms >= 3000:
            LOG.warning("camera[%s] SLOW %.0fms", self._camera_frame_count, duration_ms)
        self.cameraFrameUrlChanged.emit()

    @Slot(str, object)
    def _handle_camera_frame_failed(self, message: str, worker: object) -> None:
        duration_ms = (time.monotonic() - self._camera_frame_started_at) * 1000 if self._camera_frame_started_at else 0.0
        self._camera_refresh_in_flight = False
        self._release_worker(worker)
        LOG.warning("camera frame FAIL %.0fms: %s", duration_ms, message)
        if message != self._camera_last_error:
            self._camera_last_error = message
            self._set_status(f"Camera frame: {message}")

    @Slot(str, object, object, bool, object)
    def _handle_task_finished(
        self,
        label: str,
        result: Any,
        on_success: Callable[[Any], None],
        busy: bool,
        worker: object,
    ) -> None:
        LOG.debug("task callback start label=%s worker=%s", label, getattr(worker, "worker_id", "?"))
        on_success(result)
        LOG.debug("task callback applied label=%s worker=%s", label, getattr(worker, "worker_id", "?"))
        if label in {"Backend sync", "Startup backend health check"}:
            self._sync_backend_in_flight = False
            self._backend_sync_error = ""
            backend_changed = not self._backend_ok
            self._backend_ok = True
            if backend_changed:
                self.targetChanged.emit()
        if label == "Startup backend health check":
            self._set_startup_check_in_progress(False)
        quiet = label in {"Backend sync", "Calibration telemetry"}
        if not quiet:
            self._set_status(f"{label}: OK")
        if not quiet:
            self._append_log(f"{label}: OK")
        if label == "Calibration telemetry":
            self._calibration_telemetry_in_flight = False
        self._release_worker(worker)
        if busy:
            self._set_busy(False)
        LOG.debug("task callback done label=%s workers=%s", label, len(self._workers))

    @Slot(str, str, bool, object)
    def _handle_task_failed(self, label: str, message: str, busy: bool, worker: object) -> None:
        LOG.warning("task callback fail label=%s worker=%s message=%s", label, getattr(worker, "worker_id", "?"), message)
        if label == "Backend sync":
            self._sync_backend_in_flight = False
            if message != self._backend_sync_error:
                self._backend_sync_error = message
                self._set_status(message)
            backend_changed = self._backend_ok
            self._backend_ok = False
            if backend_changed:
                self.targetChanged.emit()
            self._release_worker(worker)
            if busy:
                self._set_busy(False)
            return
        if label == "Calibration telemetry":
            self._calibration_telemetry_in_flight = False
        self._set_status(message)
        if label != "Backend sync":
            self._append_log(f"{label}: {message}")
        if label == "Backend restart":
            self._backend_restart_output = message
            self.diagnosticsChanged.emit()
        elif label == "Full backend check":
            self._diagnostic_summary = f"Overall FAIL | {message}"
            self._diagnostic_raw_output = message
            self._diagnostic_last_run = time.strftime("%H:%M:%S")
            self.diagnosticsChanged.emit()
        elif label == "Startup backend health check":
            self._diagnostic_summary = f"Backend health check failed | {message}"
            self._diagnostic_raw_output = message
            self._diagnostic_last_run = time.strftime("%H:%M:%S")
            self._set_startup_check_in_progress(False)
            self.diagnosticsChanged.emit()
        self._error_title = label
        self._error_message = message
        self.errorChanged.emit()
        self._release_worker(worker)
        if busy:
            self._set_busy(False)
        # Keep the last verified snapshot on command failure. If the backend did
        # mutate state before failing, the state stream will still report it.

    def _release_worker(self, worker: object) -> None:
        try:
            self._workers.remove(worker)
        except ValueError:
            LOG.debug("Worker already released: %s", getattr(worker, "worker_id", "?"))

    @Slot()
    def logHeartbeat(self) -> None:
        in_flight = [
            f"{getattr(worker, 'worker_id', '?')}:{getattr(worker, 'label', '?')}"
            for worker in self._workers
        ]
        camera_age = (
            time.monotonic() - self._camera_frame_started_at
            if self._camera_refresh_in_flight and self._camera_frame_started_at
            else 0.0
        )
        LOG.info(
            "heartbeat screen=%s busy=%s workers=%s in_flight=%s camera_in_flight=%s camera_age=%.1fs frames=%s backend_ok=%s app_state=%s target_state=%s targets=%s skips(busy=%s,inflight=%s,interval=%s)",
            self._screen,
            self._busy,
            len(self._workers),
            ",".join(in_flight) if in_flight else "-",
            self._camera_refresh_in_flight,
            camera_age,
            self._camera_frame_count,
            self._backend_ok,
            self._app_state,
            self._target_state,
            self._loaded_target_count,
            self._camera_skip_busy_count,
            self._camera_skip_in_flight_count,
            self._camera_skip_interval_count,
        )

    def _log_camera_skips(self) -> None:
        now = time.monotonic()
        if now - self._last_camera_progress_log_at < 5:
            return
        LOG.info(
            "camera refresh skipped screen=%s busy=%s in_flight=%s skips(busy=%s,inflight=%s,interval=%s)",
            self._screen,
            self._busy,
            self._camera_refresh_in_flight,
            self._camera_skip_busy_count,
            self._camera_skip_in_flight_count,
            self._camera_skip_interval_count,
        )
        self._last_camera_progress_log_at = now

    @staticmethod
    def _is_supported_image(payload: bytes) -> bool:
        return (
            payload.startswith(b"\xff\xd8\xff")
            or payload.startswith(b"\x89PNG\r\n\x1a\n")
            or payload.startswith(b"BM")
        )

    def _set_status(self, status: str) -> None:
        if self._api_status == status:
            return
        self._api_status = status
        self.apiStatusChanged.emit()

    def _set_busy(self, busy: bool, label: str = "") -> None:
        self._busy = busy
        self._busy_label = label if busy else ""
        self.busyChanged.emit()

    def _set_startup_check_in_progress(self, in_progress: bool) -> None:
        if self._startup_check_in_progress == in_progress:
            return
        self._startup_check_in_progress = in_progress
        self.startupCheckChanged.emit()

    def _apply_backend_state(self, data: dict[str, Any]) -> None:
        state = data.get("state")
        if isinstance(state, dict):
            self._apply_treatment_status(state)
        health = data.get("health", {})
        if isinstance(health, dict):
            camera_ready = bool(health.get("camera_ready", False))
            camera_error = health.get("camera_error")
            if camera_ready:
                self._backend_camera_error = ""
            elif camera_error and camera_error != self._backend_camera_error:
                self._backend_camera_error = str(camera_error)
                self._append_log(f"Camera: {camera_error}")

    def _apply_startup_health_check(self, health: Any) -> None:
        health = health if isinstance(health, dict) else {}
        self._apply_backend_state({"health": health})

        checks: list[dict[str, str]] = [
            {"status": "OK", "name": "Backend API", "message": "Health endpoint reachable"}
        ]
        readiness_suffixes = ("_ready", "_connected", "_available", "_ok")

        def collect(prefix: str, value: Any) -> None:
            if not isinstance(value, dict):
                return
            for key, item in value.items():
                name = f"{prefix}.{key}" if prefix else str(key)
                if isinstance(item, dict):
                    collect(name, item)
                elif isinstance(item, bool) and str(key).lower().endswith(readiness_suffixes):
                    checks.append(
                        {
                            "status": "OK" if item else "FAIL",
                            "name": name.replace("_", " "),
                            "message": "Ready" if item else "Not ready",
                        }
                    )

        collect("", health)
        fail_count = sum(1 for check in checks if check["status"] == "FAIL")
        self._diagnostic_checks = checks
        self._diagnostic_summary = (
            f"Backend ready | {len(checks) - fail_count} checks OK"
            if fail_count == 0
            else f"Backend reachable | {fail_count} device/readiness checks failed"
        )
        self._diagnostic_raw_output = ""
        self._diagnostic_last_run = time.strftime("%H:%M:%S")
        self.diagnosticsChanged.emit()
        self.startStateSynchronization()

    @Slot()
    def startStateSynchronization(self) -> None:
        if self._state_stream_thread is not None and self._state_stream_thread.is_alive():
            return
        self._state_stream_stop.clear()

        def run() -> None:
            while not self._state_stream_stop.is_set():
                try:
                    initial = self._api.treatment_app_status()
                    if isinstance(initial, dict):
                        self._stateSnapshot.emit(initial)
                    self._api.stream_state(
                        self._state_stream_stop,
                        self._stateSnapshot.emit,
                        lambda: self._stateConnection.emit(True, ""),
                    )
                    if not self._state_stream_stop.is_set():
                        raise RuntimeError("State stream closed")
                except Exception as exc:
                    if self._state_stream_stop.is_set():
                        return
                    self._stateConnection.emit(False, str(exc))
                    self._state_stream_stop.wait(2.0)

        self._state_stream_thread = threading.Thread(
            target=run, name="backend-state-sse", daemon=True
        )
        self._state_stream_thread.start()

    @Slot()
    def stopStateSynchronization(self) -> None:
        self._state_stream_stop.set()

    @Slot(bool, str)
    def _apply_state_connection(self, connected: bool, message: str) -> None:
        changed = self._state_connected != connected
        self._state_connected = connected
        if connected:
            self._backend_ok = True
            self._backend_sync_error = ""
        elif message != self._backend_sync_error:
            self._backend_sync_error = message
            self._set_status(f"State updates disconnected: {message}")
        if changed:
            self.targetChanged.emit()

    def _apply_laser_ready(self, enabled: bool) -> None:
        self._laser_ready = enabled
        self.laserStateChanged.emit()

    def _apply_red_dot(self, enabled: bool) -> None:
        self._red_dot = enabled
        self.redDotChanged.emit()

    def _apply_vacuum_enabled(self, enabled: bool) -> None:
        self._vacuum_enabled = enabled
        self.vacuumChanged.emit()
        self.checkStates()

    def _apply_confidence(self, confidence: float) -> None:
        self._confidence = confidence
        self.targetChanged.emit()

    def _apply_loaded_targets(self, count: int) -> None:
        self._target = count > 0
        self._targeted_follicles = count
        self._loaded_target_count = count
        self.targetChanged.emit()

    def _apply_laser_temp(self, value: str) -> None:
        self._laser_temp = value
        self.targetChanged.emit()

    def _apply_calibration_status(self, data: Any) -> None:
        if not isinstance(data, dict):
            data = {}
        detection = data.get("detection", {})
        hsv = data.get("hsv", {})
        pos = data.get("pos", {})

        if isinstance(detection, dict):
            self._calibration_detection_enabled = bool(
                detection.get("detection_enabled", self._calibration_detection_enabled)
            )
            self._mask_overlay_enabled = bool(
                detection.get("mask_overlay_enabled", self._mask_overlay_enabled)
            )
            self._apply_hsv_status(detection)
        if isinstance(hsv, dict):
            self._apply_hsv_status(hsv)

        self._laser_ready = self._response_enabled(data.get("arm"), self._laser_ready)
        self._red_dot = self._response_enabled(data.get("red_dot"), self._red_dot)
        self._apply_galvo_position(pos)

        self.laserStateChanged.emit()
        self.redDotChanged.emit()
        self.calibrationChanged.emit()

    def _apply_calibration_telemetry(self, data: Any) -> None:
        if not isinstance(data, dict):
            return
        dot = data.get("dot", {})
        if isinstance(dot, dict) and dot.get("x") is not None and dot.get("y") is not None:
            self._dot_image_x = str(dot.get("x"))
            self._dot_image_y = str(dot.get("y"))
        elif "dot" in data:
            self._dot_image_x = "-"
            self._dot_image_y = "-"
        self._apply_galvo_position(data.get("pos", {}))
        self.calibrationChanged.emit()

    def _apply_calibration_detection(self, data: Any) -> None:
        if isinstance(data, dict):
            self._calibration_detection_enabled = bool(
                data.get("detection_enabled", self._calibration_detection_enabled)
            )
            self._red_dot = bool(data.get("red_dot", self._red_dot))
        self.redDotChanged.emit()
        self.calibrationChanged.emit()

    def _apply_mask_overlay(self, data: Any) -> None:
        if isinstance(data, dict):
            self._mask_overlay_enabled = bool(data.get("mask_overlay_enabled", self._mask_overlay_enabled))
        self.calibrationChanged.emit()

    def _apply_calibration_mode_disabled(self, data: Any) -> None:
        self._apply_unsafe_outputs_disabled()

    def _apply_unsafe_outputs_disabled(self) -> None:
        self._detection_enabled = False
        self._overlay_enabled = False
        self._mask_overlay_enabled = False
        self._calibration_detection_enabled = False
        self._red_dot = False
        self._laser_ready = False
        self._vacuum_enabled = False
        self.redDotChanged.emit()
        self.laserStateChanged.emit()
        self.vacuumChanged.emit()
        self.targetChanged.emit()
        self.calibrationChanged.emit()

    def _apply_treatment_entry_status(self, data: Any) -> None:
        self._apply_treatment_status(data)
        self._apply_unsafe_outputs_disabled()

    def _apply_hsv_status(self, data: Any) -> None:
        if not isinstance(data, dict):
            return
        self._set_hsv_array("_hsv_lower1", data.get("hsv_lower1"))
        self._set_hsv_array("_hsv_upper1", data.get("hsv_upper1"))
        self._set_hsv_array("_hsv_lower2", data.get("hsv_lower2"))
        self._set_hsv_array("_hsv_upper2", data.get("hsv_upper2"))
        self.calibrationChanged.emit()

    def _apply_galvo_move_result(self, data: Any) -> None:
        if isinstance(data, dict):
            if "new_position" in data:
                pos = data.get("new_position")
                if isinstance(pos, (list, tuple)) and len(pos) >= 2:
                    self._galvo_x = str(pos[0])
                    self._galvo_y = str(pos[1])
            elif "x" in data and "y" in data:
                self._galvo_x = str(data.get("x"))
                self._galvo_y = str(data.get("y"))
        self.calibrationChanged.emit()

    def _apply_calibration_start(self, data: Any) -> None:
        self._stored_count = 0
        self._homography_status = "collection started"
        self.calibrationChanged.emit()

    def _apply_calibration_store(self, data: Any) -> None:
        if isinstance(data, dict):
            self._stored_count = int(data.get("stored", self._stored_count) or 0)
            if data.get("error"):
                self._homography_status = str(data.get("error"))
        self.calibrationChanged.emit()

    def _apply_calibration_save(self, data: Any) -> None:
        if isinstance(data, dict):
            status = str(data.get("status", "-"))
            count = int(data.get("count", self._stored_count) or 0)
            self._stored_count = count
            if status == "saved":
                self._homography_status = f"saved ({count} points)"
            else:
                self._homography_status = f"{status} ({count} points)"
        self.calibrationChanged.emit()

    def _apply_homography_reload(self, data: Any) -> None:
        if isinstance(data, dict):
            self._homography_status = str(data.get("status", data.get("error", data)))
        else:
            self._homography_status = str(data)
        self.calibrationChanged.emit()

    def _apply_hsv_click(self, data: Any) -> None:
        if not isinstance(data, dict):
            return
        self._hsv_click_x = str(data.get("x", "-"))
        self._hsv_click_y = str(data.get("y", "-"))
        hsv = data.get("hsv")
        rgb = data.get("rgb")
        self._hsv_click_value = ", ".join(str(value) for value in hsv) if isinstance(hsv, list) else "-"
        self._rgb_click_value = ", ".join(str(value) for value in rgb) if isinstance(rgb, list) else "-"
        self.calibrationChanged.emit()

    def _apply_image_move(self, data: Any) -> None:
        if not isinstance(data, dict):
            self._move_result = "-"
            self.calibrationChanged.emit()
            return
        if data.get("error"):
            self._target_galvo_x = "-"
            self._target_galvo_y = "-"
            self._move_result = "homography not available"
        else:
            target = data.get("target")
            position = data.get("new_position")
            if isinstance(target, (list, tuple)) and len(target) >= 2:
                self._target_galvo_x = str(target[0])
                self._target_galvo_y = str(target[1])
            if isinstance(position, (list, tuple)) and len(position) >= 2:
                self._galvo_x = str(position[0])
                self._galvo_y = str(position[1])
                self._move_result = f"{position[0]}, {position[1]}"
            else:
                self._move_result = "OK"
        self.calibrationChanged.emit()

    def _apply_galvo_position(self, data: Any) -> None:
        if isinstance(data, dict):
            x = data.get("x")
            y = data.get("y")
            self._galvo_x = "ERR" if x is None else str(x)
            self._galvo_y = "ERR" if y is None else str(y)

    def _hsv_target(self, range_name: str, bound_name: str) -> list[int] | None:
        mapping = {
            ("1", "lower"): self._hsv_lower1,
            ("1", "upper"): self._hsv_upper1,
            ("2", "lower"): self._hsv_lower2,
            ("2", "upper"): self._hsv_upper2,
        }
        return mapping.get((str(range_name), str(bound_name)))

    def _hsv_payload(self) -> dict[str, int]:
        return {
            "lower1_h": self._hsv_lower1[0],
            "lower1_s": self._hsv_lower1[1],
            "lower1_v": self._hsv_lower1[2],
            "upper1_h": self._hsv_upper1[0],
            "upper1_s": self._hsv_upper1[1],
            "upper1_v": self._hsv_upper1[2],
            "lower2_h": self._hsv_lower2[0],
            "lower2_s": self._hsv_lower2[1],
            "lower2_v": self._hsv_lower2[2],
            "upper2_h": self._hsv_upper2[0],
            "upper2_s": self._hsv_upper2[1],
            "upper2_v": self._hsv_upper2[2],
        }

    def _set_hsv_array(self, attr: str, value: Any) -> None:
        if isinstance(value, (list, tuple)) and len(value) >= 3:
            setattr(self, attr, [int(value[0]), int(value[1]), int(value[2])])

    @staticmethod
    def _response_enabled(data: Any, fallback: bool) -> bool:
        if isinstance(data, dict):
            for key in ("armed", "enabled", "red_dot", "red_dot_enabled"):
                if key in data:
                    return bool(data.get(key))
            text = AppController._response_text(data.get("response"))
            if text:
                return "->1" in text or "[1]" in text or text.endswith(" 1")
        return fallback

    @staticmethod
    def _response_text(value: Any) -> str:
        if isinstance(value, list):
            return " | ".join(str(item) for item in value)
        if value is None:
            return ""
        return str(value)

    def _apply_backend_restart_output(self, output: str) -> None:
        self._backend_restart_output = output
        self.diagnosticsChanged.emit()

    def _apply_full_backend_check(self, data: Any) -> None:
        if not isinstance(data, dict):
            data = {}

        checks = data.get("checks", [])
        normalized_checks: list[dict[str, str]] = []
        if isinstance(checks, list):
            for check in checks:
                if not isinstance(check, dict):
                    continue
                normalized_checks.append(
                    {
                        "status": str(check.get("status", "-")),
                        "name": str(check.get("name", "-")),
                        "message": str(check.get("message", "")),
                    }
                )

        ok_count = sum(1 for check in normalized_checks if check["status"] == "OK")
        fail_count = sum(1 for check in normalized_checks if check["status"] == "FAIL")
        warn_count = sum(1 for check in normalized_checks if check["status"] == "WARN")
        duration_ms = round(float(data.get("duration_ms", 0) or 0))
        overall = "OK" if data.get("ok") else "FAIL"

        self._diagnostic_checks = normalized_checks
        self._diagnostic_summary = (
            f"Overall {overall} | OK {ok_count} | FAIL {fail_count} | "
            f"WARN {warn_count} | {duration_ms} ms"
        )
        self._diagnostic_raw_output = "\n".join(
            part
            for part in (str(data.get("stdout", "") or ""), str(data.get("stderr", "") or ""))
            if part
        )
        self._diagnostic_last_run = time.strftime("%H:%M:%S")
        self.diagnosticsChanged.emit()

    def _apply_cleanup_state(self, data: Any) -> None:
        if isinstance(data, dict) and data.get("mode"):
            self._treatment_mode = self._mode_from_api(str(data.get("mode")))

        self._laser_ready = False
        self._vacuum_enabled = False
        self._detection_enabled = False
        self._overlay_enabled = False
        self._target = False
        self._targeted_follicles = 0
        self._loaded_target_count = 0
        self._target_error_clear = True
        self._app_state = "CLEAN"
        self._target_state = "CLEAN"

        self.laserStateChanged.emit()
        self.vacuumChanged.emit()
        self.powerChanged.emit()
        self.pulseWidthChanged.emit()
        self.targetChanged.emit()

    def _verify_cleanup_result(self, data: Any) -> None:
        if not isinstance(data, dict) or data.get("ok") is not True:
            details = data.get("responses") if isinstance(data, dict) else data
            self._error_title = "Cleanup verification failed"
            self._error_message = f"Backend could not verify a safe reset. Details: {details}"
            self.errorChanged.emit()

    def _apply_treatment_status(self, data: Any, fallback_mode: str | None = None) -> None:
        if not isinstance(data, dict):
            return

        revision = data.get("revision")
        if isinstance(revision, int):
            if revision < self._state_revision:
                LOG.debug("Ignoring stale state revision=%s current=%s", revision, self._state_revision)
                return
            self._state_revision = revision

        mode = data.get("mode")
        if mode:
            self._treatment_mode = self._mode_from_api(str(mode))
        elif fallback_mode:
            self._treatment_mode = fallback_mode

        if "laser_armed" in data:
            self._laser_ready = self._nullable_bool(data.get("laser_armed"))
        vacuum = data.get("vacuum", {})
        if isinstance(vacuum, dict):
            if "vacuum_on" in vacuum:
                self._vacuum_enabled = self._nullable_bool(vacuum.get("vacuum_on"))
            if "check_vacuum_enabled" in vacuum:
                self._vacuum_lock = self._nullable_bool(vacuum.get("check_vacuum_enabled"))
        if "detection_enabled" in data:
            self._detection_enabled = self._nullable_bool(data.get("detection_enabled"))
        if "hair_detection_overlay_enabled" in data:
            self._overlay_enabled = self._nullable_bool(data.get("hair_detection_overlay_enabled"))
        if "target_error_clear" in data:
            self._target_error_clear = self._nullable_bool(data.get("target_error_clear"))
        if "app_state_running" in data:
            self._app_state_running = self._nullable_bool(data.get("app_state_running"))
        self._app_state = self._extract_payload(data.get("app_state", data.get("status", self._app_state)))
        self._target_state = self._extract_payload(data.get("target_state", self._target_state))

        target_value = data.get("loaded_targets", data.get("targets_count", self._loaded_target_count))
        target_count = -1 if target_value is None else int(target_value)
        if "manual_remaining" in data and self._treatment_mode == "manual":
            target_count = int(data.get("manual_remaining") or 0)
        self._target = target_count > 0
        self._targeted_follicles = target_count
        self._loaded_target_count = target_count

        if "detection_conf" in data:
            value = data.get("detection_conf")
            self._confidence = self._clamp_confidence(
                self._confidence if value is None else float(value)
            )

        power = data.get("laser_power", {})
        if isinstance(power, dict):
            self._p808 = max(0, min(100, int(power.get("p808", self._p808))))
            self._p980 = max(0, min(100, int(power.get("p980", self._p980))))
            self._p1064 = max(0, min(100, int(power.get("p1064", self._p1064))))

        if data.get("pulse_ms") is not None:
            self._pulse_width = max(10, min(1000, int(data.get("pulse_ms"))))

        if "targets_count" in data or "detected_count" in data:
            loaded = data.get("loaded_targets", data.get("targets_count", 0))
            detected = data.get("detected_count", "-")
            load_ms = data.get("load_ms")
            suffix = "" if load_ms is None else f", load {load_ms} ms"
            self._append_log(f"Targets loaded: {loaded}, detected: {detected}{suffix}")

        capture = data.get("capture")
        if isinstance(capture, dict) and capture.get("captured") == 0:
            self._append_log("Detect returned 0 image points")

        self.laserStateChanged.emit()
        self.vacuumChanged.emit()
        self.powerChanged.emit()
        self.pulseWidthChanged.emit()
        self.targetChanged.emit()

    @staticmethod
    def _nullable_bool(value: Any) -> bool | None:
        return value if isinstance(value, bool) else None

    @staticmethod
    def _format_boolean_state(value: bool | None, on_label: str, off_label: str) -> str:
        if value is True:
            return on_label
        if value is False:
            return off_label
        return "UNKNOWN"

    def _append_log(self, message: str) -> None:
        stamp = time.strftime("%H:%M:%S")
        self._treatment_log = f"[{stamp}] {message}\n{self._treatment_log}".strip()
        lines = self._treatment_log.splitlines()
        self._treatment_log = "\n".join(lines[:12])
        self.targetChanged.emit()

    @staticmethod
    def _extract_payload(value: Any) -> str:
        if isinstance(value, list):
            value = " ".join(str(item) for item in value)
        elif value is None:
            return "-"
        elif isinstance(value, dict):
            return str(value)
        else:
            value = str(value)

        marker = "->["
        start = value.find(marker)
        if start < 0:
            return value or "-"
        start += len(marker)
        end = value.find("]", start)
        return value[start:end] if end >= 0 else value[start:]

    @staticmethod
    def _mode_from_api(mode: str) -> str:
        return "semi-auto" if mode == "semi_auto" else mode

    @staticmethod
    def _mode_to_api(mode: str) -> str:
        return "semi_auto" if mode == "semi-auto" else mode

    @staticmethod
    def _is_ok_state(value: str) -> bool:
        return str(value).strip().upper() == "OK"

    @staticmethod
    def _percent_to_watts(percent: int | float) -> float:
        return round(max(0.0, min(100.0, float(percent))) * 15.0 / 100.0, 1)

    @staticmethod
    def _watts_to_percent(watts: int | float) -> int:
        return round(max(0.0, min(15.0, float(watts))) * 100.0 / 15.0)
