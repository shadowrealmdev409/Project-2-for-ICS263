# Earthquake Explorer - Interactive Filtering App
# Built with Streamlit, pandas, and Plotly Express
# Data: USGS Earthquake Catalog, all magnitude 4.5+ earthquakes in 2024

import datetime

import pandas as pd
import plotly.express as px
import streamlit as st

st.set_page_config(page_title="Earthquake Explorer", layout="wide")

st.title("Earthquake Explorer: Magnitude 4.5+ Earthquakes in 2024")

st.write("**How to use this app:**")
st.write("1. Use the filters in the left sidebar to choose which earthquakes you want to see.")
st.write("2. Every chart and number on this page updates when you change a filter.")
st.write("3. Hover over a chart to see exact values. Drag to zoom in, double-click to zoom out.")
st.write("4. Click a bar in chart 3 to see the earthquakes for just that region.")


# ---------- Load the data ----------
# @st.cache_data means the CSV is only read once, not every time a filter changes
@st.cache_data
def load_data():
    df = pd.read_csv("data/earthquakes_2024.csv")
    # Turn the date text into real dates so we can filter by date
    df["time"] = pd.to_datetime(df["time"])
    df["week"] = pd.to_datetime(df["week"])
    df["date"] = df["time"].dt.date
    return df


df = load_data()

# Use the same color for each depth type in every chart
depth_colors = {"Shallow": "#E45756", "Intermediate": "#F58518", "Deep": "#4C78A8"}


# ---------- Sidebar filters ----------
with st.sidebar:
    st.header("Filters")

    # Filter 1: Date range
    date_range = st.date_input(
        "Date range",
        value=(datetime.date(2024, 1, 1), datetime.date(2024, 12, 31)),
        min_value=datetime.date(2024, 1, 1),
        max_value=datetime.date(2024, 12, 31),
    )

    # Filter 2: Regions (multi-select)
    selected_regions = st.multiselect("Regions", sorted(df["region"].unique()))
    st.caption("Leave empty to show all regions. Type to search.")

    # Filter 3: Magnitude (slider)
    mag_range = st.slider("Magnitude", 4.5, 7.5, (4.5, 7.5), step=0.1)

    # Filter 4: Shallow earthquakes only (checkbox)
    shallow_only = st.checkbox("Only show shallow earthquakes (less than 70 km deep)")
    st.caption("Shallow earthquakes usually cause the most shaking at the surface.")


# ---------- Apply the filters ----------
# While the user is still picking dates, date_input only gives back one date.
# In that case we use the full year until they pick the second date.
if len(date_range) == 2:
    start_date = date_range[0]
    end_date = date_range[1]
else:
    start_date = datetime.date(2024, 1, 1)
    end_date = datetime.date(2024, 12, 31)

# Filter by date range AND magnitude range
filtered = df[
    (df["date"] >= start_date)
    & (df["date"] <= end_date)
    & (df["magnitude"] >= mag_range[0])
    & (df["magnitude"] <= mag_range[1])
]

# Only filter by region if something is selected
if selected_regions:
    filtered = filtered[filtered["region"].isin(selected_regions)]

# Only filter by depth if the box is checked
if shallow_only:
    filtered = filtered[filtered["depth_type"] == "Shallow"]


# ---------- Show results ----------
if len(filtered) == 0:
    st.warning("No data matches your current filters. Try adjusting your selections.")
else:
    # ---------- Summary statistics ----------
    st.subheader("Summary of Filtered Data")

    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.metric("Total Earthquakes", len(filtered))
    with col2:
        st.metric("Strongest", f"M {filtered['magnitude'].max():.1f}")
    with col3:
        st.metric("Average Magnitude", f"M {filtered['magnitude'].mean():.2f}")
    with col4:
        st.metric("Average Depth", f"{filtered['depth'].mean():.0f} km")

    # ---------- Chart 1: Line chart (time series) ----------
    st.subheader("1. Earthquakes Over Time")

    # Count how many earthquakes of each depth type happened each week
    weekly = filtered.groupby(["week", "depth_type"]).size().reset_index(name="count")

    fig1 = px.line(
        weekly,
        x="week",
        y="count",
        color="depth_type",
        color_discrete_map=depth_colors,
        markers=True,
        title="Number of Earthquakes per Week by Depth",
        labels={"week": "Week", "count": "Number of earthquakes", "depth_type": "Depth"},
    )
    st.plotly_chart(fig1)

    # ---------- Chart 2: Map ----------
    st.subheader("2. Where Did They Happen?")

    fig2 = px.scatter_geo(
        filtered,
        lat="latitude",
        lon="longitude",
        size="magnitude",
        color="depth_type",
        color_discrete_map=depth_colors,
        hover_name="place",
        hover_data=["magnitude", "depth", "date"],
        projection="natural earth",
        title="Earthquake Locations (bigger dot = stronger earthquake)",
        labels={"depth_type": "Depth", "depth": "Depth (km)", "magnitude": "Magnitude", "date": "Date"},
    )
    st.plotly_chart(fig2)
    st.caption("Most earthquakes line up along the edges of tectonic plates, like the Pacific 'Ring of Fire'.")

    # ---------- Chart 3: Bar chart with error bars (uncertainty) ----------
    st.subheader("3. Which Regions Have the Strongest Earthquakes?")

    # For each region, find the average magnitude, the standard deviation, and the count
    stats = filtered.groupby("region")["magnitude"].agg(["mean", "std", "count"]).reset_index()

    # A region with only 1 earthquake has no standard deviation, so use 0
    stats["std"] = stats["std"].fillna(0)

    # Only show the 10 regions with the most earthquakes
    stats = stats.sort_values("count", ascending=False).head(10)

    fig3 = px.bar(
        stats,
        x="region",
        y="mean",
        error_y="std",
        color="count",
        color_continuous_scale="Blues",
        title="Average Magnitude in the 10 Most Active Regions (error bars = standard deviation)",
        labels={"region": "Region", "mean": "Average Magnitude", "std": "Standard deviation", "count": "Number of earthquakes"},
    )
    fig3.update_yaxes(range=[4, 6])
    st.caption("Longer error bars mean the earthquakes in that region vary more in strength. "
               "Darker bars mean more earthquakes. Click a bar to see that region below.")

    # on_select="rerun" lets the user click a bar to filter the next chart
    clicked = st.plotly_chart(fig3, on_select="rerun")

    # ---------- Chart 4: Click a bar to see one region (linked filtering) ----------
    if clicked and clicked["selection"]["point_indices"]:
        selected_idx = clicked["selection"]["point_indices"][0]
        selected_region = stats.iloc[selected_idx]["region"]

        # Filter the data to only the region that was clicked
        region_data = filtered[filtered["region"] == selected_region]

        st.subheader(f"4. Earthquakes in {selected_region}")

        fig4 = px.scatter(
            region_data,
            x="time",
            y="magnitude",
            color="depth_type",
            color_discrete_map=depth_colors,
            hover_name="place",
            title=f"Every Earthquake in {selected_region} (each dot is one earthquake)",
            labels={"time": "Date", "magnitude": "Magnitude", "depth_type": "Depth"},
        )
        st.plotly_chart(fig4)
    else:
        st.info("Click a bar in chart 3 to see every earthquake in that region.")

    # ---------- Data table ----------
    st.subheader("Filtered Data")
    st.dataframe(filtered.drop(columns=["date", "week"]))

st.caption("Data source: U.S. Geological Survey (USGS) Earthquake Catalog, https://earthquake.usgs.gov/earthquakes/search/")
