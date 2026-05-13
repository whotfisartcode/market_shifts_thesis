#!/usr/bin/env python3
"""Download official SEC Financial Statement Data Set quarterly ZIP files."""

from __future__ import annotations

import argparse
import os
import sys
import time
from datetime import date
from pathlib import Path
from urllib.error import HTTPError, URLError
from urllib.request import Request, urlopen


PROJECT_ROOT = Path(__file__).resolve().parents[2]
DEFAULT_OUTPUT_DIR = PROJECT_ROOT / "data/raw/sec_fsd_zips"
BASE_URL = "https://www.sec.gov/files/dera/data/financial-statement-data-sets/{quarter}.zip"
DEFAULT_START = "2009q1"
DEFAULT_END = "latest"
DEFAULT_USER_AGENT = "market-shifts-thesis-reproducibility/1.0 contact@example.com"
USER_AGENT_ENV = "SEC_USER_AGENT"


def parse_quarter(value: str) -> tuple[int, int] | None:
    token = value.strip().lower()
    if token == "latest":
        return None
    if len(token) != 6 or token[4] != "q" or not token[:4].isdigit() or token[5] not in "1234":
        raise argparse.ArgumentTypeError("quarter must look like 2025q4 or be 'latest'")
    year = int(token[:4])
    quarter = int(token[5])
    if year < 2009:
        raise argparse.ArgumentTypeError("SEC Financial Statement Data Sets start in 2009q1")
    return year, quarter


def latest_candidate_quarter() -> tuple[int, int]:
    today = date.today()
    current_quarter = ((today.month - 1) // 3) + 1
    if current_quarter == 1:
        return today.year - 1, 4
    return today.year, current_quarter - 1


def quarter_token(year: int, quarter: int) -> str:
    return f"{year}q{quarter}"


def next_quarter(year: int, quarter: int) -> tuple[int, int]:
    if quarter == 4:
        return year + 1, 1
    return year, quarter + 1


def quarter_range(start: tuple[int, int], end: tuple[int, int]) -> list[str]:
    quarters: list[str] = []
    year, quarter = start
    while (year, quarter) <= end:
        quarters.append(quarter_token(year, quarter))
        year, quarter = next_quarter(year, quarter)
    return quarters


def format_bytes(value: int | None) -> str:
    if value is None:
        return "unknown size"
    units = ["B", "KB", "MB", "GB"]
    size = float(value)
    for unit in units:
        if size < 1024 or unit == units[-1]:
            return f"{size:.1f} {unit}"
        size /= 1024
    return f"{value} B"


def download_quarter(
    quarter: str,
    output_dir: Path,
    user_agent: str,
    timeout: int,
    overwrite: bool,
    dry_run: bool,
) -> str:
    url = BASE_URL.format(quarter=quarter)
    output_path = output_dir / f"{quarter}.zip"
    if output_path.exists() and not overwrite:
        print(f"exists {quarter}: {output_path}")
        return "exists"
    if dry_run:
        print(f"would download {quarter}: {url} -> {output_path}")
        return "dry_run"

    output_dir.mkdir(parents=True, exist_ok=True)
    tmp_path = output_path.with_suffix(output_path.suffix + ".download")
    request = Request(url, headers={"User-Agent": user_agent, "Accept-Encoding": "identity"})
    try:
        with urlopen(request, timeout=timeout) as response:
            content_length = response.headers.get("Content-Length")
            expected_bytes = int(content_length) if content_length and content_length.isdigit() else None
            with tmp_path.open("wb") as handle:
                while True:
                    chunk = response.read(1024 * 1024)
                    if not chunk:
                        break
                    handle.write(chunk)
        tmp_path.replace(output_path)
        print(f"downloaded {quarter}: {format_bytes(output_path.stat().st_size)} -> {output_path}")
        if expected_bytes is not None and output_path.stat().st_size != expected_bytes:
            print(
                f"warning {quarter}: expected {format_bytes(expected_bytes)}, "
                f"wrote {format_bytes(output_path.stat().st_size)}",
                file=sys.stderr,
            )
        return "downloaded"
    except HTTPError as exc:
        tmp_path.unlink(missing_ok=True)
        if exc.code == 404:
            print(f"missing {quarter}: SEC returned 404 for {url}")
            return "missing"
        raise
    except URLError:
        tmp_path.unlink(missing_ok=True)
        raise


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--from", dest="start", default=DEFAULT_START, type=parse_quarter)
    parser.add_argument("--to", dest="end", default=DEFAULT_END, type=parse_quarter)
    parser.add_argument("--output-dir", type=Path, default=DEFAULT_OUTPUT_DIR)
    parser.add_argument("--overwrite", action="store_true", help="download even when a ZIP already exists locally")
    parser.add_argument("--skip-missing", action="store_true", help="continue when an explicit quarter is not posted")
    parser.add_argument("--dry-run", action="store_true", help="print URLs without downloading files")
    parser.add_argument("--sleep", type=float, default=0.2, help="seconds to pause between SEC requests")
    parser.add_argument("--timeout", type=int, default=120, help="download timeout per ZIP in seconds")
    parser.add_argument(
        "--user-agent",
        default=os.environ.get(USER_AGENT_ENV, DEFAULT_USER_AGENT),
        help=f"SEC request user agent; can also be set with {USER_AGENT_ENV}",
    )
    return parser


def main() -> None:
    parser = build_parser()
    args = parser.parse_args()
    if args.start is None:
        parser.error("--from cannot be latest")

    end = args.end or latest_candidate_quarter()
    skip_missing = args.skip_missing or args.end is None
    if args.user_agent == DEFAULT_USER_AGENT and USER_AGENT_ENV not in os.environ:
        print(
            f"Using default SEC user agent. For repeated downloads, set {USER_AGENT_ENV} to your email/contact.",
            file=sys.stderr,
        )

    quarters = quarter_range(args.start, end)
    counts = {"downloaded": 0, "exists": 0, "missing": 0, "dry_run": 0}
    for index, quarter in enumerate(quarters, start=1):
        status = download_quarter(
            quarter=quarter,
            output_dir=args.output_dir,
            user_agent=args.user_agent,
            timeout=args.timeout,
            overwrite=args.overwrite,
            dry_run=args.dry_run,
        )
        counts[status] = counts.get(status, 0) + 1
        if status == "missing" and not skip_missing:
            raise SystemExit(f"SEC ZIP for {quarter} was not found; use --skip-missing to continue")
        if index < len(quarters) and not args.dry_run and args.sleep > 0:
            time.sleep(args.sleep)

    print(
        "SEC FSD ZIP download complete: "
        + ", ".join(f"{key}={value}" for key, value in sorted(counts.items()))
    )


if __name__ == "__main__":
    main()
