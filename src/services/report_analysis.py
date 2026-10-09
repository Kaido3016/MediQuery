"""Safe, deterministic PDF validation, extraction, and lab-value candidate parsing."""

from dataclasses import dataclass
from io import BytesIO
import re
from pathlib import Path

from pypdf import PdfReader


PDF_MAGIC = b"%PDF-"
MAX_EVIDENCE_CHARS = 500

# Keep the value/unit grammar deliberately conservative. Units may begin with a
# letter (g/dL, mmol/L) or a numeric multiplier (10^3/uL, 10*9/L), both common
# in real laboratory reports. Numeric units are restricted to multiplier forms
# so a reference range such as ``(3.9-5.6)`` cannot be swallowed as a unit.
UNIT_PATTERN = (
    r"(?:[A-Za-zµμ][A-Za-zµμ0-9/%^.\-*]*|" r"10(?:\^|\*)\d+[A-Za-zµμ0-9/%^.\-*]*)"
)
LAB_PATTERN = re.compile(
    r"^(?P<name>[A-Za-z][A-Za-z0-9 /()'\-]{1,80}?)\s*[:\t]+\s*"
    r"(?P<value>[<>]?\s*\d+(?:\.\d+)?)\s*"
    rf"(?P<unit>{UNIT_PATTERN})?\s*"
    r"(?:\(?\s*(?P<range>\d+(?:\.\d+)?\s*(?:-|–|to)\s*\d+(?:\.\d+)?|[<>]\s*\d+(?:\.\d+)?)\s*\)?)?\s*"
    r"(?P<flag>H|L|High|Low|Normal)?\s*$",
    re.IGNORECASE,
)
REFERENCE_RANGE_PATTERN = re.compile(
    r"^Reference Range\s*:\s*(?P<range>.+?)\s*$", re.IGNORECASE
)
FLAG_PATTERN = re.compile(
    r"^Flag\s*:\s*(?P<flag>high|low|normal|h|l)\s*$", re.IGNORECASE
)
CANDIDATE_LINE_PATTERN = re.compile(
    r"^[A-Za-z][A-Za-z0-9 /()'\-]{1,80}?\s*[:\t]+\s*[<>]?\s*\d+(?:\.\d+)?",
    re.IGNORECASE,
)


class ReportValidationError(ValueError):
    pass


@dataclass(frozen=True)
class ExtractedFinding:
    name: str
    value: str
    unit: str | None
    reference_range: str | None
    flag: str
    page: int
    evidence: str


@dataclass(frozen=True)
class ExtractionResult:
    page_count: int
    findings: list[ExtractedFinding]
    note: str | None


def validate_pdf(
    filename: str | None, content_type: str | None, raw: bytes, max_bytes: int
) -> None:
    """Validate a bounded, real PDF before parsing. MIME is advisory, magic bytes are decisive."""
    if not filename or Path(filename).suffix.lower() != ".pdf":
        raise ReportValidationError("Only PDF reports are supported")
    if content_type and content_type not in {
        "application/pdf",
        "application/octet-stream",
    }:
        raise ReportValidationError("The uploaded file must have PDF content")
    if not raw:
        raise ReportValidationError("The uploaded file is empty")
    if len(raw) > max_bytes:
        raise ReportValidationError("The uploaded report exceeds the allowed size")
    if not raw.startswith(PDF_MAGIC):
        raise ReportValidationError("The uploaded file is not a valid PDF")


def extract_report(raw: bytes, max_pages: int) -> ExtractionResult:
    try:
        reader = PdfReader(BytesIO(raw), strict=False)
    except Exception as exc:
        raise ReportValidationError("The PDF could not be read") from exc
    if reader.is_encrypted:
        raise ReportValidationError("Password-protected PDFs are not supported")
    if len(reader.pages) > max_pages:
        raise ReportValidationError("The report has too many pages")

    findings: list[ExtractedFinding] = []
    partial_candidates = 0
    extracted_any_text = False
    for page_number, page in enumerate(reader.pages, start=1):
        try:
            text = page.extract_text() or ""
        except Exception:
            text = ""
        if text.strip():
            extracted_any_text = True
            page_findings, page_partial_candidates = _parse_page_findings(
                text, page_number
            )
            findings.extend(page_findings)
            partial_candidates += page_partial_candidates

    note = None
    if not extracted_any_text:
        note = (
            "No selectable text was found. This may be a scanned report; "
            "OCR is not yet enabled."
        )
    elif partial_candidates:
        noun = "candidate was" if partial_candidates == 1 else "candidates were"
        note = (
            f"{partial_candidates} lab-value {noun} detected but could not be safely parsed. "
            "Review the original report; unsupported formats are not silently treated as extracted values."
        )
    elif not findings:
        note = (
            "Text was extracted, but no lab-value candidates could be safely "
            "identified. Review the original report."
        )
    return ExtractionResult(
        page_count=len(reader.pages), findings=findings[:200], note=note
    )


def _normalize_flag(raw_flag: str | None) -> str:
    return {
        "h": "high",
        "high": "high",
        "l": "low",
        "low": "low",
        "normal": "normal",
    }.get((raw_flag or "").lower(), "unknown")


def _parse_reference_range(value: str) -> str | None:
    normalized = " ".join(value.split())
    return normalized or None


def _parse_page_findings(text: str, page: int) -> tuple[list[ExtractedFinding], int]:
    """Parse one page and count lab-shaped lines that fail the safe grammar."""
    findings: list[ExtractedFinding] = []
    seen: set[tuple[str, str, str | None]] = set()
    partial_candidates = 0
    lines = [" ".join(line.split()) for line in text.splitlines()]

    for index, normalized in enumerate(lines):
        if len(normalized) < 4 or len(normalized) > MAX_EVIDENCE_CHARS:
            continue
        match = LAB_PATTERN.match(normalized)
        if not match:
            if CANDIDATE_LINE_PATTERN.match(normalized):
                partial_candidates += 1
            continue

        name = match.group("name").strip(" :-")
        value = re.sub(r"\s+", "", match.group("value"))
        unit = (match.group("unit") or "").strip() or None
        reference_range = (match.group("range") or "").strip() or None
        raw_flag = match.group("flag")

        if len(name) < 2 or name.lower() in {
            "page",
            "date",
            "patient",
            "patient id",
            "patient name",
            "date of birth",
            "collection date",
            "blood pressure",
            "lab status",
            "comment",
            "result",
            "reference range",
            "flag",
        }:
            continue

        # Some PDFs place the range and flag on their own lines immediately
        # after the value. Associate only those explicit adjacent metadata lines.
        evidence_lines = [normalized]
        for following in lines[index + 1 : index + 3]:
            range_match = REFERENCE_RANGE_PATTERN.match(following)
            if range_match and reference_range is None:
                reference_range = _parse_reference_range(range_match.group("range"))
                evidence_lines.append(following)
                continue
            flag_match = FLAG_PATTERN.match(following)
            if flag_match and raw_flag is None:
                raw_flag = flag_match.group("flag")
                evidence_lines.append(following)
                continue
            break

        key = (name.lower(), value, unit)
        if key in seen:
            continue
        seen.add(key)
        findings.append(
            ExtractedFinding(
                name=name,
                value=value,
                unit=unit,
                reference_range=reference_range,
                flag=_normalize_flag(raw_flag),
                page=page,
                evidence=" · ".join(evidence_lines)[:MAX_EVIDENCE_CHARS],
            )
        )
    return findings, partial_candidates


def parse_findings(text: str, page: int) -> list[ExtractedFinding]:
    """Extract conservative lab candidates without treating reference/flag lines as labs."""
    findings, _ = _parse_page_findings(text, page)
    return findings[:200]
