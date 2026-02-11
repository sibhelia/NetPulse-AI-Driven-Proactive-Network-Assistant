import React, { useState, useEffect } from 'react';
import { api } from '../services/api';
import { FaTicketAlt, FaUser, FaClock, FaMapMarkerAlt, FaCheckCircle } from 'react-icons/fa';
import './FieldTeamDashboard.css';

const FieldTeamDashboard = () => {
    const [tickets, setTickets] = useState([]);
    const [loading, setLoading] = useState(true);
    const [filter, setFilter] = useState('all'); // all, ASSIGNED, EN_ROUTE, ON_SITE
    const [selectedTicket, setSelectedTicket] = useState(null);

    useEffect(() => {
        fetchTickets();
    }, [filter]);

    const fetchTickets = async () => {
        setLoading(true);
        try {
            const filterStatus = filter === 'all' ? null : filter;
            const response = await api.getAllTickets(filterStatus);
            setTickets(response.tickets);
        } catch (error) {
            console.error('Failed to fetch tickets:', error);
        } finally {
            setLoading(false);
        }
    };

    const handleStatusUpdate = async (ticketId, newStatus) => {
        try {
            await api.updateTicketStatus(ticketId, {
                new_status: newStatus,
                changed_by: 'Saha Ekibi', // TODO: Gerçek kullanıcı adı
                note: `Status güncellendi: ${newStatus}`
            });
            fetchTickets(); // Refresh
            alert('Durum güncellendi!');
        } catch (error) {
            console.error('Status update failed:', error);
            alert('Güncelleme başarısız!');
        }
    };

    const getPriorityColor = (priority) => {
        if (priority === 'HIGH') return '#ef4444';
        if (priority === 'MEDIUM') return '#f59e0b';
        return '#10b981';
    };

    const getStatusLabel = (status) => {
        const labels = {
            'CREATED': 'Oluşturuldu',
            'ASSIGNED': 'Atan dı',
            'EN_ROUTE': 'Yolda',
            'ON_SITE': 'Sahada',
            'RESOLVED': 'Çözüldü',
            'CLOSED': 'Kapatıldı'
        };
        return labels[status] || status;
    };

    if (loading) {
        return <div className="loading">Yükleniyor...</div>;
    }

    return (
        <div className="field-team-dashboard">
            <div className="dashboard-header">
                <h1><FaTicketAlt /> Saha Ekibi - Arıza Takip Paneli</h1>
                <div className="filter-buttons">
                    <button
                        className={filter === 'all' ? 'active' : ''}
                        onClick={() => setFilter('all')}
                    >
                        Tümü ({tickets.length})
                    </button>
                    <button
                        className={filter === 'ASSIGNED' ? 'active' : ''}
                        onClick={() => setFilter('ASSIGNED')}
                    >
                        Atandı
                    </button>
                    <button
                        className={filter === 'EN_ROUTE' ? 'active' : ''}
                        onClick={() => setFilter('EN_ROUTE')}
                    >
                        Yolda
                    </button>
                    <button
                        className={filter === 'ON_SITE' ? 'active' : ''}
                        onClick={() => setFilter('ON_SITE')}
                    >
                        Sahada
                    </button>
                </div>
            </div>

            <div className="tickets-grid">
                {tickets.length === 0 ? (
                    <div className="no-tickets">Gösterilecek arıza kaydı yok</div>
                ) : (
                    tickets.map(ticket => (
                        <div
                            key={ticket.ticket_id}
                            className="ticket-card"
                            style={{ borderLeftColor: getPriorityColor(ticket.priority) }}
                        >
                            <div className="ticket-card-header">
                                <span className="ticket-id">#{ticket.ticket_id}</span>
                                <span className={`priority-badge ${ticket.priority.toLowerCase()}`}>
                                    {ticket.priority === 'HIGH' ? 'YÜKSEK' : ticket.priority === 'MEDIUM' ? 'ORTA' : 'DÜŞÜK'}
                                </span>
                            </div>

                            <div className="customer-info">
                                <div className="info-row">
                                    <FaUser /> <strong>{ticket.customer_name}</strong>
                                </div>
                                <div className="info-row">
                                    <FaMapMarkerAlt /> {ticket.customer_location}
                                </div>
                                <div className="info-row">
                                    <FaClock /> {new Date(ticket.created_at).toLocaleString('tr-TR')}
                                </div>
                            </div>

                            <div className="ticket-details">
                                <div className="detail-item">
                                    <span className="label">Durum:</span>
                                    <span className="value">{getStatusLabel(ticket.status)}</span>
                                </div>
                                <div className="detail-item">
                                    <span className="label">Kapsam:</span>
                                    <span className="value">{ticket.scope === 'REGIONAL' ? '🏢 Bölgesel' : '🏠 Bireysel'}</span>
                                </div>
                                <div className="detail-item">
                                    <span className="label">Atanan:</span>
                                    <span className="value">{ticket.assigned_to}</span>
                                </div>
                            </div>

                            <div className="action-buttons">
                                {ticket.status === 'CREATED' && (
                                    <button
                                        className="btn-accept"
                                        onClick={() => handleStatusUpdate(ticket.ticket_id, 'ASSIGNED')}
                                    >
                                        ✓ Kabul Et
                                    </button>
                                )}
                                {ticket.status === 'ASSIGNED' && (
                                    <button
                                        className="btn-enroute"
                                        onClick={() => handleStatusUpdate(ticket.ticket_id, 'EN_ROUTE')}
                                    >
                                        🚗 Yola Çıktım
                                    </button>
                                )}
                                {ticket.status === 'EN_ROUTE' && (
                                    <button
                                        className="btn-onsite"
                                        onClick={() => handleStatusUpdate(ticket.ticket_id, 'ON_SITE')}
                                    >
                                        📍 Sahadayım
                                    </button>
                                )}
                                {ticket.status === 'ON_SITE' && (
                                    <button
                                        className="btn-resolve"
                                        onClick={() => handleStatusUpdate(ticket.ticket_id, 'RESOLVED')}
                                    >
                                        <FaCheckCircle /> Arıza Giderildi
                                    </button>
                                )}
                            </div>
                        </div>
                    ))
                )}
            </div>
        </div>
    );
};

export default FieldTeamDashboard;
