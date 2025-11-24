# Frameworks_Assignment — CORD-19 Explorer

This repository contains a beginner-friendly analysis of the CORD-19 `metadata.csv` and a simple Streamlit app to explore the results.

Getting started

1. Place `metadata.csv` (from the CORD-19 dataset) in the project root `Frameworks_Assignment/`.
   - You can download just the `metadata.csv` from Kaggle: https://www.kaggle.com/allen-institute-for-ai/CORD-19-research-challenge
2. Create a Python 3.7+ virtual environment and install dependencies:

```powershell
python -m venv .venv; .\.venv\Scripts\Activate.ps1; pip install -r requirements.txt
```

3. Run the Streamlit app:

```powershell
streamlit run app.py
```

Repository contents

- `data_analysis.py` — helper functions for loading, cleaning, and plotting the metadata
- `app.py` — Streamlit application to interactively explore the dataset
- `requirements.txt` — Python dependencies
- `analysis.ipynb` — starter Jupyter notebook for exploration

Notes

- The dataset can be large; if you experience memory issues, use the `nrows` argument in the loader or work with a sampled CSV.
- This project is a learning scaffold — feel free to expand analyses and visualizations.

Contact

If you want me to extend the app (add topic modeling, abstracts search, or caching improvements), tell me which feature to add next.