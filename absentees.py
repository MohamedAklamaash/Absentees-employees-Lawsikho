import streamlit as st
import pandas as pd

st.title("Employee Attendance Checker (with TimeDoctor Stats)")

att_file = st.file_uploader("1) Upload attendance CSV", type="csv")
emp_file = st.file_uploader("2) Upload employee data CSV", type="csv")
td_file  = st.file_uploader("3) Upload TimeDoctor stats CSV", type="csv")

if not (att_file and emp_file and td_file):
    st.info("Please upload all three files to proceed.")
    st.stop()

attendance_df = pd.read_csv(att_file, engine='python', on_bad_lines='skip')
employee_df   = pd.read_csv(emp_file)
td_df         = pd.read_csv(td_file)

st.subheader("🏷️ attendance.csv columns")
st.write(attendance_df.columns.tolist())
st.subheader("🏷️ employee_data columns")
st.write(employee_df.columns.tolist())
st.subheader("🏷️ TimeDoctor columns")
st.write(td_df.columns.tolist())

attendance_df['Email']          = attendance_df['Email'].astype(str).str.strip()
employee_df['Work Email']       = employee_df['Work Email'].astype(str).str.strip()
td_email_cols = [c for c in td_df.columns if 'email' in c.lower()]
if not td_email_cols:
    st.error("❌ Couldn't find an ‘Email’ column in your TimeDoctor file.")
    st.stop()
td_email_col = td_email_cols[0]
td_df[td_email_col] = td_df[td_email_col].astype(str).str.strip()

td_name_cols = [c for c in td_df.columns 
                if 'name' in c.lower() 
                and 'email' not in c.lower()]
if not td_name_cols:
    st.error("❌ Couldn't find a ‘Name’ column in your TimeDoctor file.")
    st.stop()
td_name_col = td_name_cols[0]

td_time_cols = [c for c in td_df.columns 
                if any(k in c.lower() for k in ('time','duration','hours'))]
if not td_time_cols:
    st.error("❌ Couldn't find a ‘Time’ or ‘Duration’ column in your TimeDoctor file.")
    st.stop()
td_time_col = td_time_cols[0]

present_att = attendance_df.loc[
    attendance_df['Check-In Location'].notna() &
    ~attendance_df['Check-In Location'].isin(['N/A','null']),
    ['Employee Name','Email','Job Title']
]

present_td = td_df.loc[
    td_df[td_time_col].astype(str).str.strip().replace({'0h 0m':'0','0':'0'}) != '0',
    [td_name_col, td_email_col]
].rename(columns={td_name_col: 'Employee Name', td_email_col: 'Email'})

present_combined = pd.concat([present_att, present_td], ignore_index=True)
present_combined = present_combined.drop_duplicates(subset='Email')

all_emails     = set(employee_df['Work Email'].dropna())
present_emails = set(present_combined['Email'])
absent_emails  = all_emails - present_emails

absent_df = employee_df.loc[
    employee_df['Work Email'].isin(absent_emails),
    ['Display Name','Work Email','Job Title']
].rename(columns={'Display Name':'Employee Name','Work Email':'Email'})

st.success("✅ Done processing!")

st.subheader("Present Employees")
st.dataframe(present_combined)

st.subheader("Absent Employees")
st.dataframe(absent_df)

def to_csv(df):
    return df.to_csv(index=False).encode('utf-8')

st.download_button("Download Present CSV", to_csv(present_combined), "present_employees.csv","text/csv")
st.download_button("Download Absent CSV",  to_csv(absent_df),    "absent_employees.csv", "text/csv")
