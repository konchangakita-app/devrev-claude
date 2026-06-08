#!/usr/bin/env python3
"""
Shared event log utility — a live trail for the agent to see what's happening on any UI.

Event log location: ~/.config/computer-events/events.jsonl
Each line is a JSON object with at minimum: {source, type, timestamp, ...extra_data}

Usage as library:
    from event_log import emit, read_events, read_new_events, clear, tail

Usage as CLI:
    python3 event_log.py                     # Read all events
    python3 event_log.py --tail              # Tail new events (live, blocks)
    python3 event_log.py --since <timestamp> # Events after timestamp
    python3 event_log.py --source pat_manager # Filter by source
    python3 event_log.py --last <n>          # Last n events
    python3 event_log.py --clear             # Clear the log
"""

import json
import os
import sys
import time

EVENT_DIR = os.path.expanduser("~/.config/computer-events")
EVENT_FILE = os.path.join(EVENT_DIR, "events.jsonl")


def _ensure_dir():
    os.makedirs(EVENT_DIR, mode=0o700, exist_ok=True)


def emit(source: str, event_type: str, also_stdout: bool = True, **data):
    """Write an event to the log file (and optionally stdout).

    Args:
        source: Origin of the event (e.g. 'pat_manager', 'context', 'agent')
        event_type: Type of event (e.g. 'pat_added', 'server_started')
        also_stdout: If True, also print to stdout as JSON line
        **data: Any additional key-value pairs to include
    """
    _ensure_dir()
    event = {
        "source": source,
        "type": event_type,
        "timestamp": time.time(),
        **data,
    }
    line = json.dumps(event)
    try:
        with open(EVENT_FILE, "a") as f:
            f.write(line + "\n")
            f.flush()
    except Exception:
        pass
    if also_stdout:
        try:
            print(line, flush=True)
        except Exception:
            pass
    return event


def read_events(source: str = None, since: float = None, last_n: int = None) -> list:
    """Read events from the log, optionally filtered.

    Args:
        source: Filter by source name
        since: Only events after this Unix timestamp
        last_n: Only return the last n events (after other filters)
    """
    if not os.path.exists(EVENT_FILE):
        return []
    events = []
    with open(EVENT_FILE, "r") as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
            try:
                event = json.loads(line)
            except json.JSONDecodeError:
                continue
            if source and event.get("source") != source:
                continue
            if since and event.get("timestamp", 0) < since:
                continue
            events.append(event)
    if last_n is not None:
        events = events[-last_n:]
    return events


def read_new_events(last_timestamp: float, source: str = None) -> list:
    """Read events newer than last_timestamp. Convenience for polling."""
    return read_events(source=source, since=last_timestamp + 0.001)


def clear(source: str = None):
    """Clear the event log. If source is given, only clear events from that source."""
    if source is None:
        _ensure_dir()
        with open(EVENT_FILE, "w") as f:
            pass
    else:
        # Rewrite without events from this source
        events = read_events()
        _ensure_dir()
        with open(EVENT_FILE, "w") as f:
            for event in events:
                if event.get("source") != source:
                    f.write(json.dumps(event) + "\n")


def tail(source: str = None, poll_interval: float = 0.5):
    """Tail the event log, yielding new events as they appear. Blocks forever."""
    _ensure_dir()
    last_pos = 0
    if os.path.exists(EVENT_FILE):
        last_pos = os.path.getsize(EVENT_FILE)
    while True:
        try:
            if not os.path.exists(EVENT_FILE):
                time.sleep(poll_interval)
                continue
            size = os.path.getsize(EVENT_FILE)
            if size < last_pos:
                # File was truncated
                last_pos = 0
            if size > last_pos:
                with open(EVENT_FILE, "r") as f:
                    f.seek(last_pos)
                    for line in f:
                        line = line.strip()
                        if not line:
                            continue
                        try:
                            event = json.loads(line)
                        except json.JSONDecodeError:
                            continue
                        if source and event.get("source") != source:
                            continue
                        yield event
                    last_pos = f.tell()
            time.sleep(poll_interval)
        except KeyboardInterrupt:
            break


# --- CLI ---
def main():
    import argparse
    parser = argparse.ArgumentParser(description="Computer Event Log — live trail for agent awareness")
    parser.add_argument("--tail", action="store_true", help="Tail new events (live, blocks)")
    parser.add_argument("--since", type=float, help="Events after Unix timestamp")
    parser.add_argument("--source", type=str, help="Filter by source")
    parser.add_argument("--last", type=int, help="Last N events")
    parser.add_argument("--clear", action="store_true", help="Clear the event log")
    parser.add_argument("--json", action="store_true", help="Output as JSON array")
    args = parser.parse_args()

    if args.clear:
        clear(source=args.source)
        print(f"Event log cleared{f' (source={args.source})' if args.source else ''}.")
        return

    if args.tail:
        try:
            for event in tail(source=args.source):
                print(json.dumps(event), flush=True)
        except KeyboardInterrupt:
            pass
        return

    events = read_events(source=args.source, since=args.since, last_n=args.last)
    if args.json:
        print(json.dumps(events, indent=2))
    else:
        for event in events:
            ts = event.get("timestamp", 0)
            t = time.strftime("%H:%M:%S", time.localtime(ts))
            src = event.get("source", "?")
            etype = event.get("type", "?")
            extra = {k: v for k, v in event.items() if k not in ("source", "type", "timestamp")}
            extra_str = f"  {json.dumps(extra)}" if extra else ""
            print(f"[{t}] {src}/{etype}{extra_str}")


if __name__ == "__main__":
    main()
