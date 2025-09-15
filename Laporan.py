import streamlit as st
import re
import pandas as pd
from collections import defaultdict

st.title("📊 Laporan Order StudEX")

text = st.text_area("Masukkan teks WhatsApp di sini:")

if st.button("Proses"):
    # split baris
    lines = text.splitlines()
    
    # data driver
    driver_orders = defaultdict(lambda: {"anjem": 0, "jastip": 0, "total": 0})
    
    requests = []
    
    for line in lines:
        low = line.lower()
        
        # --- cek apakah baris permintaan ---
        if "anjem" in low:
            requests.append("anjem")
        elif "jastip" in low:
            requests.append("jastip")
        
        # --- cek apakah baris jawaban driver ---
        if re.search(r"\b(ready|redi|redikan|redii)\b", low):
            if requests:  # hanya proses kalau ada permintaan yang belum di-handle
                req_type = requests.pop(0)  # ambil request paling awal
                
                # ambil nama driver pakai regex
                match = re.search(r"\] (.*?):", line)
                if match:
                    driver_name = match.group(1).strip()
                else:
                    driver_name = "Unknown"
                
                # simpan data order driver
                driver_orders[driver_name][req_type] += 1
                driver_orders[driver_name]["total"] += 1
    
    # ubah ke dataframe
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
  
