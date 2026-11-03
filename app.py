
import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt

st.set_page_config(
    page_title="Student Performance Analyzer",
    page_icon="🎓",
    layout="wide"
)

st.title("🎓 Student Performance Analyzer")
st.write("Analyze student grades, track performance, and explore insights.")

st.divider()

uploaded_file = st.file_uploader(
    "Upload Student Data (CSV)",
    type=["csv"]
)

if uploaded_file is not None:
    df = pd.read_csv(uploaded_file)
else:
    df = pd.read_csv("students.csv")

subjects = ["Math", "Science", "English", "Programming"]

required_columns = ["Name"] + subjects

if not all(col in df.columns for col in required_columns):
    st.error("CSV must contain: " + ", ".join(required_columns))
    st.stop()

for subject in subjects:
    df[subject] = pd.to_numeric(df[subject], errors="coerce")

if df.empty or df[subjects].isna().any().any():
    st.error("Please provide valid numeric grades for every student.")
    st.stop()

if not df[subjects].apply(lambda col: col.between(0, 100)).all().all():
    st.error("All grades must be between 0 and 100.")
    st.stop()

df["Average"] = df[subjects].mean(axis=1).round(2)
df["Status"] = df["Average"].apply(
    lambda grade: "Pass" if grade >= 60 else "Fail"
)

overall_average = df["Average"].mean()
highest_grade = df["Average"].max()
lowest_grade = df["Average"].min()
pass_count = (df["Status"] == "Pass").sum()
pass_rate = pass_count / len(df) * 100

st.subheader("📊 Performance Overview")

col1, col2, col3, col4 = st.columns(4)

col1.metric("Total Students", len(df))
col2.metric("Average Grade", f"{overall_average:.1f}%")
col3.metric("Highest Average", f"{highest_grade:.1f}%")
col4.metric("Lowest Average", f"{lowest_grade:.1f}%")

st.divider()

st.subheader("📋 Student Results")

st.dataframe(
    df,
    use_container_width=True,
    hide_index=True
)

st.divider()

st.subheader("📈 Student Performance Chart")

fig, ax = plt.subplots(figsize=(10, 5))

colors = [
    "#16a34a" if grade >= 60 else "#dc2626"
    for grade in df["Average"]
]

ax.bar(df["Name"], df["Average"], color=colors)
ax.set_xlabel("Students")
ax.set_ylabel("Average Grade")
ax.set_title("Average Grade by Student")
ax.set_ylim(0, 100)
plt.xticks(rotation=45)
plt.tight_layout()

st.pyplot(fig)
plt.close(fig)

st.divider()

st.subheader("📚 Subject Analysis")

subject_averages = df[subjects].mean()

fig2, ax2 = plt.subplots(figsize=(9, 4))

ax2.bar(
    subject_averages.index,
    subject_averages.values,
    color="#6366f1"
)

ax2.set_ylabel("Average Grade")
ax2.set_title("Average Performance by Subject")
ax2.set_ylim(0, 100)
plt.tight_layout()

st.pyplot(fig2)
plt.close(fig2)

st.divider()

st.subheader("🏆 Top Performing Students")

top_students = df.sort_values(
    by="Average",
    ascending=False
).head(3)

st.dataframe(
    top_students[["Name", "Average", "Status"]],
    use_container_width=True,
    hide_index=True
)

st.divider()

st.subheader("🎯 Pass Rate")

col5, col6 = st.columns(2)

col5.metric("Passed Students", int(pass_count))
col6.metric("Pass Rate", f"{pass_rate:.1f}%")

st.progress(int(round(pass_rate)))

st.divider()

st.subheader("📥 Download Analysis")

csv = df.to_csv(index=False).encode("utf-8")

st.download_button(
    label="Download Results as CSV",
    data=csv,
    file_name="student_performance_results.csv",
    mime="text/csv"
)

st.caption("Built with Python, Pandas, Matplotlib & Streamlit")
