from __future__ import annotations

import json
import os
import threading
import time
import urllib.error
import urllib.parse
import urllib.request
from dataclasses import dataclass
from typing import Any


DEFAULT_API_BASE_URL = "http://127.0.0.1:8000/api"


class ApiError(RuntimeError):
    pass


@dataclass
class ApiClient:
    base_url: str = os.environ.get("FITPRO_API_BASE_URL", DEFAULT_API_BASE_URL)
    timeout: float = 4.0
    slow_timeout: float = 90.0

    def __post_init__(self) -> None:
        self.base_url = self._normalize_base_url(self.base_url)

    def frame_url(self, cache_bust: int | None = None) -> str:
        query = "" if cache_bust is None else f"?t={cache_bust}"
        return f"{self.base_url}/frame/snapshot{query}"

    def current_frame_url(self, cache_bust: int | None = None) -> str:
        query = "" if cache_bust is None else f"?t={cache_bust}"
        return f"{self.base_url}/frame/current{query}"

    def get(
        self,
        path: str,
        query: dict[str, Any] | None = None,
        timeout: float | None = None,
    ) -> Any:
        return self._request("GET", path, query=query, timeout=timeout)

    def post(
        self,
        path: str,
        query: dict[str, Any] | None = None,
        timeout: float | None = None,
    ) -> Any:
        return self._request("POST", path, query=query, timeout=timeout)

    def post_json(self, path: str, body: dict[str, Any], timeout: float | None = None) -> Any:
        return self._request("POST", path, body=body, timeout=timeout)

    def get_bytes(
        self,
        path: str,
        query: dict[str, Any] | None = None,
        timeout: float | None = None,
    ) -> bytes:
        last_error: Exception | None = None
        request_timeout = self.timeout if timeout is None else timeout
        for url in self._candidate_urls(path, query):
            request = urllib.request.Request(url, method="GET")
            try:
                with urllib.request.urlopen(request, timeout=request_timeout) as response:
                    self._remember_working_base(url)
                    return response.read()
            except urllib.error.HTTPError as exc:
                last_error = exc
                if exc.code != 404:
                    raise self._api_error_from_http(exc)
            except urllib.error.URLError as exc:
                raise self._api_error_from_exception(exc)

        raise self._api_error_from_exception(last_error)

    def _request(
        self,
        method: str,
        path: str,
        query: dict[str, Any] | None = None,
        body: dict[str, Any] | None = None,
        timeout: float | None = None,
    ) -> Any:
        data = None
        headers: dict[str, str] = {}

        if body is not None:
            data = json.dumps(body).encode("utf-8")
            headers["Content-Type"] = "application/json"

        last_error: Exception | None = None
        payload = b""
        request_timeout = self.timeout if timeout is None else timeout
        for url in self._candidate_urls(path, query):
            request = urllib.request.Request(url, data=data, headers=headers, method=method)
            try:
                with urllib.request.urlopen(request, timeout=request_timeout) as response:
                    self._remember_working_base(url)
                    payload = response.read()
                    break
            except urllib.error.HTTPError as exc:
                last_error = exc
                if exc.code != 404:
                    raise self._api_error_from_http(exc)
            except urllib.error.URLError as exc:
                raise self._api_error_from_exception(exc)
        else:
            raise self._api_error_from_exception(last_error)

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

    def _candidate_urls(self, path: str, query: dict[str, Any] | None = None) -> list[str]:
        bases = [self.base_url]
        parsed = urllib.parse.urlparse(self.base_url)
        if parsed.path.rstrip("/") == "/api":
            root_base = urllib.parse.urlunparse(parsed._replace(path="", params="", query="", fragment="")).rstrip("/")
            bases.append(root_base)

        seen: set[str] = set()
        urls: list[str] = []
        encoded_query = urllib.parse.urlencode(query or {})
        suffix = f"?{encoded_query}" if encoded_query else ""
        for base in bases:
            url = f"{base}{path}{suffix}"
            if url not in seen:
                seen.add(url)
                urls.append(url)
        return urls

    def _remember_working_base(self, url: str) -> None:
        parsed_url = urllib.parse.urlparse(url)
        parsed_base = urllib.parse.urlparse(self.base_url)
        if parsed_base.path.rstrip("/") == "/api" and not parsed_url.path.startswith("/api/"):
            self.base_url = urllib.parse.urlunparse(
                parsed_base._replace(path="", params="", query="", fragment="")
            ).rstrip("/")

    @staticmethod
    def _normalize_base_url(base_url: str) -> str:
        base_url = base_url.rstrip("/")
        parsed = urllib.parse.urlparse(base_url)
        if not parsed.scheme or not parsed.netloc:
            return base_url
        if parsed.path in {"", "/"}:
            return urllib.parse.urlunparse(parsed._replace(path="/api")).rstrip("/")
        return base_url

    @staticmethod
    def _api_error_from_http(exc: urllib.error.HTTPError) -> ApiError:
        message = exc.reason
        try:
            error_payload = json.loads(exc.read().decode("utf-8"))
            message = error_payload.get("error") or error_payload.get("detail") or message
        except Exception:
            pass
        return ApiError(str(message))

    @staticmethod
    def _api_error_from_exception(exc: Exception | None) -> ApiError:
        if isinstance(exc, urllib.error.HTTPError):
            return ApiClient._api_error_from_http(exc)
        if isinstance(exc, urllib.error.URLError):
            return ApiError(str(exc.reason))
        if exc is not None:
            return ApiError(str(exc))
        return ApiError("Backend request failed")

    def snapshot_bytes(self, cache_bust: int | None = None) -> bytes:
        query = None if cache_bust is None else {"t": cache_bust}
        return self.get_bytes("/frame/snapshot", query)

    def current_frame_bytes(self, cache_bust: int | None = None) -> bytes:
        query = None if cache_bust is None else {"t": cache_bust}
        last_error: Exception | None = None
        for url in self._candidate_urls("/frame/current", query):
            request = urllib.request.Request(url, method="GET")
            try:
                with urllib.request.urlopen(request, timeout=self.timeout) as response:
                    self._remember_working_base(url)
                    return self._read_first_jpeg(response)
            except urllib.error.HTTPError as exc:
                last_error = exc
                if exc.code != 404:
                    raise self._api_error_from_http(exc)
            except urllib.error.URLError as exc:
                raise self._api_error_from_exception(exc)

        raise self._api_error_from_exception(last_error)

    def keep_current_frame_stream_alive(self, stop_event: threading.Event) -> None:
        last_error: Exception | None = None
        for url in self._candidate_urls("/frame/current", {"t": int(os.getpid())}):
            request = urllib.request.Request(url, method="GET")
            try:
                with urllib.request.urlopen(request, timeout=self.timeout) as response:
                    self._remember_working_base(url)
                    while not stop_event.is_set():
                        if not response.read(8192):
                            break
                    return
            except urllib.error.HTTPError as exc:
                last_error = exc
                if exc.code != 404:
                    raise self._api_error_from_http(exc)
            except urllib.error.URLError as exc:
                raise self._api_error_from_exception(exc)

        raise self._api_error_from_exception(last_error)

    @staticmethod
    def _read_first_jpeg(response: Any) -> bytes:
        buffer = bytearray()
        start = -1
        max_bytes = 5 * 1024 * 1024

        while len(buffer) < max_bytes:
            chunk = response.read(8192)
            if not chunk:
                break
            buffer.extend(chunk)
            if start < 0:
                start = buffer.find(b"\xff\xd8")
            if start >= 0:
                end = buffer.find(b"\xff\xd9", start + 2)
                if end >= 0:
                    return bytes(buffer[start : end + 2])

        raise ApiError("No JPEG frame found in current frame stream")

    def health(self) -> Any:
        return self.get("/health")

    def wait_until_ready(self, timeout: float = 30.0, interval: float = 0.75) -> Any:
        deadline = time.monotonic() + timeout
        last_error: ApiError | None = None

        while time.monotonic() < deadline:
            try:
                return self.health()
            except ApiError as exc:
                last_error = exc
                time.sleep(interval)

        detail = f": {last_error}" if last_error is not None else ""
        raise ApiError(f"Backend is not reachable at {self.base_url}{detail}")

    def stats(self) -> Any:
        return self.get("/stats")

    def detection_status(self) -> Any:
        return self.get("/detection/status")

    def laser_settings(self) -> Any:
        return self.get("/laser/settings")

    def sensor_values(self) -> Any:
        return self.get("/sensors/values")

    def laser_temp(self) -> Any:
        return self.get("/laser/temp")

    def treatment_app_status(self) -> Any:
        return self.get("/treatment/app/status", timeout=30.0)

    def full_app_check(self, skip_model_load: bool = False) -> Any:
        return self.get(
            "/diagnostics/full_app_check",
            {"skip_model_load": "true" if skip_model_load else "false"},
            timeout=max(self.slow_timeout, 120.0),
        )

    def set_treatment_app_mode(self, mode: str) -> Any:
        return self.post("/treatment/app/mode", {"mode": mode}, timeout=15.0)

    def treatment_app_detect(self) -> Any:
        return self.post("/treatment/app/detect", timeout=self.slow_timeout)

    def treatment_app_fire(self) -> Any:
        return self.post("/treatment/app/fire", timeout=45.0)

    def treatment_app_next(self) -> Any:
        return self.post("/treatment/app/next", timeout=45.0)

    def treatment_app_settings(
        self,
        p808: int,
        p980: int,
        p1064: int,
        pulse_ms: int,
    ) -> Any:
        return self.post(
            "/treatment/app/settings",
            {
                "p808": p808,
                "p980": p980,
                "p1064": p1064,
                "pulse_ms": pulse_ms,
            },
            timeout=30.0,
        )

    def treatment_app_emergency_stop(self) -> Any:
        return self.post("/treatment/app/emergency_stop", timeout=30.0)

    def startup_clean_state(self) -> Any:
        return self.post("/startup/clean_state", timeout=45.0)

    def sequence_status(self) -> Any:
        return self.get("/seq/status")

    def set_detection_enabled(self, enabled: bool) -> Any:
        return self.post("/detection/toggle", {"enabled": enabled}, timeout=15.0)

    def set_live_overlay_enabled(self, enabled: bool) -> Any:
        return self.post("/detection/live_overlay", {"enabled": enabled}, timeout=15.0)

    def set_detection_confidence(self, confidence: float) -> Any:
        return self.post("/detection/conf", {"conf": confidence}, timeout=15.0)

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
        backend_mode = "auto" if mode == "auto" else "manual"
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
        return self.post("/vacuum/on" if enabled else "/vacuum/off")

    def set_vacuum_check_enabled(self, enabled: bool) -> Any:
        return self.post("/vacuum/check", {"enabled": enabled})
