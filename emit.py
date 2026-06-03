import json
import uuid
from datetime import datetime

def emit_event(visitor_id, event_type):
    event = {
        "event_id": str(uuid.uuid4()),
        "visitor_id": visitor_id,
        "event_type": event_type,
        "timestamp": datetime.utcnow().isoformat()
    }

    print(event)

    with open("../data/events.jsonl", "a") as f:
        f.write(json.dumps(event) + "\n")


emit_event("VIS_002", "ENTRY")