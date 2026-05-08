# memory.py
# SAVES AND RETRIEVES PAST ANALYSES
# COMPARE PRODUCTS OVER TIME, BUILD KNOWLEDGE BASE, AVOID RE-ANALYZING

import json
import os
from datetime import datetime

MEMORY_FILE = "memory.json"


def load_memory() -> dict:
    if not os.path.exists(MEMORY_FILE):
        return {}
    with open(MEMORY_FILE, "r") as f:
        return json.load(f)


def save_memory(memory: dict):
    with open(MEMORY_FILE, "w") as f:
        json.dump(memory, f, indent=2)


def store(product_name: str, analysis: dict):
    memory = load_memory()
    key = product_name.lower().strip()

    memory[key] = {
        "product_name": product_name,
        "timestamp": datetime.now().isoformat(),
        "analysis": analysis
    }

    save_memory(memory)
    print(f"[Memory] Saved analysis for '{product_name}'")


def retrieve(product_name: str) -> dict | None:
    memory = load_memory()
    key = product_name.lower().strip()
    entry = memory.get(key)

    if entry:
        print(f"[Memory] Found cached analysis for '{product_name}' from {entry['timestamp']}")
        return entry["analysis"]

    print(f"[Memory] No cached analysis found for '{product_name}'")
    return None


def compare(product_a: str, product_b: str) -> dict | None:
    analysis_a = retrieve(product_a)
    analysis_b = retrieve(product_b)

    if not analysis_a or not analysis_b:
        print("[Memory] Both products must be analyzed before comparing.")
        return None

    return {
        "product_a": {
            "name": product_a,
            "sentiment": analysis_a.get("overall_sentiment"),
            "severity_score": analysis_a.get("severity_score"),
            "verdict": analysis_a.get("verdict"),
            "key_points": analysis_a.get("key_points"),
        },
        "product_b": {
            "name": product_b,
            "sentiment": analysis_b.get("overall_sentiment"),
            "severity_score": analysis_b.get("severity_score"),
            "verdict": analysis_b.get("verdict"),
            "key_points": analysis_b.get("key_points"),
        }
    }


def list_all() -> list:
    memory = load_memory()
    return [
        {
            "product": v["product_name"],
            "analyzed_at": v["timestamp"]
        }
        for v in memory.values()
    ]


def delete(product_name: str):
    memory = load_memory()
    key = product_name.lower().strip()
    if key in memory:
        del memory[key]
        save_memory(memory)
        print(f"[Memory] Deleted analysis for '{product_name}'")
    else:
        print(f"[Memory] No entry found for '{product_name}'")