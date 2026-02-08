import { useState, useEffect } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import { api } from '../services/api';
import StatusBadge from '../components/StatusBadge';
import { LineChart, Line, AreaChart, Area, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer, BarChart, Bar } from 'recharts';
import { FaArrowLeft, FaPhone, FaMapMarkerAlt, FaServer, FaHistory, FaTools, FaRedo, FaNetworkWired, FaCheckCircle, FaExclamationTriangle } from 'react-icons/fa';
import './SubscriberDetail.css';

export default function SubscriberDetail() {
    const { id } = useParams();
    const navigate = useNavigate();
    const [loading, setLoading] = useState(true);
    const [data, setData] = useState(null);
    const [trendData, setTrendData] = useState(null);

    useEffect(() => {
        loadData();
    }, [id]);

    const loadData = async () => {
        try {
            const [detail, trend] = await Promise.all([
                api.getSubscriberDetail(id),
                api.getTrendAnalysis(id).catch(() => null)
            ]);
            setData(detail);
            setTrendData(trend);
        } catch (err) {
            console.error(err);
        } finally {
            setLoading(false);
        }
    };

    if (loading) return <div className="loading">Yükleniyor...</div>;
    if (!data) return <div className="error">Abone bulunamadı</div>;

    const { customer_info, live_metrics, ai_analysis, sms_notification } = data;

    // Mock History Data
    const historyData = [
        { id: 1, date: '08.02.2026 14:30', event: 'Sinyal Kopması', status: 'Otomatik Düzeltildi' },
        { id: 2, date: '07.02.2026 09:15', event: 'Yüksek Gecikme', status: 'İncelendi' },
        { id: 3, date: '05.02.2026 18:45', event: 'Modem Reset', status: 'Başarılı' },
    ];

    return (
        <div className="detail-page-wrapper">
            <div className="detail-container">
                {/* Header */}
                <header className="detail-header">
                    <div className="header-left">
                        <button className="back-btn" onClick={() => navigate(-1)} title="Geri Dön">
                            <FaArrowLeft />
                        </button>
                        <div className="header-title">
                            <h1>{customer_info.name}</h1>
                            <span className="sub-id">#{id}</span>
                        </div>
                    </div>
                    <div className="header-right">
                        <span className={`global-status ${ai_analysis.segment.toLowerCase()}`}>
                            {ai_analysis.segment === 'GREEN' ? 'SAĞLIKLI' :
                                ai_analysis.segment === 'YELLOW' ? 'RİSKLİ' : 'ARIZALI'}
                        </span>
                    </div>
                </header>

                {/* 3-Column Dashboard Grid */}
                <div className="dashboard-grid">

                    {/* LEFT COLUMN: PROFILE & DEVICE */}
                    <div className="grid-col left-col">
                        {/* Profile Card */}
                        <div className="card profile-card">
                            <div className="card-header">
                                <h3>👤 Abone Profili</h3>
                            </div>
                            <div className="profile-content">
                                <div className="avatar-large">{customer_info.name.charAt(0)}</div>
                                <div className="profile-details">
                                    <div className="detail-row">
                                        <FaPhone className="icon" /> <span>{customer_info.phone}</span>
                                    </div>
                                    <div className="detail-row">
                                        <FaMapMarkerAlt className="icon" /> <span>{customer_info.region}</span>
                                    </div>
                                    <div className="detail-row">
                                        <FaServer className="icon" /> <span>{customer_info.plan}</span>
                                    </div>
                                </div>
                            </div>
                        </div>

                        {/* Device Info */}
                        <div className="card device-card">
                            <div className="card-header">
                                <h3>📟 Cihaz Bilgisi</h3>
                            </div>
                            <div className="device-info">
                                <div className="info-item">
                                    <span className="label">Model:</span>
                                    <span className="value">Huawei HG255s</span>
                                </div>
                                <div className="info-item">
                                    <span className="label">Uptime:</span>
                                    <span className="value">14g 5s 32dk</span>
                                </div>
                                <div className="info-item">
                                    <span className="label">IP:</span>
                                    <span className="value">192.168.1.105</span>
                                </div>
                            </div>
                        </div>
                    </div>

                    {/* MIDDLE COLUMN: NETWORK STATUS & AI */}
                    <div className="grid-col mid-col">
                        {/* Live Metrics Grid */}
                        <div className="metrics-row">
                            <div className="metric-box">
                                <span className="metric-label">Hız</span>
                                <span className="metric-value">{live_metrics.download_speed?.toFixed(1)} <small>Mbps</small></span>
                                <div className="mini-chart speed"></div>
                            </div>
                            <div className="metric-box">
                                <span className="metric-label">Ping</span>
                                <span className="metric-value">{live_metrics.latency?.toFixed(1)} <small>ms</small></span>
                                <div className="mini-chart latency"></div>
                            </div>
                            <div className="metric-box">
                                <span className="metric-label">Jitter</span>
                                <span className="metric-value">{live_metrics.jitter?.toFixed(1)} <small>ms</small></span>
                            </div>
                            <div className="metric-box">
                                <span className="metric-label">Loss</span>
                                <span className="metric-value">{live_metrics.packet_loss?.toFixed(1)} <small>%</small></span>
                            </div>
                        </div>

                        {/* AI Analysis & Trend */}
                        <div className="card chart-card">
                            <div className="card-header">
                                <h3>📊 AI Risk Analizi & Trend</h3>
                            </div>
                            <div className="chart-content">
                                <div className="ai-summary">
                                    <div className="ai-badge">
                                        <strong>RF Model:</strong> {ai_analysis.snapshot.status}
                                    </div>
                                    <div className="ai-badge">
                                        <strong>Tahmin:</strong> {(ai_analysis.snapshot.confidence * 100).toFixed(0)}% Güven
                                    </div>
                                </div>

                                {trendData && trendData.analysis ? (
                                    <ResponsiveContainer width="100%" height={200}>
                                        <AreaChart data={trendData.analysis.risk_chart.map((risk, i) => ({ time: i, risk }))}>
                                            <defs>
                                                <linearGradient id="colorRisk" x1="0" y1="0" x2="0" y2="1">
                                                    <stop offset="5%" stopColor="#8B7FC7" stopOpacity={0.8} />
                                                    <stop offset="95%" stopColor="#8B7FC7" stopOpacity={0} />
                                                </linearGradient>
                                            </defs>
                                            <CartesianGrid strokeDasharray="3 3" vertical={false} />
                                            <XAxis dataKey="time" hide />
                                            <YAxis hide domain={[0, 100]} />
                                            <Tooltip />
                                            <Area type="monotone" dataKey="risk" stroke="#8B7FC7" strokeWidth={2} fill="url(#colorRisk)" />
                                        </AreaChart>
                                    </ResponsiveContainer>
                                ) : (
                                    <div className="no-data">Trend verisi hazırlanıyor...</div>
                                )}
                                <div className="ai-reason">
                                    <FaExclamationTriangle className="warning-icon" />
                                    <p>{ai_analysis.final_decision.reason}</p>
                                </div>
                            </div>
                        </div>
                    </div>

                    {/* RIGHT COLUMN: ACTIONS & HISTORY */}
                    <div className="grid-col right-col">
                        {/* Actions */}
                        <div className="card actions-card">
                            <div className="card-header">
                                <h3>⚡ Hızlı İşlemler</h3>
                            </div>
                            <div className="action-buttons">
                                <button className="action-btn primary">
                                    <FaRedo /> Hattı Sıfırla
                                </button>
                                <button className="action-btn secondary">
                                    <FaNetworkWired /> Ping Testi
                                </button>
                                <button className="action-btn danger">
                                    <FaTools /> Arıza Kaydı Aç
                                </button>
                            </div>
                        </div>

                        {/* History */}
                        <div className="card history-card">
                            <div className="card-header">
                                <h3><FaHistory /> Son Olaylar</h3>
                            </div>
                            <div className="history-list">
                                {historyData.map((item) => (
                                    <div key={item.id} className="history-item">
                                        <div className="history-date">{item.date}</div>
                                        <div className="history-event">{item.event}</div>
                                        <span className="history-status">{item.status}</span>
                                    </div>
                                ))}
                            </div>
                        </div>
                    </div>

                </div>
            </div>
        </div>
    );
}
