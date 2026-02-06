
# === STARTUP & SHUTDOWN EVENTS ===

@app.on_event("startup")
async def startup_event():
    """
    Backend başlangıcında:
    1. Tüm 500 abone için LSTM cache oluştur (12 ölçüm)
    2. Otomatik periodic monitoring başlat (her 5 dakika)
    """
    global background_monitor
    
    logger.info("🚀 NetPulse Backend başlatılıyor...")
    
    if lstm_service and lstm_service.is_available:
        background_monitor = BackgroundMonitor(
            get_db_func=get_db_connection,
            lstm_service=lstm_service,
            simulate_func=simulate_metrics_single
        )
        
        await background_monitor.start()
        logger.info("✅ Background monitoring aktif! (500 abone)")
    else:
        logger.warning("⚠️ LSTM unavailable, background monitoring disabled")


@app.on_event("shutdown")
async def shutdown_event():
    """Backend kapatılırken monitoring durdur"""
    if background_monitor:
        background_monitor.stop()
    logger.info("👋 NetPulse Backend kapatıldı")
