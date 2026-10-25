# Gapminder Explorer - Interactive Filtering App
# Built with Streamlit, pandas, and Plotly Express

import pandas as pd
import plotly.express as px
import streamlit as st

# ------------------------------------------------------------
# 1. Page setup
# ------------------------------------------------------------
st.set_page_config(page_title="Gapminder Explorer", layout="wide")

st.title("Gapminder Explorer: Life Expectancy & Wealth (1952-2007)")

st.markdown(
    """
**How to use this app**

1. Use the **filters in the left sidebar** to choose a date range, continents,
   a GDP per capita range, and whether to include only large countries.
2. Every chart and number on this page updates automatically when you change a filter.
3. Hover over a chart to see exact values. Drag to zoom in, and double-click to zoom back out.
"""
)


# ------------------------------------------------------------
# 2. Load the data
# ------------------------------------------------------------
# @st.cache_data means the CSV is only read once, not every time a filter changes
@st.cache_data
def load_data():
    df = pd.read_csv("data/gapminder.csv")

    # The dataset only has a "year" number, so we turn it into a real date
    # (January 1st of that year) so we can use a date range selector
    df["date"] = pd.to_datetime(df["year"].astype(str) + "-01-01")

    # Rename columns so they look nicer in charts
    df = df.rename(
        columns={
            "country": "Country",
            "continent": "Continent",
            "lifeExp": "Life Expectancy",
            "pop": "Population",
            "gdpPercap": "GDP per Capita",
        }
    )
    return df


df = load_data()


# ------------------------------------------------------------
# 3. Sidebar filters
# ------------------------------------------------------------
st.sidebar.header("Filters")

# Filter 1: Date range selector
min_date = df["date"].min().date()
max_date = df["date"].max().date()

date_range = st.sidebar.date_input(
    "Date range",
    value=(min_date, max_date),
    min_value=min_date,
    max_value=max_date,
    help="Data is recorded every 5 years (1952, 1957, ... 2007).",
)

# While the user is picking dates, Streamlit may only return one date.
# In that case we just use the full range until they pick the second date.
if len(date_range) == 2:
    start_date, end_date = date_range
else:
    start_date, end_date = min_date, max_date

# Filter 2: Multi-select for continents
all_continents = sorted(df["Continent"].unique())

selected_continents = st.sidebar.multiselect(
    "Continents",
    options=all_continents,
    default=all_continents,
)

# Filter 3: Numeric slider for GDP per capita
min_gdp = int(df["GDP per Capita"].min())
max_gdp = int(df["GDP per Capita"].max()) + 1

gdp_range = st.sidebar.slider(
    "GDP per capita (US$)",
    min_value=min_gdp,
    max_value=max_gdp,
    value=(min_gdp, max_gdp),
    step=500,
)

# Filter 4: Checkbox for a yes/no choice
large_only = st.sidebar.checkbox(
    "Only show large countries (population over 10 million)",
    value=False,
)


# ------------------------------------------------------------
# 4. Apply the filters with pandas
# ------------------------------------------------------------
filtered = df[
    (df["date"] >= pd.to_datetime(start_date))
    & (df["date"] <= pd.to_datetime(end_date))
    & (df["Continent"].isin(selected_continents))
    & (df["GDP per Capita"] >= gdp_range[0])
    & (df["GDP per Capita"] <= gdp_range[1])
]

if large_only:
    filtered = filtered[filtered["Population"] > 10_000_000]

# Edge case: stop here if no rows match the filters
if filtered.empty:
    st.warning(
        "No data matches your filters. Try widening the date range, "
        "selecting more continents, or widening the GDP range."
    )
    st.stop()


# ------------------------------------------------------------
# 5. Summary statistics (these update with the filters)
# ------------------------------------------------------------
st.subheader("Summary of Filtered Data")

col1, col2, col3, col4 = st.columns(4)
col1.metric("Rows", f"{len(filtered):,}")
col2.metric("Countries", filtered["Country"].nunique())
col3.metric("Avg. Life Expectancy", f"{filtered['Life Expectancy'].mean():.1f} yrs")
col4.metric("Median GDP per Capita", f"${filtered['GDP per Capita'].median():,.0f}")

with st.expander("Show detailed statistics table"):
    stats = filtered[["Life Expectancy", "Population", "GDP per Capita"]].describe()
    st.dataframe(stats.round(1))

# Use the same colors for each continent in every chart
continent_colors = {
    "Africa": "#E45756",
    "Americas": "#4C78A8",
    "Asia": "#F58518",
    "Europe": "#54A24B",
    "Oceania": "#B279A2",
}


# ------------------------------------------------------------
# 6. Chart 1: Time series (Week 7)
# ------------------------------------------------------------
st.subheader("1. Life Expectancy Over Time")

# Average life expectancy for each continent in each year
trend = (
    filtered.groupby(["date", "Continent"])["Life Expectancy"]
    .mean()
    .reset_index()
)

fig_line = px.line(
    trend,
    x="date",
    y="Life Expectancy",
    color="Continent",
    color_discrete_map=continent_colors,
    markers=True,
    title="Average Life Expectancy by Continent Over Time",
    labels={"date": "Year", "Life Expectancy": "Average Life Expectancy (years)"},
)
st.plotly_chart(fig_line, width="stretch")


# ------------------------------------------------------------
# 7. Chart 2: Map (Week 8)
# ------------------------------------------------------------
st.subheader("2. World Map")

# Let the user pick which year to show on the map (only years in the filtered data)
map_years = sorted(filtered["year"].unique())
map_year = st.select_slider("Year shown on map", options=map_years, value=map_years[-1])

map_data = filtered[filtered["year"] == map_year]

fig_map = px.choropleth(
    map_data,
    locations="iso_alpha",
    color="Life Expectancy",
    hover_name="Country",
    hover_data={"iso_alpha": False, "GDP per Capita": ":,.0f", "Population": ":,"},
    color_continuous_scale="Viridis",
    range_color=(df["Life Expectancy"].min(), df["Life Expectancy"].max()),
    title=f"Life Expectancy by Country in {map_year}",
    labels={"Life Expectancy": "Life Expectancy (years)"},
)
st.plotly_chart(fig_map, width="stretch")
st.caption("Grey countries are not in the filtered data.")


# ------------------------------------------------------------
# 8. Chart 3: Uncertainty with error bars (Week 9)
# ------------------------------------------------------------
st.subheader("3. How Certain Are the Averages?")

# For each continent, calculate the mean, standard deviation, and count
ci_data = (
    map_data.groupby("Continent")["Life Expectancy"]
    .agg(["mean", "std", "count"])
    .reset_index()
)

# 95% confidence interval = 1.96 * (standard deviation / square root of count)
ci_data["std"] = ci_data["std"].fillna(0)  # a group with 1 country has no std
ci_data["ci_95"] = 1.96 * ci_data["std"] / (ci_data["count"] ** 0.5)

fig_ci = px.bar(
    ci_data,
    x="Continent",
    y="mean",
    error_y="ci_95",
    color="Continent",
    color_discrete_map=continent_colors,
    hover_data={"count": True, "ci_95": ":.2f", "mean": ":.1f"},
    title=f"Average Life Expectancy by Continent in {map_year} (with 95% Confidence Intervals)",
    labels={
        "mean": "Average Life Expectancy (years)",
        "count": "Number of countries",
        "ci_95": "95% CI (+/- years)",
    },
)
fig_ci.update_layout(showlegend=False)
st.plotly_chart(fig_ci, width="stretch")

st.caption(
    "The black lines are 95% confidence intervals. Longer lines mean we are less sure "
    "about the average, usually because there are fewer countries or they differ a lot."
)


# ------------------------------------------------------------
# 9. Show the filtered data
# ------------------------------------------------------------
with st.expander("Show filtered data table"):
    st.dataframe(filtered.drop(columns=["date", "iso_num"]))

st.caption("Data source: Gapminder Foundation (via the Plotly Express sample datasets).")
