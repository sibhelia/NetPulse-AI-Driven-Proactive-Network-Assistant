import './StatusBadge.css';

export default function StatusBadge({ status }) {
    const getStatusConfig = (status) => {
        switch (status) {
            case 'GREEN':
                return { label: 'Sağlıklı', icon: '🟢', className: 'status-green' };
            case 'YELLOW':
                return { label: 'Riskli', icon: '🟡', className: 'status-yellow' };
            case 'RED':
                return { label: 'Arızalı', icon: '🔴', className: 'status-red' };
            default:
                return { label: 'Bilinmiyor', icon: '⚪', className: 'status-unknown' };
        }
    };

    const config = getStatusConfig(status);

    return (
        <div className={`status-badge ${config.className}`}>
            <span className="status-icon">{config.icon}</span>
            <span className="status-label">{config.label}</span>
        </div>
    );
}
