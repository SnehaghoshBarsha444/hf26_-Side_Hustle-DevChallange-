from __future__ import annotations

import csv
import re
from pathlib import Path
from typing import Any, Dict, Iterable, List

try:
    import pytesseract
except Exception:  # pragma: no cover
    pytesseract = None

try:
    from PIL import Image
except Exception:  # pragma: no cover
    Image = None

try:
    from pypdf import PdfReader
except Exception:  # pragma: no cover
    PdfReader = None


DATE_PATTERNS = [
    r"\b(?:0?[1-9]|[12][0-9]|3[01])[/-](?:0?[1-9]|1[0-2])[/-](?:\d{2,4})\b",
    r"\b(?:\d{4})[/-](?:0?[1-9]|1[0-2])[/-](?:0?[1-9]|[12][0-9]|3[01])\b",
    r"\b(?:Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec)[a-z]*\s+\d{1,2},\s+\d{4}\b",
    r"\b\d{1,2}\s+(?:Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec)[a-z]*\s+\d{4}\b",
]

TOTAL_PATTERNS = [
    "total", "amount due", "grand total", "net total", "balance due", "total amount"
]
TAX_PATTERNS = ["tax", "vat", "gst", "sales tax", "sales tax amount", "tax amount"]
CATEGORY_KEYWORDS = {
    "travel": ["uber", "lyft", "airline", "hotel", "taxi", "flight", "train", "fuel"],
    "software": ["github", "slack", "zoom", "adobe", "notion", "stripe", "aws", "digitalocean"],
    "office": ["office depot", "staples", "printer", "paper", "stationery", "supplies"],
    "marketing": ["meta", "google ads", "facebook", "linkedin", "canva", "mailchimp", "hubspot"],
    "meals": ["coffee", "restaurant", "cafe", "catering", "food", "burger", "pizza"],
    "utilities": ["electric", "water", "internet", "phone", "wifi", "utility"],
}


def normalize_text(value: str) -> str:
    return re.sub(r"\s+", " ", value or "").strip()


def find_vendor(text: str) -> str:
    lines = [line.strip() for line in text.splitlines() if line.strip()]
    if not lines:
        return "Unknown Vendor"

    # Prefer a top-of-document business name in first few lines.
    for line in lines[:8]:
        if len(line) > 3 and not re.fullmatch(r".*?(invoice|receipt|bill|tax|total|date).*", line, re.I):
            return line

    # Use a known vendor pattern from any line like "Acme Store"
    for line in lines:
        if re.search(r"[A-Z][a-z]+(?:\s+[A-Z][a-z]+)+|[A-Z][a-z]+\s+[A-Z][a-z]+", line):
            return line

    return "Unknown Vendor"


def find_date(text: str) -> str:
    for pattern in DATE_PATTERNS:
        match = re.search(pattern, text, flags=re.I)
        if match:
            return match.group(0)
    return "Unknown Date"


def parse_currency(value: str) -> float:
    if not value:
        return 0.0
    cleaned = value.replace(",", "").replace("$", "").replace("€", "").replace("£", "")
    cleaned = re.sub(r"[^0-9.\-]", "", cleaned)
    try:
        return float(cleaned)
    except ValueError:
        return 0.0


def extract_amount_from_line(line: str) -> float:
    if not line:
        return 0.0
    lower = line.lower()
    if not any(keyword in lower for keyword in TOTAL_PATTERNS):
        return 0.0

    number_match = re.search(r"\$?\d[\d,]*\.\d{2}|\$?\d[\d,]*", line)
    if not number_match:
        return 0.0
    return parse_currency(number_match.group(0))


def find_amount(text: str) -> float:
    for line in text.splitlines():
        amount = extract_amount_from_line(line)
        if amount > 0:
            return amount

    # Fallback: look for the largest currency-like value in the document
    numbers = [parse_currency(match.group(0)) for match in re.finditer(r"\$?\d[\d,]*\.\d{2}|\$?\d[\d,]*", text)]
    return max(numbers, default=0.0)


def find_tax(text: str) -> float:
    for line in text.splitlines():
        lower = line.lower()
        if any(keyword in lower for keyword in TAX_PATTERNS):
            match = re.search(r"\$?\d[\d,]*\.\d{2}|\$?\d[\d,]*", line)
            if match:
                return parse_currency(match.group(0))
    return 0.0


def classify_category(text: str, vendor: str) -> str:
    haystack = f"{text} {vendor}".lower()
    for category, keywords in CATEGORY_KEYWORDS.items():
        if any(keyword in haystack for keyword in keywords):
            return category.title()
    return "Other"


def ocr_image(file_path: Path) -> str:
    if Image is None or pytesseract is None:
        return ""
    try:
        image = Image.open(file_path)
        image = image.convert("RGB")
        return pytesseract.image_to_string(image)
    except Exception:
        return ""


def read_pdf_text(file_path: Path) -> str:
    if PdfReader is None:
        return ""
    try:
        reader = PdfReader(str(file_path))
        text_blocks = []
        for page in reader.pages:
            page_text = page.extract_text() or ""
            text_blocks.append(page_text)
        return "\n".join(text_blocks)
    except Exception:
        return ""


def read_text_file(file_path: Path) -> str:
    try:
        return file_path.read_text(encoding="utf-8", errors="ignore")
    except Exception:
        return ""


def extract_document(file_path: Path) -> Dict[str, Any]:
    suffix = file_path.suffix.lower()
    text = ""

    if suffix in {".txt", ".md", ".csv"}:
        text = read_text_file(file_path)
    elif suffix == ".pdf":
        text = read_pdf_text(file_path)
    elif suffix in {".png", ".jpg", ".jpeg"}:
        text = ocr_image(file_path)
    elif suffix == ".html":
        text = read_text_file(file_path)
    else:
        text = read_text_file(file_path)

    if not text:
        text = file_path.stem.replace("-", " ")

    vendor = find_vendor(text)
    amount = find_amount(text)
    date = find_date(text)
    tax = find_tax(text)
    category = classify_category(text, vendor)

    return {
        "vendor": vendor,
        "amount": round(amount, 2),
        "date": date,
        "tax": round(tax, 2),
        "category": category,
        "source_file": file_path.name,
    }


def detect_duplicates(records: Iterable[Dict[str, Any]]) -> List[List[Dict[str, Any]]]:
    groups: Dict[str, List[Dict[str, Any]]] = {}
    for record in records:
        key = f"{record.get('vendor','unknown')}|{record.get('date','unknown')}|{record.get('amount',0)}"
        groups.setdefault(key, []).append(record)
    return [items for items in groups.values() if len(items) > 1]


def summarize_by_category(records: Iterable[Dict[str, Any]]) -> Dict[str, float]:
    totals: Dict[str, float] = {}
    for record in records:
        category = record.get("category", "Other")
        totals[category] = totals.get(category, 0.0) + float(record.get("amount", 0.0) or 0.0)
    return {key: round(value, 2) for key, value in sorted(totals.items())}
