
import React, { useState, useEffect } from 'react';
import { FaTimes, FaMagic, FaBuilding, FaHome, FaSave, FaExclamationCircle, FaClock, FaTools, FaChartLine } from 'react-icons/fa';
import { api } from '../services/api';
import './TicketModal.css';

const TicketModal = ({ isOpen, onClose, subscriberId, currentStatus, aiAnalysis, liveMetrics, onSuccess }) => {
    const [loading, setLoading] = useState(false);
    const [generating, setGenerating] = useState(false);
    const [ticketData, setTicketData] = useState(null);

    useEffect(() => {
        if (isOpen) {
            generateAutoNote();
        }
    }, [isOpen]);

    const generateAutoNote = async () => {
        setGenerating(true);
        try {
            const response = await api.generateTicketNote({
                subscriber_id: subscriberId,
                current_status: currentStatus,
                ai_analysis: aiAnalysis,
                live_metrics: liveMetrics
            });
            setTicketData(response);
        } catch (error) {
            console.error("Error generating note:", error);
            setTicketData(null);
        } finally {
            setGenerating(false);
        }
    };

    const handleSubmit = async () => {
        setLoading(true);
        try {
            // Ticket data hazırla
            const ticketPayload = {
                subscriber_id: subscriberId,
                priority: currentStatus === 'RED' ? 'HIGH' : currentStatus === 'YELLOW' ? 'MEDIUM' : 'LOW',
                fault_type: ticketData.scope === 'REGIONAL' ? 'INFRASTRUCTURE' : 'CPE',
                scope: ticketData.scope,
                technician_note: JSON.stringify(ticketData, null, 2), // Tüm data'yı JSON olarak sakla
                assigned_to: "Teknisyen Ekibi"
            };

            const response = await api.createTicket(ticketPayload);

            console.log('Ticket created:', response);

            // Success
            onClose();
            if (onSuccess) onSuccess();

        } catch (error) {
            console.error("Ticket creation error:", error);
            alert("Arıza kaydı oluşturulamadı! Lütfen tekrar deneyin.");
        } finally {
            setLoading(false);
        }
    };

    if (!isOpen) return null;

    return (
        <div className="ticket-modal-overlay">
            <div className="ticket-modal ticket-modal-wide">
                <div className="ticket-modal-header">
                    <h2><FaMagic /> Saha Ekibi Arıza Raporu</h2>
                    <button className="close-btn" onClick={onClose}><FaTimes /></button>
                </div>

                <div className="ticket-modal-body">
                    {generating ? (
                        <div style={{ textAlign: 'center', padding: '3rem' }}>
                            <FaMagic className="fa-spin" style={{ fontSize: '3rem', color: '#8b5cf6' }} />
                            <p style={{ marginTop: '1rem', color: '#64748b' }}>Analiz ediliyor...</p>
                        </div>
                    ) : ticketData ? (
                        <div className="ticket-cards-grid">
                            {/* Kart 1: Arıza Kapsamı */}
                            <div className={`ticket-card scope-card ${ticketData.scope.toLowerCase()}`}>
                                <div className="card-icon">
                                    {ticketData.scope === 'REGIONAL' ? <FaBuilding /> : <FaHome />}
                                </div>
                                <h3>{ticketData.scope === 'REGIONAL' ? 'Bölgesel Arıza' : 'Bireysel Arıza'}</h3>
                                <div className="scope-details">
                                    <div className="detail-row">
                                        <span className="label">Bölge:</span>
                                        <span className="value">{ticketData.header.region}</span>
                                    </div>
                                    <div className="detail-row">
                                        <span className="label">Etkilenen Komşu:</span>
                                        <span className="value">{ticketData.neighbor_count} abone</span>
                                    </div>
                                    <div className="detail-row">
                                        <span className="label">Öncelik:</span>
                                        <span className={`priority-badge ${currentStatus.toLowerCase()}`}>
                                            {ticketData.header.status_icon} {ticketData.header.priority}
                                        </span>
                                    </div>
                                </div>
                            </div>

                            {/* Kart 2: Ağ Metrikleri */}
                            <div className="ticket-card metrics-card">
                                <div className="card-icon"><FaChartLine /></div>
                                <h3>Ağ Metrikleri</h3>
                                <div className="metrics-list">
                                    {ticketData.metrics.latency && (
                                        <div className="metric-item">
                                            <span className="metric-name">Ping (Gecikme)</span>
                                            <span className="metric-value">
                                                {ticketData.metrics.latency.value.toFixed(0)} {ticketData.metrics.latency.unit}
                                                <span className={ticketData.metrics.latency.ok ? 'status-ok' : 'status-fail'}>
                                                    {ticketData.metrics.latency.ok ? ' ✅' : ' ❌'}
                                                </span>
                                            </span>
                                        </div>
                                    )}
                                    {ticketData.metrics.packet_loss && (
                                        <div className="metric-item">
                                            <span className="metric-name">Paket Kaybı</span>
                                            <span className="metric-value">
                                                {ticketData.metrics.packet_loss.value.toFixed(1)} {ticketData.metrics.packet_loss.unit}
                                                <span className={ticketData.metrics.packet_loss.ok ? 'status-ok' : 'status-fail'}>
                                                    {ticketData.metrics.packet_loss.ok ? ' ✅' : ' ❌'}
                                                </span>
                                            </span>
                                        </div>
                                    )}
                                    {ticketData.metrics.download_speed && (
                                        <div className="metric-item">
                                            <span className="metric-name">Download Hızı</span>
                                            <span className="metric-value">
                                                {ticketData.metrics.download_speed.value.toFixed(1)} {ticketData.metrics.download_speed.unit}
                                                <span className={ticketData.metrics.download_speed.ok ? 'status-ok' : 'status-fail'}>
                                                    {ticketData.metrics.download_speed.ok ? ' ✅' : ' ❌'}
                                                </span>
                                            </span>
                                        </div>
                                    )}
                                    {ticketData.metrics.jitter && (
                                        <div className="metric-item">
                                            <span className="metric-name">Jitter</span>
                                            <span className="metric-value">
                                                {ticketData.metrics.jitter.value.toFixed(1)} {ticketData.metrics.jitter.unit}
                                                <span className={ticketData.metrics.jitter.ok ? 'status-ok' : 'status-fail'}>
                                                    {ticketData.metrics.jitter.ok ? ' ✅' : ' ❌'}
                                                </span>
                                            </span>
                                        </div>
                                    )}
                                </div>
                            </div>

                            {/* Kart 3: Teşhis */}
                            <div className="ticket-card diagnosis-card">
                                <div className="card-icon"><FaExclamationCircle /></div>
                                <h3>Teşhis</h3>
                                <p className="diagnosis-text">{ticketData.diagnosis.text}</p>
                                <div className="ai-insight">
                                    <strong>AI Analizi:</strong>
                                    <p>{ticketData.diagnosis.ai_analysis}</p>
                                </div>
                                {ticketData.diagnosis.estimated_time && (
                                    <div className="estimated-time">
                                        <FaClock /> Tahmini Çözüm: <strong>{ticketData.diagnosis.estimated_time}</strong>
                                    </div>
                                )}
                            </div>

                            {/* Kart 4: Önerilen Aksiyonlar */}
                            <div className="ticket-card actions-card">
                                <div className="card-icon"><FaTools /></div>
                                <h3>Önerilen Aksiyonlar</h3>
                                <ol className="actions-list">
                                    {ticketData.actions.map((action, index) => (
                                        <li key={index} className={action.startsWith('[ACİL]') ? 'urgent-action' : ''}>
                                            {action}
                                        </li>
                                    ))}
                                </ol>
                            </div>
                        </div>
                    ) : (
                        <div style={{ textAlign: 'center', padding: '2rem', color: '#ef4444' }}>
                            Rapor oluşturulamadı. Lütfen tekrar deneyin.
                        </div>
                    )}
                </div>

                <div className="ticket-modal-footer">
                    <button className="cancel-btn" onClick={onClose}>İptal</button>
                    <button className="submit-btn" onClick={handleSubmit} disabled={loading || generating || !ticketData}>
                        {loading ? 'Oluşturuluyor...' : <><FaSave /> Kaydı Oluştur</>}
                    </button>
                </div>
            </div>
        </div>
    );
};

export default TicketModal;
