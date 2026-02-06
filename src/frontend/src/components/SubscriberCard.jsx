import { useNavigate } from 'react-router-dom';
import StatusBadge from './StatusBadge';
import './SubscriberCard.css';

export default function SubscriberCard({ subscriber }) {
    const navigate = useNavigate();

    return (
        <div className="subscriber-card card fade-in">
            <div className="card-header">
                <h3 className="subscriber-name">{subscriber.name}</h3>
                <StatusBadge status={subscriber.metrics?.segment || 'GREEN'} />
            </div>

            <div className="card-body">
                <div className="info-row">
                    <span className="info-label">📍 Bölge:</span>
                    <span className="info-value">{subscriber.region}</span>
                </div>

                {subscriber.issue && (
                    <div className="issue-badge">
                        <span>⚠️ {subscriber.issue}</span>
                    </div>
                )}
            </div>

            <button
                className="detail-button"
                onClick={() => navigate(`/subscriber/${subscriber.id}`)}
            >
                Detaylı Analiz →
            </button>
        </div>
    );
}
