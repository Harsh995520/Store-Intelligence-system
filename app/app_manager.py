import json
import uuid
from datetime import datetime, UTC


def emit_event(visitor_id, event_type):
    event = {
        "event_id": str(uuid.uuid4()),
        "visitor_id": visitor_id,
        "event_type": event_type,
        "timestamp": datetime.now(UTC).isoformat()
    }

    print("EVENT:", event)

    with open("../data/events.jsonl", "a") as f:
        f.write(json.dumps(event) + "\n")