import streamlit as st
import re
import pandas as pd
from collections import defaultdict
import gspread
from google.oauth2.service_account import Credentials

st.title("📊 Laporan Order StudEX")

# === Setup Google Sheets ===
SHEET_ID = "PASTE_SHEET_ID_KAMU_DISINI"
SHEET_NAME = "Sheet1"

scope = ["https://www.googleapis.com/auth/spreadsheets"]
creds = Credentials.from_service_account_file("service_account.json", scopes=scope)
client = gspread.authorize(creds)
sheet = client.open_by_key(SHEET_ID).worksheet(SHEET_NAME)

# === Input Teks ===
text = st.text_area("Masukkan teks WhatsApp di sini:")

if st.button("Proses & Simpan ke Sheets"):
    lines = text.splitlines()
    driver_orders = defaultdict(lambda: {"anjem": 0, "jastip": 0, "total": 0})
    requests = []

    for line in lines:
        # cek permintaan
        if re.search(r"anjem", line.lower()) and not re.search(r"ready", line.lower()):
            requests.append("anjem")
        elif re.search(r"jastip", line.lower()) and not re.search(r"ready", line.lower()):
            requests.append("jastip")

        # cek driver ready
        if re.search(r"ready|redi", line.lower()):
            if requests:
                req_type = requests.pop(0)
                driver_name = line.split(":")[0].split("]")[-1].strip()
                driver_orders[driver_name][req_type] += 1
                driver_orders[driver_name]["total"] += 1

    # convert ke DataFrame
    df = pd.DataFrame([
        {"Driver": driver, "Anjem": data["anjem"], "Jastip": data["jastip"], "Total": data["total"]}
        for driver, data in driver_orders.items()
    ])
    df = df.sort_values(by="Total", ascending=False).reset_index(drop=True)

    # tampilkan tabel
    st.subheader("📋 Laporan Per Driver")
    st.dataframe(df, use_container_width=True)

    # total keseluruhan
    total_anjem = df["Anjem"].sum()
    total_jastip = df["Jastip"].sum()
    total_all = df["Total"].sum()
    st.subheader("📌 Rekap Keseluruhan")
    st.write(f"**Total: {total_all} orderan** ({total_anjem} anjem + {total_jastip} jastip)")

    # === Simpan ke Google Sheets ===
    # ubah dataframe jadi list
    values = df.values.tolist()
    header = ["Driver", "Anjem", "Jastip", "Total"]

    # tulis header + data ke sheets (append biar tambah terus)
    sheet.append_row(header)
    for row in values:
        sheet.append_row(row)

    st.success("✅ Data berhasil dikirim ke Google Sheets!")
  
