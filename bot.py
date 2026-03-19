import tkinter as tk
from tkinter import scrolledtext
import re
from itertools import groupby
from collections import defaultdict
import requests  # Thư viện để đọc dữ liệu từ web

# ===== LOGIC PHÂN TÍCH =====

def get_stats(day_so, key_func):
    c2, c3, cl = 0, 0, 0
    for _, nhom in groupby(day_so, key=key_func):
        d = len(list(nhom))
        if d == 2:
            c2 += 1
        elif d == 3:
            c3 += 1
        elif d >= 4:
            cl += 1
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
        if d == 2:
            current += 95
        elif d == 3:
            current -= 5
        elif d >= 4:
            current -= 200
        peak = max(peak, current)
        m_dd = max(m_dd, peak - current)
    return m_dd

def format_full_streak(streak_dict):
    return "\n".join([f"  • Streak {k}: {v}" for k, v in streak_dict.items()])

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
    
    res = f"\n📊 {name}\n"
    res += f"Tổng (2|3|4+): {tc2} | {tc3} | {tcl}\n"
    res += f"Soi {len(data_sub)}: {sc2} | {sc3} | {scl}\n"
    res += f"Lợi nhuận: {p_sub}%\n"
    res += f"Lãi 100 gần nhất: {p_100}%\n"
    res += f"THUA SÂU: -{max_dd}%\n"
    res += f"DỰ BÁO: {signal}\n"
    res += "\nFULL STREAK:\n" + format_full_streak(full_streak) + "\n"
    return res, p_sub, max_dd

# ===== HÀM ĐỌC DATA CHUẨN (TỪ TRÊN XUỐNG DƯỚI) =====

def fetch_from_sheets():
    # Đã sửa lại link thành định dạng CSV chuẩn để đọc chuẩn hàng dọc
    url = "https://docs.google.com/spreadsheets/d/e/2PACX-1vS5-pPONvbU7PR7FteVtEBvN6EuudQ2rgbV3sHX-Ngy1PALF4nvyTBidXOXXE325_TLKKDJwZB7xFgH/pub?output=csv"
    
    try:
        response = requests.get(url)
        if response.status_code == 200:
            raw_content = response.text
            
            # Tách dữ liệu theo từng dòng (vì ông xếp hàng dọc)
            lines = raw_content.splitlines()
            
            data_list = []
            for line in lines:
                # Loại bỏ khoảng trắng và chỉ lấy ký tự là 1,2,3,4
                clean_char = line.strip().replace('"', '') # Loại bỏ dấu ngoặc kép nếu có
                if clean_char in '1234':
                    data_list.append(clean_char)
            
            # Ghép lại thành chuỗi theo đúng thứ tự A1 -> An
            final_data = ''.join(data_list)
            
            input_box.delete("1.0", tk.END)
            input_box.insert(tk.END, final_data)
            
            output_box.delete("1.0", tk.END)
            output_box.insert(tk.END, f"✅ Đã tải thành công {len(final_data)} số.\nThứ tự: Từ ô A1 xuống dưới.\n\nBấm 'PHÂN TÍCH' ngay!")
        else:
            output_box.delete("1.0", tk.END)
            output_box.insert(tk.END, "❌ Lỗi: Không kết nối được Sheets. Kiểm tra lại link công bố!")
    except Exception as e:
        output_box.delete("1.0", tk.END)
        output_box.insert(tk.END, f"❌ Lỗi hệ thống: {str(e)}")

# ===== MAIN RUN =====

def run_analysis():
    raw_text = input_box.get("1.0", tk.END)
    day_so = ''.join(filter(lambda x: x in '1234', raw_text))

    range_text = range_entry.get().strip()
    if "-" in range_text:
        try:
            start, end = map(int, range_text.split("-"))
            day_so = day_so[start:end]
        except:
            pass

    try:
        moc_soi = int(moc_entry.get())
    except:
        moc_soi = 250

    if moc_soi > len(day_so):
        moc_soi = len(day_so)

    if len(day_so) < 20:
        output_box.delete(1.0, tk.END)
        output_box.insert(tk.END, "❌ Không đủ dữ liệu!")
        return

    res_cl, p_cl, dd_cl = check_trend(day_so, lambda x: int(x) % 2 == 0, "CHẴN/LẺ", moc_soi)
    res_tn, p_tn, dd_tn = check_trend(day_so, lambda x: int(x) in [3, 4], "TO/NHỎ", moc_soi)

    result = f"🔍 PHÂN TÍCH\n"
    result += f"Range: {range_text if range_text else 'FULL'}\n"
    result += f"Tổng số: {len(day_so)} | Soi: {moc_soi}\n"
    result += "----------------------\n"
    result += res_cl + res_tn
    result += "----------------------\n"
    result += f"TỔNG LỢI NHUẬN: {p_cl + p_tn}%\n"
    result += f"VỐN: {(max(dd_cl, dd_tn)*2/100):.1f} đơn vị"

    output_box.delete(1.0, tk.END)
    output_box.insert(tk.END, result)

# ===== GIAO DIỆN (GUI) =====

root = tk.Tk()
root.title("BOT PRO MAX 🔥")
root.geometry("750x700")

tk.Label(root, text="Dữ liệu hiện tại:", font=("Arial", 12, "bold")).pack(pady=5)
input_box = scrolledtext.ScrolledText(root, height=5, font=("Courier New", 10))
input_box.pack(fill="both", padx=10, pady=5)

# Nút Cloud
tk.Button(root, text="☁️ TẢI DỮ LIỆU TỪ SHEETS (A1 -> An)", command=fetch_from_sheets, 
          height=2, bg="#0078d4", fg="white", font=("Arial", 10, "bold")).pack(pady=5)

# Cấu hình Range & Mốc soi
frame_config = tk.Frame(root)
frame_config.pack(pady=5)

tk.Label(frame_config, text="Range (vd: 0-1000):").grid(row=0, column=0, padx=5)
range_entry = tk.Entry(frame_config)
range_entry.grid(row=0, column=1, padx=5)

tk.Label(frame_config, text="Số soi (vd: 250):").grid(row=1, column=0, padx=5)
moc_entry = tk.Entry(frame_config)
moc_entry.insert(0, "250")
moc_entry.grid(row=1, column=1, padx=5)

# Nút Phân tích
tk.Button(root, text="🚀 BẮT ĐẦU PHÂN TÍCH", command=run_analysis, 
          height=2, width=30, bg="#28a745", fg="white", font=("Arial", 11, "bold")).pack(pady=10)

tk.Label(root, text="Kết quả chi tiết:", font=("Arial", 12, "bold")).pack()
output_box = scrolledtext.ScrolledText(root, height=22, font=("Courier New", 10))
output_box.pack(fill="both", padx=10, pady=5)

root.mainloop()