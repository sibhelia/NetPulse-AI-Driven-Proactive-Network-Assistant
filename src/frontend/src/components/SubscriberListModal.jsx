import React, { useEffect } from 'react';
import SubscriberCard from './SubscriberCard';
import { IoClose } from 'react-icons/io5';
import './SubscriberListModal.css';

export default function SubscriberListModal({ isOpen, filter, subscribers, onClose }) {
    if (!isOpen) return null;

    useEffect(() => {
        const handleEsc = (e) => {
            if (e.key === 'Escape') onClose();
        };
        window.addEventListener('keydown', handleEsc);
        return () => window.removeEventListener('keydown', handleEsc);
    }, [onClose]);

    // Filter subscribers based on selection
    let displayList = [];
    let title = "";
    let headerClass = "";

    switch (filter) {
        case 'GREEN':
            displayList = subscribers.GREEN || [];
            title = "🟢 Sağlıklı Aboneler";
            headerClass = "GREEN";
            break;
        case 'YELLOW':
            displayList = subscribers.YELLOW || [];
            title = "🟡 Riskli Aboneler";
            headerClass = "YELLOW";
            break;
        case 'RED':
            displayList = subscribers.RED || [];
            title = "🔴 Arızalı Aboneler";
            headerClass = "RED";
            break;
        case 'ALL':
        default:
            displayList = [
                ...(subscribers.RED || []),
                ...(subscribers.YELLOW || []),
                ...(subscribers.GREEN || [])
            ];
            title = "📋 Tüm Aboneler";
            headerClass = "ALL";
            break;
    }

    return (
        <div className="modal-backdrop" onClick={onClose}>
            <div className="modal-container" onClick={e => e.stopPropagation()}>
                <div className={`modal-header ${headerClass}`}>
                    <h3>{title} <span style={{ fontSize: '1rem', color: '#666', fontWeight: 'normal' }}>({displayList.length})</span></h3>
                    <button className="close-button" onClick={onClose}>
                        <IoClose />
                    </button>
                </div>

                <div className="modal-content">
                    {displayList.length > 0 ? (
                        <div className="modal-list">
                            {displayList.map(sub => (
                                <SubscriberCard key={sub.id} subscriber={sub} />
                            ))}
                        </div>
                    ) : (
                        <div className="empty-state">
                            <p>Bu kategoride abone bulunmamaktadır.</p>
                        </div>
                    )}
                </div>
            </div>
        </div>
    );
}
