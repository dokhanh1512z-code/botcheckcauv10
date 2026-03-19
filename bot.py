import streamlit as st
import pandas as pd
from itertools import groupby
from collections import defaultdict
import requests

# ===== CẤU HÌNH GIAO DIỆN WEB =====
st.set_page_config(page_title="BOT V36 PRO MAX 🔥", layout="wide")
st.title("🔥 V36 SYSTEM BEHAVIOR AI")
st.markdown("---")

# ===== LOGIC PHÂN TÍCH CHUẨN =====
def get_stats(day_so, key_func):
    c2, c3, cl = 0, 0, 0
    for _, nhom in groupby(day_so, key=key_func):
        d = len(list(nhom))
        if d == 2: c2 += 1
        elif d == 3: c3 += 1
        elif d >= 4: cl += 1
    return c2, c3, cl

def get_full_streak_stats(day_so, key_func):
    streak_count = defaultdict(int)
    for _, nhom in groupby(day_so, key=key_func):
        d = len(list(nhom))
        streak_count[d] += 1
    return dict(sorted(streak_count.items()))

def calculate_profit(c2, c3, cl):
    return (c2 * 95) + (c3 * -5) + (cl * -200)

def calculate_max_dd(day_so, key_func):
    current, peak, m_dd = 0, 0, 0
    for _, nhom in groupby(day_so, key=key_func):
        d = len(list(nhom))
        if d == 2: current += 95
        elif d == 3: current -= 5
        elif d >= 4: current -= 200
        peak = max(peak, current)
        m_dd = max(m_dd, peak - current)
    return m_dd

# ===== GIAO DIỆN NHẬP LIỆU =====
col_input, col_btn = st.columns([1, 1])

with col_input:
    range_input = st.text_input("Chọn đoạn dữ liệu (vd: 0-1000)", placeholder="Để trống nếu lấy hết")
    moc_soi_input = st.number_input("Số lượng soi gần nhất", value=250)

with col_btn:
    st.write("Thao tác dữ liệu:")
    if st.button("☁️ TẢI DỮ LIỆU TỪ SHEETS", use_container_width=True):
        url = "https://docs.google.com/spreadsheets/d/e/2PACX-1vS5-pPONvbU7PR7FteVtEBvN6EuudQ2rgbV3sHX-Ngy1PALF4nvyTBidXOXXE325_TLKKDJwZB7xFgH/pub?output=csv"
        try:
            response = requests.get(url)
            if response.status_code == 200:
                lines = response.text.splitlines()
                data_list = [l.strip().replace('"', '') for l in lines if l.strip().replace('"', '') in '1234']
                st.session_state['day_so'] = ''.join(data_list)
                st.success(f"✅ Đã tải thành công!")
            else: st.error("❌ Lỗi kết nối Sheets")
        except Exception as e: st.error(f"❌ Lỗi: {e}")

day_so_raw = st.text_area("Dữ liệu chuỗi số:", value=st.session_state.get('day_so', ''), height=100)
day_so_clean = ''.join(filter(lambda x: x in '1234', day_so_raw))

if day_so_clean:
    st.subheader("📊 Thống kê dữ liệu nạp")
    count_cols = st.columns(5)
    count_cols[0].metric("Tổng số", len(day_so_clean))
    count_cols[1].metric("Số 1", day_so_clean.count('1'))
    count_cols[2].metric("Số 2", day_so_clean.count('2'))
    count_cols[3].metric("Số 3", day_so_clean.count('3'))
    count_cols[4].metric("Số 4", day_so_clean.count('4'))
    st.markdown("---")

if st.button("🚀 BẮT ĐẦU PHÂN TÍCH", type="primary", use_container_width=True):
    # --- PHẦN 1: XỬ LÝ ĐOẠN RANGE (N-M) ---
    day_so_range = day_so_clean
    label_range = "FULL DATA"
    if range_input and "-" in range_input:
        try:
            start, end = map(int, range_input.split("-"))
            day_so_range = day_so_clean[start:end]
            label_range = f"ĐOẠN {range_input}"
        except: pass
    
    # --- PHẦN 2: XỬ LÝ ĐOẠN MỐC SOI (X SỐ CUỐI CỦA RANGE) ---
    day_so_recent = day_so_range[-moc_soi_input:]

    if len(day_so_range) < 10:
        st.warning("⚠️ Không đủ dữ liệu!")
    else:
        # 1. Tính cho Đoạn Range
        cl_key = lambda x: int(x) % 2 == 0
        tn_key = lambda x: int(x) in [3, 4]
        
        # Stats & Profit của đoạn Range
        r_cl_s = get_stats(day_so_range, cl_key)
        r_tn_s = get_stats(day_so_range, tn_key)
        p_range_cl = calculate_profit(*r_cl_s)
        p_range_tn = calculate_profit(*r_tn_s)
        dd_cl = calculate_max_dd(day_so_range, cl_key)
        dd_tn = calculate_max_dd(day_so_range, tn_key)

        # 2. Tính cho Đoạn Mốc Soi (Recent)
        m_cl_s = get_stats(day_so_recent, cl_key)
        m_tn_s = get_stats(day_so_recent, tn_key)
        p_recent_cl = calculate_profit(*m_cl_s)
        p_recent_tn = calculate_profit(*m_tn_s)

        # --- HIỂN THỊ ---
        st.header("🏆 KẾT QUẢ SO SÁNH LỢI NHUẬN")
        tab1, tab2 = st.tabs([f"📅 THEO ĐOẠN ({label_range})", f"⚡ THEO MỐC SOI ({moc_soi_input} SỐ CUỐI)"])

        with tab1:
            st.info(f"Dữ liệu đang xét: {len(day_so_range)} số")
            c1, c2 = st.columns(2)
            c1.metric("Lãi Chẵn/Lẻ", f"{p_range_cl}%")
            c2.metric("Lãi To/Nhỏ", f"{p_range_tn}%")
            st.subheader(f"Tổng lãi đoạn này: {p_range_cl + p_range_tn}%")
            st.error(f"Thua sâu nhất (DD): -{max(dd_cl, dd_tn)}%")
            
            # Show stats chi tiết cho đoạn Range
            col_a, col_b = st.columns(2)
            col_a.write(f"Stats CL: {r_cl_s[0]} | {r_cl_s[1]} | {r_cl_s[2]}")
            col_b.write(f"Stats TN: {r_tn_s[0]} | {r_tn_s[1]} | {r_tn_s[2]}")

        with tab2:
            st.info(f"Dữ liệu đang xét: {len(day_so_recent)} số")
            c1, c2 = st.columns(2)
            c1.metric("Lãi Chẵn/Lẻ (Mốc)", f"{p_recent_cl}%", delta=f"{p_recent_cl - p_range_cl}% so với đoạn")
            c2.metric("Lãi To/Nhỏ (Mốc)", f"{p_recent_tn}%", delta=f"{p_recent_tn - p_range_tn}% so với đoạn")
            st.success(f"Tổng lãi mốc soi: {p_recent_cl + p_recent_tn}%")

        st.markdown("---")
        st.subheader("🔍 Chi tiết biến động & Streak (Mốc soi)")
        col_cl, col_tn = st.columns(2)
        with col_cl:
            st.write("**📊 CẦU CHẴN/LẺ**")
            st.write(f"Stats (2|3|4+): {m_cl_s[0]} | {m_cl_s[1]} | {m_cl_s[2]}")
            with st.expander("Xem Streak"):
                fs = get_full_streak_stats(day_so_recent, cl_key)
                for k, v in fs.items(): st.write(f"• Streak {k}: {v}")
        with col_tn:
            st.write("**📊 CẦU TO/NHỎ**")
            st.write(f"Stats (2|3|4+): {m_tn_s[0]} | {m_tn_s[1]} | {m_tn_s[2]}")
            with st.expander("Xem Streak"):
                fs = get_full_streak_stats(day_so_recent, tn_key)
                for k, v in fs.items(): st.write(f"• Streak {k}: {v}")
