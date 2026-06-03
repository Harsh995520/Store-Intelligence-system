from fastapi import FastAPI
import json

app = FastAPI(title="Store Intelligence System")


@app.get("/")
def root():
    return {"status": "running"}


@app.get("/events")
def get_events():

    events = []

    try:
        with open("data/events.jsonl", "r") as f:
            for line in f:
                events.append(json.loads(line))

    except FileNotFoundError:
        pass

    return events


@app.get("/metrics")
def get_metrics():

    events = []

    try:
        with open("data/events.jsonl", "r") as f:
            for line in f:
                events.append(json.loads(line))

    except FileNotFoundError:
        pass

    entries = sum(
        1 for e in events
        if e["event_type"] == "ENTRY"
    )

    browsing = sum(
        1 for e in events
        if e["event_type"] == "BROWSING"
    )

    checkout = sum(
        1 for e in events
        if e["event_type"] == "CHECKOUT"
    )

    conversion_rate = (
        checkout / entries * 100
        if entries > 0 else 0
    )

    return {
        "entries": entries,
        "browsing": browsing,
        "checkout": checkout,
        "conversion_rate": round(conversion_rate, 2)
    }


@app.get("/visitors")
def get_visitors():

    events = []

    try:
        with open("data/events.jsonl", "r") as f:
            for line in f:
                events.append(json.loads(line))

    except FileNotFoundError:
        pass

    visitors = {}

    for e in events:
        visitor_id = e["visitor_id"]

        if visitor_id not in visitors:
            visitors[visitor_id] = 0

        visitors[visitor_id] += 1

    return visitors

@app.get("/journey")
def get_journey():

    events = []

    try:
        with open("data/events.jsonl", "r") as f:
            for line in f:
                events.append(json.loads(line))
    except FileNotFoundError:
        pass

    journeys = {}

    for e in events:
        visitor_id = e["visitor_id"]

        if visitor_id not in journeys:
            journeys[visitor_id] = []

        if e["event_type"] not in journeys[visitor_id]:
            journeys[visitor_id].append(e["event_type"])

    return journeys