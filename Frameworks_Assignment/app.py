def _load(path, fileobj, nrows):
import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt

from data_analysis import (
    load_data,
    clean_data,
    publications_by_year,
    top_journals,
    title_word_frequency,
    plot_publications_by_year,
    plot_top_journals,
    plot_title_wordcloud,
    plot_source_distribution,
)

# Estimated numbers helpers
from estimated_analysis import (
    load_estimated,
    clean_estimated,
    summary_estimated,
    plot_cases_over_time,
    plot_top_countries_for_year,
)

st.set_page_config(page_title="CORD-19 & Estimates Explorer", layout='wide')

st.title("CORD-19 & Country Estimates Explorer")
st.write("Explore CORD-19 `metadata.csv` or country-level estimated numbers (`estimated_numbers.csv`).")

# Dataset selector
dataset = st.sidebar.selectbox('Select dataset', ['CORD-19 metadata', 'Estimated numbers'])

if dataset == 'CORD-19 metadata':
    st.header('CORD-19 Metadata View')
    # Allow user to upload file or provide path
    uploaded = st.file_uploader('Upload metadata.csv (or leave empty to use local file path)', type=['csv'])
    use_path = st.text_input('Or enter local path to metadata.csv', value='metadata_sample.csv')
    nrows = st.number_input('Read only N rows (0 = all)', min_value=0, step=1000, value=0)

    @st.cache_data
    def _load_metadata(path, fileobj, nrows):
        if fileobj is not None:
            df = pd.read_csv(fileobj, nrows=nrows if nrows and nrows>0 else None)
        else:
            df = load_data(path, nrows=nrows if nrows and nrows>0 else None)
        df = clean_data(df)
        return df

    if uploaded is None and not use_path:
        st.warning('Please upload `metadata.csv` or enter its path.')
        st.stop()

    df = _load_metadata(use_path, uploaded, int(nrows))

    st.sidebar.header('Filters')
    min_year = int(df['year'].dropna().min()) if 'year' in df.columns and df['year'].dropna().size>0 else 2019
    max_year = int(df['year'].dropna().max()) if 'year' in df.columns and df['year'].dropna().size>0 else 2022
    year_range = st.sidebar.slider('Select year range', min_year, max_year, (min_year, max_year))

    filtered = df.copy()
    if 'year' in filtered.columns:
        filtered = filtered[(filtered['year'] >= year_range[0]) & (filtered['year'] <= year_range[1])]

    st.markdown(f"**Dataset loaded:** {len(df):,} rows — **Filtered:** {len(filtered):,} rows")

    # Publications over time
    st.subheader('Publications by Year')
    counts = publications_by_year(filtered)
    fig = plot_publications_by_year(counts)
    st.pyplot(fig)

    # Top journals
    st.subheader('Top Journals')
    journal_counts = top_journals(filtered, top_n=20)
    fig_j = plot_top_journals(journal_counts)
    st.pyplot(fig_j)

    # Title word cloud
    st.subheader('Title Word Cloud')
    word_freq = title_word_frequency(filtered, top_n=200)
    try:
        fig_w = plot_title_wordcloud(word_freq)
        st.pyplot(fig_w)
    except Exception:
        st.write('Word cloud generation requires the `wordcloud` package. Install it to see this visualization.')

    # Sources distribution
    st.subheader('Source Distribution')
    from data_analysis import source_counts
    src_counts = source_counts(filtered)
    fig_s = plot_source_distribution(src_counts)
    st.pyplot(fig_s)

    # Show sample data
    st.subheader('Sample Records')
    cols = [c for c in ['title','authors','journal','year'] if c in filtered.columns]
    st.dataframe(filtered[cols].head(50))

    st.write('Notes: This view reads the CORD-19 `metadata.csv`, cleans basic fields, and shows visualizations.')

else:
    st.header('Estimated Numbers View')
    st.write('Country-year estimates (cases/deaths median) from `estimated_numbers.csv`.')

    # Allow upload or path
    uploaded_est = st.file_uploader('Upload estimated_numbers.csv (optional)', type=['csv'], key='est')
    est_path = st.text_input('Or enter local path to estimated_numbers.csv', value='../estimated_numbers.csv')

    nrows_est = st.number_input('Read only N rows (0 = all) for estimated data', min_value=0, step=1000, value=0)

    @st.cache_data
    def _load_est(path, fileobj, nrows):
        if fileobj is not None:
            df = pd.read_csv(fileobj, nrows=nrows if nrows and nrows>0 else None)
        else:
            df = load_estimated(path, nrows=nrows if nrows and nrows>0 else None)
        df = clean_estimated(df)
        return df

    try:
        df_est = _load_est(est_path, uploaded_est, int(nrows_est))
    except FileNotFoundError:
        st.error(f'Estimated file not found at {est_path}. Please upload or correct the path.')
        st.stop()
    except Exception as e:
        st.error(f'Failed to load estimated data: {e}')
        st.stop()

    st.sidebar.header('Estimated data controls')
    # Year selection for top countries
    if 'Year' in df_est.columns and df_est['Year'].dropna().size>0:
        years = sorted(df_est['Year'].dropna().astype(int).unique())
        year_selected = st.sidebar.selectbox('Select year for top countries', years, index=len(years)-1)
    else:
        year_selected = None

    plot_choice = st.sidebar.radio('Plot type', ['Cases over time (aggregate)', 'Top countries for year'])

    if plot_choice == 'Cases over time (aggregate)':
        st.subheader('Estimated Cases Over Time')
        try:
            fig = plot_cases_over_time(df_est, agg='sum')
            st.pyplot(fig)
        except Exception as e:
            st.error(f'Plot failed: {e}')

    else:
        st.subheader(f'Top Countries by Estimated Cases — {year_selected}')
        top_n = st.sidebar.slider('Top N countries', 5, 30, 10)
        try:
            fig = plot_top_countries_for_year(df_est, int(year_selected), top_n=top_n)
            st.pyplot(fig)
        except Exception as e:
            st.error(f'Plot failed: {e}')

    st.subheader('Estimated Data Summary')
    st.write(summary_estimated(df_est))

    st.subheader('Sample Rows')
    st.dataframe(df_est.head(50))
