"""Export the canonical Python inventory model for the static website."""
import argparse
import json
from pathlib import Path

from .core import PROCEDURES, investigate, report, stock, summary

DEFAULT_OUTPUT = Path(__file__).resolve().parents[1] / "docs" / "demo-data.json"


def build_payload() -> dict:
    rows = stock()
    return {
        "schema_version": 1,
        "synthetic": True,
        "summary": summary(),
        "stock": rows,
        "procedures": PROCEDURES,
        "cases": {row["sku"]: investigate(row["sku"]) for row in rows},
        "reports": {row["sku"]: report(row["sku"]) for row in rows},
    }


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT)
    parser.add_argument("--check", action="store_true", help="Check committed JSON against the Python engine.")
    args = parser.parse_args()
    payload = build_payload()
    if args.check:
        if not args.output.is_file() or json.loads(args.output.read_text(encoding="utf-8")) != payload:
            parser.exit(1, "Demo export is missing or stale. Run python -m inventory.build_demo.\n")
        print("Demo export matches the Python engine.")
        return
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(payload, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    print(f"Exported {args.output}")


if __name__ == "__main__":
    main()
