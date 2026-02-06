import { useState, useEffect } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import { api } from '../services/api';
import StatusBadge from '../components/StatusBadge';
import { LineChart, Line, AreaChart, Area, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer } from 'recharts';
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

    return (
        <div className="detail-page">
            <div className="container">
                <button className="back-button" onClick={() => navigate('/')}>
                    ← Dashboard'a Dön
                </button>

                <div className="detail-grid">
                    {/* Customer Info */}
                    <div className="card info-card">
                        <h2>{customer_info.name}</h2>
                        <div className="info-grid">
                            <div><strong>📞 Telefon:</strong> {customer_info.phone}</div>
                            <div><strong>📍 Bölge:</strong> {customer_info.region}</div>
                            <div><strong>📦 Paket:</strong> {customer_info.plan}</div>
                            <div>
                                <strong>Durum:</strong>
                                <StatusBadge status={ai_analysis.segment} />
                            </div>
                        </div>
                    </div>

                    {/* Metrics */}
                    <div className="card metrics-card">
                        <h3>📊 Anlık Metrikler</h3>
                        <div className="metrics-grid">
                            <div className="metric">
                                <span className="metric-label">Ping</span>
                                <span className="metric-value">{live_metrics.latency?.toFixed(1)} ms</span>
                            </div>
                            <div className="metric">
                                <span className="metric-label">Paket Kaybı</span>
                                <span className="metric-value">{live_metrics.packet_loss?.toFixed(2)}%</span>
                            </div>
                            <div className="metric">
                                <span className="metric-label">Hız</span>
                                <span className="metric-value">{live_metrics.download_speed?.toFixed(1)} Mbps</span>
                            </div>
                            <div className="metric">
                                <span className="metric-label">Jitter</span>
                                <span className="metric-value">{live_metrics.jitter?.toFixed(1)} ms</span>
                            </div>
                        </div>
                    </div>

                    {/* AI Analysis */}
                    <div className="card ai-card">
                        <h3>🤖 AI Analizi</h3>
                        <div className="analysis-section">
                            <div className="model-result">
                                <strong>Random Forest:</strong> {ai_analysis.snapshot.status}
                                <span className="confidence">({(ai_analysis.snapshot.confidence * 100).toFixed(0)}%)</span>
                            </div>
                            <div className="model-result">
                                <strong>LSTM:</strong> {ai_analysis.trend.available ? 'Aktif' : 'Veri yetersiz'}
                                {ai_analysis.trend.confidence && (
                                    <span className="confidence">({(ai_analysis.trend.confidence * 100).toFixed(0)}%)</span>
                                )}
                            </div>
                            <div className="final-decision">
                                <strong>Final Karar:</strong>
                                <p>{ai_analysis.final_decision.reason}</p>
                            </div>
                        </div>
                    </div>

                    {/* SMS History */}
                    {sms_notification?.sent && (
                        <div className="card sms-card">
                            <h3>📱 SMS Bildirimi</h3>
                            <div className="sms-info">
                                <p><strong>Durum:</strong> Gönderildi ✅</p>
                                <p><strong>Geçiş:</strong> {sms_notification.transition}</p>
                                <p className="sms-message">{sms_notification.message}</p>
                            </div>
                        </div>
                    )}

                    {/* Trend Chart */}
                    {trendData && trendData.analysis && (
                        <div className="card chart-card">
                            <h3>📈 LSTM Trend Analizi</h3>
                            <ResponsiveContainer width="100%" height={300}>
                                <AreaChart data={trendData.analysis.risk_chart.map((risk, i) => ({ time: i, risk }))}>
                                    <defs>
                                        <linearGradient id="colorRisk" x1="0" y1="0" x2="0" y2="1">
                                            <stop offset="5%" stopColor="#8B7FC7" stopOpacity={0.8} />
                                            <stop offset="95%" stopColor="#8B7FC7" stopOpacity={0} />
                                        </linearGradient>
                                    </defs>
                                    <CartesianGrid strokeDasharray="3 3" />
                                    <XAxis dataKey="time" label={{ value: 'Zaman', position: 'insideBottom', offset: -5 }} />
                                    <YAxis label={{ value: 'Risk', angle: -90, position: 'insideLeft' }} />
                                    <Tooltip />
                                    <Area type="monotone" dataKey="risk" stroke="#8B7FC7" fillOpacity={1} fill="url(#colorRisk)" />
                                </AreaChart>
                            </ResponsiveContainer>
                            <div className="trend-summary">
                                <p><strong>Trend:</strong> {trendData.analysis.trend_direction}</p>
                                <p><strong>30 dk Tahmin:</strong> {trendData.analysis.forecast_30min?.toFixed(2)}</p>
                                <p><strong>Öneri:</strong> {trendData.analysis.recommendation}</p>
                            </div>
                        </div>
                    )}
                </div>
            </div>
        </div>
    );
}
