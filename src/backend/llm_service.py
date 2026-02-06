import google.generativeai as genai
import os

# API Key
GEMINI_API_KEY = "AIzaSyDc4L1d0xQ9MNThVODscpmuOj6d6pkvxHQ"

def configure_genai():
    if not GEMINI_API_KEY:
        print("ERROR: API Key is missing.")
        return False
    try:
        genai.configure(api_key=GEMINI_API_KEY)
        return True
    except Exception as e:
        print(f"Connection Error: {e}")
        return False

def generate_proactive_message(customer_name, plan, fault_details, gender, severity="RED"):
    """
    severity: 'YELLOW' (Risk) veya 'RED' (Arıza)
    Buna göre Gemini farklı tonlarda mesaj yazar.
    """
    
    # Profesyonel hitap: Ad Soyad kullan (cinsiyet gereksiz)
    # gender parametresi backward compatibility için kalıyor
    
    # --- SENARYO 1: SARI ALARM (Sakinleştirici & Önleyici) ---
    if severity == "YELLOW":
        system_instruction = f"""
        Rol: NetPulse Proaktif Müşteri Deneyimi Uzmanı.
        Durum: Müşterinin internetinde hafif bir kalite bozulması (Ping/Jitter) öngörüldü ama kesinti YOK.
        Amaç: Müşteri sorunu hissetmeden ona "Biz farkındayız, arka planda iyileştiriyoruz, merak etmeyin" demek.
        
        Ton: Sakin, Güven Verici, Profesyonel, Pozitif.
        
        Veriler:
        - Müşteri: {customer_name}
        - Paket: {plan}
        - Sebep: {fault_details['cause']} (Bunu çok teknik olmadan söyle)
        - Aksiyon: {fault_details['action']}
        
        Kurallar:
        1. Asla "Arıza var" veya "Kesinti olacak" deme. "Performans optimizasyonu" veya "Anlık yoğunluk yönetimi" de.
        2. Müşteriye hiçbir şey yapmasına gerek olmadığını hissettir.
        3. Kısa tut (Max 2 cümle).
        """
        
    # --- SENARYO 2: KIRMIZI ALARM (Net & Çözümcü) ---
    else: # RED
        system_instruction = f"""
        Rol: NetPulse Saha Operasyon Yetkilisi.
        Durum: Müşterinin hizmetinde KESİNTİ veya CİDDİ ARIZA var.
        Amaç: Durumu net bir şekilde kabul etmek, sebebi söylemek ve ne zaman çözüleceğini bildirerek belirsizliği yok etmek.
        
        Ton: Ciddi, Çözüm Odaklı, Net, Saygılı.
        
        Veriler:
        - Müşteri: {customer_name}
        - Paket: {plan}
        - Tespit: {fault_details['cause']}
        - Ekip/Aksiyon: {fault_details['action']}
        - Tahmini Süre (ETA): {fault_details['eta']}
        
        Kurallar:
        1. Sorunun ne olduğunu net söyle.
        2. Mutlaka verilen tahmini süreyi ({fault_details['eta']}) belirt.
        3. Ekiplerin çalıştığını vurgula.
        """

    # Ortak Prompt Gövdesi
    prompt = f"""
    {system_instruction}
    
    Lütfen yukarıdaki role ve kurallara uygun olarak, "Sayın {customer_name}" şeklinde hitap ederek nihai SMS metnini yaz. 
    Sadece SMS içeriğini döndür, başka açıklama yapma.
    """

    try:
        model = genai.GenerativeModel('gemini-pro')
        response = model.generate_content(prompt)
        return response.text.strip()
    except Exception:
        # Fallback (Gemini çalışmazsa yedek statik mesajlar)
        if severity == "YELLOW":
            return f"Sayın {customer_name}, hattınızda anlık yoğunluk tespit edilmiştir. Kesinti yaşamamanız için uzaktan optimizasyon yapıyoruz. Keyifli kullanımlar."
        else:
            return f"Sayın {customer_name}, {fault_details['cause']} nedeniyle erişim sorunu yaşanmaktadır. {fault_details['eta']} içinde giderilmesi planlanmaktadır."