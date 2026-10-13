# Local Invoice & Receipt Sorter

This project is a local-only invoice and receipt sorter designed for freelancers and small-side-hustle operators who want a privacy-first bookkeeping workflow without sending financial documents to a third-party cloud tool.

The app uploads one or more invoice/receipt files, extracts a few bookkeeping fields, and exports a clean CSV row for each document. It also flags possible duplicates and groups monthly totals by category.

## What it does

- Reads invoice and receipt files from disk
- Extracts vendor, amount, date, tax, and category
- Flags duplicate entries by vendor + date + amount
- Exports CSV rows for bookkeeping workflows
- Keeps all processing local, which matches the privacy-first side-hustle use case described in the product brief

## Project goals

This builds the MVP for a small paid utility that helps freelancers avoid manual expense entry. The core open-source story is preserved: local inference, offline capability, lower cost, and fast adaptation to niche receipt formats.

## Tech stack

- Python
- Flask
- OCR-friendly document parsing via pytesseract and Pillow
- PDF text extraction with pypdf
- CSV export and simple bookkeeping summaries

## Setup

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
python app.py
```

Then open http://localhost:5000 in your browser.

## How to use

1. Upload one or more invoice or receipt images/PDFs.
2. Let the app extract the essential fields.
3. Review the duplicate checks and category totals.
4. Download the CSV export for your bookkeeping workflow.

## Notes

This project is intentionally lightweight and local-first. It is an MVP starter that fits the README idea of a privacy-preserving, low-cost invoice sorter for freelancers.

## Future enhancements

- Better OCR tuning for mixed-language receipts
- Auto-classification based on detected vendor and transaction patterns
- Monthly summary dashboard with charts
- Local model integration for stronger document understanding
- Account-specific rules and duplicate matching refinements

