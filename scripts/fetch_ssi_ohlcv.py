#!/usr/bin/env python3
"""
Fetch daily OHLCV data for a symbol from SSI APIs and save to CSV.

- Source API: URL 1 (statistics/company/ssmi/stock-info) with pagination
- Fields extracted: date, open, high, low, close, volume
"""

from __future__ import annotations

import argparse
import csv
import os
import sys
import time
from dataclasses import dataclass
from datetime import date, datetime
from typing import Any, Dict, Iterable, List, Optional, Tuple

import requests


BASE_URL = "https://iboard-api.ssi.com.vn/statistics/company/ssmi/stock-info"


@dataclass
class FetchConfig:
    symbol: str
    start_date: date
    end_date: date
    page_size: int = 100
    max_pages: int = 10000
    request_timeout: float = 20.0
    rate_limit_delay: float = 0.2
    output_dir: str = "./output"


def format_ddmmyyyy(d: date) -> str:
    return d.strftime("%d/%m/%Y")


def build_url(config: FetchConfig, page: int) -> str:
    params = {
        "symbol": config.symbol,
        "page": str(page),
        "pageSize": str(config.page_size),
        "fromDate": format_ddmmyyyy(config.start_date),
        "toDate": format_ddmmyyyy(config.end_date),
    }
    # Manual querystring build to avoid adding requests dependency quirks
    query = "&".join(f"{k}={requests.utils.quote(v)}" for k, v in params.items())
    return f"{BASE_URL}?{query}"


def safe_get(d: Dict[str, Any], keys: Iterable[str]) -> Optional[Any]:
    for k in keys:
        if k in d and d[k] is not None:
            return d[k]
    return None


def parse_row(raw: Dict[str, Any]) -> Optional[Dict[str, Any]]:
    # Date may appear as 'date' or 'tradingDate'
    date_str = safe_get(raw, ("date", "tradingDate"))
    if not date_str:
        return None
    # Normalize date to YYYY-MM-DD
    try:
        if len(date_str) == 10 and date_str[2] == "/":
            # dd/mm/yyyy
            dt = datetime.strptime(date_str, "%d/%m/%Y").date()
        else:
            # yyyy-mm-dd
            dt = datetime.strptime(date_str[:10], "%Y-%m-%d").date()
    except Exception:
        return None

    open_val = safe_get(raw, ("open_price", "openPrice", "open", "open_raw"))
    high_val = safe_get(raw, ("high_price", "highPrice", "high", "high_raw"))
    low_val = safe_get(raw, ("low_price", "lowPrice", "low", "low_raw"))
    close_val = safe_get(raw, ("close_price", "closePrice", "close", "close_raw"))
    volume_val = safe_get(raw, ("volume", "totalMatchVol", "total_match_vol"))

    return {
        "date": dt.isoformat(),
        "open": try_float(open_val),
        "high": try_float(high_val),
        "low": try_float(low_val),
        "close": try_float(close_val),
        "volume": try_int(volume_val),
    }


def try_float(v: Any) -> Optional[float]:
    try:
        if v is None:
            return None
        return float(v)
    except Exception:
        return None


def try_int(v: Any) -> Optional[int]:
    try:
        if v is None:
            return None
        return int(float(v))
    except Exception:
        return None


def fetch_page(url: str, timeout: float) -> Dict[str, Any]:
    headers = {
        "Accept": "application/json, text/plain, */*",
        "User-Agent": "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 Chrome/119.0.0.0 Safari/537.36",
        "Referer": "https://iboard.ssi.com.vn/",
        "Origin": "https://iboard.ssi.com.vn",
        "Connection": "keep-alive",
    }
    resp = requests.get(url, headers=headers, timeout=timeout)
    resp.raise_for_status()
    return resp.json()


def extract_items(payload: Dict[str, Any]) -> List[Dict[str, Any]]:
    # The API may return data in different keys; handle robustly
    if isinstance(payload, list):
        return payload  # rare, but handle
    for key in ("data", "items", "rows", "list", "records", "payload"):
        if key in payload and isinstance(payload[key], list):
            return payload[key]
    # Sometimes nested like { data: { items: [] } }
    data = payload.get("data") if isinstance(payload, dict) else None
    if isinstance(data, dict):
        for key in ("items", "rows", "list", "records"):
            val = data.get(key)
            if isinstance(val, list):
                return val
    return []


def fetch_ohlcv(config: FetchConfig) -> List[Dict[str, Any]]:
    all_rows: List[Dict[str, Any]] = []
    for page in range(1, config.max_pages + 1):
        url = build_url(config, page)
        try:
            payload = fetch_page(url, config.request_timeout)
        except Exception as exc:
            # stop on network/HTTP errors
            if page == 1:
                raise
            break

        items = extract_items(payload)
        if not items:
            break

        parsed = [r for r in (parse_row(item) for item in items) if r is not None]
        if not parsed:
            # if server returns non-empty items but unparseable, stop to avoid loop
            break

        all_rows.extend(parsed)

        # If returned less than page size, likely last page
        if len(items) < config.page_size:
            break

        time.sleep(config.rate_limit_delay)

    # Deduplicate by date (keep latest occurrence)
    dedup: Dict[str, Dict[str, Any]] = {}
    for r in all_rows:
        dedup[r["date"]] = r
    # Sort ascending by date
    result = [dedup[k] for k in sorted(dedup.keys())]
    return result


def ensure_output_dir(path: str) -> None:
    os.makedirs(path, exist_ok=True)


def write_csv(rows: List[Dict[str, Any]], out_path: str) -> None:
    fieldnames = ["date", "open", "high", "low", "close", "volume"]
    with open(out_path, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        for r in rows:
            writer.writerow({k: r.get(k) for k in fieldnames})


def parse_args(argv: Optional[List[str]] = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Fetch SSI OHLCV data and save to CSV")
    parser.add_argument("--symbol", default="DIG", help="Stock symbol, default DIG")
    parser.add_argument("--start", default="2020-01-01", help="Start date YYYY-MM-DD")
    parser.add_argument("--end", default=date.today().isoformat(), help="End date YYYY-MM-DD")
    parser.add_argument("--output-dir", default="/Users/macintoshhd/Project/Project/stock_playing/tracking_data/output", help="Output directory")
    return parser.parse_args(argv)


def main() -> int:
    args = parse_args()
    try:
        start_d = datetime.strptime(args.start, "%Y-%m-%d").date()
        end_d = datetime.strptime(args.end, "%Y-%m-%d").date()
    except ValueError:
        print("Invalid date format. Use YYYY-MM-DD.", file=sys.stderr)
        return 2

    if start_d > end_d:
        print("Start date must be <= end date", file=sys.stderr)
        return 2

    config = FetchConfig(
        symbol=args.symbol.upper(),
        start_date=start_d,
        end_date=end_d,
        output_dir=args.output_dir,
    )

    rows = fetch_ohlcv(config)
    ensure_output_dir(config.output_dir)
    out_file = os.path.join(
        config.output_dir,
        f"{config.symbol}_daily_{config.start_date.isoformat()}_{config.end_date.isoformat()}.csv",
    )
    write_csv(rows, out_file)
    print(out_file)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())


