"""
Background Monitoring Service
Otomatik periyodik ölçüm ve LSTM cache yönetimi
"""
import asyncio
import logging
from typing import List
import random

logger = logging.getLogger(__name__)

class BackgroundMonitor:
    """
    Profesyonel background monitoring servisi:
    - Startup'ta tüm aboneler için initial cache doldurur
    - Her 5 dakikada periyodik ölçüm yapar
    - LSTM için sürekli veri akışı sağlar
    """
    
    def __init__(self, get_db_func, lstm_service, simulate_func):
        self.get_db = get_db_func
        self.lstm_service = lstm_service
        self.simulate_metrics = simulate_func
        self.is_running = False
        self.monitored_subscribers = []
    
    async def initialize_cache(self):
        """
        Başlangıçta TÜM aboneler için 12 ölçüm oluştur
        LSTM hemen aktif olsun - Profesyonel sistem!
        """
        logger.info("🔧 LSTM Cache initialization başlatıldı (500 abone)...")
        
        conn = self.get_db()
        if not conn:
            logger.error("Database bağlantısı yok!")
            return
        
        try:
            cursor = conn.cursor()
            # TÜM 500 aboneyi al
            cursor.execute("SELECT subscriber_id, subscription_plan, region_id FROM customers ORDER BY subscriber_id")
            subscribers = cursor.fetchall()
            conn.close()
            
            logger.info(f"📊 {len(subscribers)} abone için cache oluşturuluyor...")
            
            # Bölgesel arıza simülasyonu için
            # %5 ihtimalle bir bölgede toplu sorun olsun
            faulty_regions = set()
            all_regions = list(set([sub[2] for sub in subscribers]))
            if random.random() < 0.05:
                faulty_regions.add(random.choice(all_regions))
                logger.info(f"⚠️ Simülasyon: {list(faulty_regions)[0]} bölgesinde arıza")
            
            for sub_id, plan, region in subscribers:
                # Bölgesel arıza varsa %70 ihtimalle etkilenir
                regional_fault = region in faulty_regions and random.random() < 0.7
                
                # Her abone için 12 ölçüm ekle
                for i in range(12):
                    # İlk ölçümlerde arıza yok, sonraki ölçümlerde gelişsin (gerçekçi)
                    force_trouble = regional_fault and i >= 6
                    
                    metrics, _, _ = self.simulate_metrics(plan, force_trouble=force_trouble)
                    
                    if self.lstm_service and self.lstm_service.is_available:
                        self.lstm_service.add_measurement(sub_id, metrics)
                
                self.monitored_subscribers.append((sub_id, plan, region))
            
            logger.info(f"✅ {len(subscribers)} abone için LSTM cache hazır!")
            logger.info(f"📈 Toplam cache boyutu: {len(subscribers) * 12} ölçüm")
            
        except Exception as e:
            logger.error(f"Cache initialization hatası: {e}")
    
    async def periodic_monitoring(self):
        """
        Her 5 dakikada bir TÜM 500 aboneyi tara
        Gerçekçi dinamik varyasyon ile
        """
        logger.info("🔄 Periyodik monitoring başlatıldı (5 dakika interval)")
        
        while self.is_running:
            try:
                await asyncio.sleep(300)  # 5 dakika = 300 saniye
                
                logger.info("📡 Periyodik ölçüm yapılıyor (500 abone)...")
                
                # Bölgesel arıza simülasyonu
                # Her döngüde %3 ihtimalle bir bölgede sorun çıksın
                faulty_regions = set()
                if self.monitored_subscribers:
                    all_regions = list(set([region for _, _, region in self.monitored_subscribers]))
                    if random.random() < 0.03:
                        faulty_regions.add(random.choice(all_regions))
                        logger.warning(f"⚠️ Bölgesel arıza simüle ediliyor: {list(faulty_regions)[0]}")
                
                problem_count = 0
                
                for sub_id, plan, region in self.monitored_subscribers:
                    # Bölgesel arıza
                    if region in faulty_regions:
                        force_trouble = random.random() < 0.6  # %60 etkilenir
                    else:
                        # Normal durum: %5 bireysel arıza ihtimali
                        force_trouble = random.random() < 0.05
                    
                    if force_trouble:
                        problem_count += 1
                    
                    metrics, _, _ = self.simulate_metrics(plan, force_trouble=force_trouble)
                    
                    if self.lstm_service and self.lstm_service.is_available:
                        self.lstm_service.add_measurement(sub_id, metrics)
                
                logger.info(f"✅ {len(self.monitored_subscribers)} abone ölçümü tamamlandı")
                logger.info(f"📊 {problem_count} abone sorunlu durumdaydı")
                
            except Exception as e:
                logger.error(f"Monitoring hatası: {e}")
    
    async def start(self):
        """Background monitoring'i başlat"""
        self.is_running = True
        
        # 1. Initial cache oluştur
        await self.initialize_cache()
        
        # 2. Periyodik monitoring başlat
        asyncio.create_task(self.periodic_monitoring())
        
        logger.info("🚀 Background monitoring aktif!")
    
    def stop(self):
        """Monitoring'i durdur"""
        self.is_running = False
        logger.info("⏹️  Background monitoring durduruldu")
