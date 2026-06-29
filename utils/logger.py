import json
import datetime
import os
import logging

logger = logging.getLogger("rare.audit")


class AuditLogger:
    def __init__(self, filename: str = "audit_trail.json"):
        self.filename = filename
        if not os.path.exists(self.filename):
            self._write([])

    def _write(self, data):
        with open(self.filename, "w") as f:
            json.dump(data, f, indent=2, default=str)

    def log_event(self, stage: str, agent: str, input_text: str, output_text: str, latency: float):
        entry = {
            "timestamp": datetime.datetime.now().isoformat(),
            "stage": stage,
            "agent": agent,
            "input": (input_text or "")[:200],
            "output": output_text,
            "latency": latency,
        }
        try:
            with open(self.filename, "r") as f:
                data = json.load(f)
        except (json.JSONDecodeError, FileNotFoundError):
            data = []
        data.append(entry)
        self._write(data)

    def get_all(self) -> list:
        try:
            with open(self.filename, "r") as f:
                return json.load(f)
        except (json.JSONDecodeError, FileNotFoundError):
            return []


audit_logger = AuditLogger()