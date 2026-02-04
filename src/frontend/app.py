import streamlit as st
import requests
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import time
from datetime import datetime

# --- AYARLAR ---
API_URL = "http://127.0.0.1:8000/api"

st.set_page_config(
    page_title="NetPulse NOC Center",
    page_icon="📡",
    layout="wide",
    initial_sidebar_state="expanded"
)

# --- CSS: NOC GÖRÜNÜMÜ ---
st.markdown("""
    <style>
    .stApp { background-color: #0b0e11; }
    .metric-card { background-color: #161b22; border: 1px solid #30363d; padding: 15px; border-radius: 8px; text-align: center; }
    .status-red { color: #ff4b4b; font-weight: bold; }
    .status-yellow { color: #ffa700; font-weight: bold; }
    .status-green { color: #00cc96; font-weight: bold; }
    div[data-testid="stDataFrame"] { width: 100%; }
    button[kind="secondary"] { border-color: #30363d; color: #c9d1d9; }
    </style>
""", unsafe_allow_html=True)

# --- SESSION STATE & LOG YÖNETİMİ ---
if 'view_mode' not in st.session_state:
    st.session_state.view_mode = "dashboard"
if 'selected_user' not in st.session_state:
    st.session_state.selected_user = None
if 'system_logs' not in st.session_state:
    # Başlangıçta boş log veya örnek birkaç veri
    st.session_state.system_logs = []

def add_log(action_type, details, user_name):
    """Sisteme yeni bir log kaydı ekler"""
    timestamp = datetime.now().strftime("%H:%M:%S")
    log_entry = {
        "Saat": timestamp,
        "İşlem Türü": action_type,
        "Abone": user_name,
        "Detay": details,
        "Durum": "✅ Başarılı"
    }
    # En başa ekle (Son işlem en üstte)
    st.session_state.system_logs.insert(0, log_entry)

# --- YARDIMCI FONKSİYONLAR ---
def go_to_detail(user_id):
    st.session_state.selected_user = user_id
    st.session_state.view_mode = "detail"
    st.rerun()

def go_to_dashboard():
    st.session_state.selected_user = None
    st.session_state.view_mode = "dashboard"
    st.rerun()

def go_to_logs():
    st.session_state.view_mode = "logs"
    st.rerun()

def create_gauge(value, title):
    fig = go.Figure(go.Indicator(
        mode="gauge+number", value=value,
        title={'text': title, 'font': {'size': 18, 'color': "white"}},
        gauge={
            'axis': {'range': [None, 1200], 'tickcolor': "white"},
            'bar': {'color': "#3B82F6"},
            'bgcolor': "#0d1117",
            'borderwidth': 2, 'bordercolor': "#30363d",
            'steps': [
                {'range': [0, 100], 'color': 'rgba(239, 68, 68, 0.5)'}, 
                {'range': [100, 1200], 'color': 'rgba(16, 185, 129, 0.1)'}
            ]
        }
    ))
    fig.update_layout(height=250, margin={"t":40,"b":20}, paper_bgcolor="rgba(0,0,0,0)", font={'color': "white"})
    return fig

# --- YAN MENÜ (NAVİGASYON) ---
with st.sidebar:
    st.title("📡 NetPulse")
    st.caption("v2.0 Enterprise")
    
    if st.button("🌍 Şebeke Paneli", use_container_width=True):
        go_to_dashboard()
    
    if st.button("📜 Sistem Logları", use_container_width=True):
        go_to_logs()
        
    st.divider()
    st.info("Backend: 🟢 Online")

# ==========================================
# 🦅 GÖRÜNÜM 1: DASHBOARD
# ==========================================
if st.session_state.view_mode == "dashboard":
    st.header("🌍 Şebeke Operasyon Merkezi (NOC)")
    
    # Üst Kontrol
    col1, col2 = st.columns([3, 1])
    with col2:
        if st.button("🔄 Canlı Tarama (Scan)", type="primary", use_container_width=True):
            with st.spinner("Tüm bölgeler taranıyor..."):
                time.sleep(0.8)
    
    # API İsteği
    try:
        response = requests.get(f"{API_URL}/scan_network")
        if response.status_code == 200:
            data = response.json()
            counts = data["counts"]
            
            # KPI
            k1, k2, k3, k4 = st.columns(4)
            k1.metric("Toplam Abone", data["total"], border=True)
            k2.metric("Sağlam", counts["GREEN"], border=True)
            k3.metric("Riskli (Warning)", counts["YELLOW"], border=True)
            k4.metric("Kritik (Critical)", counts["RED"], border=True)
            
            st.markdown("---")
            
            c1, c2 = st.columns([1, 2])
            with c1:
                st.subheader("📊 Sağlık Dağılımı")
                df_chart = pd.DataFrame({
                    "Durum": ["Sağlam", "Riskli", "Kritik"],
                    "Sayı": [counts["GREEN"], counts["YELLOW"], counts["RED"]]
                })
                fig = px.pie(df_chart, values="Sayı", names="Durum", hole=0.4, 
                             color="Durum",
                             color_discrete_map={"Sağlam":"#00cc96", "Riskli":"#ffa700", "Kritik":"#ff4b4b"})
                fig.update_layout(paper_bgcolor="rgba(0,0,0,0)", font_color="white", showlegend=False)
                st.plotly_chart(fig, use_container_width=True)

            with c2:
                st.subheader("🚨 Aksiyon Listesi")
                problematic_users = []
                for u in data["lists"]["RED"]:
                    u["status"] = "🔴 KRİTİK"
                    problematic_users.append(u)
                for u in data["lists"]["YELLOW"]:
                    u["status"] = "🟡 RİSKLİ"
                    problematic_users.append(u)
                
                if problematic_users:
                    for user in problematic_users:
                        with st.container(border=True):
                            cols = st.columns([1, 2, 2, 2])
                            cols[0].write(f"**{user['status']}**")
                            cols[1].write(f"🆔 {user['id']} - {user['name']}")
                            cols[2].write(f"📍 {user['region']}")
                            if cols[3].button("Analiz Et", key=f"btn_{user['id']}"):
                                go_to_detail(user['id'])
                else:
                    st.success("Sistem nominal.")
    except:
        st.error("API Bağlantı Hatası!")

# ==========================================
# 📜 GÖRÜNÜM 3: SİSTEM LOGLARI (YENİ)
# ==========================================
elif st.session_state.view_mode == "logs":
    st.header("📜 Sistem Denetim Kayıtları (Audit Logs)")
    st.markdown("AI tarafından gerçekleştirilen otonom işlemlerin tarihçesi.")
    
    if st.session_state.system_logs:
        df_log = pd.DataFrame(st.session_state.system_logs)
        st.dataframe(df_log, use_container_width=True, hide_index=True)
    else:
        st.info("Henüz kaydedilmiş bir işlem yok.")

# ==========================================
# 🔍 GÖRÜNÜM 2: DETAY & AKSİYON
# ==========================================
elif st.session_state.view_mode == "detail":
    user_id = st.session_state.selected_user
    
    if st.button("⬅️ Geri Dön", type="secondary"):
        go_to_dashboard()
        
    st.markdown("---")
    
    col_opt1, col_opt2 = st.columns([3, 1])
    col_opt1.title(f"🔍 Abone Detay: #{user_id}")
    force_trouble = col_opt2.checkbox("🔥 Simülasyon: Arızayı Zorla", value=True)
    
    params = {"force_trouble": "true"} if force_trouble else {}
    
    try:
        res = requests.get(f"{API_URL}/simulate/{user_id}", params=params)
        if res.status_code == 200:
            d = res.json()
            info = d["customer_info"]
            metrics = d["live_metrics"]
            ai = d["ai_analysis"]
            
            with st.container(border=True):
                c1, c2, c3, c4 = st.columns(4)
                c1.write(f"**İsim:** {info['name']}")
                c2.write(f"**Paket:** {info['plan']}")
                c3.write(f"**Bölge:** {info['region']}")
                color_map = {"RED": "🔴 KRİTİK", "YELLOW": "🟡 RİSKLİ", "GREEN": "🟢 NORMAL"}
                c4.metric("Segment", color_map.get(ai["segment"], "Bilinmiyor"))

            m1, m2 = st.columns([1, 2])
            with m1:
                st.plotly_chart(create_gauge(metrics['download_speed'], "Hız (Mbps)"), use_container_width=True)
            with m2:
                st.subheader("Telemetri")
                col_m1, col_m2, col_m3 = st.columns(3)
                col_m1.metric("Ping", f"{metrics['latency']:.1f} ms", delta_color="inverse")
                col_m2.metric("Jitter", f"{metrics['jitter']:.1f} ms")
                col_m3.metric("Loss", f"%{metrics['packet_loss']:.2f}")
                st.info(f"**Teşhis:** {ai['fault_details']['cause'] if ai['fault_details'] else 'Stabil'}")

            # AKSİYON KUTUSU
            st.subheader("🧠 NetPulse AI Aksiyonu")
            action_container = st.container(border=True)
            
            if ai["segment"] != "GREEN":
                action_container.error(f"Tespit Edilen Durum: {ai['status_text']}")
                ac1, ac2 = action_container.columns([1, 3])
                with ac1:
                    st.image("https://cdn-icons-png.flaticon.com/512/4712/4712109.png", width=80)
                with ac2:
                    st.markdown("**🤖 Gemini Tarafından Üretilen Mesaj:**")
                    st.code(ai["explanation"], language="text")
                    
                    b1, b2 = st.columns(2)
                    # BUTONLARA LOGLAMA EKLENDİ
                    if b1.button("📩 SMS Gönder", type="primary"):
                        add_log("SMS Bildirimi", "Müşteriye proaktif bilgilendirme yapıldı.", info['name'])
                        st.success("SMS İletildi!")
                        time.sleep(1.5)
                        go_to_logs() # İşlem bitince loglara at
                        
                    if b2.button("🛠️ Ekip Yönlendir"):
                        add_log("İş Emri (Ticket)", "Saha ekibi (Ahmet Y.) atandı.", info['name'])
                        st.success("Ekip Yönlendirildi!")
                        time.sleep(1.5)
                        go_to_logs() # İşlem bitince loglara at
            else:
                action_container.success("Hat değerleri mükemmel.")

    except Exception as e:
        st.error(f"Hata: {e}")