
import streamlit as st
import pandas as pd
import plotly.express as px

st.set_page_config(
    page_title="Student Performance Analyzer",
    page_icon="🎓",
    layout="wide"
)

SUBJECTS = ["Math", "Science", "English", "Programming"]
COLUMNS = ["Name"] + SUBJECTS


def validate_data(data):
    if not all(col in data.columns for col in COLUMNS):
        raise ValueError(
            "CSV must contain: " + ", ".join(COLUMNS)
        )

    data = data[COLUMNS].copy()

    if data.empty:
        raise ValueError("Please provide at least one student.")

    data["Name"] = data["Name"].fillna("").astype(str).str.strip()

    if data["Name"].eq("").any():
        raise ValueError("Student names cannot be empty.")

    for subject in SUBJECTS:
        data[subject] = pd.to_numeric(
            data[subject], errors="coerce"
        )

    if data[SUBJECTS].isna().any().any():
        raise ValueError("All grades must be numeric.")

    if not data[SUBJECTS].apply(
        lambda col: col.between(0, 100)
    ).all().all():
        raise ValueError("Grades must be between 0 and 100.")

    return data.reset_index(drop=True)


def default_data():
    return validate_data(pd.read_csv("students.csv"))


if "students" not in st.session_state:
    st.session_state.students = default_data()


st.title("🎓 Student Performance Analyzer")
st.write(
    "An interactive dashboard for managing and analyzing "
    "student academic performance."
)

st.caption("Python • Pandas • Plotly • Streamlit")
st.divider()

# ADD STUDENT
st.subheader("➕ Add New Student")

with st.form("add_student", clear_on_submit=True):
    name = st.text_input("Student Name")

    c1, c2 = st.columns(2)

    with c1:
        math = st.number_input("Math", 0, 100, 80)
        science = st.number_input("Science", 0, 100, 80)

    with c2:
        english = st.number_input("English", 0, 100, 80)
        programming = st.number_input(
            "Programming", 0, 100, 80
        )

    add = st.form_submit_button(
        "Add Student",
        use_container_width=True
    )

    if add:
        if not name.strip():
            st.error("Please enter a student name.")
        else:
            new_row = pd.DataFrame([{
                "Name": name.strip(),
                "Math": math,
                "Science": science,
                "English": english,
                "Programming": programming
            }])

            st.session_state.students = pd.concat(
                [st.session_state.students, new_row],
                ignore_index=True
            )

            st.rerun()

st.divider()

# IMPORT DATA
st.subheader("📁 Import Student Data")

uploaded_file = st.file_uploader(
    "Upload a CSV file",
    type=["csv"]
)

if uploaded_file is not None:
    try:
        imported_data = validate_data(
            pd.read_csv(uploaded_file)
        )

        if st.button("Import CSV"):
            st.session_state.students = imported_data
            st.rerun()

    except (ValueError, pd.errors.ParserError) as error:
        st.error(str(error))

st.divider()

# EDIT STUDENTS
st.subheader("✏️ Edit Student Grades")

st.info(
    "Edit names or grades directly in the table. "
    "Changes update the charts automatically."
)

edited_df = st.data_editor(
    st.session_state.students,
    num_rows="dynamic",
    use_container_width=True,
    hide_index=True,
    key="student_editor",
    column_config={
        "Name": st.column_config.TextColumn(
            "Student Name",
            required=True
        ),
        **{
            subject: st.column_config.NumberColumn(
                subject,
                min_value=0,
                max_value=100,
                step=1,
                required=True
            )
            for subject in SUBJECTS
        }
    }
)

if st.button("💾 Save Changes", use_container_width=True):
    try:
        st.session_state.students = validate_data(edited_df)
        st.success("Changes saved successfully!")
        st.rerun()
    except ValueError as error:
        st.error(str(error))

if st.button("🔄 Reset Default Data"):
    st.session_state.students = default_data()
    st.rerun()

st.divider()

# ANALYSIS
df = st.session_state.students.copy()

if df.empty:
    st.warning("Add a student to view the analysis.")
    st.stop()

df["Average"] = df[SUBJECTS].mean(axis=1).round(2)
df["Status"] = df["Average"].apply(
    lambda grade: "Pass" if grade >= 60 else "Fail"
)

# FILTERS
st.subheader("🔎 Filter Results")

selected_subject = st.selectbox(
    "Select a subject",
    ["Overall Average"] + SUBJECTS
)

selected_status = st.selectbox(
    "Student Status",
    ["All", "Pass", "Fail"]
)

filtered_df = df.copy()

if selected_status != "All":
    filtered_df = filtered_df[
        filtered_df["Status"] == selected_status
    ]

grade_column = (
    "Average"
    if selected_subject == "Overall Average"
    else selected_subject
)

st.divider()

# METRICS
st.subheader("📊 Performance Overview")

if filtered_df.empty:
    st.warning("No students match the selected filters.")
    st.stop()

average = filtered_df[grade_column].mean()
highest = filtered_df[grade_column].max()
lowest = filtered_df[grade_column].min()

m1, m2, m3, m4 = st.columns(4)

m1.metric("Students", len(filtered_df))
m2.metric("Average Grade", f"{average:.1f}%")
m3.metric("Highest Grade", f"{highest:.1f}%")
m4.metric("Lowest Grade", f"{lowest:.1f}%")

st.divider()

# RESULTS TABLE
st.subheader("📋 Student Results")

st.dataframe(
    filtered_df,
    use_container_width=True,
    hide_index=True
)

# INTERACTIVE BAR CHART
st.subheader("📈 Interactive Student Performance")

fig = px.bar(
    filtered_df,
    x="Name",
    y=grade_column,
    color="Status",
    color_discrete_map={
        "Pass": "#16a34a",
        "Fail": "#dc2626"
    },
    hover_data=SUBJECTS + ["Average"],
    title="Student Performance"
)

fig.update_layout(
    yaxis_range=[0, 100],
    xaxis_title="Students",
    yaxis_title="Grade (%)"
)

st.plotly_chart(fig, use_container_width=True)

# SUBJECT COMPARISON
st.subheader("📚 Interactive Subject Comparison")

subject_means = filtered_df[SUBJECTS].mean().reset_index()
subject_means.columns = ["Subject", "Average"]

fig2 = px.bar(
    subject_means,
    x="Subject",
    y="Average",
    color="Subject",
    title="Average Grade by Subject"
)

fig2.update_layout(yaxis_range=[0, 100])

st.plotly_chart(fig2, use_container_width=True)

# GRADE DISTRIBUTION
st.subheader("📊 Grade Distribution")

fig3 = px.histogram(
    filtered_df,
    x="Average",
    nbins=10,
    title="Distribution of Student Averages"
)

fig3.update_layout(
    xaxis_title="Average Grade",
    yaxis_title="Number of Students"
)

st.plotly_chart(fig3, use_container_width=True)

# PASS RATE
st.subheader("🎯 Pass and Fail Analysis")

pass_count = int((df["Status"] == "Pass").sum())
fail_count = int((df["Status"] == "Fail").sum())

status_df = pd.DataFrame({
    "Status": ["Pass", "Fail"],
    "Count": [pass_count, fail_count]
})

fig4 = px.pie(
    status_df,
    names="Status",
    values="Count",
    color="Status",
    color_discrete_map={
        "Pass": "#16a34a",
        "Fail": "#dc2626"
    },
    title="Pass vs Fail"
)

st.plotly_chart(fig4, use_container_width=True)

# TOP STUDENTS
st.subheader("🏆 Top Performing Students")

top_students = df.nlargest(3, "Average")

st.dataframe(
    top_students[["Name", "Average", "Status"]],
    use_container_width=True,
    hide_index=True
)

# DOWNLOAD
st.divider()
st.subheader("📥 Download Analysis")

csv = df.to_csv(index=False).encode("utf-8")

st.download_button(
    "Download Results as CSV",
    data=csv,
    file_name="student_performance_results.csv",
    mime="text/csv",
    use_container_width=True
)

st.caption("Developed with Python, Pandas, Plotly & Streamlit")
