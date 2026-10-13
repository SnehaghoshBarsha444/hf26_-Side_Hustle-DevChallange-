from flask import Flask, render_template, request, send_file, redirect, url_for
from werkzeug.utils import secure_filename
from pathlib import Path
import csv
import json
from datetime import datetime

from invoice_sorter.extractor import extract_document, summarize_by_category, detect_duplicates

app = Flask(__name__)
app.config["UPLOAD_FOLDER"] = Path("storage/uploads")
app.config["EXPORT_FOLDER"] = Path("storage/exports")
app.config["MAX_CONTENT_LENGTH"] = 16 * 1024 * 1024

app.config["UPLOAD_FOLDER"].mkdir(parents=True, exist_ok=True)
app.config["EXPORT_FOLDER"].mkdir(parents=True, exist_ok=True)


@app.route("/")
def index():
    return render_template("index.html")


@app.route("/process", methods=["POST"])
def process():
    files = request.files.getlist("files")
    if not files or all(f.filename == "" for f in files):
        return render_template("index.html", error="Please upload at least one invoice or receipt file.")

    records = []
    seen = set()

    for file in files:
        if file.filename == "":
            continue
        filename = secure_filename(file.filename)
        source = app.config["UPLOAD_FOLDER"] / filename
        file.save(source)

        record = extract_document(source)
        key = (record.get("vendor") or "unknown", record.get("date") or "unknown", record.get("amount") or 0)
        if key not in seen:
            seen.add(key)
            records.append(record)

    duplicate_groups = detect_duplicates(records)
    category_summary = summarize_by_category(records)

    csv_path = app.config["EXPORT_FOLDER"] / "export.csv"
    with csv_path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=["vendor", "amount", "date", "tax", "category", "source_file"])
        writer.writeheader()
        for record in records:
            writer.writerow(record)

    return render_template(
        "results.html",
        records=records,
        duplicate_groups=duplicate_groups,
        category_summary=category_summary,
        csv_path=str(csv_path),
        exported_at=datetime.now().strftime("%Y-%m-%d %H:%M")
    )


@app.route("/download")
def download():
    csv_path = app.config["EXPORT_FOLDER"] / "export.csv"
    if not csv_path.exists():
        return redirect(url_for("index"))
    return send_file(csv_path, as_attachment=True, download_name="invoice_export.csv")


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)
