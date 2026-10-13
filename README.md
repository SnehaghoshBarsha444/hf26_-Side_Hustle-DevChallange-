# Side Hustle: Local Invoice & Receipt Sorter (Open-Source AI)

## What I built
I built a small AI tool for freelancers that reads invoice and receipt files, extracts key details (vendor, amount, date, tax, category), and exports clean bookkeeping rows.

It is designed as a paid side-hustle utility for people who hate manual expense entry but cannot share client financial documents with third-party cloud tools.

## Open-source AI at the core
This project relies on open pieces end-to-end:
- **Open-weight model** for document understanding and field extraction.
- **Open-source inference stack** to run locally on a laptop.
- **Open-source agent workflow** to validate extracted fields and flag uncertain values for review.

The open components are not optional extras; they are the core reason the product works for this audience.

## Why open innovation matters here
Open innovation makes this side hustle viable in ways closed APIs do not:
- **Privacy-first by default:** sensitive invoices stay on the user’s machine.
- **Offline-capable:** works with no internet for travel or low-connectivity use.
- **Lower operating cost:** no per-document API fees, so pricing can stay affordable.
- **No vendor lock-in:** models can be swapped or fine-tuned for niche invoice formats.
- **Custom behavior:** extraction rules can be tuned for local tax/accounting patterns.

## Where open worked better than closed
For this use case, open-source AI beat a closed hosted API because:
- Users had strict privacy concerns about uploading client documents.
- Niche formatting (local vendors, mixed-language receipts) needed adaptation.
- Predictable cost mattered for a micro-business tool with tight margins.

## First-user feedback (bonus)
I tested it with one freelancer who processes monthly client expenses.

Result:
- They said it saved them repetitive data-entry time.
- They would pay for it if CSV export and duplicate detection are included.
- Their next request: automatic monthly summary reports by category.

## Why this fits the Side Hustle theme
This is a small, specific, useful tool someone would realistically pay for, and it only works this well because open-weight models and open-source infrastructure make privacy, customization, and cost control possible.