import streamlit as st
import requests
import pandas as pd
import plotly.graph_objects as go
import plotly.express as px
import numpy as np
import time
import random  # <-- İşte unuttuğumuz kahraman bu!
from datetime import datetime, timedelta

# --- AYARLAR ---
API_URL = "http://127.0.0.1:8000/api/simulate"
st.set_page_config(
    page_title="NetPulse Enterprise NOC",
    page_icon="📡",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# --- CSS: KURUMSAL GÖRÜNÜM ---
st.markdown("""
    <style>
    .stApp { background-color: #0b0e11; font-family: 'Segoe UI', sans-serif; }
    div.css-1r6slb0, div.stMetric {
        background-color: #161b22;
        border: 1px solid #30363d;
        border-radius: 6px;
        padding: 10px;
        color: #c9d1d9;
    }
    h1, h2, h3 { color: #58a6ff !important; font-weight: 600; }
    .dataframe { font-size: 12px !important; color: #c9d1d9 !important; background-color: #161b22 !important; }
    section[data-testid="stSidebar"] { background-color: #0d1117; border-right: 1px solid #30363d; }
    label[data-testid="stMetricLabel"] { font-size: 14px; color: #8b949e; }
    div[data-testid="stMetricValue"] { font-size: 24px; color: #f0f6fc; }
    .custom-alert {
        padding: 1rem; border-radius: 0.5rem; margin-bottom: 1rem;
        background-color: rgba(239, 68, 68, 0.1); border: 1px solid rgba(239, 68, 68, 0.5); color: #fca5a5;
    }
    </style>
""", unsafe_allow_html=True)

# --- SESSION STATE ---
if 'traffic_data' not in st.session_state:
    dates = pd.date_range(end=datetime.now(), periods=100, freq='15min')
    st.session_state.traffic_data = pd.DataFrame({
        'Zaman': dates,
        'Download (Gbps)': np.random.normal(800, 100, 100),
        'Upload (Gbps)': np.random.normal(200, 50, 100)
    })

if 'logs' not in st.session_state:
    st.session_state.logs = []

def add_log(message, type="INFO"):
    timestamp = datetime.now().strftime("%H:%M:%S")
    st.session_state.logs.insert(0, {"Saat": timestamp, "Tür": type, "Mesaj": message})
    if len(st.session_state.logs) > 50: st.session_state.logs.pop()

# --- GRAFİK FONKSİYONLARI ---
def plot_network_map():
    nodes = pd.DataFrame({
        'lat': np.random.uniform(36.0, 42.0, 20),
        'lon': np.random.uniform(26.0, 45.0, 20),
        'status': np.random.choice(['Normal', 'Warning', 'Critical'], 20, p=[0.7, 0.2, 0.1]),
        'region': [f"Node_{i}" for i in range(20)]
    })
    color_map = {'Normal': '#10B981', 'Warning': '#F59E0B', 'Critical': '#EF4444'}
    fig = px.scatter_mapbox(nodes, lat="lat", lon="lon", color="status", size_max=15, zoom=4.5,
                            color_discrete_map=color_map, hover_name="region",
                            mapbox_style="carto-darkmatter", center={"lat": 39.0, "lon": 35.0})
    fig.update_layout(margin={"r":0,"t":0,"l":0,"b":0}, height=400, paper_bgcolor="#161b22")
    return fig

def plot_traffic_trend():
    df = st.session_state.traffic_data
    fig = px.area(df, x='Zaman', y=['Download (Gbps)', 'Upload (Gbps)'],
                  color_discrete_sequence=['#3B82F6', '#6366F1'])
    fig.update_layout(
        plot_bgcolor="#161b22", paper_bgcolor="#161b22",
        font_color="#c9d1d9", height=300,
        margin={"r":10,"t":30,"l":10,"b":10},
        legend=dict(orientation="h", y=1.1)
    )
    return fig

def plot_gauge(value, title):
    fig = go.Figure(go.Indicator(
        mode = "gauge+number", value = value,
        title = {'text': title, 'font': {'size': 18, 'color': "#c9d1d9"}},
        gauge = {
            'axis': {'range': [None, 1200], 'tickcolor': "white"},
            'bar': {'color': "#58a6ff"},
            'bgcolor': "#0d1117",
            'borderwidth': 2, 'bordercolor': "#30363d",
            'steps': [
                {'range': [0, 100], 'color': 'rgba(239, 68, 68, 0.3)'},
                {'range': [100, 1200], 'color': 'rgba(16, 185, 129, 0.1)'}]
        }))
    fig.update_layout(height=250, margin={"r":20,"t":40,"l":20,"b":20}, paper_bgcolor="rgba(0,0,0,0)", font={'color': "white"})
    return fig

# --- SAYFA YAPISI ---
with st.sidebar:
    st.title("📡 NetPulse NOC")
    st.caption("AI-Driven Network Operations")
    selected_page = st.radio("Modüller", 
        ["🌐 Şebeke Genel Bakış", "🔍 Abone Derin Analiz", "📜 Sistem Logları"],
        index=1
    )
    st.divider()
    st.info("Backend Durumu: 🟢 Aktif")

if selected_page == "🌐 Şebeke Genel Bakış":
    st.subheader("🌍 Canlı Şebeke Topolojisi (NOC View)")
    k1, k2, k3, k4 = st.columns(4)
    k1.metric("Toplam Bant Genişliği", "4.2 Tbps", "+120 Gbps")
    k2.metric("Aktif Alarm", "14", "-3", delta_color="inverse")
    k3.metric("AI Müdahalesi (24s)", "342", "+12")
    k4.metric("Sistem Sağlığı", "%99.8", "Stabil")
    
    c1, c2 = st.columns([3, 2])
    with c1:
        st.markdown("**📍 Bölgesel Node Durumları**")
        st.plotly_chart(plot_network_map(), use_container_width=True)
    with c2:
        st.markdown("**📉 Trafik Eğilimi (24 Saat)**")
        st.plotly_chart(plot_traffic_trend(), use_container_width=True)

elif selected_page == "🔍 Abone Derin Analiz":
    st.subheader("🔍 Tekil Abone Arıza Tespiti (RCA)")
    with st.container():
        c1, c2, c3, c4 = st.columns([1, 1, 1, 3])
        user_id = c1.number_input("Abone ID", value=1001, step=1)
        force_mode = c2.checkbox("🔥 Zorla: Arıza", help="Demo için API'ye arıza emri verir")
        analyze_btn = c3.button("Analizi Başlat", type="primary")

    if analyze_btn or force_mode:
        params = {"force_trouble": "true"} if force_mode else {}
        try:
            response = requests.get(f"{API_URL}/{user_id}", params=params)
            if response.status_code == 200:
                data = response.json()
                info = data["customer_info"]
                metrics = data["live_metrics"]
                ai = data["ai_analysis"]
                
                log_type = "ERROR" if ai["status_code"] != 0 else "INFO"
                add_log(f"Abone {user_id} tarandı. Durum: {ai['status_text']}", log_type)

                with st.expander("👤 Abone Profili", expanded=True):
                    col1, col2, col3, col4 = st.columns(4)
                    col1.write(f"**Ad Soyad:**\n{info['name']}")
                    col2.write(f"**Paket:**\n{info['plan']}")
                    col3.write(f"**Lokasyon:**\n{info['region']}")
                    col4.write(f"**Segment:**\n{'💎 VIP' if 'Platin' in info['plan'] else 'Standart'}")

                st.markdown("#### ⚡ Canlı Hat Telemetrisi")
                m1, m2, m3 = st.columns([1, 1, 2])
                with m1:
                    st.plotly_chart(plot_gauge(metrics['download_speed'], "Download (Mbps)"), use_container_width=True)
                with m2:
                    st.metric("Ping", f"{metrics['latency']:.1f} ms", delta_color="inverse")
                    st.divider()
                    st.metric("Jitter", f"{metrics['jitter']:.2f} ms")
                    st.divider()
                    st.metric("Packet Loss", f"%{metrics['packet_loss']:.2f}", delta_color="inverse")
                with m3:
                    st.markdown("#### 🧠 NetPulse Neural Engine")
                    if ai["status_code"] != 0:
                        st.markdown(f"""<div class="custom-alert"><h3>🚨 TESPİT: {ai['status_text']}</h3></div>""", unsafe_allow_html=True)
                        with st.chat_message("assistant", avatar="🤖"):
                            st.write("Gemini LLM Bildirimi:")
                            st.info(ai['explanation'])
                    else:
                        st.success("✅ Hat Değerleri Nominal")
                        st.info(f"Model Güven Skoru: %{random.randint(95, 99)}") # HATA BURADAYDI, ARTIK DÜZELDİ
            else:
                st.error("Kullanıcı Bulunamadı")
        except Exception as e:
            st.error(f"Sunucuya Erişilemiyor: {e}")

elif selected_page == "📜 Sistem Logları":
    st.subheader("📜 System Audit Logs")
    if st.session_state.logs:
        st.dataframe(pd.DataFrame(st.session_state.logs), use_container_width=True)
    else:
        st.info("Henüz log kaydı yok.")