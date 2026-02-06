import { useState, useEffect } from 'react';
import { api } from '../services/api';
import SubscriberCard from '../components/SubscriberCard';
import './Dashboard.css';

export default function Dashboard() {
    const [loading, setLoading] = useState(true);
    const [data, setData] = useState(null);
    const [error, setError] = useState(null);

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

    if (loading) return <div className="loading">Yükleniyor...</div>;
    if (error) return <div className="error">{error}</div>;

    const { lists, counts } = data;

    return (
        <div className="dashboard">
            <div className="container">
                <header className="dashboard-header">
                    <h2>Network Operations Center</h2>
                    <div className="stats-overview">
                        <div className="stat-box green">
                            <span className="stat-number">{counts.GREEN}</span>
                            <span className="stat-label">🟢 Sağlıklı</span>
                        </div>
                        <div className="stat-box yellow">
                            <span className="stat-number">{counts.YELLOW}</span>
                            <span className="stat-label">🟡 Riskli</span>
                        </div>
                        <div className="stat-box red">
                            <span className="stat-number">{counts.RED}</span>
                            <span className="stat-label">🔴 Arızalı</span>
                        </div>
                    </div>
                </header>

                <div className="subscribers-grid">
                    <div className="column green-column">
                        <h3 className="column-title">🟢 Sağlıklı Aboneler</h3>
                        <div className="cards-list">
                            {lists.GREEN.slice(0, 10).map(sub => (
                                <SubscriberCard key={sub.id} subscriber={sub} />
                            ))}
                        </div>
                    </div>

                    <div className="column yellow-column">
                        <h3 className="column-title">🟡 Riskli Aboneler</h3>
                        <div className="cards-list">
                            {lists.YELLOW.map(sub => (
                                <SubscriberCard key={sub.id} subscriber={sub} />
                            ))}
                        </div>
                    </div>

                    <div className="column red-column">
                        <h3 className="column-title">🔴 Arızalı Aboneler</h3>
                        <div className="cards-list">
                            {lists.RED.map(sub => (
                                <SubscriberCard key={sub.id} subscriber={sub} />
                            ))}
                        </div>
                    </div>
                </div>
            </div>
        </div>
    );
}
