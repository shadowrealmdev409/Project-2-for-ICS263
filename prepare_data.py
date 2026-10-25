# Downloads and cleans the earthquake data used by app.py.
# You only need to run this once: python prepare_data.py
# It saves the cleaned data to data/earthquakes_2024.csv

import pandas as pd

# USGS Earthquake Catalog: all earthquakes of magnitude 4.5 or higher in 2024
url = (
    "https://earthquake.usgs.gov/fdsnws/event/1/query?format=csv"
    "&starttime=2024-01-01&endtime=2025-01-01&minmagnitude=4.5&orderby=time-asc"
)
df = pd.read_csv(url)


# The "place" column looks like "272 km N of Saipan, Northern Mariana Islands".
# We want just the region at the end, like "Northern Mariana Islands".
def get_region(place):
    if ", " in place:
        region = place.split(", ")[-1]
    elif " of " in place:
        region = place.split(" of ")[-1]
    else:
        region = place

    # Clean up names so "the Fiji Islands", "Fiji region" and "Fiji" all match
    region = region.replace(" region", "").replace(" Earthquake", "")
    for word in ["the ", "northern ", "southern ", "central ", "eastern ", "western "]:
        if region.startswith(word):
            region = region[len(word):]
    if region == "Fiji Islands":
        region = "Fiji"
    return region


df["region"] = df["place"].apply(get_region)


# Group earthquakes by depth using the standard USGS depth classes
def get_depth_type(depth):
    if depth < 70:
        return "Shallow"
    elif depth < 300:
        return "Intermediate"
    else:
        return "Deep"


df["depth_type"] = df["depth"].apply(get_depth_type)

# Turn the time text into a real date (and remove the UTC time zone to keep things simple)
df["time"] = pd.to_datetime(df["time"]).dt.tz_localize(None)

# The first day (Monday) of the week each earthquake happened in, for the weekly line chart
df["week"] = df["time"].dt.to_period("W").dt.start_time

# Keep only the columns the app uses
df = df[["time", "week", "latitude", "longitude", "depth", "depth_type", "mag", "place", "region"]]
df = df.rename(columns={"mag": "magnitude"})

df.to_csv("data/earthquakes_2024.csv", index=False)
print(f"Saved {len(df)} earthquakes from {df['region'].nunique()} regions")
