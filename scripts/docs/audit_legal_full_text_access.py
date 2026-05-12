#!/usr/bin/env python3
"""Audit legal full-text access for the thesis bibliography.

The script uses Unpaywall for DOI-based open-access metadata and downloads
only URLs that Unpaywall marks as legal OA PDF locations. It writes:

- reports/literature/legal_full_text_access_audit.csv
- reports/literature/legal_full_text_pdfs/*.pdf
- reports/literature/legal_full_text_extracts/*.txt
"""

from __future__ import annotations

import json
import re
import time
import urllib.error
import urllib.parse
import urllib.request
from pathlib import Path

import pandas as pd
from pypdf import PdfReader


PROJECT_ROOT = Path(__file__).resolve().parents[2]
MATRIX_PATH = PROJECT_ROOT / "reports/literature/literature_matrix.csv"
OUT_CSV = PROJECT_ROOT / "reports/literature/legal_full_text_access_audit.csv"
PDF_DIR = PROJECT_ROOT / "reports/literature/legal_full_text_pdfs"
TEXT_DIR = PROJECT_ROOT / "reports/literature/legal_full_text_extracts"
USER_AGENT = "Mozilla/5.0 thesis-literature-audit/1.0"
UNPAYWALL_EMAIL = "codex@openai.com"


def safe_name(text: str) -> str:
    return re.sub(r"[^A-Za-z0-9_.-]+", "_", text).strip("_")[:120]


def doi_from_url(value: str) -> str | None:
    value = str(value or "").strip()
    if not value:
        return None
    m = re.search(r"(10\.\d{4,9}/\S+)", value)
    if not m:
        return None
    return m.group(1).rstrip(").,;")


def request_json(url: str) -> tuple[dict | None, str | None]:
    req = urllib.request.Request(url, headers={"User-Agent": USER_AGENT})
    try:
        with urllib.request.urlopen(req, timeout=30) as resp:
            return json.load(resp), None
    except Exception as exc:  # noqa: BLE001 - audit should keep moving
        return None, repr(exc)


def download_pdf(url: str, path: Path) -> tuple[bool, str | None]:
    if path.exists() and path.stat().st_size > 1000:
        return True, None
    req = urllib.request.Request(url, headers={"User-Agent": USER_AGENT})
    try:
        with urllib.request.urlopen(req, timeout=60) as resp:
            ctype = resp.headers.get("Content-Type", "")
            data = resp.read()
        if len(data) < 1000:
            return False, f"download_too_small:{len(data)}"
        if not (data[:4] == b"%PDF" or "pdf" in ctype.lower()):
            return False, f"not_pdf_content_type:{ctype}"
        path.write_bytes(data)
        return True, None
    except Exception as exc:  # noqa: BLE001
        return False, repr(exc)


def extract_pdf_text(pdf_path: Path, text_path: Path) -> tuple[bool, str | None, int]:
    if text_path.exists() and text_path.stat().st_size > 1000:
        return True, None, text_path.stat().st_size
    try:
        reader = PdfReader(str(pdf_path))
        pages = []
        for page in reader.pages:
            pages.append(page.extract_text() or "")
        text = "\n\n".join(pages).strip()
        text_path.write_text(text, encoding="utf-8")
        return True, None, len(text)
    except Exception as exc:  # noqa: BLE001
        return False, repr(exc), 0


def main() -> None:
    PDF_DIR.mkdir(parents=True, exist_ok=True)
    TEXT_DIR.mkdir(parents=True, exist_ok=True)

    matrix = pd.read_csv(MATRIX_PATH)
    rows = []

    for _, row in matrix.iterrows():
        key = str(row["citation_key"])
        source_url = str(row.get("doi_or_url", ""))
        doi = doi_from_url(source_url)

        audit = {
            "citation_key": key,
            "title": row.get("title", ""),
            "year": row.get("year", ""),
            "source_type": row.get("source_type", ""),
            "doi_or_url": source_url,
            "doi": doi or "",
            "unpaywall_checked": bool(doi),
            "is_oa": "",
            "oa_status": "",
            "best_oa_host_type": "",
            "best_oa_license": "",
            "best_oa_pdf_url": "",
            "best_oa_landing_url": "",
            "downloaded_pdf_path": "",
            "download_status": "not_attempted",
            "download_error": "",
            "text_extract_path": "",
            "text_extract_status": "not_attempted",
            "text_extract_error": "",
            "text_chars": 0,
            "access_bucket": "",
        }

        if not doi:
            audit["access_bucket"] = "non_doi_or_official_url_manual_check"
            rows.append(audit)
            continue

        api = (
            "https://api.unpaywall.org/v2/"
            + urllib.parse.quote(doi, safe="")
            + "?email="
            + urllib.parse.quote(UNPAYWALL_EMAIL)
        )
        data, err = request_json(api)
        if err or not data:
            audit["download_error"] = err or "no_unpaywall_data"
            audit["access_bucket"] = "unpaywall_lookup_failed"
            rows.append(audit)
            continue

        audit["is_oa"] = data.get("is_oa", "")
        audit["oa_status"] = data.get("oa_status", "")
        best = data.get("best_oa_location") or {}
        audit["best_oa_host_type"] = best.get("host_type", "") or ""
        audit["best_oa_license"] = best.get("license", "") or ""
        pdf_url = best.get("url_for_pdf") or ""
        landing_url = best.get("url_for_landing_page") or ""
        audit["best_oa_pdf_url"] = pdf_url
        audit["best_oa_landing_url"] = landing_url

        if data.get("is_oa") and pdf_url:
            pdf_path = PDF_DIR / f"{safe_name(key)}.pdf"
            ok, download_err = download_pdf(pdf_url, pdf_path)
            audit["download_status"] = "downloaded" if ok else "failed"
            audit["download_error"] = download_err or ""
            if ok:
                audit["downloaded_pdf_path"] = str(pdf_path)
                text_path = TEXT_DIR / f"{safe_name(key)}.txt"
                text_ok, text_err, text_chars = extract_pdf_text(pdf_path, text_path)
                audit["text_extract_status"] = "extracted" if text_ok else "failed"
                audit["text_extract_error"] = text_err or ""
                audit["text_chars"] = text_chars
                if text_ok:
                    audit["text_extract_path"] = str(text_path)
                audit["access_bucket"] = "open_access_pdf_downloaded"
            else:
                audit["access_bucket"] = "open_access_pdf_download_failed"
        elif data.get("is_oa") and landing_url:
            audit["access_bucket"] = "open_access_landing_page_no_pdf"
        elif data.get("is_oa"):
            audit["access_bucket"] = "open_access_no_location"
        else:
            audit["access_bucket"] = "not_open_access_by_unpaywall"

        rows.append(audit)
        time.sleep(0.15)

    out = pd.DataFrame(rows)
    out.to_csv(OUT_CSV, index=False)
    print(f"Wrote {OUT_CSV}")
    print(out["access_bucket"].value_counts(dropna=False).to_string())


if __name__ == "__main__":
    main()
