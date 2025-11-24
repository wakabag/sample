"""
Helpers to load and analyze `estimated_numbers.csv`.
This file provides simple loading, cleaning, summary, and plotting functions
that use the median columns (e.g., `No. of cases_median`) for numeric analysis.
"""

import pandas as pd
import matplotlib.pyplot as plt
from typing import Tuple


def load_estimated(path: str, nrows: int = None) -> pd.DataFrame:
    """Load the estimated numbers CSV.

    Args:
        path: path to `estimated_numbers.csv`
        nrows: optional number of rows to read
    Returns:
        DataFrame
    """
    df = pd.read_csv(path, nrows=nrows)
    return df


def clean_estimated(df: pd.DataFrame) -> pd.DataFrame:
    """Basic cleaning:
    - strip whitespace from string columns
    - normalize column names
    - convert `Year` to int
    - convert median columns to numeric (coerce errors)
    - drop rows without `Country` or `Year`
    """
    df = df.copy()
    # strip column names
    df.columns = [c.strip() for c in df.columns]

    # strip string values
    for col in df.select_dtypes(include=['object']).columns:
        df[col] = df[col].astype(str).str.strip()

    # Normalize common names
    if 'No. of cases_median' in df.columns:
        cases_col = 'No. of cases_median'
    else:
        cases_col = None

    if 'No. of deaths_median' in df.columns:
        deaths_col = 'No. of deaths_median'
    else:
        deaths_col = None

    # Year
    if 'Year' in df.columns:
        df['Year'] = df['Year'].astype(str).str.strip()
        df['Year'] = pd.to_numeric(df['Year'], errors='coerce').astype('Int64')

    # Numeric medians
    if cases_col:
        df['cases_median'] = pd.to_numeric(df[cases_col], errors='coerce')
    else:
        df['cases_median'] = pd.NA

    if deaths_col:
        df['deaths_median'] = pd.to_numeric(df[deaths_col], errors='coerce')
    else:
        df['deaths_median'] = pd.NA

    # Keep useful columns
    keep = ['Country', 'Year', 'cases_median', 'deaths_median', 'WHO Region']
    existing = [c for c in keep if c in df.columns]
    result = df[existing].copy()

    # Drop rows without Country or Year
    result = result[result['Country'].notna()]
    if 'Year' in result.columns:
        result = result[result['Year'].notna()]

    return result


def summary_estimated(df: pd.DataFrame) -> dict:
    """Return basic summary statistics and counts."""
    s = {}
    s['rows'] = len(df)
    s['columns'] = df.columns.tolist()
    s['dtypes'] = df.dtypes.apply(lambda x: str(x)).to_dict()
    s['missing'] = df.isnull().sum().to_dict()
    # Most recent and earliest year
    if 'Year' in df.columns:
        years = df['Year'].dropna().astype(int)
        if len(years) > 0:
            s['year_min'] = int(years.min())
            s['year_max'] = int(years.max())
    return s


def plot_cases_over_time(df: pd.DataFrame, agg='sum') -> plt.Figure:
    """Plot total `cases_median` per year aggregated across countries.

    Args:
        df: cleaned DataFrame
        agg: aggregation method for numeric column ('sum' or 'median')
    Returns:
        matplotlib Figure
    """
    if 'Year' not in df.columns or 'cases_median' not in df.columns:
        raise ValueError('DataFrame must contain Year and cases_median columns')

    grouped = df.groupby('Year')['cases_median']
    if agg == 'sum':
        series = grouped.sum()
    else:
        series = grouped.median()

    fig, ax = plt.subplots(figsize=(8, 4))
    series.plot(ax=ax, marker='o')
    ax.set_title('Estimated Cases (median) by Year')
    ax.set_xlabel('Year')
    ax.set_ylabel('Cases (median)')
    plt.tight_layout()
    return fig


def plot_top_countries_for_year(df: pd.DataFrame, year: int, top_n: int = 10) -> plt.Figure:
    """Plot top countries by `cases_median` for a given year."""
    if 'Year' not in df.columns:
        raise ValueError('Year column not found')
    sub = df[df['Year'] == year]
    sub = sub.dropna(subset=['cases_median'])
    top = sub.sort_values('cases_median', ascending=False).head(top_n)
    fig, ax = plt.subplots(figsize=(8, 5))
    ax.barh(top['Country'][::-1], top['cases_median'][::-1], color='#2b8cbe')
    ax.set_title(f'Top {top_n} Countries by Estimated Cases (median) — {year}')
    ax.set_xlabel('Cases (median)')
    plt.tight_layout()
    return fig


if __name__ == '__main__':
    import sys
    path = sys.argv[1] if len(sys.argv) > 1 else 'estimated_numbers.csv'
    nrows = int(sys.argv[2]) if len(sys.argv) > 2 else None
    df = load_estimated(path, nrows=nrows)
    print('Loaded rows:', len(df))
    dfc = clean_estimated(df)
    print('After cleaning rows:', len(dfc))
    print('Summary:')
    from pprint import pprint
    pprint(summary_estimated(dfc))
    try:
        fig = plot_cases_over_time(dfc)
        fig.savefig('cases_over_time.png')
        print('Saved cases_over_time.png')
    except Exception as e:
        print('Plot failed:', e)
