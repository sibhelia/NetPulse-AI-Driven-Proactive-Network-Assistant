from datetime import datetime, timedelta
import logging
import psycopg2

logger = logging.getLogger(__name__)

class StatusTracker:
    """
    Subscriber durumlarını track eder ve değişiklikleri tespit eder.
    GREEN → YELLOW → RED geçişlerini izler ve SMS tetikler.
    """
    
    def __init__(self, db_connection):
        self.conn = db_connection
    
    def get_current_status(self, subscriber_id: int) -> dict:
        """
        Kullanıcının mevcut durumunu al
        
        Returns:
            {"current": "GREEN", "previous": None}
        """
        cursor = self.conn.cursor()
        cursor.execute(
            "SELECT current_status, previous_status FROM subscriber_status WHERE subscriber_id = %s",
            (subscriber_id,)
        )
        result = cursor.fetchone()
        
        if not result:
            # İlk kez sorgulanıyor, GREEN olarak başlat
            cursor.execute(
                "INSERT INTO subscriber_status (subscriber_id, current_status) VALUES (%s, 'GREEN')",
                (subscriber_id,)
            )
            self.conn.commit()
            return {"current": "GREEN", "previous": None}
        
        return {"current": result[0], "previous": result[1]}
    
    def update_status(
        self, 
        subscriber_id: int, 
        new_status: str,
        fault_type: str = None,
        estimated_fix_hours: int = 2
    ) -> dict:
        """
        Durumu güncelle ve değişiklik olup olmadığını döndür
        
        Args:
            subscriber_id: Abone ID
            new_status: Yeni durum (GREEN, YELLOW, RED)
            fault_type: Arıza türü (ping_high, packet_loss, line_fault)
            estimated_fix_hours: Tahmini düzeltme süresi (saat)
        
        Returns:
            {
                "changed": bool,
                "old_status": str,
                "new_status": str,
                "should_send_sms": bool,
                "transition_type": str  # "degradation", "recovery", "none"
            }
        """
        current = self.get_current_status(subscriber_id)
        old_status = current["current"]
        
        if old_status == new_status:
            # Durum değişmedi
            # Sadece last_checked'i güncelle
            cursor = self.conn.cursor()
            cursor.execute(
                "UPDATE subscriber_status SET last_checked = NOW() WHERE subscriber_id = %s",
                (subscriber_id,)
            )
            self.conn.commit()
            
            return {
                "changed": False,
                "old_status": old_status,
                "new_status": new_status,
                "should_send_sms": False,
                "transition_type": "none"
            }
        
        # Durum değişti!
        logger.info(f"🔄 Status Change: Subscriber {subscriber_id}: {old_status} → {new_status}")
        
        # Tahmini düzelme saati
        estimated_fix = datetime.now() + timedelta(hours=estimated_fix_hours)
        
        cursor = self.conn.cursor()
        cursor.execute("""
            UPDATE subscriber_status
            SET 
                previous_status = %s,
                current_status = %s,
                status_changed_at = NOW(),
                last_checked = NOW(),
                fault_type = %s,
                estimated_fix_time = %s,
                sms_sent = FALSE
            WHERE subscriber_id = %s
        """, (old_status, new_status, fault_type, estimated_fix, subscriber_id))
        
        self.conn.commit()
        
        # SMS gönderilmeli mi ve ne türden bir geçiş?
        transition = self._analyze_transition(old_status, new_status)
        
        return {
            "changed": True,
            "old_status": old_status,
            "new_status": new_status,
            "should_send_sms": transition["send_sms"],
            "transition_type": transition["type"],
            "estimated_fix_time": estimated_fix
        }
    
    def _analyze_transition(self, old: str, new: str) -> dict:
        """
        Durum geçişini analiz et
        
        Returns:
            {
                "type": "degradation" | "recovery" | "stable",
                "send_sms": bool,
                "severity": "info" | "warning" | "critical"
            }
        """
        # Kötüleşme (Degradation)
        if (old, new) in [("GREEN", "YELLOW"), ("GREEN", "RED"), ("YELLOW", "RED")]:
            return {
                "type": "degradation",
                "send_sms": True,
                "severity": "critical" if new == "RED" else "warning"
            }
        
        # İyileşme (Recovery)
        elif (old, new) in [("RED", "GREEN"), ("RED", "YELLOW"), ("YELLOW", "GREEN")]:
            # RED → GREEN: Tam düzelme, SMS gönder
            # YELLOW → GREEN: Tam düzelme, SMS gönder
            # RED → YELLOW: Kısmi iyileşme, henüz SMS yok
            send_sms = (new == "GREEN")
            return {
                "type": "recovery",
                "send_sms": send_sms,
                "severity": "info"
            }
        
        # Diğer durumlar
        else:
            return {
                "type": "stable",
                "send_sms": False,
                "severity": "info"
            }
    
    def should_allow_status_change(self, subscriber_id: int, new_status: str) -> dict:
        """
        Check if status change should be allowed based on minimum duration rules
        
        Rules:
        - RED must stay for minimum 10 minutes before recovery
        - YELLOW must stay for minimum 5 minutes before recovery
        - Degradation (GREEN→YELLOW, YELLOW→RED) is always allowed
        - GREEN has no minimum duration
        
        Returns:
            {
                "allowed": bool,
                "reason": str,
                "time_remaining_seconds": int (if blocked)
            }
        """
        current = self.get_current_status(subscriber_id)
        current_status = current["current"]
        
        # If status not changing, allow
        if current_status == new_status:
            return {"allowed": True, "reason": "No change"}
        
        # Degradation is always allowed (problem getting worse)
        if (current_status, new_status) in [("GREEN", "YELLOW"), ("GREEN", "RED"), ("YELLOW", "RED")]:
            return {"allowed": True, "reason": "Degradation allowed"}
        
        # Recovery check - need minimum duration
        if (current_status, new_status) in [("RED", "YELLOW"), ("RED", "GREEN"), ("YELLOW", "GREEN")]:
            cursor = self.conn.cursor()
            cursor.execute(
                "SELECT status_changed_at FROM subscriber_status WHERE subscriber_id = %s",
                (subscriber_id,)
            )
            result = cursor.fetchone()
            
            if not result or not result[0]:
                # No timestamp, allow change
                return {"allowed": True, "reason": "No previous timestamp"}
            
            status_changed_at = result[0]
            time_elapsed = datetime.now() - status_changed_at
            
            # Minimum durations
            min_duration_minutes = 10 if current_status == "RED" else 5  # RED=10min, YELLOW=5min
            min_duration = timedelta(minutes=min_duration_minutes)
            
            if time_elapsed < min_duration:
                remaining = (min_duration - time_elapsed).total_seconds()
                return {
                    "allowed": False,
                    "reason": f"{current_status} status must persist for at least {min_duration_minutes} minutes",
                    "time_remaining_seconds": int(remaining)
                }
            else:
                return {"allowed": True, "reason": "Minimum duration elapsed"}
        
        # Other transitions allowed
        return {"allowed": True, "reason": "Allowed"}
    
    def mark_sms_sent(self, subscriber_id: int):
        """SMS gönderildi olarak işaretle"""
        cursor = self.conn.cursor()
        cursor.execute(
            "UPDATE subscriber_status SET sms_sent = TRUE, sms_sent_at = NOW() WHERE subscriber_id = %s",
            (subscriber_id,)
        )
        self.conn.commit()
        logger.info(f"✅ SMS sent flag updated for subscriber {subscriber_id}")
    
    def get_all_by_status(self) -> dict:
        """
        Tüm kullanıcıları durumlarına göre grupla
        
        Returns:
            {
                "GREEN": [...],
                "YELLOW": [...],
                "RED": [...]
            }
        """
        cursor = self.conn.cursor()
        cursor.execute("""
            SELECT 
                c.subscriber_id,
                c.full_name,
                c.phone_number,
                c.region_id,
                ss.current_status,
                ss.fault_type,
                ss.estimated_fix_time
            FROM customers c
            JOIN subscriber_status ss ON c.subscriber_id = ss.subscriber_id
            ORDER BY ss.current_status DESC, c.full_name
        """)
        
        results = {"GREEN": [], "YELLOW": [], "RED": []}
        
        for row in cursor.fetchall():
            sub_id, name, phone, region, status, fault, fix_time = row
            
            results[status].append({
                "id": sub_id,
                "name": name,
                "phone": phone,
                "region": region,
                "fault_type": fault,
                "estimated_fix": fix_time.isoformat() if fix_time else None
            })
        
        return results
