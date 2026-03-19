import streamlit as st
import pandas as pd
from itertools import groupby
from collections import defaultdict
import requests

# ===== CẤU HÌNH GIAO DIỆN WEB =====
st.set_page_config(page_title="BOT V36 PRO MAX 🔥", layout="wide")
st.title("🔥 V36 SYSTEM BEHAVIOR AI")
st.markdown("---")

# ===== LOGIC PHÂN TÍCH =====
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
    moc_soi_input = st.number_input("Số lượng soi gần nhất (để tính lợi nhuận riêng)", value=250)

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
    # 1. Cắt đoạn dữ liệu theo Range (n-m)
    day_so_range = day_so_clean
    label_range = "FULL DATA"
    if range_input and "-" in range_input:
        try:
            start, end = map(int, range_input.split("-"))
            day_so_range = day_so_clean[start:end]
            label_range = f"ĐOẠN {range_input}"
        except: pass
    
    # 2. Lấy đoạn soi gần nhất (Mốc soi)
    day_so_recent = day_so_range[-moc_soi_input:]

    if len(day_so_range) < 10:
        st.warning("⚠️ Không đủ dữ liệu!")
    else:
        # TÍNH TOÁN CHO CHẴN LẺ
        cl_key = lambda x: int(x) % 2 == 0
        r_c2, r_c3, r_cl = get_stats(day_so_range, cl_key)
        m_c2, m_c3, m_cl = get_stats(day_so_recent, cl_key)
        profit_range_cl = calculate_profit(r_c2, r_c3, r_cl)
        profit_recent_cl = calculate_profit(m_c2, m_c3, m_cl)
        dd_cl = calculate_max_dd(day_so_range, cl_key)

        # TÍNH TOÁN CHO TO NHỎ
        tn_key = lambda x: int(x) in [3, 4]
        rt_c2, rt_c3, rt_cl = get_stats(day_so_range, tn_key)
        mt_c2, mt_c3, mt_cl = get_stats(day_so_recent, tn_key)
        profit_range_tn = calculate_profit(rt_c2, rt_c3, rt_cl)
        profit_recent_tn = calculate_profit(mt_c2, mt_c3, mt_cl)
        dd_tn = calculate_max_dd(day_so_range, tn_key)

        # HIỂN THỊ KẾT QUẢ TÁCH BIỆT
        st.header("🏆 BẢNG TÍNH LỢI NHUẬN")
        
        tab1, tab2 = st.tabs([f"📅 THEO ĐOẠN ({label_range})", f"⚡ THEO MỐC SOI ({moc_soi_input} SỐ CUỐI)"])

        with tab1:
            c1, c2 = st.columns(2)
            c1.metric("Lãi Chẵn/Lẻ", f"{profit_range_cl}%")
            c2.metric("Lãi To/Nhỏ", f"{profit_range_tn}%")
            st.info(f"Tổng lợi nhuận cả đoạn: **{profit_range_cl + profit_range_tn}%**")
            st.warning(f"Thua sâu nhất (DD) của đoạn: -{max(dd_cl, dd_tn)}%")

        with tab2:
            c1, c2 = st.columns(2)
            c1.metric("Lãi Chẵn/Lẻ Gần Đây", f"{profit_recent_cl}%")
            c2.metric("Lãi To/Nhỏ Gần Đây", f"{profit_recent_tn}%")
            st.success(f"Tổng lợi nhuận mốc soi: **{profit_recent_cl + profit_recent_tn}%**")

        st.markdown("---")
        # Giữ lại phần chi tiết bên dưới cho ông soi cầu
        st.subheader("🔍 Chi tiết biến động (Dựa trên mốc soi)")
        col_cl, col_tn = st.columns(2)
        with col_cl:
            st.write("**📊 CẦU CHẴN/LẺ**")
            st.write(f"Stats (2|3|4+): {m_c2} | {m_c3} | {m_cl}")
            with st.expander("Full Streak Chẵn/Lẻ"):
                fs = get_full_streak_stats(day_so_recent, cl_key)
                for k, v in fs.items(): st.write(f"• Streak {k}: {v}")
        with col_tn:
            st.write("**📊 CẦU TO/NHỎ**")
            st.write(f"Stats (2|3|4+): {mt_c2} | {mt_c3} | {mt_cl}")
            with st.expander("Full Streak To/Nhỏ"):
                fs = get_full_streak_stats(day_so_recent, tn_key)
                for k, v in fs.items(): st.write(f"• Streak {k}: {v}")
