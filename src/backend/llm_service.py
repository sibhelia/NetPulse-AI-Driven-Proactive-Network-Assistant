import google.generativeai as genai
import os

# API Ayarlari
GEMINI_API_KEY = "AIzaSyDc4L1d0xQ9MNThVODscpmuOj6d6pkvxHQ"

def configure_genai():
    if not GEMINI_API_KEY:
        print("HATA: API Key eksik.")
        return False
    try:
        genai.configure(api_key=GEMINI_API_KEY)
        return True
    except Exception as e:
        print(f"Baglanti hatasi: {e}")
        return False

def generate_explanation(alert_type, customer_name, plan, region, gender):
    # Ariza kodlari
    reasons = {
        0: "Planlı bakım çalışması",
        1: "Bölgesel yoğunluk",
        2: "Sinyal kalitesi düşüklüğü",
        3: "Veri paketi kaybı"
    }
    
    reason_text = reasons.get(alert_type, "Teknik aksaklık")
    
    # Veritabanindan gelen cinsiyete gore hitap
    title = "Hanım" if gender == "Kadın" else "Bey"

    prompt = f"""
    Rol: NetPulse telekom asistanı.
    Gorev: Musteriye SMS metni hazirla.
    
    Detaylar:
    - Musteri: {customer_name}
    - Hitap: {title}
    - Paket: {plan}
    - Sorun: {reason_text}
    
    Kurallar:
    - 'Sayın {customer_name} {title}' seklinde basla.
    - {plan} paket ismini gecir.
    - 'Ekiplerimiz ilgileniyor' de.
    - Cok kisa ve profesyonel ol.
    """

    try:
        model = genai.GenerativeModel('gemini-pro')
        response = model.generate_content(prompt)
        return response.text.strip()
    except Exception:
        return f"Sayın {customer_name} {title}, {plan} hizmetinizdeki kesinti incelenmektedir."

if __name__ == "__main__":
    if configure_genai():
        # Testler (Artik cinsiyet parametresi de gonderiliyor)
        print(generate_explanation(2, "Sibel Kaya", "1000 Mbps Gamer", "Region_1", "Kadın"))
        print(generate_explanation(0, "Ahmet Yılmaz", "100 Mbps Fiber", "Region_2", "Erkek"))