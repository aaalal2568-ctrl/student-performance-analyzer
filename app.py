
import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt

st.set_page_config(
    page_title="Student Performance Analyzer",
    page_icon="🎓",
    layout="wide"
)

SUBJECTS = ["Math", "Science", "English", "Programming"]
COLUMNS = ["Name"] + SUBJECTS


def load_default_data():
    return pd.read_csv("students.csv")[COLUMNS].copy()


def validate_data(data):
    if not all(col in data.columns for col in COLUMNS):
        raise ValueError(
            "CSV must contain: " + ", ".join(COLUMNS)
        )

    data = data[COLUMNS].copy()

    if data.empty:
        raise ValueError("Please add at least one student.")

    data["Name"] = data["Name"].astype(str).str.strip()

    if data["Name"].eq("").any():
        raise ValueError("Student names cannot be empty.")

    for subject in SUBJECTS:
        data[subject] = pd.to_numeric(
            data[subject], errors="coerce"
        )

    if data[SUBJECTS].isna().any().any():
        raise ValueError("All grades must be valid numbers.")

    if not data[SUBJECTS].apply(
        lambda col: col.between(0, 100)
    ).all().all():
        raise ValueError("Grades must be between 0 and 100.")

    return data


if "students" not in st.session_state:
    st.session_state.students = load_default_data()

st.title("🎓 Student Performance Analyzer")
st.write(
    "Manage student grades and explore academic performance."
)

st.divider()

# ADD STUDENT
st.subheader("➕ Add New Student")

with st.form("add_student_form", clear_on_submit=True):

    name = st.text_input("Student Name")

    col1, col2 = st.columns(2)

    with col1:
        math = st.number_input(
            "Math Grade", 0, 100, 80
        )
        science = st.number_input(
            "Science Grade", 0, 100, 80
        )

    with col2:
        english = st.number_input(
            "English Grade", 0, 100, 80
        )
        programming = st.number_input(
            "Programming Grade", 0, 100, 80
        )

    submitted = st.form_submit_button(
        "Add Student",
        use_container_width=True
    )

    if submitted:
        if not name.strip():
            st.error("Please enter a student name.")
        else:
            new_student = pd.DataFrame([{
                "Name": name.strip(),
                "Math": math,
                "Science": science,
                "English": english,
                "Programming": programming
            }])

            st.session_state.students = pd.concat(
                [st.session_state.students, new_student],
                ignore_index=True
            )

            st.success("Student added successfully!")
            st.rerun()

st.divider()

# UPLOAD CSV
st.subheader("📁 Import Student Data")

uploaded_file = st.file_uploader(
    "Upload CSV File",
    type=["csv"]
)

if uploaded_file is not None:
    try:
        uploaded_df = validate_data(
            pd.read_csv(uploaded_file)
        )

        if st.button("Import CSV Data"):
            st.session_state.students = uploaded_df
            st.success("CSV imported successfully!")
            st.rerun()

    except (ValueError, pd.errors.ParserError) as error:
        st.error(str(error))

st.divider()

# MANAGE STUDENTS
st.subheader("👩‍🎓 Manage Students")

df = st.session_state.students.copy()

if not df.empty:
    student_options = list(df.index)

    selected_student = st.selectbox(
        "Select a student to remove",
        options=student_options,
        format_func=lambda i: f"{i + 1}. {df.loc[i, 'Name']}"
    )

    if st.button("🗑️ Remove Selected Student"):
        st.session_state.students = df.drop(
            index=selected_student
        ).reset_index(drop=True)

        st.rerun()

if st.button("🔄 Reset to Default Data"):
    st.session_state.students = load_default_data()
    st.rerun()

st.divider()

# ANALYSIS
df = st.session_state.students.copy()

if df.empty:
    st.info("Add a student to view the analysis.")
    st.stop()

df["Average"] = df[SUBJECTS].mean(axis=1).round(2)

df["Status"] = df["Average"].apply(
    lambda grade: "Pass" if grade >= 60 else "Fail"
)

overall_average = df["Average"].mean()
highest_average = df["Average"].max()
lowest_average = df["Average"].min()

pass_count = int((df["Status"] == "Pass").sum())
fail_count = int((df["Status"] == "Fail").sum())
pass_rate = pass_count / len(df) * 100

# METRICS
st.subheader("📊 Performance Overview")

col1, col2, col3, col4 = st.columns(4)

col1.metric("Total Students", len(df))
col2.metric("Average Grade", f"{overall_average:.1f}%")
col3.metric("Highest Average", f"{highest_average:.1f}%")
col4.metric("Lowest Average", f"{lowest_average:.1f}%")

st.divider()

# TABLE
st.subheader("📋 Student Results")

st.dataframe(
    df,
    use_container_width=True,
    hide_index=True
)

st.divider()

# STUDENT CHART
st.subheader("📈 Student Performance")

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

# SUBJECT CHART
st.subheader("📚 Subject Analysis")

subject_averages = df[SUBJECTS].mean()

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

# TOP STUDENTS
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

# PASS RATE
st.subheader("🎯 Pass Rate")

col5, col6, col7 = st.columns(3)

col5.metric("Passed Students", pass_count)
col6.metric("Failed Students", fail_count)
col7.metric("Pass Rate", f"{pass_rate:.1f}%")

st.progress(int(round(pass_rate)))

st.divider()

# DOWNLOAD RESULTS
st.subheader("📥 Download Analysis")

csv = df.to_csv(index=False).encode("utf-8")

st.download_button(
    "Download Results as CSV",
    data=csv,
    file_name="student_performance_results.csv",
    mime="text/csv",
    use_container_width=True
)

st.caption(
    "Built with Python, Pandas, Matplotlib & Streamlit"
)
