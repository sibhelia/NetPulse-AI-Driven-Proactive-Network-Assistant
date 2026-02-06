import streamlit as st
import requests
import pandas as pd
import plotly.graph_objects as go
import time
from datetime import datetime
# Yeni oluşturduğumuz SMS dosyasını dahil ediyoruz
# (Eğer dosya yoksa hata vermemesi için try-except)
try:
    from src.backend import sms_sender
except ImportError:
    sms_sender = None

# --- AYARLAR ---
API_URL = "http://127.0.0.1:8000/api"

st.set_page_config(page_title="NetPulse NOC", page_icon="📡", layout="wide", initial_sidebar_state="expanded")

# --- CSS ---
st.markdown("""
    <style>
    .stApp { background-color: #0b0e11; }
    .metric-card { background-color: #161b22; border: 1px solid #30363d; padding: 15px; border-radius: 8px; text-align: center; }
    div[data-testid="stDataFrame"] { width: 100%; }
    button[kind="secondary"] { border-color: #30363d; color: #c9d1d9; }
    </style>
""", unsafe_allow_html=True)

# --- SESSION STATE ---
if 'view_mode' not in st.session_state: st.session_state.view_mode = "dashboard"
if 'selected_user' not in st.session_state: st.session_state.selected_user = None
if 'system_logs' not in st.session_state: st.session_state.system_logs = []
if 'fixed_users' not in st.session_state: st.session_state.fixed_users = [] # Onarılanları hafızada tut

def add_log(action, details, user):
    st.session_state.system_logs.insert(0, {
        "Saat": datetime.now().strftime("%H:%M:%S"),
        "İşlem": action, "Abone": user, "Detay": details, "Durum": "✅ Başarılı"
    })

def create_gauge(value, title, color_hex="#3B82F6"):
    fig = go.Figure(go.Indicator(
        mode="gauge+number", value=value,
        title={'text': title, 'font': {'size': 18, 'color': "white"}},
        gauge={
            'axis': {'range': [None, 1200], 'tickcolor': "white"},
            'bar': {'color': color_hex},
            'bgcolor': "#0d1117", 'borderwidth': 2, 'bordercolor': "#30363d",
            'steps': [{'range': [0, 100], 'color': 'rgba(239, 68, 68, 0.2)'}]
        }
    ))
    fig.update_layout(height=250, margin={"t":40,"b":20}, paper_bgcolor="rgba(0,0,0,0)", font={'color': "white"})
    return fig

# --- NAVİGASYON ---
with st.sidebar:
    st.title("📡 NetPulse")
    if st.button("🌍 Dashboard"): st.session_state.view_mode = "dashboard"; st.rerun()
    if st.button("📜 Loglar"): st.session_state.view_mode = "logs"; st.rerun()

# ==========================================
# 🦅 DASHBOARD
# ==========================================
if st.session_state.view_mode == "dashboard":
    st.header("🌍 Şebeke Operasyon Merkezi")
    if st.button("🔄 Canlı Tarama", type="primary"):
        with st.spinner("Taranıyor..."): time.sleep(0.5)
    
    try:
        data = requests.get(f"{API_URL}/scan_network").json()
        counts = data["counts"]
        
        k1, k2, k3, k4 = st.columns(4)
        k1.metric("Toplam Abone", data["total"], border=True)
        k2.metric("Sağlam", counts["GREEN"], border=True)
        k3.metric("Riskli", counts["YELLOW"], border=True)
        k4.metric("Arızalı", counts["RED"], border=True)
        
        st.divider()
        
        # Risk Listesi
        c1, c2 = st.columns([1, 2])
        with c2:
            st.subheader("🚨 Müdahale Bekleyenler")
            # Kırmızı ve Sarı listeyi birleştir
            alerts = data["lists"]["RED"] + data["lists"]["YELLOW"]
            
            if alerts:
                for u in alerts:
                    # Eğer daha önce düzelttiysek listede gösterme!
                    if u['id'] in st.session_state.fixed_users:
                        continue
                        
                    with st.container(border=True):
                        cl1, cl2, cl3, cl4 = st.columns([1, 2, 2, 2])
                        status_icon = "🔴" if u in data["lists"]["RED"] else "🟡"
                        cl1.write(f"**{status_icon}**")
                        cl2.write(f"{u['id']} - {u['name']}")
                        cl3.write(f"📍 {u['region']}")
                        if cl4.button("Analiz Et", key=f"btn_{u['id']}"):
                            st.session_state.selected_user = u['id']
                            st.session_state.view_mode = "detail"
                            st.rerun()
            else:
                st.success("Tüm sistemler stabil.")
    except: st.error("API Bağlantı Hatası!")

# ==========================================
# 🔍 DETAY VE ONARIM EKRANI
# ==========================================
elif st.session_state.view_mode == "detail":
    uid = st.session_state.selected_user
    if st.button("⬅️ Geri"): st.session_state.view_mode = "dashboard"; st.rerun()
    
    # "Zorla: Arıza" checkbox'ı, eğer kullanıcı daha önce düzeltildiyse kapalı gelsin
    is_fixed = uid in st.session_state.fixed_users
    force_val = True if not is_fixed else False
    
    col_t1, col_t2 = st.columns([3, 1])
    col_t1.title(f"🔍 Abone: #{uid}")
    force_trouble = col_t2.checkbox("🔥 Arıza Simülasyonu", value=force_val, disabled=is_fixed)

    params = {"force_trouble": "true"} if force_trouble else {}
    
    try:
        res = requests.get(f"{API_URL}/simulate/{uid}", params=params).json()
        info = res["customer_info"]
        ai = res["ai_analysis"]
        metrics = res["live_metrics"]
        
        # --- CANLI ONARIM EFEKTİ ---
        # Eğer kullanıcı "Onarıldı" listesindeyse, verileri manuel olarak "MÜKEMMEL" yap
        if is_fixed:
            metrics["download_speed"] = 980.5
            metrics["latency"] = 4.2
            metrics["packet_loss"] = 0.0
            ai["segment"] = "GREEN"
            ai["status_text"] = "Onarım Tamamlandı"
            ai["explanation"] = "Hizmet normale döndü."

        # Üst Bilgi
        with st.container(border=True):
            c1, c2, c3, c4 = st.columns(4)
            c1.write(f"**{info['name']}**")
            c2.write(f"{info['plan']}")
            c3.write(f"{info['region']}")
            
            color_map = {"RED": "🔴 KRİTİK", "YELLOW": "🟡 RİSKLİ", "GREEN": "🟢 NORMAL"}
            c4.metric("Durum", color_map.get(ai["segment"], "Normal"))

        # Göstergeler
        g1, g2 = st.columns([1, 2])
        gauge_color = "#10B981" if ai["segment"] == "GREEN" else "#EF4444"
        with g1: st.plotly_chart(create_gauge(metrics['download_speed'], "Hız (Mbps)", gauge_color), use_container_width=True)
        with g2:
            m1, m2, m3 = st.columns(3)
            m1.metric("Ping", f"{metrics['latency']:.1f} ms")
            m2.metric("Jitter", f"{metrics['jitter']:.1f} ms")
            m3.metric("Loss", f"%{metrics['packet_loss']:.1f}")
            
            if not is_fixed:
                st.info(f"💡 **Teşhis:** {ai['fault_details']['cause'] if ai['fault_details'] else 'Hat stabil'}")
            else:
                st.success("✅ **Sonuç:** Arıza başarıyla giderildi.")

        # --- AKSİYON PANELİ ---
        st.subheader("🧠 NetPulse Aksiyon Merkezi")
        
        if ai["segment"] != "GREEN" and not is_fixed:
            with st.container(border=True):
                st.error(f"🚨 **Sorun:** {ai['status_text']}")
                st.code(ai["explanation"], language="text")
                
                b1, b2 = st.columns(2)
                
                # 1. BUTON: SADECE SMS
                if b1.button("📩 Bilgilendirme SMS'i At"):
                    if sms_sender:
                        sms_sender.send_real_sms(ai["explanation"]) # GERÇEK SMS
                    st.toast("SMS Gönderildi!", icon="📨")
                    add_log("SMS", "Müşteri bilgilendirildi.", info['name'])

                # 2. BUTON: EKİP YÖNLENDİR VE ÇÖZ (MAGIC BUTTON)
                if b2.button("🛠️ Ekip Yönlendir ve ONAR"):
                    # Adım 1: SMS At
                    if sms_sender:
                        sms_sender.send_real_sms(f"Sayın {info['name']}, ekiplerimiz müdahaleye başladı.")
                    
                    # Adım 2: Görsel İlerleme Çubuğu (Proses Simülasyonu)
                    progress_text = "Saha ekipleri yönlendiriliyor..."
                    my_bar = st.progress(0, text=progress_text)
                    
                    for percent_complete in range(100):
                        time.sleep(0.03) # 3 saniyelik bekleme efekti
                        my_bar.progress(percent_complete + 1, text="Arıza kaynağına müdahale ediliyor...")
                    
                    time.sleep(0.5)
                    my_bar.empty()
                    
                    # Adım 3: Düzelme
                    st.session_state.fixed_users.append(uid) # Hafızaya at
                    add_log("Onarım", "Arıza giderildi ve hat normale döndü.", info['name'])
                    st.success("✅ Arıza Giderildi! Sistem normale döndü.")
                    time.sleep(1)
                    st.rerun() # Sayfayı yenile (Yeşil hali gelsin)

        elif is_fixed:
            st.balloons() # Kutlama efekti 🎉
            st.success("Bu abone için operasyon başarıyla tamamlandı.")
        else:
            st.success("Herhangi bir aksiyon gerekmiyor.")

# ==========================================
# 📜 LOGLAR
# ==========================================
elif st.session_state.view_mode == "logs":
    st.header("📜 Sistem Logları")
    if st.button("⬅️ Geri"): st.session_state.view_mode = "dashboard"; st.rerun()
    st.dataframe(pd.DataFrame(st.session_state.system_logs), use_container_width=True)