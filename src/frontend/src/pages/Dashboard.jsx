import { useState, useEffect } from 'react';
import { api } from '../services/api';
import SubscriberListModal from '../components/SubscriberListModal';
import RegionalMap from '../components/RegionalMap';
import StatusPieChart from '../components/StatusPieChart';
import './Dashboard.css';

export default function Dashboard() {
    const [loading, setLoading] = useState(true);
    const [data, setData] = useState(null);
    const [error, setError] = useState(null);

    // Modal State
    const [isModalOpen, setIsModalOpen] = useState(false);
    const [modalFilter, setModalFilter] = useState('ALL');

    useEffect(() => {
        loadData();
        const interval = setInterval(loadData, 30000); // 30 saniyede bir yenile
        return () => clearInterval(interval);
    }, []);

    const loadData = async () => {
        try {
            const result = await api.getAllSubscribers();
            setData(result);
            setError(null);
        } catch (err) {
            setError('Veri yüklenemedi');
        } finally {
            setLoading(false);
        }
    };

    const handleStatClick = (filter) => {
        setModalFilter(filter);
        setIsModalOpen(true);
    };

    if (loading) return <div className="loading">Yükleniyor...</div>;
    if (error) return <div className="error">{error}</div>;

    const { lists, counts } = data;
    const totalCount = counts.GREEN + counts.YELLOW + counts.RED;

    return (
        <div className="dashboard">
            <div className="container">
                <header className="dashboard-header">
                    <h2>Network Operations Center</h2>

                    {/* Clickable Stats Overview */}
                    <div className="stats-overview">
                        <div className="stat-box all" onClick={() => handleStatClick('ALL')}>
                            <span className="stat-number">{totalCount}</span>
                            <span className="stat-label">📋 Tüm Aboneler</span>
                        </div>
                        <div className="stat-box green" onClick={() => handleStatClick('GREEN')}>
                            <span className="stat-number">{counts.GREEN}</span>
                            <span className="stat-label">🟢 Sağlıklı</span>
                        </div>
                        <div className="stat-box yellow" onClick={() => handleStatClick('YELLOW')}>
                            <span className="stat-number">{counts.YELLOW}</span>
                            <span className="stat-label">🟡 Riskli</span>
                        </div>
                        <div className="stat-box red" onClick={() => handleStatClick('RED')}>
                            <span className="stat-number">{counts.RED}</span>
                            <span className="stat-label">🔴 Arızalı</span>
                        </div>
                    </div>
                </header>

                {/* Main Visualization Grid */}
                <div className="viz-grid">
                    <div className="viz-item">
                        <StatusPieChart counts={counts} />
                    </div>
                    <div className="viz-item">
                        <RegionalMap subscribers={lists} />
                    </div>
                </div>

                {/* Subscriber List Modal */}
                <SubscriberListModal
                    isOpen={isModalOpen}
                    filter={modalFilter}
                    subscribers={lists}
                    onClose={() => setIsModalOpen(false)}
                />
            </div>
        </div>
    );
}
