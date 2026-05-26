from __future__ import annotations

import time
from collections.abc import Callable
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
    _taskFinished = Signal(str, object, object, bool)
    _taskFailed = Signal(str, str, bool)

    def __init__(self, api: ApiClient | None = None) -> None:
        super().__init__()
        self._api = api or ApiClient()
        self._pool = QThreadPool.globalInstance()

        self._screen = "start"
        self._api_status = "Backend: checking"
        self._busy = False
        self._laser_ready = False
        self._p808 = 12
        self._p980 = 12
        self._p1064 = 12
        self._pulse_width = 80
        self._red_dot = False
        self._vacuum_enabled = False
        self._vacuum_lock = False
        self._target = False
        self._targeted_follicles = 0
        self._loaded_target_count = 0
        self._confidence = 0.1
        self._treatment_mode = "semi-auto"
        self._camera_frame_url = self._api.frame_url(int(time.time() * 1000))
        self._error_title = ""
        self._error_message = ""

        self._taskFinished.connect(self._handle_task_finished)
        self._taskFailed.connect(self._handle_task_failed)

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

    @Property(int, notify=powerChanged)
    def totalPower(self) -> int:
        return self._p808 + self._p980 + self._p1064

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

    @Property(str, notify=cameraFrameUrlChanged)
    def cameraFrameUrl(self) -> str:
        return self._camera_frame_url

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
        self._camera_frame_url = self._api.frame_url(int(time.time() * 1000))
        self.cameraFrameUrlChanged.emit()

    @Slot()
    def syncBackend(self) -> None:
        def task() -> dict[str, Any]:
            health = self._api.health()
            laser = self._api.laser_settings()
            detection = self._api.detection_status()
            stats = self._api.stats()
            return {
                "health": health,
                "laser": laser,
                "detection": detection,
                "stats": stats,
            }

        self._run("Backend sync", task, self._apply_backend_state, busy=False)

    @Slot(bool)
    def setLaserReady(self, enabled: bool) -> None:
        def task() -> bool:
            self._api.arm_laser(enabled)
            self._api.update_laser_settings(
                enabled,
                self._p808,
                self._p980,
                self._p1064,
                self._pulse_width,
            )
            return enabled

        self._run("Laser arm" if enabled else "Laser disarm", task, self._apply_laser_ready)

    @Slot(str, int)
    def setPower(self, channel: str, value: int) -> None:
        value = max(0, min(100, int(value)))
        if channel == "p808":
            self._p808 = value
        elif channel == "p980":
            self._p980 = value
        elif channel == "p1064":
            self._p1064 = value
        else:
            return

        self.powerChanged.emit()
        self._push_laser_settings()

    @Slot(int)
    def setPulseWidth(self, value: int) -> None:
        self._pulse_width = max(1, min(1000, int(value)))
        self.pulseWidthChanged.emit()
        self._push_laser_settings()

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
        self._treatment_mode = mode
        self.targetChanged.emit()

    @Slot(float)
    def setConfidence(self, confidence: float) -> None:
        confidence = max(0.01, min(1.0, float(confidence)))

        def task() -> float:
            self._api.set_detection_confidence(confidence)
            return confidence

        self._run("Detection confidence", task, self._apply_confidence)

    @Slot()
    def captureAndLoadTargets(self) -> None:
        def task() -> int:
            self._api.clear_targets()
            self._api.clear_points()
            self._api.show_targets(False)
            capture = self._api.capture_detections()
            captured = int(capture.get("captured", 0))
            if captured <= 0:
                return 0
            targets = self._api.update_targets()
            self._api.show_targets(True)
            return int(targets.get("targets_count", captured))

        self._run("Capture targets", task, self._apply_loaded_targets)

    @Slot()
    def fire(self) -> None:
        def task() -> Any:
            self._api.set_sequence_mode(self._treatment_mode)
            if self._treatment_mode == "manual":
                return self._api.step_sequence()
            return self._api.start_sequence()

        self._run("Fire sequence", task, lambda _: self.syncBackend())

    @Slot()
    def stop(self) -> None:
        def task() -> Any:
            try:
                return self._api.stop_sequence()
            finally:
                self._api.clear_app_error()

        self._run("Stop sequence", task, lambda _: self.syncBackend())

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
        worker.signals.finished.connect(
            lambda result: self._taskFinished.emit(label, result, on_success, busy)
        )
        worker.signals.failed.connect(
            lambda message: self._taskFailed.emit(label, message, busy)
        )
        self._pool.start(worker)

    @Slot(str, object, object, bool)
    def _handle_task_finished(
        self,
        label: str,
        result: Any,
        on_success: Callable[[Any], None],
        busy: bool,
    ) -> None:
        on_success(result)
        self._set_status(f"{label}: OK")
        if busy:
            self._set_busy(False)

    @Slot(str, str, bool)
    def _handle_task_failed(self, label: str, message: str, busy: bool) -> None:
        self._set_status(message)
        self._error_title = label
        self._error_message = message
        self.errorChanged.emit()
        if busy:
            self._set_busy(False)

    def _set_status(self, status: str) -> None:
        self._api_status = status
        self.apiStatusChanged.emit()

    def _set_busy(self, busy: bool) -> None:
        self._busy = busy
        self.busyChanged.emit()

    def _apply_backend_state(self, data: dict[str, Any]) -> None:
        laser = data["laser"]
        detection = data["detection"]
        stats = data["stats"]

        power = laser.get("power", {})
        self._laser_ready = bool(laser.get("armed", False))
        self._p808 = int(power.get("p808", self._p808))
        self._p980 = int(power.get("p980", self._p980))
        self._p1064 = int(power.get("p1064", self._p1064))
        self._pulse_width = int(laser.get("pulse_ms", self._pulse_width))
        self._confidence = float(detection.get("conf", self._confidence))
        self._red_dot = bool(detection.get("red_dot") or stats.get("red_dot_enabled", False))
        target_count = int(
            laser.get("targets_count")
            or stats.get("detected_points")
            or stats.get("detection_count")
            or 0
        )
        self._target = target_count > 0
        self._targeted_follicles = target_count
        self._loaded_target_count = int(laser.get("targets_count") or 0)

        self.laserStateChanged.emit()
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

    def _apply_confidence(self, confidence: float) -> None:
        self._confidence = confidence
        self.targetChanged.emit()

    def _apply_loaded_targets(self, count: int) -> None:
        self._target = count > 0
        self._targeted_follicles = count
        self._loaded_target_count = count
        self.targetChanged.emit()
