import pandas as pd
import os
import datetime
from collections import defaultdict
import pyodbc
from datetime import datetime
import requests
import tkinter as tk
import threading
import time
import streamlit as st

# Create the main window
from openpyxl.cell.cell import ILLEGAL_CHARACTERS_RE
def clean_illegal_chars(df):
    for col in df.select_dtypes(include=['object']).columns:
        df[col] = df[col].astype(str).apply(lambda x: ILLEGAL_CHARACTERS_RE.sub('', x))
    return df

today = datetime.now().date()

conn_str = (
    r'DRIVER={Tally ODBC Driver64};'
    r'SERVER=localhost;'
    r'PORT=2024;'
)
conn = pyodbc.connect(conn_str)
print("✅ Data Getting Exported to Power BI.....")




#Sales Extraction
query = "Select $Vchdat,$Vnum,$nme,$Vchtype,$opt,$parnam,$lednaminitem,$AMOUNT,$billname,$billamt from ODBC_sales"
cursor = conn.cursor()
cursor.execute(query)

# Get columns and data
columns = [column[0] for column in cursor.description]
rows = cursor.fetchall()

# Convert to DataFrame
df_sal = pd.DataFrame.from_records(rows, columns=columns)
df_sal.dropna(subset=['$billname'], inplace=True)
df_sal = df_sal[df_sal['$opt'] != 1.0]

df_sal['Bill No'] = df_sal['$parnam'] + ' - ' + df_sal['$billname']
summary_df_sal = df_sal[["Bill No","$billamt"]]
summary_df_sal = df_sal[["Bill No","$billamt"]].drop_duplicates(subset=["Bill No", "$billamt"]) # Removes dublicates
summary_df_sal["$billamt"] = summary_df_sal["$billamt"].astype(float)
# Summarize: total Sales per unique bill_no
summary_df_sal = summary_df_sal.groupby('Bill No')['$billamt'].sum().reset_index()
summary_df_sal.columns = ['Bill No', 'Amount Receivable']  # Rename for clarity if needed
with st.expander("Audit Finding summary"):
    st.write(df_sal)