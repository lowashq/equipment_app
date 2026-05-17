from datetime import date
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
import json


def decide(payload: dict) -> dict:
    reasons = []

    try:
        start_date = date.fromisoformat(payload["start_date"])
        end_date = date.fromisoformat(payload["end_date"])
    except (KeyError, ValueError):
        return {
            "approved": False,
            "score": 0,
            "reasons": ["Invalid reservation dates"],
        }

    rental_days = (end_date - start_date).days + 1
    max_days = int(payload.get("equipment_max_rental_days") or 0)

    if end_date < start_date:
        reasons.append("Reservation end date cannot be before start date")

    if max_days > 0 and rental_days > max_days:
        reasons.append("Rental period exceeds maximum allowed days")

    if payload.get("equipment_status") != "available":
        reasons.append("Equipment is not available")

    if int(payload.get("user_active_rentals") or 0) >= 3:
        reasons.append("User has too many active rentals")

    if int(payload.get("user_overdue_rentals") or 0) > 0:
        reasons.append("User has overdue rentals")

    approved = not reasons
    return {
        "approved": approved,
        "score": 100 if approved else 20,
        "reasons": reasons,
    }


class Handler(BaseHTTPRequestHandler):
    def _send_json(self, status_code: int, payload: dict) -> None:
        body = json.dumps(payload).encode("utf-8")
        self.send_response(status_code)
        self.send_header("Content-Type", "application/json")
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def do_GET(self) -> None:
        self._send_json(200, {"status": "decision-engine-placeholder"})

    def do_POST(self) -> None:
        if self.path != "/decide":
            self._send_json(404, {"detail": "Not found"})
            return

        content_length = int(self.headers.get("Content-Length", "0"))
        raw_body = self.rfile.read(content_length)

        try:
            payload = json.loads(raw_body.decode("utf-8"))
        except json.JSONDecodeError:
            self._send_json(400, {"detail": "Invalid JSON"})
            return

        self._send_json(200, decide(payload))

    def log_message(self, format: str, *args) -> None:
        return


if __name__ == "__main__":
    server = ThreadingHTTPServer(("0.0.0.0", 3001), Handler)
    server.serve_forever()
