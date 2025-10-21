#!/usr/bin/env python3
"""
Export daily OHLCV for a symbol using the same SSI pagination/fields as automation_vn100_direct.py

Output: CSV compatible with pandas (date, open, high, low, close, volume)
"""

from __future__ import annotations

import argparse
import csv
import os
import sys
import time
from dataclasses import dataclass
from datetime import date, datetime
from typing import Any, Dict, List, Optional

import requests


@dataclass
class ExportConfig:
    symbol: str
    start_date: date
    end_date: date
    page_size: int = 100
    max_pages: int = 10000
    timeout: float = 30.0
    output_dir: str = "/Users/macintoshhd/Project/Project/stock_playing/tracking_data/output"
    ssi_url: str = "https://iboard-api.ssi.com.vn/statistics/company/ssmi/stock-info"


def safe_float(value: Any) -> Optional[float]:
    if value is None or value == '' or value == '-':
        return None
    try:
        return float(str(value).replace(',', ''))
    except (ValueError, TypeError):
        return None


def safe_int(value: Any) -> Optional[int]:
    if value is None or value == '' or value == '-':
        return None
    try:
        return int(str(value).replace(',', ''))
    except (ValueError, TypeError):
        return None


def fetch_all(config: ExportConfig) -> List[Dict[str, Any]]:
    session = requests.Session()
    session.headers.update({
        'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36',
        'Accept': 'application/json, text/plain, */*',
        'Accept-Language': 'en-US,en;q=0.9',
        'Referer': 'https://iboard.ssi.com.vn/',
        'Origin': 'https://iboard.ssi.com.vn'
    })

    all_rows: List[Dict[str, Any]] = []
    page = 1

    while page <= config.max_pages:
        params = {
            'symbol': config.symbol,
            'page': page,
            'pageSize': config.page_size,
            'fromDate': config.start_date.strftime('%d/%m/%Y'),
            'toDate': config.end_date.strftime('%d/%m/%Y')
        }

        resp = session.get(config.ssi_url, params=params, timeout=config.timeout)
        resp.raise_for_status()
        payload = resp.json()

        data_list = payload.get('data', []) if isinstance(payload, dict) else []
        paging = payload.get('paging', {}) if isinstance(payload, dict) else {}
        total = paging.get('total', 0)
        current_page_size = paging.get('pageSize', len(data_list))

        if not data_list:
            break

        for item in data_list:
            trading_date_str = item.get('tradingDate')
            if not trading_date_str:
                continue
            try:
                d = datetime.strptime(trading_date_str, '%d/%m/%Y').date()
            except ValueError:
                continue

            if d < config.start_date or d > config.end_date:
                continue

            all_rows.append({
                'date': d.isoformat(),
                'open': safe_float(item.get('open')),
                'high': safe_float(item.get('high')),
                'low': safe_float(item.get('low')),
                'close': safe_float(item.get('close')),
                'volume': safe_int(item.get('volume'))
            })

        # Continue pages using paging.total if provided
        if total and page * current_page_size >= total:
            break
        if not total and len(data_list) < config.page_size:
            break

        page += 1
        time.sleep(0.1)

    # Deduplicate by date (keep last), then sort by date asc
    dedup: Dict[str, Dict[str, Any]] = {}
    for r in all_rows:
        dedup[r['date']] = r
    ordered = [dedup[k] for k in sorted(dedup.keys())]
    return ordered


def write_csv(rows: List[Dict[str, Any]], out_path: str) -> None:
    os.makedirs(os.path.dirname(out_path), exist_ok=True)
    with open(out_path, 'w', newline='', encoding='utf-8') as f:
        w = csv.DictWriter(f, fieldnames=['date', 'open', 'high', 'low', 'close', 'volume'])
        w.writeheader()
        w.writerows(rows)


def main() -> int:
    parser = argparse.ArgumentParser(description='Export SSI OHLCV using automation-style pagination')
    parser.add_argument('--symbol', default='DIG')
    parser.add_argument('--start', default='2020-01-01')
    parser.add_argument('--end', default=date.today().isoformat())
    parser.add_argument('--output-dir', default='/Users/macintoshhd/Project/Project/stock_playing/tracking_data/output')
    args = parser.parse_args()

    start_d = datetime.strptime(args.start, '%Y-%m-%d').date()
    end_d = datetime.strptime(args.end, '%Y-%m-%d').date()

    cfg = ExportConfig(
        symbol=args.symbol.upper(),
        start_date=start_d,
        end_date=end_d,
        output_dir=args.output_dir
    )

    rows = fetch_all(cfg)
    out_file = os.path.join(cfg.output_dir, f"{cfg.symbol}_daily_{cfg.start_date.isoformat()}_{cfg.end_date.isoformat()}_full.csv")
    write_csv(rows, out_file)
    print(out_file)
    return 0


if __name__ == '__main__':
    raise SystemExit(main())


