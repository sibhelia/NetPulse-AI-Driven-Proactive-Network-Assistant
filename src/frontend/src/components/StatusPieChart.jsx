import React from 'react';
import { PieChart, Pie, Cell, ResponsiveContainer, Tooltip, Legend } from 'recharts';
import { FaChartPie } from 'react-icons/fa'; // Importing a professional icon
import './StatusPieChart.css';

export default function StatusPieChart({ counts }) {
    // Pastel colors
    const COLORS = {
        GREEN: '#77DD77', // Pastel Green
        YELLOW: '#FFB347', // Pastel Orange
        RED: '#FF6961'    // Pastel Red
    };

    const total = counts.GREEN + counts.YELLOW + counts.RED;

    const data = [
        { name: 'Sağlıklı', value: counts.GREEN, color: COLORS.GREEN },
        { name: 'Riskli', value: counts.YELLOW, color: COLORS.YELLOW },
        { name: 'Arızalı', value: counts.RED, color: COLORS.RED }
    ];

    // Filter out zero values
    const activeData = data.filter(item => item.value > 0);

    // Custom Legend Render
    const renderLegend = (props) => {
        const { payload } = props;
        return (
            <div className="custom-legend">
                {payload.map((entry, index) => {
                    const count = entry.payload.value;
                    const percent = total > 0 ? ((count / total) * 100).toFixed(1) : 0;

                    return (
                        <div key={`item-${index}`} className="legend-item-custom">
                            <span
                                className="legend-color"
                                style={{ backgroundColor: entry.color }}
                            ></span>
                            <span className="legend-text-container">
                                <span className="legend-label">{entry.payload.name}</span>
                                <span className="legend-value-container">
                                    <strong className="legend-count">{count}</strong>
                                    <span className="legend-percent">(%{percent})</span>
                                </span>
                            </span>
                        </div>
                    );
                })}
            </div>
        );
    };

    return (
        <div className="status-chart-card">
            <div className="chart-header">
                <h3><FaChartPie className="chart-icon" /> Ağ Durum Dağılımı</h3>
                <p className="chart-description">Anlık ağ sağlık durumu dağılımı</p>
            </div>

            <div className="chart-container">
                <ResponsiveContainer width="100%" height="100%">
                    <PieChart>
                        <Pie
                            data={activeData}
                            cx="50%"
                            cy="50%"
                            innerRadius={60}
                            outerRadius={100}
                            paddingAngle={5}
                            dataKey="value"
                        >
                            {activeData.map((entry, index) => (
                                <Cell key={`cell-${index}`} fill={entry.color} stroke="none" />
                            ))}
                        </Pie>
                        <Tooltip
                            contentStyle={{ borderRadius: '8px', border: 'none', boxShadow: '0 4px 12px rgba(0,0,0,0.1)' }}
                        />
                        <Legend
                            content={renderLegend}
                            verticalAlign="bottom"
                            height={120}
                        />
                    </PieChart>
                </ResponsiveContainer>
            </div>
        </div>
    );
}
