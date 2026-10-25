# Gapminder Explorer

An interactive Streamlit app for exploring life expectancy, population, and GDP per capita for 142 countries from 1952 to 2007.

Built with **pandas** (filtering), **Plotly Express** (interactive charts), and **Streamlit** (web app).

## Run it locally

```bash
pip install -r requirements.txt
streamlit run app.py
```

## Deploy on Streamlit Community Cloud

1. Go to https://share.streamlit.io and sign in with GitHub.
2. Click **Create app** and pick **Deploy a public app from GitHub**.
3. Choose this repository, branch `main`, and main file `app.py`.
4. Click **Deploy**.

## Part 1: Dataset and Filtering Plan

**Dataset description.** This app uses the Gapminder dataset from the Gapminder Foundation, loaded from the copy included with Plotly Express and saved as `data/gapminder.csv`. It has 1,704 rows: 142 countries measured every five years from 1952 to 2007. The main variables are `country` and `continent` (categorical), `year` (temporal), `lifeExp` (life expectancy in years), `pop` (population), `gdpPercap` (GDP per capita in US dollars, adjusted for inflation), and `iso_alpha` (three-letter country codes used for the map).

**Filtering opportunities and target questions.** Users can filter on four dimensions: a **date range** (the year is converted to a date), a **multi-select of continents**, a **GDP per capita slider**, and a **checkbox** that keeps only large countries (population over 10 million). These filters help answer questions like: *How has life expectancy changed on each continent over time? Which countries had the lowest life expectancy in a given year, and where are they? Do richer countries always live longer, and what happens when we only look at low-income countries? How confident can we be in each continent's average, given how many countries it has and how much they differ?*

## Files

| File | Purpose |
| --- | --- |
| `app.py` | The Streamlit app |
| `data/gapminder.csv` | The dataset |
| `requirements.txt` | Python packages Streamlit Cloud installs |
