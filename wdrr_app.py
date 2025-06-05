import pandas as pd
import streamlit as st
import matplotlib.pyplot as plt

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

# Utility function to generate grouped outcome summary
def generate_outcome_summary(filtered_df, scenario_title):
    total_rows = len(filtered_df)
    filtered_df["Outcome"] = filtered_df["End Day"].astype(str) + " " + filtered_df["End point seq"].astype(str)

    outcome_summary = (
        filtered_df.groupby("Outcome")
        .size()
        .reset_index(name="Count")
    )
    outcome_summary["End Day"] = outcome_summary["Outcome"].str.extract(r'(Day \d)').fillna("Unknown")
    outcome_summary["Sequence"] = outcome_summary["Outcome"].str.extract(r'Day \d (.*)')
    outcome_summary["Percentage"] = (outcome_summary["Count"] / outcome_summary["Count"].sum() * 100).round(1)

    day_order = sorted(outcome_summary["End Day"].unique(), key=lambda x: int(x.split()[1]) if x != "Unknown" else 99)

    st.markdown(f"### {scenario_title}")
    st.subheader("📊 Outcome Frequencies")
    for i, day in enumerate(day_order, 1):
        group = outcome_summary[outcome_summary["End Day"] == day]
        total = group["Count"].sum()
        pct_total = round((total / outcome_summary["Count"].sum()) * 100, 1)
        st.markdown(f"**{i}. {day}**")
        for _, row in group.iterrows():
            st.markdown(f"&nbsp;&nbsp;&nbsp;&nbsp;{row['Sequence']} / Count: {row['Count']} ({row['Percentage']}%)")
        st.markdown(f"&nbsp;&nbsp;&nbsp;&nbsp;_Outcomes in {day} - {total} ({pct_total}% of total)_\n")

    st.subheader("📈 Outcome Distribution")
    fig, ax = plt.subplots(figsize=(12, 6))
    ax.bar(outcome_summary["Outcome"], outcome_summary["Percentage"])
    ax.set_ylabel("Percentage")
    ax.set_xlabel("Outcome")
    ax.set_xticks(range(len(outcome_summary["Outcome"])))
    ax.set_xticklabels(outcome_summary["Outcome"], rotation=45, ha='right')
    fig.tight_layout()
    st.pyplot(fig)

    st.subheader("📦 Dataset Summary")
    st.write(f"**Number of datasets:** {total_rows}")

    st.subheader("🧮 End High/Low session possibilities")
    hl_summary = filtered_df["End High/Low"].value_counts().reset_index()
    hl_summary.columns = ["End High/Low", "Count"]
    hl_summary["Percentage"] = (hl_summary["Count"] / hl_summary["Count"].sum() * 100).round(2)
    st.dataframe(hl_summary)

# SCENARIO FILTERS
col1, col2 = st.columns(2)

with col1:
    st.header("🟢 Scenario 1 Filters")
    conf1 = st.selectbox("Confirmation", ["All"] + sorted(df["Confirmation"].dropna().unique()))
    conf_tf1 = st.selectbox("Confirmation True/False", ["All"] + sorted(df["Conf True/False"].dropna().unique()))
    model1 = st.selectbox("Model (Tuesday RDR-Wednesday ODR)", ["All"] + sorted(df["Model"].dropna().unique()))
    start_day1 = st.selectbox("Start Day", ["All"] + sorted(df["Start Day"].dropna().unique()))
    start_hl1 = st.selectbox("Starting Point High/Low", ["All"] + sorted(df["Start High/Low.1"].dropna().unique()))
    start_sess1 = st.selectbox("Starting Point Session", ["", "All"] + sorted(df["Start session"].dropna().unique()))

with col2:
    st.header("🔵 Scenario 2 Filters")
    conf2 = st.selectbox("Confirmation ", ["All"] + sorted(df["Confirmation"].dropna().unique()), key="conf2")
    conf_tf2 = st.selectbox("Confirmation True/False", ["All"] + sorted(df["Conf True/False"].dropna().unique()), key="conf_tf2")
    model2 = st.selectbox("Model (Tuesday RDR-Wednesday ODR)", ["All"] + sorted(df["Model"].dropna().unique()), key="model2")
    start_day2 = st.selectbox("Start Day ", ["All"] + sorted(df["Start Day"].dropna().unique()), key="start_day2")
    start_hl2 = st.selectbox("Starting Point High/Low ", ["All"] + sorted(df["Start High/Low.1"].dropna().unique()), key="start_hl2")
    start_sess2 = st.selectbox("Starting Point Session ", ["", "All"] + sorted(df["Start session"].dropna().unique()), key="start_sess2")

# APPLY FILTERS
filtered1 = df.copy()
if conf1 != "All":
    filtered1 = filtered1[filtered1["Confirmation"] == conf1]
if conf_tf1 != "All":
    filtered1 = filtered1[filtered1["Conf True/False"] == conf_tf1]
if model1 != "All":
    filtered1 = filtered1[filtered1["Model"] == model1]
if start_day1 != "All":
    filtered1 = filtered1[filtered1["Start Day"] == start_day1]
if start_hl1 != "All":
    filtered1 = filtered1[filtered1["Start High/Low.1"] == start_hl1]
if start_sess1 not in ["", "All"]:
    filtered1 = filtered1[filtered1["Start session"] == start_sess1]

filtered2 = df.copy()
if conf2 != "All":
    filtered2 = filtered2[filtered2["Confirmation"] == conf2]
if conf_tf2 != "All":
    filtered2 = filtered2[filtered2["Conf True/False"] == conf_tf2]
if model2 != "All":
    filtered2 = filtered2[filtered2["Model"] == model2]
if start_day2 != "All":
    filtered2 = filtered2[filtered2["Start Day"] == start_day2]
if start_hl2 != "All":
    filtered2 = filtered2[filtered2["Start High/Low.1"] == start_hl2]
if start_sess2 not in ["", "All"]:
    filtered2 = filtered2[filtered2["Start session"] == start_sess2]

# DISPLAY RESULTS
st.divider()
col3, col4 = st.columns(2)
with col3:
    if not filtered1.empty:
        generate_outcome_summary(filtered1, "🟢 Scenario 1 Results")
    else:
        st.warning("No data found for Scenario 1 filters.")

with col4:
    if not filtered2.empty:
        generate_outcome_summary(filtered2, "🔵 Scenario 2 Results")
    else:
        st.warning("No data found for Scenario 2 filters.")

# FINAL COMPARISON SECTION
st.divider()
st.markdown("<h3 style='text-align: center;'>🔍 Comparison</h3>", unsafe_allow_html=True)

count1 = len(filtered1)
count2 = len(filtered2)
combined_total = count1 + count2 if count1 + count2 > 0 else 1

pct1 = round((count1 / combined_total) * 100, 1)
pct2 = round((count2 / combined_total) * 100, 1)

c1, c2, c3 = st.columns([1, 2, 1])
with c2:
    st.markdown(f"<p style='text-align: center;'><strong>Scenario 1:</strong> {pct1}% ({count1} datasets)</p>", unsafe_allow_html=True)
    st.markdown(f"<p style='text-align: center;'><strong>Scenario 2:</strong> {pct2}% ({count2} datasets)</p>", unsafe_allow_html=True)

# PERCENTAGE OF OCCURRENCE SECTION
st.divider()
st.markdown("<h3 style='text-align: center;'>📌 Percentage of occurrence</h3>", unsafe_allow_html=True)

full_total = len(df)
occ_pct1 = round((count1 / full_total) * 100, 1)
occ_pct2 = round((count2 / full_total) * 100, 1)

c4, c5, c6 = st.columns([1, 2, 1])
with c5:
    st.markdown(f"<p style='text-align: center;'><strong>Scenario 1:</strong> {occ_pct1}% of total ({count1} datasets from {full_total})</p>", unsafe_allow_html=True)
    st.markdown(f"<p style='text-align: center;'><strong>Scenario 2:</strong> {occ_pct2}% of total ({count2} datasets from {full_total})</p>", unsafe_allow_html=True)
