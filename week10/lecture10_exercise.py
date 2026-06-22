import streamlit as st
import pandas as pd
import plotly.express as px
from pathlib import Path

st.set_page_config(
    page_title="CO2 Dashboard",
    page_icon="🌱",
    layout="wide"
)

# ---------------- DATA ----------------

@st.cache_data
def load_data():

    path = Path(__file__).parent / "co2_emissions.csv"

    df = pd.read_csv(path)

    df["Date"] = pd.to_datetime(
        df["Year"].astype(str) + "-01-01"
    )

    return df


df = load_data()

st.title("🌱 CO2 Emissions Explorer")

st.caption(
    "Source: Our World in Data"
)

# ---------------- SIDEBAR ----------------

with st.sidebar:

    st.header("Filters")

    regions = ["All"] + sorted(
        df["Region"].unique().tolist()
    )

    selected_region = st.selectbox(
        "Region",
        regions
    )

    if selected_region == "All":

        countries = sorted(
            df["Country"].unique()
        )

    else:

        countries = sorted(

            df[
                df["Region"] == selected_region
            ]["Country"].unique()

        )

    selected_countries = st.multiselect(

        "Countries",

        countries,

        default=countries[:5]

    )

    min_date = df["Date"].min().date()

    max_date = df["Date"].max().date()

    date_range = st.date_input(

        "Date Range",

        value=(min_date, max_date),

        min_value=min_date,

        max_value=max_date

    )

    metric = st.radio(

        "Metric",

        [

            "Total CO2 (Mt)",

            "CO2 per capita"

        ]

    )

    highlight = st.checkbox(

        "Show only top emitter highlighted"

    )

# ---------------- GUARDS ----------------

if len(selected_countries) == 0:

    st.warning("Please select at least one country.")

    st.stop()

if len(date_range) != 2:

    st.warning("Please select start and end date.")

    st.stop()

start_date = pd.Timestamp(date_range[0])

end_date = pd.Timestamp(date_range[1])

# ---------------- FILTER ----------------

filtered = df[

    (df["Country"].isin(selected_countries))

    &

    (df["Date"] >= start_date)

    &

    (df["Date"] <= end_date)

]

if selected_region != "All":

    filtered = filtered[

        filtered["Region"] == selected_region

    ]

# ---------------- METRIC ----------------

if metric == "Total CO2 (Mt)":

    y_col = "CO2_Mt"

else:

    y_col = "CO2_per_capita"

# ---------------- SUMMARY ----------------

st.caption(

    f"{len(selected_countries)} Countries | "

    f"{selected_region} | "

    f"{start_date.year}-{end_date.year} | "

    f"{metric} | "

    f"{len(filtered)} records"

)

# ---------------- KPI ----------------

latest_year = filtered["Year"].max()

latest_df = filtered[

    filtered["Year"] == latest_year

]

total = latest_df[y_col].sum()

first_year = filtered["Year"].min()

first_df = filtered[

    filtered["Year"] == first_year

]

first_total = first_df[y_col].sum()

if first_total != 0:

    change = (

        (total - first_total)

        / first_total

    ) * 100

else:

    change = 0

top_country = latest_df.loc[

    latest_df[y_col].idxmax(),

    "Country"

]

k1, k2, k3 = st.columns(3)

k1.metric(

    "Total CO2",

    f"{total:.2f}"

)

k2.metric(

    "% Change",

    f"{change:.2f}%"

)

k3.metric(

    "Top Country",

    top_country

)

# ---------------- CHARTS ----------------

left, right = st.columns([2,1])

with left:

    fig = px.line(

        filtered,

        x="Year",

        y=y_col,

        color="Country",

        markers=True,

        title="CO2 Emissions Over Time"

    )

    fig.update_layout(

        template="plotly_white"

    )

    st.plotly_chart(

        fig,

        use_container_width=True

    )

with right:

    rank_df = latest_df.sort_values(

        y_col,

        ascending=False

    )

    fig2 = px.bar(

        rank_df,

        x="Country",

        y=y_col,

        title=f"Ranking in {latest_year}"

    )

    fig2.update_layout(

        template="plotly_white"

    )

    st.plotly_chart(

        fig2,

        use_container_width=True

    )