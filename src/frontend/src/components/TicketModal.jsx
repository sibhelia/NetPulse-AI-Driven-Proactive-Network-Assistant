import React, { useState, useEffect } from 'react';
import { api } from '../services/api';
import './TicketModal.css';

const TicketModal = ({ isOpen, onClose, subscriberId, onSuccess }) => {
    const [technicians, setTechnicians] = useState([]);
    const [selectedTech, setSelectedTech] = useState('');
    const [issueType, setIssueType] = useState('Bağlantı Sorunu');
    const [notes, setNotes] = useState('');
    const [loading, setLoading] = useState(false);

    useEffect(() => {
        if (isOpen) {
            // Fetch technicians
            api.getTechnicians()
                .then(data => setTechnicians(data))
                .catch(err => console.error("Tech fetch error:", err));
        }
    }, [isOpen]);

    const handleSubmit = async (e) => {
        e.preventDefault();
        setLoading(true);
        try {
            await api.createTicket({
                subscriber_id: subscriberId,
                technician_id: parseInt(selectedTech),
                issue_type: issueType,
                notes: notes
            });
            onSuccess(); // Refresh parent or show toast
            onClose();
        } catch (error) {
            alert("Kayıt oluşturulamadı: " + error.message);
        } finally {
            setLoading(false);
        }
    };

    if (!isOpen) return null;

    return (
        <div className="modal-overlay">
            <div className="modal-content">
                <div className="modal-header">
                    <h3>Yeni Arıza Kaydı Oluştur</h3>
                    <button className="close-btn" onClick={onClose}>&times;</button>
                </div>
                <form onSubmit={handleSubmit}>
                    <div className="form-group">
                        <label>Teknisyen Atama</label>
                        <select
                            value={selectedTech}
                            onChange={(e) => setSelectedTech(e.target.value)}
                            required
                        >
                            <option value="">Teknisyen Seçiniz...</option>
                            {technicians.map(tech => (
                                <option key={tech.id} value={tech.id}>
                                    {tech.name} - {tech.expertise} ({tech.status})
                                </option>
                            ))}
                        </select>
                    </div>

                    <div className="form-group">
                        <label>Arıza Türü</label>
                        <select value={issueType} onChange={(e) => setIssueType(e.target.value)}>
                            <option value="Bağlantı Sorunu">Bağlantı Sorunu</option>
                            <option value="Hız Düşüklüğü">Hız Düşüklüğü (Yavaşlık)</option>
                            <option value="Modem Arızası">Modem / Cihaz Arızası</option>
                            <option value="Kablo Sorunu">Kablo / Altyapı Sorunu</option>
                        </select>
                    </div>

                    <div className="form-group">
                        <label>Notlar</label>
                        <textarea
                            value={notes}
                            onChange={(e) => setNotes(e.target.value)}
                            rows="4"
                            placeholder="Arıza detaylarını buraya giriniz..."
                        ></textarea>
                    </div>

                    <div className="modal-actions">
                        <button type="button" className="btn-secondary" onClick={onClose}>İptal</button>
                        <button type="submit" className="btn-primary" disabled={loading}>
                            {loading ? 'Oluşturuluyor...' : 'Kaydı Oluştur'}
                        </button>
                    </div>
                </form>
            </div>
        </div>
    );
};

export default TicketModal;
