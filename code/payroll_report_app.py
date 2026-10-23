"""payroll_report_app.py - the quarter in review."""

import streamlit as st

from payroll.extract import load_employees, load_export
from payroll.summarize import build_history, summarize_employees
from payroll.reshape import hours_grid, missed_weeks, pay_by_month

st.title("Salt City Coffee — Quarterly Payroll Report")
st.write("Upload a quarter of weekly payroll exports to see the full picture.")

roster = load_employees()

uploads = st.file_uploader(
    "Upload payroll export CSVs:",
    type=["csv"],
    accept_multiple_files=True,
    key="exports",
)

if uploads:
    exports = [load_export(u) for u in uploads]
    history = build_history(exports, roster)

    unmatched = history[history["department"].isna()]
    if len(unmatched) > 0:
        ids = ", ".join(sorted(unmatched["employeeid"].unique()))
        st.warning(f"Unmatched employee IDs (not on the roster): {ids}")

    history = history[history["department"].notna()]

    departments = ["All"] + sorted(history["department"].unique())
    department = st.selectbox("Department:", departments, key="department")

    first_date = history["pay_date"].min().date()
    last_date = history["pay_date"].max().date()
    dates = st.date_input(
        "Pay dates",
        value=(first_date, last_date),
        min_value=first_date,
        max_value=last_date,
        key="dates",
    )
    start, end = dates if len(dates) == 2 else (dates[0], dates[0])

    filtered = history
    if department != "All":
        filtered = filtered[filtered["department"] == department]
    filtered = filtered[
        (filtered["pay_date"].dt.date >= start) & (filtered["pay_date"].dt.date <= end)
    ]

    col1, col2, col3, col4 = st.columns(4)
    col1.metric("Weeks", filtered["week_ending"].nunique())
    col2.metric("Employees", filtered["employee_id"].nunique())
    col3.metric("Total hours", f"{filtered['hours_worked'].sum():,.2f}")
    col4.metric("Total gross pay", f"${filtered['gross_pay'].sum():,.2f}")

    monthly = pay_by_month(filtered)
    st.bar_chart(monthly, x="month")

    st.subheader("Employee summary")
    st.dataframe(summarize_employees(filtered))

    st.subheader("Hours grid")
    st.dataframe(hours_grid(filtered))

    st.subheader("Missed weeks")
    st.dataframe(missed_weeks(hours_grid(filtered)))

    st.download_button(
        "Download pay-by-month CSV for the accountant",
        data=monthly.to_csv(index=False),
        file_name="pay_by_month.csv",
        mime="text/csv",
        key="download",
    )
