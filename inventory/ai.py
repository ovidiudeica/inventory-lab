"""Deterministic guidance only; deliberately no network provider."""
from .core import investigate, PROCEDURES


def explain(sku: str) -> dict:
    case = investigate(sku)
    return {
        "mode": "offline",
        "text": case["hypothesis"] + " " + case["conclusion"],
        "procedures": {pid: PROCEDURES[pid] for pid in case["procedure_ids"]},
        "warning": "Deterministic guidance, not generative AI.",
    }
