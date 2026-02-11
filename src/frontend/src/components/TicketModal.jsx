
import React, { useState, useEffect } from 'react';
import { FaTimes, FaMagic, FaBuilding, FaHome, FaSave, FaExclamationCircle } from 'react-icons/fa';
import { api } from '../services/api';
import './TicketModal.css';

const TicketModal = ({ isOpen, onClose, subscriberId, currentStatus, aiAnalysis, onSuccess }) => {
    const [loading, setLoading] = useState(false);
    const [generating, setGenerating] = useState(false);
    const [ticketData, setTicketData] = useState({
        scope: 'INDIVIDUAL',
        note: '',
        neighborCount: 0
    });

    // Reset state when modal opens
    useEffect(() => {
        if (isOpen) {
            generateAutoNote();
        }
    }, [isOpen]);

    const generateAutoNote = async () => {
        setGenerating(true);
        try {
            // Call backend to generate note based on context
            const response = await api.generateTicketNote({
                subscriber_id: subscriberId,
                current_status: currentStatus,
                ai_analysis: aiAnalysis
            });

            setTicketData({
                scope: response.scope,
                note: response.note,
                neighborCount: response.neighbor_count
            });
        } catch (error) {
            console.error("Error generating note:", error);
            setTicketData(prev => ({
                ...prev,
                note: "Error generating AI note. Please enter details manually."
            }));
        } finally {
            setGenerating(false);
        }
    };

    const handleSubmit = async () => {
        // Here you would call the actual create ticket endpoint
        // For now we simulate success
        setLoading(true);
        setTimeout(() => {
            setLoading(false);
            onClose();
            if (onSuccess) onSuccess();
        }, 1000);
    };

    if (!isOpen) return null;

    return (
        <div className="ticket-modal-overlay">
            <div className="ticket-modal">
                <div className="ticket-modal-header">
                    <h2><FaMagic /> Akıllı Arıza Kaydı Oluştur</h2>
                    <button className="close-btn" onClick={onClose}><FaTimes /></button>
                </div>

                <div className="ticket-modal-body">

                    {/* 1. Scope Indicator */}
                    <div className={`scope-indicator ${ticketData.scope.toLowerCase()}`}>
                        <div className="scope-icon">
                            {ticketData.scope === 'REGIONAL' ? <FaBuilding /> : <FaHome />}
                        </div>
                        <div className="scope-details">
                            <h3>
                                {ticketData.scope === 'REGIONAL' ? 'Bölgesel Arıza Olasılığı' : 'Bireysel Arıza'}
                            </h3>
                            <p>
                                {ticketData.scope === 'REGIONAL'
                                    ? `Dikkat: Bu bölgede ${ticketData.neighborCount} farklı abonede benzer sorun var.`
                                    : 'Arıza sadece bu aboneye özgü görünüyor.'}
                            </p>
                        </div>
                    </div>

                    {/* 2. Priority & Type */}
                    <div className="form-row">
                        <div className="form-group">
                            <label>Öncelik Seviyesi</label>
                            <select disabled value={currentStatus === 'RED' ? 'High' : 'Medium'}>
                                <option value="High">🚨 Yüksek (Kritik)</option>
                                <option value="Medium">⚠️ Orta (Performans)</option>
                                <option value="Low">ℹ️ Düşük (Talep)</option>
                            </select>
                        </div>
                        <div className="form-group">
                            <label>Arıza Tipi</label>
                            <input type="text" value={ticketData.scope === 'REGIONAL' ? 'Altyapı / Genel' : 'CPE / Modem'} readOnly />
                        </div>
                    </div>

                    {/* 3. AI Generated Note */}
                    <div className="form-group full-width">
                        <div className="label-with-badge">
                            <label>Teknisyen İçin AI Notu</label>
                            {generating && <span className="generating-badge"><FaMagic /> Oluşturuluyor...</span>}
                        </div>
                        <textarea
                            value={ticketData.note}
                            onChange={(e) => setTicketData({ ...ticketData, note: e.target.value })}
                            rows={8}
                            className="ai-note-textarea"
                        />
                        <small className="hint-text">
                            * Bu not NetPulse AI tarafından bölgesel veriler analiz edilerek hazırlanmıştır. Teknisyene iletilmeden önce düzenleyebilirsiniz.
                        </small>
                    </div>
                </div>

                <div className="ticket-modal-footer">
                    <button className="cancel-btn" onClick={onClose}>İptal</button>
                    <button className="submit-btn" onClick={handleSubmit} disabled={loading || generating}>
                        {loading ? 'Oluşturuluyor...' : <><FaSave /> Kaydı Oluştur</>}
                    </button>
                </div>
            </div>
        </div>
    );
};

export default TicketModal;
