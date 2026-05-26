from __future__ import annotations

import json
import os
import urllib.error
import urllib.parse
import urllib.request
from dataclasses import dataclass
from typing import Any


DEFAULT_API_BASE_URL = "http://127.0.0.1:8000"


class ApiError(RuntimeError):
    pass


@dataclass
class ApiClient:
    base_url: str = os.environ.get("FITPRO_API_BASE_URL", DEFAULT_API_BASE_URL)
    timeout: float = 4.0

    def __post_init__(self) -> None:
        self.base_url = self.base_url.rstrip("/")

    def frame_url(self, cache_bust: int | None = None) -> str:
        query = "" if cache_bust is None else f"?t={cache_bust}"
        return f"{self.base_url}/frame/current{query}"

    def get(self, path: str, query: dict[str, Any] | None = None) -> Any:
        return self._request("GET", path, query=query)

    def post(self, path: str, query: dict[str, Any] | None = None) -> Any:
        return self._request("POST", path, query=query)

    def post_json(self, path: str, body: dict[str, Any]) -> Any:
        return self._request("POST", path, body=body)

    def _request(
        self,
        method: str,
        path: str,
        query: dict[str, Any] | None = None,
        body: dict[str, Any] | None = None,
    ) -> Any:
        url = self._build_url(path, query)
        data = None
        headers: dict[str, str] = {}

        if body is not None:
            data = json.dumps(body).encode("utf-8")
            headers["Content-Type"] = "application/json"

        request = urllib.request.Request(url, data=data, headers=headers, method=method)

        try:
            with urllib.request.urlopen(request, timeout=self.timeout) as response:
                payload = response.read()
        except urllib.error.HTTPError as exc:
            message = exc.reason
            try:
                error_payload = json.loads(exc.read().decode("utf-8"))
                message = error_payload.get("error") or error_payload.get("detail") or message
            except Exception:
                pass
            raise ApiError(str(message)) from exc
        except urllib.error.URLError as exc:
            raise ApiError(str(exc.reason)) from exc

        if not payload:
            return {}

        try:
            return json.loads(payload.decode("utf-8"))
        except json.JSONDecodeError as exc:
            raise ApiError("Invalid JSON response from backend") from exc

    def _build_url(self, path: str, query: dict[str, Any] | None = None) -> str:
        encoded_query = urllib.parse.urlencode(query or {})
        suffix = f"?{encoded_query}" if encoded_query else ""
        return f"{self.base_url}{path}{suffix}"

    def health(self) -> Any:
        return self.get("/health")

    def stats(self) -> Any:
        return self.get("/stats")

    def detection_status(self) -> Any:
        return self.get("/detection/status")

    def laser_settings(self) -> Any:
        return self.get("/laser/settings")

    def sensor_values(self) -> Any:
        return self.get("/sensors/values")

    def sequence_status(self) -> Any:
        return self.get("/seq/status")

    def set_detection_enabled(self, enabled: bool) -> Any:
        return self.post("/detection/toggle", {"enabled": enabled})

    def set_detection_confidence(self, confidence: float) -> Any:
        return self.post("/detection/conf", {"conf": confidence})

    def capture_detections(self) -> Any:
        return self.post("/detection/capture")

    def clear_points(self) -> Any:
        return self.post("/points/clear")

    def update_targets(self) -> Any:
        return self.post("/seq/update_targets")

    def clear_targets(self) -> Any:
        return self.post("/seq/clear_targets")

    def show_targets(self, enabled: bool) -> Any:
        return self.post("/seq/show_targets", {"enabled": enabled})

    def set_sequence_mode(self, mode: str) -> Any:
        backend_mode = "manual" if mode == "manual" else "auto"
        return self.post("/seq/mode", {"mode": backend_mode})

    def start_sequence(self) -> Any:
        return self.post("/seq/start")

    def step_sequence(self) -> Any:
        return self.post("/seq/step")

    def stop_sequence(self) -> Any:
        return self.post("/seq/stop")

    def clear_app_error(self) -> Any:
        return self.post("/app/clear_error")

    def arm_laser(self, enabled: bool) -> Any:
        return self.post("/laser/arm" if enabled else "/laser/disarm")

    def update_laser_settings(
        self,
        armed: bool,
        p808: int,
        p980: int,
        p1064: int,
        pulse_ms: int,
        reload_targets: bool = False,
    ) -> Any:
        return self.post_json(
            "/laser/settings",
            {
                "armed": armed,
                "p808": p808,
                "p980": p980,
                "p1064": p1064,
                "pulse_ms": pulse_ms,
                "reload_targets": reload_targets,
            },
        )

    def set_red_dot(self, enabled: bool) -> Any:
        return self.post("/laser/red_dot", {"enabled": enabled})

    def fire_laser(self, duration_ms: int) -> Any:
        return self.post("/laser/fire", {"duration_ms": duration_ms})

    def set_vacuum_enabled(self, enabled: bool) -> Any:
        return self.post_json(
            "/app/raw_command",
            {"command": f"APP_SET_VACUUM_EN {1 if enabled else 0}"},
        )

    def set_vacuum_check_enabled(self, enabled: bool) -> Any:
        return self.post_json(
            "/app/raw_command",
            {"command": f"APP_SET_CHECK_VACUUM {1 if enabled else 0}"},
        )
