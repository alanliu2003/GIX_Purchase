"""
GIX campus resources for the Wayfinder prototype (in-memory dictionary).

Each resource is keyed by a stable id; values are dicts with a consistent schema.
"""

from __future__ import annotations

REQUIRED_RESOURCE_KEYS: frozenset[str] = frozenset(
    {"name", "category", "building", "description"}
)

# Local campus knowledge base: id -> resource fields
CAMPUS_RESOURCES: dict[str, dict[str, str | list[str]]] = {
    "makerspace": {
        "name": "GIX Makerspace",
        "category": "Makerspace & fabrication",
        "building": "Steve Ballmer Building (GIX Bellevue)",
        "description": (
            "Prototyping space with hand tools, 3D printers, and laser cutters (availability varies). "
            "Ask reception or your cohort lead for access training and hours."
        ),
        "tags": ["3d printing", "laser", "tools", "prototyping"],
    },
    "bike_storage": {
        "name": "Bike storage",
        "category": "Transportation & storage",
        "building": "Steve Ballmer Building (GIX Bellevue)",
        "description": (
            "Indoor bike parking for students and staff. Bring your own lock; do not block walkways or exits."
        ),
        "tags": ["bike", "cycling", "lock"],
    },
    "free_printing": {
        "name": "Student printing (quota)",
        "category": "Printing & computing",
        "building": "Steve Ballmer Building (GIX Bellevue)",
        "description": (
            "Follow program instructions for printer locations and print quotas. "
            "Use double-sided printing when possible to save paper."
        ),
        "tags": ["printer", "quota", "documents"],
    },
    "quiet_study": {
        "name": "Quiet study nooks",
        "category": "Study spaces",
        "building": "Steve Ballmer Building (GIX Bellevue)",
        "description": (
            "Small tables and soft seating away from main studio traffic. Best for focused reading or calls with headphones."
        ),
        "tags": ["quiet", "focus", "reading"],
    },
    "studio_floor": {
        "name": "Open studio / team tables",
        "category": "Study spaces",
        "building": "Steve Ballmer Building (GIX Bellevue)",
        "description": (
            "Primary collaborative workspace for teams. Respect noise during class hours; use breakout rooms when available."
        ),
        "tags": ["teams", "collaboration", "tables"],
    },
    "kitchen": {
        "name": "Kitchen & microwaves",
        "category": "Food & amenities",
        "building": "Steve Ballmer Building (GIX Bellevue)",
        "description": (
            "Shared fridge, microwaves, and dish area. Label your food; clean up after yourself to keep the space usable for everyone."
        ),
        "tags": ["food", "microwave", "fridge"],
    },
    "reception": {
        "name": "Front desk / reception",
        "category": "Help & facilities",
        "building": "Steve Ballmer Building (GIX Bellevue)",
        "description": (
            "First stop for building access questions, lost items, and general wayfinding. Hours may differ on holidays."
        ),
        "tags": ["access", "lost and found", "directions"],
    },
    "lockers": {
        "name": "Day lockers",
        "category": "Transportation & storage",
        "building": "Steve Ballmer Building (GIX Bellevue)",
        "description": (
            "Short-term storage for bags and project materials. Do not store valuables overnight unless your program assigns a locker."
        ),
        "tags": ["storage", "bags"],
    },
    "wellness": {
        "name": "Wellness / rest space",
        "category": "Food & amenities",
        "building": "Steve Ballmer Building (GIX Bellevue)",
        "description": (
            "Low-stimulation space to step away between sessions. Keep voices low; follow posted room rules."
        ),
        "tags": ["rest", "wellness", "quiet"],
    },
}


def _assert_campus_resources_integrity(resources: dict[str, dict[str, str | list[str]]]) -> None:
    """Verify every entry has required fields and non-empty ids (lab Component E)."""
    for rid, record in resources.items():
        assert rid and isinstance(rid, str) and rid.strip(), "Resource id must be a non-empty string"
        assert isinstance(record, dict), f"Resource {rid!r} value must be a dict"
        missing = REQUIRED_RESOURCE_KEYS - record.keys()
        assert not missing, f"Resource {rid!r} missing keys: {sorted(missing)}"
        for key in REQUIRED_RESOURCE_KEYS:
            val = record[key]
            assert isinstance(val, str) and val.strip(), f"Resource {rid!r} field {key!r} must be non-empty str"


_assert_campus_resources_integrity(CAMPUS_RESOURCES)
