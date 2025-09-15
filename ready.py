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
    current_request = None  # Variabel untuk melacak permintaan yang sedang menunggu 'ready'

    for line in lines:
        line_lower = line.lower()
        
        # Cari jenis pesanan (anjem/jastip) dan simpan jika ditemukan
        if "anjem" in line_lower and "ready" not in line_lower and "redi" not in line_lower:
            current_request = "anjem"
            continue
        elif "jastip" in line_lower and "ready" not in line_lower and "redi" not in line_lower:
            current_request = "jastip"
            continue
        
        # Cek jika ada kata "ready" (atau variasinya) yang menjadi konfirmasi
        ready_match = re.search(r"\b(ready|redi|ridii|redikak)\b", line_lower)
        if ready_match and current_request:
            # Dapatkan nama driver
            match = re.search(r"\] (.*?):", line)
            driver_name = match.group(1).strip() if match else "Unknown"

            # Inisialisasi data driver jika belum ada
            if driver_name not in driver_orders:
                driver_orders[driver_name] = {"anjem": 0, "jastip": 0, "total": 0}

            # Tambahkan poin berdasarkan permintaan yang terdeteksi sebelumnya
            driver_orders[driver_name][current_request] += 1
            driver_orders[driver_name]["total"] += 1
            
            # Reset permintaan setelah dihitung
            current_request = None
            
        # Logika tambahan untuk "request" anjem/jastip yang langsung ready di satu baris
        elif ("anjem" in line_lower or "jastip" in line_lower) and ready_match:
            req_type = "anjem" if "anjem" in line_lower else "jastip"
            
            match = re.search(r"\] (.*?):", line)
            driver_name = match.group(1).strip() if match else "Unknown"
            
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
    except Exception as e:
        st.warning(f"Gagal mengambil data lama, membuat data baru. Error: {e}")
        new_data = df

    st.subheader("📌 Data di Spreadsheet (tergabung)")
    st.dataframe(new_data, use_container_width=True)
