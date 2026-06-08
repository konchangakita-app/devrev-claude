#!/usr/bin/env python3
"""PAT Manager — Local web server for managing DevRev PATs securely.

Runs for a configurable duration (default 120s / 2 min).
Outputs JSON events to stdout so the calling agent can process changes in real-time.

Events emitted (one JSON object per line):
  {"event": "server_started", "url": "...", "timeout": 120}
  {"event": "pat_added", "org_slug": "...", "org_display_name": "...", "user": "...", "email": "...", "expires": "...", "masked_token": "..."}
  {"event": "pat_updated", "org_slug": "...", ...}  (same shape as pat_added)
  {"event": "pat_removed", "org_slug": "..."}
  {"event": "window_closed"}
  {"event": "heartbeat_timeout", "last_heartbeat_ago": N}
  {"event": "timeout", "reason": "idle" | "max_duration" | "window_closed" | "heartbeat_lost"}
  {"event": "server_stopped"}

Note: After "window_closed", the server waits a 2-second grace period before
shutting down. This ensures any events emitted just before (e.g. pat_added)
have time to be read from stdout by the calling agent.
"""

import http.server
import json
import os
import subprocess
import sys
import threading
import time
import webbrowser
import urllib.parse

PORT = 19847
IDLE_TIMEOUT = 120  # 2 minutes default
HEARTBEAT_TIMEOUT = 15  # If no heartbeat for 15s, assume window closed
SCRIPTS_DIR = os.path.dirname(os.path.abspath(__file__))
SKILL_DIR = os.path.dirname(SCRIPTS_DIR)
# Twenty UX static assets — local copy in skill's static/ dir (self-contained)
TWENTY_UX_DIR = os.path.join(SKILL_DIR, "static")
if not os.path.exists(TWENTY_UX_DIR):
    # Fallback: project root twenty-ux library
    _PROJECT_ROOT = os.path.dirname(os.path.dirname(SKILL_DIR))
    TWENTY_UX_DIR = os.path.join(_PROJECT_ROOT, "twenty-ux", "components")
PAT_MANAGER = os.path.join(SCRIPTS_DIR, "pat_manager.py")
# Look for HTML template: first in templates/ (skill dir), then fallback to scripts/ dir
HTML_FILE = os.path.join(SKILL_DIR, "templates", "pat-entry.html")
if not os.path.exists(HTML_FILE):
    HTML_FILE = os.path.join(SCRIPTS_DIR, "pat-entry.html")
# Shared event log - local module with graceful error handling
sys.path.insert(0, SCRIPTS_DIR)
try:
    from event_log import emit as _emit_event, clear as _clear_events
except ImportError as e:
    print(json.dumps({
        "error": True,
        "message": "Required module 'event_log.py' not found in scripts directory. Ensure the skill is complete.",
        "details": str(e),
        "expected_path": os.path.join(SCRIPTS_DIR, "event_log.py")
    }), file=sys.stderr)
    sys.exit(1)

EVENT_SOURCE = "pat_manager"


def emit_event(data):
    """Write event to shared event log (and stdout). Wraps event_log.emit()."""
    event_type = data.pop("event", data.pop("type", "unknown"))
    _emit_event(EVENT_SOURCE, event_type, also_stdout=True, **data)


def run_pat_manager(*args):
    """Run pat_manager.py with given args and return parsed JSON."""
    cmd = [sys.executable, PAT_MANAGER] + list(args)
    r = subprocess.run(cmd, capture_output=True, text=True)
    try:
        return json.loads(r.stdout)
    except json.JSONDecodeError:
        return {"error": r.stderr.strip() or r.stdout.strip()}


class PatHandler(http.server.BaseHTTPRequestHandler):
    last_activity = time.time()
    last_heartbeat = time.time()
    start_time = time.time()
    idle_timeout = IDLE_TIMEOUT
    window_open = True
    shutdown_reason = None
    server_ref = None

    def log_message(self, fmt, *args):
        pass  # Suppress request logs

    def _touch_activity(self):
        PatHandler.last_activity = time.time()

    def _send_json(self, data, status=200):
        self.send_response(status)
        self.send_header("Content-Type", "application/json")
        self.send_header("Access-Control-Allow-Origin", "*")
        self.end_headers()
        self.wfile.write(json.dumps(data).encode())

    def _send_file(self, path, content_type):
        try:
            with open(path, "rb") as f:
                content = f.read()
            self.send_response(200)
            self.send_header("Content-Type", content_type)
            self.end_headers()
            self.wfile.write(content)
        except FileNotFoundError:
            self.send_error(404)

    def do_OPTIONS(self):
        self._touch_activity()
        self.send_response(200)
        self.send_header("Access-Control-Allow-Origin", "*")
        self.send_header("Access-Control-Allow-Methods", "GET, POST, PUT, DELETE, OPTIONS")
        self.send_header("Access-Control-Allow-Headers", "Content-Type")
        self.end_headers()

    def do_GET(self):
        path = urllib.parse.urlparse(self.path).path

        # Don't count /api/status or /api/heartbeat as activity (polling shouldn't reset idle)
        if path not in ("/api/status", "/api/heartbeat"):
            self._touch_activity()

        if path == "/" or path == "/index.html":
            self._send_file(HTML_FILE, "text/html")
        elif path == "/components/design-tokens.css":
            self._send_file(os.path.join(TWENTY_UX_DIR, "design-tokens.css"), "text/css")
        elif path == "/components/components.css":
            self._send_file(os.path.join(TWENTY_UX_DIR, "components.css"), "text/css")
        elif path == "/components/components.js":
            self._send_file(os.path.join(TWENTY_UX_DIR, "components.js"), "application/javascript")
        elif path == "/api/pats":
            # List all stored PATs (masked)
            result = run_pat_manager("list-masked")
            self._send_json(result)
        elif path == "/api/status":
            # Server status + timer info (based on max duration from start, not idle)
            now = time.time()
            elapsed = now - PatHandler.start_time
            remaining = max(0, PatHandler.idle_timeout - elapsed)
            self._send_json({
                "uptime": round(elapsed),
                "timeout_seconds": PatHandler.idle_timeout,
                "seconds_remaining": round(remaining)
            })
        elif path == "/api/heartbeat":
            # Webpage pings this every 5s to prove it's still open
            PatHandler.last_heartbeat = time.time()
            self._send_json({"ok": True})
        elif path == "/api/dropbox/status":
            dropbox_path = os.path.expanduser("~/.config/devrev-pat-vault/dropbox.json")
            if os.path.exists(dropbox_path):
                try:
                    with open(dropbox_path) as f:
                        data = json.load(f)
                    self._send_json({"pending": True, "org": data.get("org_slug", "unknown")})
                except Exception:
                    self._send_json({"pending": False})
            else:
                self._send_json({"pending": False})
        else:
            self.send_error(404)

    def do_POST(self):
        self._touch_activity()
        path = urllib.parse.urlparse(self.path).path
        content_length = int(self.headers.get("Content-Length", 0))
        body = self.rfile.read(content_length).decode() if content_length else "{}"

        if path == "/api/pat":
            # Add a new PAT — validate and store directly
            try:
                data = json.loads(body)
                token = data.get("token", "").strip()
                if not token:
                    self._send_json({"error": "No token provided"}, 400)
                    return

                # Check if this org already has a PAT (= update vs add)
                # We'll detect after storing
                result = run_pat_manager("store", token)
                if "error" in result:
                    self._send_json(result, 400)
                    return

                masked = token[:4] + "..." + token[-4:] if len(token) > 8 else "****"
                event_data = {
                    "org_slug": result.get("org_slug", ""),
                    "org_display_name": result.get("org_display_name", ""),
                    "user": result.get("user_display_name", ""),
                    "email": result.get("user_email", ""),
                    "expires": result.get("expires", ""),
                    "masked_token": masked,
                }

                # Emit event for agent to process
                emit_event({"event": "pat_added", **event_data})

                self._send_json({
                    "status": "stored",
                    **event_data,
                    "message": "PAT validated, encrypted & stored."
                })
            except json.JSONDecodeError:
                self._send_json({"error": "Invalid JSON"}, 400)
            except Exception as e:
                self._send_json({"error": str(e)}, 500)

        elif path == "/api/pat/pickup":
            result = run_pat_manager("pickup")
            self._send_json(result)

        elif path == "/api/window-closed":
            # Ignore window-closed signals within 5s of server start —
            # Arc browser sometimes reloads localhost pages on open,
            # triggering beforeunload/sendBeacon prematurely.
            uptime = time.time() - PatHandler.start_time
            if uptime < 5:
                self._send_json({"ok": True, "ignored": True})
                return
            # Browser page is closing — signal to shut down
            PatHandler.window_open = False
            PatHandler.shutdown_reason = "window_closed"
            emit_event({"event": "window_closed"})
            self._send_json({"ok": True})
            # Grace period: wait a couple seconds before shutdown so the agent
            # can read any events (e.g. pat_added) emitted just before this.
            threading.Thread(target=self._shutdown_server_with_grace, daemon=True).start()

        else:
            self.send_error(404)

    def do_DELETE(self):
        self._touch_activity()
        path = urllib.parse.urlparse(self.path).path

        if path.startswith("/api/pat/"):
            org_slug = urllib.parse.unquote(path.split("/api/pat/")[1])
            if not org_slug:
                self._send_json({"error": "No org specified"}, 400)
                return
            result = run_pat_manager("remove", org_slug)
            if result.get("removed"):
                emit_event({"event": "pat_removed", "org_slug": org_slug})
            self._send_json(result)
        else:
            self.send_error(404)

    def _shutdown_server(self):
        time.sleep(0.3)  # Let the response finish
        if PatHandler.server_ref:
            PatHandler.server_ref.shutdown()

    def _shutdown_server_with_grace(self):
        """Wait a grace period after window_closed before shutting down.
        This ensures events emitted just before (e.g. pat_added) have time
        to be read by the agent from stdout before the process exits."""
        time.sleep(3.0)  # 3-second grace period
        if PatHandler.server_ref:
            PatHandler.server_ref.shutdown()


def main():
    port = PORT
    timeout = IDLE_TIMEOUT

    if len(sys.argv) > 1:
        for i, arg in enumerate(sys.argv[1:]):
            if arg == "--port" and i + 2 <= len(sys.argv):
                port = int(sys.argv[i + 2])
            if arg == "--timeout" and i + 2 <= len(sys.argv):
                timeout = int(sys.argv[i + 2])

    # Clear events from previous pat_manager sessions
    _clear_events(source=EVENT_SOURCE)

    PatHandler.idle_timeout = timeout
    PatHandler.start_time = time.time()
    PatHandler.last_activity = time.time()
    PatHandler.last_heartbeat = time.time()
    PatHandler.window_open = True
    PatHandler.shutdown_reason = None

    server = http.server.HTTPServer(("127.0.0.1", port), PatHandler)
    PatHandler.server_ref = server
    url = f"http://localhost:{port}"

    emit_event({"event": "server_started", "url": url, "timeout": timeout})

    # Prefer Arc browser on macOS; fall back to default
    try:
        subprocess.Popen(["open", "-a", "Arc", url], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    except Exception:
        webbrowser.open(url)

    def watchdog():
        """Shuts down server when:
        1. Max duration exceeded (hard timeout from start)
        2. No heartbeat from webpage for HEARTBEAT_TIMEOUT seconds (window closed/navigated away)
        3. Explicit window-closed signal received
        """
        while True:
            time.sleep(3)

            now = time.time()
            elapsed = now - PatHandler.start_time
            heartbeat_ago = now - PatHandler.last_heartbeat

            # Hard max duration
            if elapsed >= timeout:
                PatHandler.shutdown_reason = "max_duration"
                emit_event({"event": "timeout", "reason": "max_duration"})
                server.shutdown()
                return

            # Explicit window close already handled — just exit watchdog
            if not PatHandler.window_open:
                return

            # Heartbeat lost (window closed without sending window-closed event)
            if heartbeat_ago >= HEARTBEAT_TIMEOUT and elapsed > 10:
                PatHandler.shutdown_reason = "heartbeat_lost"
                emit_event({"event": "heartbeat_timeout", "last_heartbeat_ago": round(heartbeat_ago)})
                emit_event({"event": "timeout", "reason": "heartbeat_lost"})
                server.shutdown()
                return

    watchdog_thread = threading.Thread(target=watchdog, daemon=True)
    watchdog_thread.start()

    try:
        server.serve_forever()
    except KeyboardInterrupt:
        pass
    finally:
        server.server_close()
        emit_event({"event": "server_stopped"})


if __name__ == "__main__":
    main()
