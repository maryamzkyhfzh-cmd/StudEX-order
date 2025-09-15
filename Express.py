import streamlit as st
import pandas as pd
import re

SPREADSHEET_ID = "1G5D23nN6lcmg3SAz9IKjLf5XxHJemh6i5ad5x2NRPpE"
SHEET_NAME = "Sheet1"

url = f"https://docs.google.com/spreadsheets/d/{SPREADSHEET_ID}/gviz/tq?tqx=out:csv&sheet={SHEET_NAME}"

st.title("📊 Laporan Order StudEX")

text = st.text_area("Masukkan teks WhatsApp di sini:")

if st.button("Proses"):
    lines = text.splitlines()
    driver_orders = {}
    requests_queue = []

    for line in lines:
        # Cek tipe request
        if re.search(r"anjem", line.lower()):
            requests_queue.append("anjem")
        elif re.search(r"jastip", line.lower()):
            requests_queue.append("jastip")

        # Cek jika ready
        if re.search(r"ready|redi", line.lower()):
            if requests_queue:
                req_type = requests_queue.pop(0)

                # Ambil nama driver tanpa tanggal & jam
                match = re.search(r"\] (.*?):", line)
                if match:
                    driver_name = match.group(1).strip()
                else:
                    driver_name = "Unknown"

                if driver_name not in driver_orders:
                    driver_orders[driver_name] = {"anjem": 0, "jastip": 0, "total": 0}

                driver_orders[driver_name][req_type] += 1
                driver_orders[driver_name]["total"] += 1

    # Ubah ke DataFrame
    df = pd.DataFrame([
        {"Driver": driver, "Anjem": data["anjem"], "Jastip": data["jastip"], "Total": data["total"]}
        for driver, data in driver_orders.items()
    ])

    st.subheader("📋 Laporan Per Driver")
    st.dataframe(df, use_container_width=True)

    # Simpan ke Google Sheets
    try:
        old_data = pd.read_csv(url)  # ambil data lama
        new_data = pd.concat([old_data, df], ignore_index=True)
    except:
        new_data = df

    st.subheader("📌 Data di Spreadsheet (tergabung)")
    st.dataframe(new_data, use_container_width=True)
  
