import React, { useState, useEffect } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import { api } from '../services/api';
import StatusBadge from '../components/StatusBadge';
import TicketModal from '../components/TicketModal';
import { FaArrowLeft, FaServer, FaNetworkWired, FaMapMarkerAlt, FaHistory, FaTools, FaBolt, FaRedo, FaExclamationTriangle, FaMale, FaFemale, FaUser } from 'react-icons/fa';
import './SubscriberDetail.css';

// Recharts for micro-charts
import { LineChart, Line, ResponsiveContainer, YAxis } from 'recharts';

const SubscriberDetail = () => {
    const { id } = useParams();
    const navigate = useNavigate();

    const [subscriber, setSubscriber] = useState(null);
    const [loading, setLoading] = useState(true);
    const [error, setError] = useState(null);
    const [isTicketModalOpen, setIsTicketModalOpen] = useState(false);
    const [actionLoading, setActionLoading] = useState(null);

    // Mock data for sparklines (since we only have instantaneous values usually)
    const [sparkData, setSparkData] = useState([]);

    const fetchSubscriber = async () => {
        try {
            const data = await api.getSubscriberDetail(id);
            setSubscriber(data);

            // Generate mock sparkline data based on current value mostly
            const currentLatency = data.live_metrics.latency;
            const history = Array.from({ length: 10 }).map((_, i) => ({
                value: currentLatency + (Math.random() * 10 - 5)
            }));
            setSparkData(history);

        } catch (err) {
            setError(err.message);
        } finally {
            setLoading(false);
        }
    };

    useEffect(() => {
        fetchSubscriber();
        // Poll every 5 seconds for live updates
        const interval = setInterval(fetchSubscriber, 5000);
        return () => clearInterval(interval);
    }, [id]);

    const handleAction = async (actionType) => {
        setActionLoading(actionType);
        try {
            await api.performAction(actionType, id);
            // Show simple alert or toast (using native alert for simplicity here)
            alert(`${actionType === 'reset' ? 'Hat sıfırlama' : 'Ping testi'} işlemi başarıyla tamamlandı.`);
            fetchSubscriber(); // Refresh data
        } catch (err) {
            alert("İşlem başarısız: " + err.message);
        } finally {
            setActionLoading(null);
        }
    };

    if (loading) return <div className="loading-screen">Yükleniyor...</div>;
    if (error) return <div className="error-screen">Hata: {error}</div>;
    if (!subscriber) return <div>Abone bulunamadı.</div>;

    const { customer_info, live_metrics, ai_analysis, history } = subscriber;

    return (
        <div className="detail-page-wrapper">
            {/* Header */}
            <div className="detail-header">
                <div className="header-left">
                    <button onClick={() => navigate(-1)} className="back-btn">
                        <FaArrowLeft />
                    </button>
                    {/* Avatar based on gender */}
                    <div className="subscriber-avatar">
                        {customer_info.gender === 'Erkek' ? <FaMale /> : customer_info.gender === 'Kadın' ? <FaFemale /> : <FaUser />}
                    </div>
                    <div className="subscriber-title">
                        <h1>{customer_info.name}</h1>
                        <span className="sub-id">#{subscriber.subscriber_id} - {customer_info.plan}</span>
                    </div>
                </div>
                <div className="header-right">
                    <StatusBadge status={ai_analysis.segment} />
                </div>
            </div>

            <div className="dashboard-grid">

                {/* 1. LEFT COLUMN: PROFILE & DEVICE */}
                <div className="left-column">
                    <div className="dashboard-card">
                        <div className="card-header" style={{ color: '#9333ea' }}>
                            <h3><FaNetworkWired /> Abonelik Bilgileri</h3>
                        </div>
                        <div className="profile-info-row">
                            <span className="info-label">Telefon:</span>
                            <span className="info-value">{customer_info.phone}</span>
                        </div>
                        <div className="profile-info-row">
                            <span className="info-label">Paket:</span>
                            <span className="info-value">{customer_info.plan}</span>
                        </div>
                        <div className="profile-info-row">
                            <span className="info-label">Bölge:</span>
                            <span className="info-value">{customer_info.region}</span>
                        </div>
                    </div>

                    <div className="dashboard-card device-card">
                        <div className="card-header" style={{ color: '#9333ea' }}>
                            <h3><FaServer /> Cihaz Durumu</h3>
                        </div>
                        <div className="device-status">
                            <div className="status-item">
                                <span className="info-label">Modem:</span>
                                <span className="info-value">{customer_info.modem}</span>
                            </div>
                            <div className="status-item">
                                <span className="info-label">IP Adresi:</span>
                                <span className="info-value">{customer_info.ip}</span>
                            </div>
                            <div className="status-item">
                                <span className="info-label">Uptime:</span>
                                <span className="info-value">{customer_info.uptime}</span>
                            </div>
                        </div>
                    </div>

                    <div className="dashboard-card location-card">
                        <div className="card-header">
                            <h3><FaMapMarkerAlt /> Konum</h3>
                        </div>
                        <div style={{ textAlign: 'center', marginBottom: '0.75rem', padding: '0.5rem', background: 'linear-gradient(135deg, #667eea 0%, #764ba2 100%)', borderRadius: '8px', color: 'white', fontWeight: '600', fontSize: '0.9rem' }}>
                            📍 {customer_info.location.address}
                        </div>
                        <div style={{ borderRadius: '8px', overflow: 'hidden', height: '200px' }}>
                            <iframe
                                width="100%"
                                height="200"
                                frameBorder="0"
                                scrolling="no"
                                marginHeight="0"
                                marginWidth="0"
                                src={`https://www.openstreetmap.org/export/embed.html?bbox=${customer_info.location.longitude - 0.006}%2C${customer_info.location.latitude - 0.004}%2C${customer_info.location.longitude + 0.006}%2C${customer_info.location.latitude + 0.004}&layer=mapnik&marker=${customer_info.location.latitude}%2C${customer_info.location.longitude}`}
                                style={{ border: 0 }}
                            ></iframe>
                            <small style={{ display: 'block', textAlign: 'center', marginTop: '4px', color: '#64748b', fontSize: '11px' }}>
                                📍 {customer_info.location.address}
                            </small>
                        </div>
                    </div>
                </div>

                {/* 2. MIDDLE COLUMN: LIVE METRICS & ANALYSIS */}
                <div className="middle-column">
                    <div className="dashboard-card">
                        <div className="card-header">
                            <h3><FaBolt /> Canlı Ağ Performansı</h3>
                        </div>
                        <div className="metrics-grid">
                            <div className="metric-box">
                                <h4>Download Hızı</h4>
                                <div className="metric-value">
                                    {live_metrics.download_speed.toFixed(1)} <span className="metric-unit">Mbps</span>
                                </div>
                                <div style={{ height: 30, marginTop: 8 }}>
                                    <ResponsiveContainer width="100%" height="100%">
                                        <LineChart data={sparkData.map(d => ({ value: d.value * live_metrics.download_speed / 50 }))}>
                                            <Line type="monotone" dataKey="value" stroke="#10b981" strokeWidth={2} dot={false} />
                                            <YAxis hide domain={['dataMin', 'dataMax']} />
                                        </LineChart>
                                    </ResponsiveContainer>
                                </div>
                            </div>
                            <div className="metric-box">
                                <h4>Gecikme (Ping)</h4>
                                <div className="metric-value">
                                    {live_metrics.latency.toFixed(0)} <span className="metric-unit">ms</span>
                                </div>
                                <div style={{ height: 30 }}>
                                    <ResponsiveContainer width="100%" height="100%">
                                        <LineChart data={sparkData}>
                                            <Line type="monotone" dataKey="value" stroke="#8884d8" strokeWidth={2} dot={false} />
                                            <YAxis hide domain={['dataMin', 'dataMax']} />
                                        </LineChart>
                                    </ResponsiveContainer>
                                </div>
                            </div>
                            <div className="metric-box">
                                <h4>Jitter</h4>
                                <div className="metric-value">
                                    {live_metrics.jitter.toFixed(1)} <span className="metric-unit">ms</span>
                                </div>
                                <div style={{ height: 30, marginTop: 8 }}>
                                    <ResponsiveContainer width="100%" height="100%">
                                        <LineChart data={sparkData.map(d => ({ value: d.value * live_metrics.jitter / 50 }))}>
                                            <Line type="monotone" dataKey="value" stroke="#f59e0b" strokeWidth={2} dot={false} />
                                            <YAxis hide domain={['dataMin', 'dataMax']} />
                                        </LineChart>
                                    </ResponsiveContainer>
                                </div>
                            </div>
                            <div className="metric-box">
                                <h4>Packet Loss</h4>
                                <div className="metric-value" style={{ color: live_metrics.packet_loss > 0 ? '#dc2626' : '#16a34a' }}>
                                    %{live_metrics.packet_loss.toFixed(1)}
                                </div>
                                <div style={{ height: 30, marginTop: 8 }}>
                                    <ResponsiveContainer width="100%" height="100%">
                                        <LineChart data={sparkData.map(d => ({ value: Math.abs(d.value - 50) * live_metrics.packet_loss / 50 }))}>
                                            <Line type="monotone" dataKey="value" stroke="#dc2626" strokeWidth={2} dot={false} />
                                            <YAxis hide domain={[0, 'dataMax']} />
                                        </LineChart>
                                    </ResponsiveContainer>
                                </div>
                            </div>
                        </div>
                    </div>

                    <div className="dashboard-card ai-analysis-card" style={{ display: 'flex', flexDirection: 'column' }}>
                        <div className="card-header">
                            <h3><FaExclamationTriangle /> NetPulse AI Analizi (Admin Raporu)</h3>
                        </div>
                        <div className="analysis-content" style={{ display: 'flex', flexDirection: 'column' }}>
                            <div className="analysis-text" style={{ display: 'flex', flexDirection: 'column' }}>
                                <p className="analysis-story" style={{ marginBottom: '1.5rem' }}>
                                    {ai_analysis.story || ai_analysis.explanation}
                                </p>

                                <div style={{ paddingTop: '1rem', borderTop: '1px solid #f1f5f9', marginTop: 'auto' }}>
                                    <div className="analysis-meta" style={{ marginBottom: '1rem', border: 'none', padding: 0, background: 'transparent' }}>
                                        <div className="meta-item">
                                            <strong>Tahmini Çözüm:</strong> {ai_analysis.estimated_fix || 'Belirsiz'}
                                        </div>
                                        <div className="meta-item">
                                            <strong>Risk Skoru:</strong> {(ai_analysis.risk_score * 100).toFixed(0)}/100
                                        </div>
                                    </div>

                                    {/* SMS Notification Button for RED/YELLOW status */}
                                    {(ai_analysis.segment === 'RED' || ai_analysis.segment === 'YELLOW') && (
                                        <button
                                            className="sms-notify-btn"
                                            onClick={() => alert(`SMS gönderilecek: Sayın ${customer_info.name}, internet bağlantınızda bir sorun tespit ettik. Ekiplerimiz durumdan haberdar edildi ve en kısa sürede iletişime geçecektir. - NetPulse Destek`)}
                                        >
                                            <FaBolt /> Kullanıcıyı Bilgilendir (SMS)
                                        </button>
                                    )}
                                </div>
                            </div>
                        </div>
                    </div>
                </div>

                {/* 3. RIGHT COLUMN: ACTIONS & HISTORY */}
                <div className="right-column">
                    <div className="dashboard-card">
                        <div className="card-header">
                            <h3><FaTools /> Hızlı İşlemler</h3>
                        </div>
                        <div className="action-buttons">
                            <button
                                className="action-btn reset"
                                onClick={() => handleAction('reset')}
                                disabled={actionLoading}
                            >
                                <FaRedo className={actionLoading === 'reset' ? 'fa-spin' : ''} />
                                {actionLoading === 'reset' ? 'Sıfırlanıyor...' : 'Hattı Sıfırla (Port Reset)'}
                            </button>
                            <button
                                className="action-btn ping"
                                onClick={() => handleAction('ping')}
                                disabled={actionLoading}
                            >
                                <FaNetworkWired className={actionLoading === 'ping' ? 'fa-spin' : ''} />
                                {actionLoading === 'ping' ? 'Test Ediliyor...' : 'Ping Testi Başlat'}
                            </button>
                            <button className="action-btn ticket" onClick={() => setIsTicketModalOpen(true)}>
                                <FaTools /> Arıza Kaydı Aç
                            </button>
                        </div>
                    </div>

                    <div className="dashboard-card">
                        <div className="card-header">
                            <h3><FaHistory /> İşlem Geçmişi / Loglar</h3>
                        </div>
                        <ul className="history-list">
                            {history && history.length > 0 ? history.map((item, index) => (
                                <li key={index} className="history-item">
                                    <div className="history-header">
                                        <span className="history-date">{item.date}</span>
                                        <span className={`status-tag ${item.status.toLowerCase()}`}>{item.status}</span>
                                    </div>
                                    <span className="history-event">{item.event}</span>
                                    <div className="history-meta">
                                        <span>Teknisyen:</span>
                                        <span className="tech-name">{item.tech || 'Sistem'}</span>
                                    </div>
                                </li>
                            )) : (
                                <li className="history-item" style={{ textAlign: 'center', color: '#94a3b8' }}>
                                    Kayıt bulunamadı.
                                </li>
                            )}
                        </ul>
                    </div>
                </div>

            </div>

            {/* Ticket Modal */}
            <TicketModal
                isOpen={isTicketModalOpen}
                onClose={() => setIsTicketModalOpen(false)}
                subscriberId={subscriber.subscriber_id}
                currentStatus={ai_analysis.segment}
                aiAnalysis={ai_analysis.reason}
                liveMetrics={live_metrics}
                onSuccess={() => {
                    fetchSubscriber();
                    alert("Arıza kaydı başarıyla oluşturuldu ve ekibe iletildi.");
                }}
            />
        </div>
    );
};

export default SubscriberDetail;
