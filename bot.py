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

def check_trend(day_so, key_func, name, moc_soi):
    tc2, tc3, tcl = get_stats(day_so, key_func)
    data_sub = day_so[-moc_soi:]
    sc2, sc3, scl = get_stats(data_sub, key_func)
    p_sub = (sc2 * 95) + (sc3 * -5) + (scl * -200)
    data_100 = day_so[-100:]
    c2_100, c3_100, cl_100 = get_stats(data_100, key_func)
    p_100 = (c2_100 * 95) + (c3_100 * -5) + (cl_100 * -200)
    max_dd = calculate_max_dd(day_so, key_func)
    _, _, rl_200 = get_stats(day_so[-200:], key_func)
    signal = "🔴 BÃO" if rl_200 >= 4 else "🟡 CẢNH BÁO" if rl_200 >= 2 else "🟢 TỐT"
    full_streak = get_full_streak_stats(data_sub, key_func)
    
    res = {
        "name": name, "tong": f"{tc2} | {tc3} | {tcl}", "soi": f"{sc2} | {sc3} | {scl}",
        "lai": f"{p_sub}%", "lai100": f"{p_100}%", "thua_sau": f"-{max_dd}%",
        "dubao": signal, "streaks": full_streak
    }
    return res, p_sub, max_dd

# ===== GIAO DIỆN NHẬP LIỆU TRÊN WEB =====
col_input, col_btn = st.columns([1, 1])

with col_input:
    range_input = st.text_input("Range (vd: 0-1000)", placeholder="Để trống nếu lấy hết")
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

# Ô nhập liệu dữ liệu thô
day_so_raw = st.text_area("Dữ liệu chuỗi số:", value=st.session_state.get('day_so', ''), height=100)
day_so_clean = ''.join(filter(lambda x: x in '1234', day_so_raw))

# --- BỘ ĐẾM DỮ LIỆU (MỚI THÊM) ---
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
    day_so = day_so_clean
    if range_input and "-" in range_input:
        try:
            start, end = map(int, range_input.split("-"))
            day_so = day_so[start:end]
        except: pass

    if len(day_so) < 20:
        st.warning("⚠️ Không đủ dữ liệu!")
    else:
        res_cl, p_cl, dd_cl = check_trend(day_so, lambda x: int(x) % 2 == 0, "CHẴN/LẺ", moc_soi_input)
        res_tn, p_tn, dd_tn = check_trend(day_so, lambda x: int(x) in [3, 4], "TO/NHỎ", moc_soi_input)

        c1, c2 = st.columns(2)
        for r, col in zip([res_cl, res_tn], [c1, c2]):
            with col:
                st.subheader(f"📊 {r['name']}")
                st.write(f"Tổng (2|3|4+): **{r['tong']}**")
                st.write(f"Soi {moc_soi_input}: **{r['soi']}**")
                st.write(f"Lợi nhuận: {r['lai']}")
                st.error(f"THUA SÂU: {r['thua_sau']}")
                st.info(f"DỰ BÁO: {r['dubao']}")
                with st.expander("Xem Full Streak"):
                    for k, v in r['streaks'].items():
                        st.write(f"• Streak {k}: {v}")

        st.markdown("---")
        st.metric("TỔNG LỢI NHUẬN", f"{p_cl + p_tn}%")
        st.metric("VỐN KHUYẾN NGHỊ", f"{(max(dd_cl, dd_tn)*2/100):.1f} đơn vị")
