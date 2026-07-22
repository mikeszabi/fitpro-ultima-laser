from __future__ import annotations

import json
import logging
from dataclasses import dataclass
from pathlib import Path
from typing import Any


LOG = logging.getLogger(__name__)
CONFIG_PATH = Path(__file__).resolve().parent / "config.json"


@dataclass(frozen=True)
class ConfidenceConfig:
    minimum: float = 0.0
    maximum: float = 0.25
    default: float = 0.1
    step: float = 0.005


def load_confidence_config(path: Path = CONFIG_PATH) -> ConfidenceConfig:
    try:
        raw: Any = json.loads(path.read_text(encoding="utf-8"))
        values = raw.get("confidence", {})
        config = ConfidenceConfig(
            minimum=float(values["minimum"]),
            maximum=float(values["maximum"]),
            default=float(values["default"]),
            step=float(values.get("step", 0.005)),
        )
        if config.minimum >= config.maximum:
            raise ValueError("minimum must be less than maximum")
        if not config.minimum <= config.default <= config.maximum:
            raise ValueError("default must be within the configured range")
        if config.step <= 0 or config.step > config.maximum - config.minimum:
            raise ValueError("step must be positive and no larger than the range")
        return config
    except (OSError, ValueError, TypeError, KeyError, json.JSONDecodeError) as exc:
        LOG.error("Invalid confidence configuration in %s: %s; using defaults", path, exc)
        return ConfidenceConfig()
