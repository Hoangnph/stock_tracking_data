#!/usr/bin/env python3
"""
VN-Index Data Analyzer and Gap Handler
=====================================

This script analyzes VN-Index data to identify missing days and handles gaps
in the data appropriately.

Features:
- Identifies missing trading days
- Analyzes data gaps and patterns
- Provides statistics on data completeness
- Handles weekends and holidays appropriately
"""

from __future__ import annotations

import argparse
import csv
import os
import sys
from datetime import date, datetime, timedelta
from typing import Dict, List, Set, Tuple

import pandas as pd


def load_csv_data(file_path: str) -> List[Dict[str, any]]:
    """Load CSV data into a list of dictionaries"""
    data = []
    with open(file_path, 'r', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        for row in reader:
            row['date'] = datetime.strptime(row['date'], '%Y-%m-%d').date()
            row['open'] = float(row['open']) if row['open'] else None
            row['high'] = float(row['high']) if row['high'] else None
            row['low'] = float(row['low']) if row['low'] else None
            row['close'] = float(row['close']) if row['close'] else None
            row['volume'] = int(row['volume']) if row['volume'] else 0
            data.append(row)
    return data


def get_expected_trading_days(start_date: date, end_date: date) -> Set[date]:
    """Get all expected trading days (excluding weekends)"""
    trading_days = set()
    current_date = start_date
    
    while current_date <= end_date:
        # Skip weekends (Saturday = 5, Sunday = 6)
        if current_date.weekday() < 5:
            trading_days.add(current_date)
        current_date += timedelta(days=1)
    
    return trading_days


def get_actual_trading_days(data: List[Dict[str, any]]) -> Set[date]:
    """Get actual trading days from data"""
    return {row['date'] for row in data}


def identify_missing_days(expected_days: Set[date], actual_days: Set[date]) -> Set[date]:
    """Identify missing trading days"""
    return expected_days - actual_days


def analyze_data_gaps(data: List[Dict[str, any]]) -> Dict[str, any]:
    """Analyze data for gaps and patterns"""
    if not data:
        return {}
    
    # Sort data by date
    data.sort(key=lambda x: x['date'])
    
    gaps = []
    prev_date = None
    
    for row in data:
        current_date = row['date']
        if prev_date:
            days_diff = (current_date - prev_date).days
            if days_diff > 1:
                gaps.append({
                    'start': prev_date,
                    'end': current_date,
                    'gap_days': days_diff - 1,
                    'gap_type': 'weekend' if days_diff <= 3 else 'holiday_or_missing'
                })
        prev_date = current_date
    
    return {
        'total_records': len(data),
        'date_range': f"{data[0]['date']} to {data[-1]['date']}",
        'gaps': gaps,
        'total_gaps': len(gaps),
        'weekend_gaps': len([g for g in gaps if g['gap_type'] == 'weekend']),
        'holiday_gaps': len([g for g in gaps if g['gap_type'] == 'holiday_or_missing']),
    }


def generate_missing_days_report(missing_days: Set[date]) -> Dict[str, any]:
    """Generate a report on missing days"""
    if not missing_days:
        return {'total_missing': 0, 'missing_by_year': {}, 'missing_by_month': {}}
    
    missing_by_year = {}
    missing_by_month = {}
    
    for missing_date in missing_days:
        year = missing_date.year
        month = f"{year}-{missing_date.month:02d}"
        
        missing_by_year[year] = missing_by_year.get(year, 0) + 1
        missing_by_month[month] = missing_by_month.get(month, 0) + 1
    
    return {
        'total_missing': len(missing_days),
        'missing_by_year': missing_by_year,
        'missing_by_month': missing_by_month,
        'missing_dates': sorted(list(missing_days))
    }


def print_analysis_report(analysis: Dict[str, any], missing_report: Dict[str, any]):
    """Print a comprehensive analysis report"""
    print("=" * 80)
    print("VN-INDEX DATA ANALYSIS REPORT")
    print("=" * 80)
    
    # Basic statistics
    print(f"📊 Total Records: {analysis['total_records']:,}")
    print(f"📅 Date Range: {analysis['date_range']}")
    print(f"📈 Total Gaps: {analysis['total_gaps']}")
    print(f"🏖️  Weekend Gaps: {analysis['weekend_gaps']}")
    print(f"🎉 Holiday/Missing Gaps: {analysis['holiday_gaps']}")
    
    print("\n" + "-" * 80)
    print("MISSING DAYS ANALYSIS")
    print("-" * 80)
    
    if missing_report['total_missing'] == 0:
        print("✅ No missing trading days detected!")
    else:
        print(f"⚠️  Total Missing Days: {missing_report['total_missing']}")
        
        print("\n📅 Missing Days by Year:")
        for year, count in sorted(missing_report['missing_by_year'].items()):
            print(f"   {year}: {count} days")
        
        print("\n📅 Missing Days by Month (Top 10):")
        sorted_months = sorted(missing_report['missing_by_month'].items(), 
                             key=lambda x: x[1], reverse=True)[:10]
        for month, count in sorted_months:
            print(f"   {month}: {count} days")
    
    print("\n" + "-" * 80)
    print("DATA GAPS DETAILS")
    print("-" * 80)
    
    if analysis['gaps']:
        print("Gap Analysis (showing gaps > 3 days):")
        significant_gaps = [g for g in analysis['gaps'] if g['gap_days'] > 3]
        
        if significant_gaps:
            for gap in significant_gaps[:10]:  # Show top 10
                print(f"   {gap['start']} to {gap['end']}: {gap['gap_days']} days ({gap['gap_type']})")
        else:
            print("   No significant gaps found (all gaps ≤ 3 days)")
    
    print("=" * 80)


def create_clean_csv(data: List[Dict[str, any]], output_path: str):
    """Create a clean CSV file with proper formatting"""
    fieldnames = ["date", "open", "high", "low", "close", "volume"]
    
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    
    with open(output_path, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        
        for row in data:
            # Convert date back to string for CSV
            csv_row = {
                'date': row['date'].strftime('%Y-%m-%d'),
                'open': row['open'],
                'high': row['high'],
                'low': row['low'],
                'close': row['close'],
                'volume': row['volume']
            }
            writer.writerow(csv_row)


def main():
    """Main function"""
    parser = argparse.ArgumentParser(description="Analyze VN-Index data for gaps and missing days")
    parser.add_argument("--input", required=True, help="Input CSV file path")
    parser.add_argument("--output", help="Output CSV file path (optional)")
    parser.add_argument("--start-date", help="Start date for analysis (YYYY-MM-DD)")
    parser.add_argument("--end-date", help="End date for analysis (YYYY-MM-DD)")
    
    args = parser.parse_args()
    
    try:
        # Load data
        print("Loading VN-Index data...")
        data = load_csv_data(args.input)
        
        if not data:
            print("Error: No data found in input file")
            return 1
        
        # Determine analysis date range
        if args.start_date and args.end_date:
            start_date = datetime.strptime(args.start_date, '%Y-%m-%d').date()
            end_date = datetime.strptime(args.end_date, '%Y-%m-%d').date()
        else:
            start_date = data[0]['date']
            end_date = data[-1]['date']
        
        print(f"Analyzing data from {start_date} to {end_date}...")
        
        # Analyze data
        analysis = analyze_data_gaps(data)
        
        # Identify missing days
        expected_days = get_expected_trading_days(start_date, end_date)
        actual_days = get_actual_trading_days(data)
        missing_days = identify_missing_days(expected_days, actual_days)
        
        # Generate missing days report
        missing_report = generate_missing_days_report(missing_days)
        
        # Print report
        print_analysis_report(analysis, missing_report)
        
        # Create clean CSV if output specified
        if args.output:
            print(f"\nCreating clean CSV file: {args.output}")
            create_clean_csv(data, args.output)
            print("✅ Clean CSV file created successfully!")
        
        return 0
        
    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    sys.exit(main())
