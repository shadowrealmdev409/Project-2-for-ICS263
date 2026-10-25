# Part 4: Reflection (Draft)

> Draft: edit this so it sounds like you, and add your own experiences (especially the User Testing section) before you submit.

## Filtering Implementation

I used pandas for all of the filtering in the app. Each sidebar control returns a value, and I combined those values into one boolean mask with the `&` operator. For example, `df["Continent"].isin(selected_continents)` keeps only the continents the user picked, and `df["GDP per Capita"] >= gdp_range[0]` together with the matching `<=` check keeps rows inside the slider range. The "large countries only" checkbox is handled by a separate `if` statement, because it only applies when the box is checked. Doing all the filtering in one place at the top of the script means every chart and statistic below uses the same `filtered` DataFrame.

The biggest data type challenge was time. The Gapminder dataset stores the year as a plain integer, but Streamlit's `date_input` widget works with real dates. I created a new `date` column by combining the year with "-01-01" and running it through `pd.to_datetime`. Then I had to convert the widget's values back with `pd.to_datetime` before comparing them, because pandas cannot compare a datetime column to a Python `date` object directly. Another surprise was that `date_input` returns only one date while the user is still choosing the second one. Without a check, the app crashed when trying to unpack two values, so I added a fallback that uses the full range until both dates are selected.

Numeric data needed some care too. GDP per capita is a float with a very wide range (about $241 up to over $113,000), so I converted the minimum and maximum to integers and used a step of 500 to keep the slider usable. Finally, I handled the edge case where filters remove every row. If the filtered DataFrame is empty, the app shows a warning explaining which filters to loosen and then calls `st.stop()` so the charts do not try to draw empty data and throw errors.

## Interactivity Design

The multi-select for continents felt the most intuitive, because it shows exactly what is included and lets users remove a continent with one click. The checkbox was also very easy to understand since it is a simple yes or no question. The date range picker was the least intuitive: the data is only recorded every five years, so picking a random date like March 1980 just snaps to the nearest available years. I added help text explaining that the data is recorded every five years to make this clearer.

To balance flexibility with usability, I put all of the main filters in the sidebar so they do not clutter the charts, and I set every filter's default to "include everything." That way users see the full picture first and then narrow it down. I also added numbered instructions at the top of the page. The map has its own year slider, because a map can only show one year at a time. That slider only offers years that survived the sidebar filters, so users cannot pick a year with no data. The year chosen on the map also controls the confidence interval chart, which is an example of linked filtering: one control updates two charts at once, and the sidebar filters update all three charts and the summary statistics.

## Technical Decisions

I chose a **line chart** for the time series because life expectancy is a continuous trend, and lines make it easy to compare the slope of each continent over time. I added markers so it is clear that the data points are five years apart. For the geographic view, I used a **choropleth map**, because coloring each country makes regional patterns, like the gap between Sub-Saharan Africa and Europe, visible immediately. I fixed the color scale range to the full dataset so colors mean the same thing no matter which year or filter is selected. Otherwise, a country could look "high" just because the filters removed the countries above it.

For uncertainty, I used a **bar chart with error bars** showing a 95% confidence interval for each continent's average life expectancy, calculated as 1.96 times the standard deviation divided by the square root of the number of countries. This shows that Oceania's average, for example, is based on only two countries, so its interval is very wide compared to Africa's, which has 52 countries. When a group has only one country, the standard deviation is missing, so I replaced it with zero to avoid an error.

Color is used on purpose, not for decoration. Each continent has the same color in the line chart and the bar chart, so users can connect them. The map uses the Viridis sequential scale because life expectancy is a continuous value, and Viridis is readable for people with color blindness.

For performance, the dataset is small (1,704 rows), but Streamlit reruns the whole script every time a filter changes. I used `@st.cache_data` on the loading function so the CSV is only read and processed once. The pandas filtering on top of that is fast. With a much larger dataset, I would also pre-aggregate the data and cache the grouped results.

## User Testing (Optional)

*Add your own notes here if you tested the app with anyone. For example: who tried it, what confused them, and what you changed afterward.*
