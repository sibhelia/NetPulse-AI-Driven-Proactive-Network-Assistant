import React from 'react';
import { FaCheckCircle, FaCircle, FaClock } from 'react-icons/fa';
import './TicketProgressBar.css';

const TicketProgressBar = ({ ticket }) => {
    const statusSteps = [
        { key: 'CREATED', label: 'Oluşturuldu', icon: FaCheckCircle },
        { key: 'ASSIGNED', label: 'Atandı', icon: FaCheckCircle },
        { key: 'EN_ROUTE', label: 'Yolda', icon: FaClock },
        { key: 'ON_SITE', label: 'Sahada', icon: FaClock },
        { key: 'RESOLVED', label: 'Çözüldü', icon: FaCheckCircle },
        { key: 'CLOSED', label: 'Kapatıldı', icon: FaCheckCircle }
    ];

    const currentIndex = statusSteps.findIndex(step => step.key === ticket.status);

    const getStatusClass = (index) => {
        if (index < currentIndex) return 'step-completed';
        if (index === currentIndex) return 'step-active';
        return 'Step-pending';
    };

    const getPriorityColor = () => {
        if (ticket.priority === 'HIGH') return '#ef4444';
        if (ticket.priority === 'MEDIUM') return '#f59e0b';
        return '#10b981';
    };

    return (
        <div className="ticket-progress-container">
            <div className="ticket-progress-header">
                <div className="ticket-info">
                    <span className="ticket-id">Arıza #{ticket.ticket_id}</span>
                    <span className={`priority-badge ${ticket.priority.toLowerCase()}`}>
                        {ticket.priority === 'HIGH' ? 'YÜKSEK' : ticket.priority === 'MEDIUM' ? 'ORTA' : 'DÜŞÜK'}
                    </span>
                    <span className="ticket-scope">{ticket.scope === 'REGIONAL' ? '🏢 Bölgesel' : '🏠 Bireysel'}</span>
                </div>
                <div className="ticket-time">
                    Oluşturma: {new Date(ticket.created_at).toLocaleString('tr-TR', {
                        day: '2-digit',
                        month: '2-digit',
                        hour: '2-digit',
                        minute: '2-digit'
                    })}
                </div>
            </div>

            <div className="progress-bar-wrapper">
                <div className="progress-fill" style={{
                    width: `${((currentIndex + 1) / statusSteps.length) * 100}%`,
                    background: getPriorityColor()
                }}></div>
            </div>

            <div className="status-steps">
                {statusSteps.map((step, index) => {
                    const Icon = step.icon;
                    return (
                        <div key={step.key} className={`status-step ${getStatusClass(index)}`}>
                            <div className="step-icon">
                                <Icon />
                            </div>
                            <div className="step-label">{step.label}</div>
                        </div>
                    );
                })}
            </div>
        </div>
    );
};

export default TicketProgressBar;
