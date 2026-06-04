from __future__ import annotations

import os
import tempfile
import threading
import time
from collections.abc import Callable
from pathlib import Path
from typing import Any

from PySide6.QtCore import QObject, Property, QRunnable, QThreadPool, Signal, Slot

from api_client import ApiClient


class WorkerSignals(QObject):
    finished = Signal(object)
    failed = Signal(str)


class ApiWorker(QRunnable):
    def __init__(self, task: Callable[[], Any]) -> None:
        super().__init__()
        self.task = task
        self.signals = WorkerSignals()

    def run(self) -> None:
        try:
            self.signals.finished.emit(self.task())
        except Exception as exc:
            self.signals.failed.emit(str(exc))


class AppController(QObject):
    screenChanged = Signal()
    apiStatusChanged = Signal()
    busyChanged = Signal()
    laserStateChanged = Signal()
    powerChanged = Signal()
    pulseWidthChanged = Signal()
    redDotChanged = Signal()
    vacuumChanged = Signal()
    targetChanged = Signal()
    cameraFrameUrlChanged = Signal()
    errorChanged = Signal()
    _cameraFrameReady = Signal(str, object)
    _cameraFrameFailed = Signal(str, object)
    _taskFinished = Signal(str, object, object, bool, object)
    _taskFailed = Signal(str, str, bool, object)
    _streamLog = Signal(str)

    def __init__(self, api: ApiClient | None = None) -> None:
        super().__init__()
        self._api = api or ApiClient()
        self._pool = QThreadPool.globalInstance()
        self._workers: list[ApiWorker] = []

        self._screen = "start"
        self._api_status = "Backend: checking"
        self._busy = False
        self._laser_ready = False
        self._p808 = 20
        self._p980 = 25
        self._p1064 = 50
        self._pulse_width = 50
        self._red_dot = False
        self._vacuum_enabled = False
        self._vacuum_lock = False
        self._target = False
        self._targeted_follicles = 0
        self._loaded_target_count = 0
        self._confidence = 0.1
        self._treatment_mode = "semi-auto"
        self._detection_enabled = False
        self._overlay_enabled = False
        self._app_state = "-"
        self._target_state = "-"
        self._target_error_clear = True
        self._app_state_running = False
        self._laser_temp = "-"
        self._settings_dirty = True
        self._treatment_log = ""
        self._camera_frame_dir = Path(tempfile.gettempdir()) / "fitpro-ultima-laser"
        self._camera_frame_dir.mkdir(parents=True, exist_ok=True)
        self._camera_frame_slot = 0
        self._camera_refresh_in_flight = False
        self._camera_frame_url = ""
        self._treatment_stream_stop: threading.Event | None = None
        self._treatment_stream_thread: threading.Thread | None = None
        self._error_title = ""
        self._error_message = ""

        self._cameraFrameReady.connect(self._handle_camera_frame_ready)
        self._cameraFrameFailed.connect(self._handle_camera_frame_failed)
        self._taskFinished.connect(self._handle_task_finished)
        self._taskFailed.connect(self._handle_task_failed)
        self._streamLog.connect(self._append_log)

    @Property(str, notify=screenChanged)
    def screen(self) -> str:
        return self._screen

    @Property(str, notify=apiStatusChanged)
    def apiStatus(self) -> str:
        return self._api_status

    @Property(bool, notify=busyChanged)
    def busy(self) -> bool:
        return self._busy

    @Property(bool, notify=laserStateChanged)
    def laserReady(self) -> bool:
        return self._laser_ready

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
        return self._vacuum_enabled

    @Property(bool, notify=vacuumChanged)
    def vacuumLock(self) -> bool:
        return self._vacuum_lock

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

    @Property(str, notify=targetChanged)
    def treatmentMode(self) -> str:
        return self._treatment_mode

    @Property(bool, notify=targetChanged)
    def detectionEnabled(self) -> bool:
        return self._detection_enabled

    @Property(bool, notify=targetChanged)
    def overlayEnabled(self) -> bool:
        return self._overlay_enabled

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
        return self._app_state_running

    @Property(str, notify=targetChanged)
    def laserTemp(self) -> str:
        return self._laser_temp

    @Property(bool, notify=targetChanged)
    def settingsDirty(self) -> bool:
        return self._settings_dirty

    @Property(str, notify=targetChanged)
    def treatmentLog(self) -> str:
        return self._treatment_log

    @Property(str, notify=targetChanged)
    def treatmentLogHead(self) -> str:
        return self._treatment_log.splitlines()[0] if self._treatment_log else ""

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

    @Slot(str)
    def navigate(self, screen: str) -> None:
        if self._screen == screen:
            return
        if self._screen == "laser-treatment" and screen != "laser-treatment":
            self.stopTreatmentCameraStream()
        self._screen = screen
        self.screenChanged.emit()
        if screen == "laser-treatment":
            self.syncBackend()

    @Slot()
    def clearError(self) -> None:
        self._error_title = ""
        self._error_message = ""
        self.errorChanged.emit()

    @Slot()
    def refreshCameraFrame(self) -> None:
        if self._busy:
            return
        if self._camera_refresh_in_flight:
            return

        self._camera_refresh_in_flight = True

        def task() -> str:
            timestamp = int(time.time() * 1000)
            if self._overlay_enabled or self._loaded_target_count > 0:
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

        worker = ApiWorker(task)
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
        def task() -> dict[str, Any]:
            health = self._api.health()
            return {
                "health": health,
            }

        self._run("Backend sync", task, self._apply_backend_state, busy=False)

    @Slot(bool)
    def setLaserReady(self, enabled: bool) -> None:
        def task() -> bool:
            self._api.arm_laser(enabled)
            return enabled

        self._run("Laser arm" if enabled else "Laser disarm", task, self._apply_laser_ready)

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
            lambda _: self._apply_vacuum_enabled(enabled),
        )

    @Slot(str)
    def setTreatmentMode(self, mode: str) -> None:
        if mode not in {"auto", "semi-auto", "manual"}:
            return
        api_mode = self._mode_to_api(mode)

        def task() -> Any:
            self._api.set_treatment_app_mode(api_mode)
            return self._api.treatment_app_status()

        self._run(
            f"Mode {mode.upper()}",
            task,
            lambda result: self._apply_treatment_status(result, fallback_mode=mode),
        )

    @Slot(float)
    def setConfidence(self, confidence: float) -> None:
        confidence = max(0.01, min(1.0, float(confidence)))

        def task() -> float:
            self._api.set_detection_confidence(confidence)
            return confidence

        self._run("Detection confidence", task, self._apply_confidence)

    @Slot()
    def captureAndLoadTargets(self) -> None:
        self.detectTargets()

    @Slot()
    def applyLaserSettings(self) -> None:
        self._run("Laser settings", self._apply_settings_task, self._apply_treatment_status)

    @Slot()
    def initializeTreatmentPage(self) -> None:
        self.startTreatmentCameraStream()

        def task() -> Any:
            self._api.startup_clean_state()
            self._api.set_treatment_app_mode("semi_auto")
            return self._api.treatment_app_status()

        self._run("Treatment init", task, self._apply_treatment_status)

    @Slot()
    def startTreatmentCameraStream(self) -> None:
        if self._treatment_stream_thread is not None and self._treatment_stream_thread.is_alive():
            return

        stop_event = threading.Event()
        self._treatment_stream_stop = stop_event

        def stream_task() -> None:
            while not stop_event.is_set():
                try:
                    self._api.keep_current_frame_stream_alive(stop_event)
                except Exception as exc:
                    if not stop_event.is_set():
                        self._streamLog.emit(f"Camera stream: {exc}")
                        time.sleep(2.5)

        self._treatment_stream_thread = threading.Thread(
            target=stream_task,
            name="fitpro-treatment-camera-stream",
            daemon=True,
        )
        self._treatment_stream_thread.start()

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
            data = self._api.treatment_app_detect()
            return self._status_with_result(data)

        self._run("Detect targets", task, self._apply_treatment_status)

    @Slot()
    def fire(self) -> None:
        def task() -> Any:
            if self._settings_dirty:
                self._apply_settings_task()
            data = self._api.treatment_app_fire()
            return self._status_with_result(data)

        self._run("Fire", task, self._apply_treatment_status)

    @Slot()
    def nextTarget(self) -> None:
        def task() -> Any:
            if self._settings_dirty:
                self._apply_settings_task()
            data = self._api.treatment_app_next()
            return self._status_with_result(data)

        self._run("Next target", task, self._apply_treatment_status)

    @Slot()
    def stop(self) -> None:
        def task() -> Any:
            try:
                return self._api.stop_sequence()
            finally:
                self._api.clear_app_error()

        self._run("Stop sequence", task, lambda _: self.syncBackend())

    @Slot()
    def emergencyStop(self) -> None:
        def task() -> Any:
            data = self._api.treatment_app_emergency_stop()
            return self._status_with_result(data)

        self._run("Emergency stop", task, self._apply_treatment_status)

    @Slot()
    def cleanupStates(self) -> None:
        def task() -> Any:
            self._api.startup_clean_state()
            return self._api.treatment_app_status()

        self._run("Cleanup states", task, self._apply_treatment_status)

    @Slot()
    def checkStates(self) -> None:
        self._run("Check states", self._api.treatment_app_status, self._apply_treatment_status, busy=False)

    @Slot()
    def toggleArm(self) -> None:
        self.setLaserReady(not self._laser_ready)

    @Slot()
    def toggleVacuum(self) -> None:
        self.setVacuumEnabled(not self._vacuum_enabled)

    @Slot()
    def toggleDetection(self) -> None:
        enabled = not self._detection_enabled
        self._run(
            "Detection on" if enabled else "Detection off",
            lambda: self._api.set_detection_enabled(enabled),
            lambda _: self.checkStates(),
        )

    @Slot()
    def toggleOverlay(self) -> None:
        enabled = not self._overlay_enabled
        self._run(
            "Live overlay on" if enabled else "Live overlay off",
            lambda: self._api.set_live_overlay_enabled(enabled),
            lambda _: self.checkStates(),
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
        return self._status_with_result(result)

    def _status_with_result(self, data: Any) -> dict[str, Any]:
        status = self._api.treatment_app_status()
        if isinstance(status, dict) and isinstance(data, dict):
            status.update(data)
        return status if isinstance(status, dict) else {}

    def _run(
        self,
        label: str,
        task: Callable[[], Any],
        on_success: Callable[[Any], None],
        busy: bool = True,
    ) -> None:
        if busy:
            self._set_busy(True)
        self._set_status(f"{label}...")
        worker = ApiWorker(task)
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
        self._camera_refresh_in_flight = False
        self._release_worker(worker)
        self._camera_frame_url = url
        self.cameraFrameUrlChanged.emit()

    @Slot(str, object)
    def _handle_camera_frame_failed(self, message: str, worker: object) -> None:
        self._camera_refresh_in_flight = False
        self._release_worker(worker)
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
        on_success(result)
        self._set_status(f"{label}: OK")
        self._append_log(f"{label}: OK")
        self._release_worker(worker)
        if busy:
            self._set_busy(False)

    @Slot(str, str, bool, object)
    def _handle_task_failed(self, label: str, message: str, busy: bool, worker: object) -> None:
        self._set_status(message)
        self._append_log(f"{label}: {message}")
        self._error_title = label
        self._error_message = message
        self.errorChanged.emit()
        self._release_worker(worker)
        if busy:
            self._set_busy(False)
        if label in {"Detect targets", "Fire", "Next target", "Cleanup states", "Emergency stop"}:
            self.checkStates()

    def _release_worker(self, worker: object) -> None:
        try:
            self._workers.remove(worker)
        except ValueError:
            pass

    @staticmethod
    def _is_supported_image(payload: bytes) -> bool:
        return (
            payload.startswith(b"\xff\xd8\xff")
            or payload.startswith(b"\x89PNG\r\n\x1a\n")
            or payload.startswith(b"BM")
        )

    def _set_status(self, status: str) -> None:
        self._api_status = status
        self.apiStatusChanged.emit()

    def _set_busy(self, busy: bool) -> None:
        self._busy = busy
        self.busyChanged.emit()

    def _apply_backend_state(self, data: dict[str, Any]) -> None:
        health = data.get("health", {})
        if isinstance(health, dict):
            camera_ready = bool(health.get("camera_ready", False))
            camera_error = health.get("camera_error")
            if not camera_ready and camera_error:
                self._append_log(f"Camera: {camera_error}")
        self.laserStateChanged.emit()
        self.vacuumChanged.emit()
        self.powerChanged.emit()
        self.pulseWidthChanged.emit()
        self.redDotChanged.emit()
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

    def _apply_treatment_status(self, data: Any, fallback_mode: str | None = None) -> None:
        if not isinstance(data, dict):
            data = {}

        mode = data.get("mode")
        if mode:
            self._treatment_mode = self._mode_from_api(str(mode))
        elif fallback_mode:
            self._treatment_mode = fallback_mode

        self._laser_ready = bool(data.get("laser_armed", self._laser_ready))
        vacuum = data.get("vacuum", {})
        if isinstance(vacuum, dict):
            self._vacuum_enabled = bool(vacuum.get("vacuum_on", self._vacuum_enabled))
        self._detection_enabled = bool(data.get("detection_enabled", self._detection_enabled))
        self._overlay_enabled = bool(
            data.get("hair_detection_overlay_enabled", self._overlay_enabled)
        )
        self._target_error_clear = bool(data.get("target_error_clear", self._target_error_clear))
        self._app_state_running = bool(data.get("app_state_running", self._app_state_running))
        self._app_state = self._extract_payload(data.get("app_state", data.get("status", self._app_state)))
        self._target_state = self._extract_payload(data.get("target_state", self._target_state))

        target_count = int(data.get("loaded_targets", data.get("targets_count", self._loaded_target_count)) or 0)
        if "manual_remaining" in data and self._treatment_mode == "manual":
            target_count = int(data.get("manual_remaining") or 0)
        self._target = target_count > 0
        self._targeted_follicles = target_count
        self._loaded_target_count = target_count

        if "detection_conf" in data:
            self._confidence = max(0.01, min(1.0, float(data.get("detection_conf") or self._confidence)))

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
    def _percent_to_watts(percent: int | float) -> float:
        return round(max(0.0, min(100.0, float(percent))) * 15.0 / 100.0, 1)

    @staticmethod
    def _watts_to_percent(watts: int | float) -> int:
        return round(max(0.0, min(15.0, float(watts))) * 100.0 / 15.0)
