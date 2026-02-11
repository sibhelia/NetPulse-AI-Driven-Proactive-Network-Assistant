-- Ticket Sistemi Database Schema
-- NetPulse - Saha Ekibi Takip Sistemi

-- Tickets tablosu
CREATE TABLE IF NOT EXISTS tickets (
    ticket_id SERIAL PRIMARY KEY,
    subscriber_id INT NOT NULL,
    status VARCHAR(20) DEFAULT 'CREATED',
    priority VARCHAR(10) NOT NULL,
    fault_type VARCHAR(50),
    scope VARCHAR(20),
    technician_note TEXT,
    assigned_to VARCHAR(100),
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW(),
    resolved_at TIMESTAMP,
    resolution_note TEXT,
    CONSTRAINT fk_subscriber FOREIGN KEY (subscriber_id) REFERENCES customers(subscriber_id) ON DELETE CASCADE
);

-- Ticket status geçmişi
CREATE TABLE IF NOT EXISTS ticket_status_history (
    history_id SERIAL PRIMARY KEY,
    ticket_id INT NOT NULL,
    old_status VARCHAR(20),
    new_status VARCHAR(20) NOT NULL,
    changed_by VARCHAR(100),
    changed_at TIMESTAMP DEFAULT NOW(),
    note TEXT,
    CONSTRAINT fk_ticket FOREIGN KEY (ticket_id) REFERENCES tickets(ticket_id) ON DELETE CASCADE
);

-- Index'ler (performance için)
CREATE INDEX IF NOT EXISTS idx_tickets_subscriber ON tickets(subscriber_id);
CREATE INDEX IF NOT EXISTS idx_tickets_status ON tickets(status);
CREATE INDEX IF NOT EXISTS idx_tickets_created_at ON tickets(created_at DESC);
CREATE INDEX IF NOT EXISTS idx_history_ticket ON ticket_status_history(ticket_id);

-- Status enum değerleri (comment olarak)
-- CREATED: Ticket oluşturuldu
-- ASSIGNED: Teknisyene atandı
-- EN_ROUTE: Teknisyen yolda
-- ON_SITE: Teknisyen sahada
-- RESOLVED: Arıza giderildi
-- CLOSED: Ticket kapatıldı

COMMENT ON TABLE tickets IS 'Saha ekibi arıza kayıtları';
COMMENT ON TABLE ticket_status_history IS 'Ticket durum değişikliği geçmişi';
