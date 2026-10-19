import os
from pathlib import Path
from python_shared import ValidationRules

BASE_DIR = Path(__file__).resolve().parents[3]
CONTRACT_FILE = os.getenv("CONTRACTS_PATH", BASE_DIR / "contracts" / "jobs" / "enrich-span.yaml")

if not Path(CONTRACT_FILE).exists():
    # Fallback for site-packages installation where contracts/ might be at /app/contracts
    CONTRACT_FILE = Path("/app/contracts/jobs/enrich-span.yaml")


class ContractValidationError(ValueError):
    pass


def _extract_int(text: str, key: str) -> int:
    try:
        return ValidationRules.extract_int(text, key)
    except ValueError as e:
        raise ContractValidationError(str(e))


def load_enrich_span_contract() -> dict:
    text = CONTRACT_FILE.read_text()
    validate_enrich_span_contract(text)
    return {"job": "enrich-span", "version": _extract_int(text, "version")}


def validate_enrich_span_contract(text: str) -> None:
    required_lines = [
        "job: enrich-span",
        "queue: span-enrichment",
        "timeout_seconds:",
        "retry:",
        "max_attempts:",
        "backoff_ms:",
        "payload:",
        "result:",
        "required: [trace_id, span_id, model, text]",
        "pattern: '^emb_[a-f0-9]{24}$'",
    ]
    for line in required_lines:
        if line not in text:
            raise ContractValidationError(f"Missing required contract fragment: {line}")

    if _extract_int(text, "version") < 1:
        raise ContractValidationError("version must be positive integer")
    if _extract_int(text, "timeout_seconds") <= 0:
        raise ContractValidationError("timeout_seconds must be > 0")
