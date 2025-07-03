import pandas as pd
import streamlit as st
import matplotlib.pyplot as plt
import plotly.express as px

# Page configuration
st.set_page_config(layout="wide")
st.markdown("<h1 style='text-align: center;'>WDRR Sequence Calculator for CL</h1>", unsafe_allow_html=True)

# Load data
@st.cache_data
def load_data():
    df = pd.read_csv("WDRR_seq_CSV.csv")
    df.columns = df.columns.str.strip()
    return df

df = load_data()
# Define colors for each scenario
scenario1_color = "#09AEB2"           # uploaded color for scenario 1
scenario2_color = "mediumslateblue"   # existing scenario 2 color


# Utility function to generate grouped outcome summary
def generate_outcome_summary(filtered_df, scenario_title):
    total_rows = len(filtered_df)
    filtered_df["Outcome"] = filtered_df["End Day"].astype(str) + " " + filtered_df["End point seq"].astype(str)
    outcome_summary = filtered_df.groupby("Outcome").size().reset_index(name="Count")
    outcome_summary["End Day"] = outcome_summary["Outcome"].str.extract(r'(Day \d)').fillna("Unknown")
    outcome_summary["Sequence"] = outcome_summary["Outcome"].str.extract(r'Day \d (.*)')
    outcome_summary["Percentage"] = (outcome_summary["Count"] / outcome_summary["Count"].sum() * 100).round(1)
    day_order = sorted(outcome_summary["End Day"].unique(), key=lambda x: int(x.split()[1]) if x != "Unknown" else 99)

    st.markdown(f"### {scenario_title}")
    st.subheader("\U0001F4CA Outcome Frequencies")
    for i, day in enumerate(day_order, 1):
        group = outcome_summary[outcome_summary["End Day"] == day]
        total = group["Count"].sum()
        pct_total = round((total / outcome_summary["Count"].sum()) * 100, 1)
        st.markdown(f"**{i}. {day}**")
        for _, row in group.iterrows():
            st.markdown(f"&nbsp;&nbsp;&nbsp;&nbsp;{row['Sequence']} / Count: {row['Count']} ({row['Percentage']}%)")
        st.markdown(f"&nbsp;&nbsp;&nbsp;&nbsp;_Outcomes in {day} - {total} ({pct_total}% of total)_\n")

    st.subheader("\U0001F4C8 Outcome Distribution")
    fig, ax = plt.subplots(figsize=(12, 6))
    ax.bar(outcome_summary["Outcome"], outcome_summary["Percentage"])
    ax.set_ylabel("Percentage")
    ax.set_xlabel("Outcome")
    ax.set_xticks(range(len(outcome_summary["Outcome"])))
    ax.set_xticklabels(outcome_summary["Outcome"], rotation=45, ha='right')
    fig.tight_layout()
    st.pyplot(fig)

    st.subheader("\U0001F4E6 Dataset Summary")
    st.write(f"**Number of datasets:** {total_rows}")

    st.subheader("\U0001F9EE End High/Low session possibilities")
    hl_summary = filtered_df["End High/Low"].value_counts().reset_index()
    hl_summary.columns = ["End High/Low", "Count"]
    hl_summary["Percentage"] = (hl_summary["Count"] / hl_summary["Count"].sum() * 100).round(2)
    st.dataframe(hl_summary)

def plot_model_distribution(df, column, scenario, key_prefix, color):
    st.subheader(f"{column} Distribution ({scenario})")
    default_values = sorted(df[column].dropna().unique())
    selected_values = st.multiselect(
        f"Select {column} values to include:",
        default_values,
        default=default_values,
        key=f"{key_prefix}_{column.replace(' ', '_')}_select"
    )
    filtered = df[df[column].isin(selected_values)]
    counts = filtered[column].value_counts().sort_index()
    percentages = (counts / counts.sum() * 100).round(1)
    fig = px.bar(
        x=percentages.index,
        y=percentages.values,
        labels={'x': 'Model Type', 'y': '%'},
        text=[f"{p}%" for p in percentages.values],
    )
    fig.update_traces(marker_color=color, textposition='outside')
    fig.update_layout(yaxis_range=[0, 100])
    st.plotly_chart(fig, use_container_width=True, key=f"{key_prefix}_chart")
    return filtered

# SCENARIO FILTERS
col1, col2 = st.columns(2)
with col1:
    st.header("\U0001F7E2 Scenario 1 Filters")
    conf1 = st.selectbox("Confirmation", ["All"] + sorted(df["Confirmation"].dropna().unique()))
    conf_tf1 = st.selectbox("Confirmation True/False", ["All"] + sorted(df["Conf True/False"].dropna().unique()))
    model1 = st.selectbox("Model (Tuesday RDR-Wednesday ODR)", ["All"] + sorted(df["Model"].dropna().unique()))
    start_day1 = st.selectbox("Start Day", ["All"] + sorted(df["Start Day"].dropna().unique()))
    start_hl1 = st.selectbox("Starting Point High/Low", ["All"] + sorted(df["Start High/Low.1"].dropna().unique()))
    start_point1 = st.selectbox("Start point", ["All"] + sorted(df["Start point seq"].dropna().unique()))  # <-- NEW FILTER
    start_sess1 = st.selectbox("Starting Point Session", ["", "All"] + sorted(df["Start session"].dropna().unique()))

with col2:
    st.header("\U0001F535 Scenario 2 Filters")
    conf2 = st.selectbox("Confirmation ", ["All"] + sorted(df["Confirmation"].dropna().unique()), key="conf2")
    conf_tf2 = st.selectbox("Confirmation True/False", ["All"] + sorted(df["Conf True/False"].dropna().unique()), key="conf_tf2")
    model2 = st.selectbox("Model (Tuesday RDR-Wednesday ODR)", ["All"] + sorted(df["Model"].dropna().unique()), key="model2")
    start_day2 = st.selectbox("Start Day ", ["All"] + sorted(df["Start Day"].dropna().unique()), key="start_day2")
    start_hl2 = st.selectbox("Starting Point High/Low ", ["All"] + sorted(df["Start High/Low.1"].dropna().unique()), key="start_hl2")
    start_point2 = st.selectbox("Start point ", ["All"] + sorted(df["Start point seq"].dropna().unique()), key="start_point2")  # <-- NEW FILTER
    start_sess2 = st.selectbox("Starting Point Session ", ["", "All"] + sorted(df["Start session"].dropna().unique()), key="start_sess2")

# APPLY SCENARIO FILTERS
filtered1 = df.copy()
filtered2 = df.copy()
filters1 = [
    (conf1, "Confirmation"), (conf_tf1, "Conf True/False"), (model1, "Model"),
    (start_day1, "Start Day"), (start_hl1, "Start High/Low.1"), (start_point1, "Start point seq"), (start_sess1, "Start session")
]
filters2 = [
    (conf2, "Confirmation"), (conf_tf2, "Conf True/False"), (model2, "Model"),
    (start_day2, "Start Day"), (start_hl2, "Start High/Low.1"), (start_point2, "Start point seq"), (start_sess2, "Start session")
]
for val, col in filters1:
    if val not in ["", "All"]:
        filtered1 = filtered1[filtered1[col] == val]
for val, col in filters2:
    if val not in ["", "All"]:
        filtered2 = filtered2[filtered2[col] == val]

# DISPLAY RESULTS
st.divider()
col3, col4 = st.columns(2)
with col3:
    if not filtered1.empty:
        generate_outcome_summary(filtered1, "\U0001F7E2 Scenario 1 Results")
    else:
        st.warning("No data found for Scenario 1 filters.")
with col4:
    if not filtered2.empty:
        generate_outcome_summary(filtered2, "\U0001F535 Scenario 2 Results")
    else:
        st.warning("No data found for Scenario 2 filters.")

# The rest of your existing Weekly High/Low Day section, Weekly Model Distribution, and comparison sections go here unchanged.
# They will automatically use the filtered1 and filtered2 DataFrames updated with the new filter.


# WEEKLY HIGH AND LOW DAY SECTION
st.divider()
st.markdown("<h2 style='text-align: center;'>📅 Weekly High and Low Day</h2>", unsafe_allow_html=True)

hl1_high = sorted(filtered1["High Day"].dropna().unique())
hl1_low = sorted(filtered1["Low Day"].dropna().unique())
hl2_high = sorted(filtered2["High Day"].dropna().unique())
hl2_low = sorted(filtered2["Low Day"].dropna().unique())

col_hd1, col_ld1, col_hd2, col_ld2 = st.columns(4)

with col_hd1:
    st.subheader("High Day Distribution (Scenario 1)")
    s1_high_selected = st.multiselect(
        "Select High Day to include:",
        hl1_high,
        default=hl1_high,
        key="s1_high_multi",
    )
with col_ld1:
    st.subheader("Low Day Distribution (Scenario 1)")
    s1_low_selected = st.multiselect(
        "Select Low Day to include:",
        hl1_low,
        default=hl1_low,
        key="s1_low_multi",
    )
with col_hd2:
    st.subheader("High Day Distribution (Scenario 2)")
    s2_high_selected = st.multiselect(
        "Select High Day to include:",
        hl2_high,
        default=hl2_high,
        key="s2_high_multi",
    )
with col_ld2:
    st.subheader("Low Day Distribution (Scenario 2)")
    s2_low_selected = st.multiselect(
        "Select Low Day to include:",
        hl2_low,
        default=hl2_low,
        key="s2_low_multi",
    )

# Apply combined filtering per scenario
hl_filtered1 = filtered1[
    filtered1["High Day"].isin(s1_high_selected) & filtered1["Low Day"].isin(s1_low_selected)
]
hl_filtered2 = filtered2[
    filtered2["High Day"].isin(s2_high_selected) & filtered2["Low Day"].isin(s2_low_selected)
]

# Plot charts
with col_hd1:
    counts = hl_filtered1["High Day"].value_counts().sort_index()
    percentages = (counts / counts.sum() * 100).round(1)
    fig = px.bar(
        x=[f"Day {int(d)}" if str(d).isdigit() else str(d) for d in percentages.index],
        y=percentages.values,
        labels={'x': 'Day', 'y': '%'},
        text=[f"{p}%" for p in percentages.values],
    )
    fig.update_traces(marker_color='#09AEB2', textposition='outside')
    fig.update_layout(yaxis_range=[0, 100])
    st.plotly_chart(fig, use_container_width=True, key="s1_hd_plot")

with col_ld1:
    counts = hl_filtered1["Low Day"].value_counts().sort_index()
    percentages = (counts / counts.sum() * 100).round(1)
    fig = px.bar(
        x=[f"Day {int(d)}" if str(d).isdigit() else str(d) for d in percentages.index],
        y=percentages.values,
        labels={'x': 'Day', 'y': '%'},
        text=[f"{p}%" for p in percentages.values],
    )
    fig.update_traces(marker_color='#09AEB2', textposition='outside')
    fig.update_layout(yaxis_range=[0, 100])
    st.plotly_chart(fig, use_container_width=True, key="s1_ld_plot")

with col_hd2:
    counts = hl_filtered2["High Day"].value_counts().sort_index()
    percentages = (counts / counts.sum() * 100).round(1)
    fig = px.bar(
        x=[f"Day {int(d)}" if str(d).isdigit() else str(d) for d in percentages.index],
        y=percentages.values,
        labels={'x': 'Day', 'y': '%'},
        text=[f"{p}%" for p in percentages.values],
    )
    fig.update_traces(marker_color='mediumslateblue', textposition='outside')
    fig.update_layout(yaxis_range=[0, 100])
    st.plotly_chart(fig, use_container_width=True, key="s2_hd_plot")

with col_ld2:
    counts = hl_filtered2["Low Day"].value_counts().sort_index()
    percentages = (counts / counts.sum() * 100).round(1)
    fig = px.bar(
        x=[f"Day {int(d)}" if str(d).isdigit() else str(d) for d in percentages.index],
        y=percentages.values,
        labels={'x': 'Day', 'y': '%'},
        text=[f"{p}%" for p in percentages.values],
    )
    fig.update_traces(marker_color='mediumslateblue', textposition='outside')
    fig.update_layout(yaxis_range=[0, 100])
    st.plotly_chart(fig, use_container_width=True, key="s2_ld_plot")

# WEEKLY MODEL DISTRIBUTION SECTION
st.divider()
st.markdown("<h2 style='text-align: center;'>📊 Weekly Model Distribution</h2>", unsafe_allow_html=True)

model_filtered1, model_filtered2 = filtered1.copy(), filtered2.copy()
s1_cols = st.columns(4)
for i, day in enumerate(["Day 2 Model", "Day 3 Model", "Day 4 Model", "Day 5 Model"]):
    with s1_cols[i]:
        model_filtered1 = plot_model_distribution(model_filtered1, day, "", key_prefix=f"s1_{day.replace(' ', '_')}", color=scenario1_color)

s2_cols = st.columns(4)
for i, day in enumerate(["Day 2 Model", "Day 3 Model", "Day 4 Model", "Day 5 Model"]):
    with s2_cols[i]:
        model_filtered2 = plot_model_distribution(model_filtered2, day, "", key_prefix=f"s2_{day.replace(' ', '_')}", color=scenario2_color)


# FINAL COMPARISON SECTION
st.divider()
st.markdown("<h3 style='text-align: center;'>\U0001F50D Comparison</h3>", unsafe_allow_html=True)
count1, count2 = len(filtered1), len(filtered2)
combined_total = count1 + count2 if count1 + count2 > 0 else 1
pct1, pct2 = round((count1/combined_total)*100, 1), round((count2/combined_total)*100, 1)
c1, c2, c3 = st.columns([1,2,1])
with c2:
    st.markdown(f"<p style='text-align: center;'><strong>Scenario 1:</strong> {pct1}% ({count1} datasets)</p>", unsafe_allow_html=True)
    st.markdown(f"<p style='text-align: center;'><strong>Scenario 2:</strong> {pct2}% ({count2} datasets)</p>", unsafe_allow_html=True)

# PERCENTAGE OF OCCURRENCE SECTION
st.divider()
st.markdown("<h3 style='text-align: center;'>\U0001F4CC Percentage of occurrence</h3>", unsafe_allow_html=True)
full_total = len(df)
occ_pct1, occ_pct2 = round((count1/full_total)*100,1), round((count2/full_total)*100,1)
c4, c5, c6 = st.columns([1,2,1])
with c5:
    st.markdown(f"<p style='text-align: center;'><strong>Scenario 1:</strong> {occ_pct1}% of total ({count1} datasets from {full_total})</p>", unsafe_allow_html=True)
    st.markdown(f"<p style='text-align: center;'><strong>Scenario 2:</strong> {occ_pct2}% of total ({count2} datasets from {full_total})</p>", unsafe_allow_html=True)
