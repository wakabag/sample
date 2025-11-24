"""
Helpers for loading, cleaning, and plotting CORD-19 `metadata.csv`.
Designed to be simple and beginner-friendly.
"""

from collections import Counter
import re
from typing import Tuple, List

import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns

sns.set(style="whitegrid")

# Small stopword list for title word frequency
STOPWORDS = set([
    'the','and','of','in','to','a','for','on','with','by','an','from','study','studies','using','use','based'
])


def load_data(path: str, nrows: int = None) -> pd.DataFrame:
    """Load CSV into a DataFrame. Provide nrows to sample large files.

    Args:
        path: Path to metadata.csv
        nrows: optional number of rows to read

    Returns:
        pd.DataFrame
    """
    df = pd.read_csv(path, nrows=nrows)
    return df


def clean_data(df: pd.DataFrame) -> pd.DataFrame:
    """Basic cleaning:
    - ensure publish_time parsed to datetime (if available)
    - extract year into `year` column
    - compute `abstract_word_count`
    - drop rows with neither title nor abstract
    """
    df = df.copy()

    # Normalize column names for common variants
    # Many CORD-19 metadata files use 'publish_time'
    if 'publish_time' in df.columns:
        date_col = 'publish_time'
    elif 'publish_date' in df.columns:
        date_col = 'publish_date'
    else:
        date_col = None

    if date_col:
        df[date_col] = pd.to_datetime(df[date_col], errors='coerce')
        df['year'] = df[date_col].dt.year
    else:
        df['year'] = pd.NaT

    # Abstract word count
    if 'abstract' in df.columns:
        df['abstract_word_count'] = df['abstract'].fillna('').astype(str).apply(lambda s: len(s.split()))
    else:
        df['abstract_word_count'] = 0

    # Ensure title exists
    if 'title' in df.columns:
        df['title'] = df['title'].fillna('').astype(str)

    # Drop rows with no title and no abstract
    df = df[(df['title'].str.strip() != '') | (df['abstract_word_count'] > 0)]

    return df


# Analysis helpers

def publications_by_year(df: pd.DataFrame) -> pd.Series:
    """Return series indexed by year with counts."""
    if 'year' not in df.columns:
        return pd.Series(dtype=int)
    counts = df['year'].dropna().astype(int).value_counts().sort_index()
    return counts


def top_journals(df: pd.DataFrame, top_n: int = 10) -> pd.Series:
    """Return top publishing journals (by `journal` column)."""
    col = None
    for candidate in ['journal', 'journal_x', 'doi', 'journal_title']:
        if candidate in df.columns:
            col = candidate
            break
    if col is None:
        return pd.Series(dtype=int)
    counts = df[col].fillna('Unknown').value_counts().head(top_n)
    return counts


def source_counts(df: pd.DataFrame) -> pd.Series:
    """Return counts by source (e.g., `source_x`)."""
    col = None
    for candidate in ['source_x', 'source', 'publish_year']:
        if candidate in df.columns:
            col = candidate
            break
    if col is None:
        return pd.Series(dtype=int)
    return df[col].fillna('Unknown').value_counts()


def title_word_frequency(df: pd.DataFrame, top_n: int = 50) -> List[Tuple[str, int]]:
    """Compute simple word frequency from titles (lowercased, remove non-alpha).

    Returns list of (word, count) sorted by count desc.
    """
    texts = df['title'].dropna().astype(str).str.lower().tolist() if 'title' in df.columns else []
    words = []
    for t in texts:
        # split on non-alpha
        for w in re.findall(r"[a-zA-Z]{2,}", t):
            if w in STOPWORDS:
                continue
            words.append(w)
    c = Counter(words)
    return c.most_common(top_n)


# Plot helpers returning matplotlib Figure objects

def plot_publications_by_year(counts: pd.Series) -> plt.Figure:
    fig, ax = plt.subplots(figsize=(8, 4))
    counts.plot(kind='bar', ax=ax, color='#4C72B0')
    ax.set_xlabel('Year')
    ax.set_ylabel('Number of publications')
    ax.set_title('Publications by Year')
    plt.tight_layout()
    return fig


def plot_top_journals(counts: pd.Series) -> plt.Figure:
    fig, ax = plt.subplots(figsize=(8, 5))
    counts.sort_values().plot(kind='barh', ax=ax, color='#55A868')
    ax.set_xlabel('Number of publications')
    ax.set_title('Top Publishing Journals')
    plt.tight_layout()
    return fig


def plot_title_wordcloud(word_freq: List[Tuple[str, int]]) -> plt.Figure:
    try:
        from wordcloud import WordCloud
    except Exception:
        raise RuntimeError('wordcloud package is required to generate word cloud')

    freq_dict = dict(word_freq)
    wc = WordCloud(width=800, height=400, background_color='white')
    wc.generate_from_frequencies(freq_dict)
    fig, ax = plt.subplots(figsize=(10, 4))
    ax.imshow(wc, interpolation='bilinear')
    ax.axis('off')
    ax.set_title('Word Cloud — Titles')
    plt.tight_layout()
    return fig


def plot_source_distribution(counts: pd.Series) -> plt.Figure:
    fig, ax = plt.subplots(figsize=(6, 6))
    counts.head(10).plot(kind='pie', ax=ax, autopct='%1.1f%%')
    ax.set_ylabel('')
    ax.set_title('Top Sources (by count)')
    plt.tight_layout()
    return fig


if __name__ == '__main__':
    # Tiny CLI for quick testing
    import sys
    if len(sys.argv) < 2:
        print('Usage: python data_analysis.py metadata.csv [nrows]')
        sys.exit(1)
    path = sys.argv[1]
    nrows = int(sys.argv[2]) if len(sys.argv) > 2 else None
    df = load_data(path, nrows=nrows)
    print('Loaded rows:', len(df))
    df = clean_data(df)
    print('After cleaning rows:', len(df))
    print('Columns:', df.columns.tolist())
