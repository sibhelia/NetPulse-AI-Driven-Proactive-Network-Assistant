import React from 'react';
import { PieChart, Pie, Cell, ResponsiveContainer, Tooltip, Legend } from 'recharts';
import './StatusPieChart.css';

export default function StatusPieChart({ counts }) {
    const data = [
        { name: 'Sağlıklı', value: counts.GREEN, color: '#4CAF50' },
        { name: 'Riskli', value: counts.YELLOW, color: '#FFC107' },
        { name: 'Arızalı', value: counts.RED, color: '#F44336' }
    ];

    // Filter out zero values to avoid ugly empty segments
    const activeData = data.filter(item => item.value > 0);

    return (
        <div className="status-chart-card">
            <div className="chart-header">
                <h3>📊 Ağ Durum Dağılımı</h3>
            </div>

            <div className="chart-container">
                <ResponsiveContainer width="100%" height="100%">
                    <PieChart>
                        <Pie
                            data={activeData}
                            cx="50%"
                            cy="50%"
                            innerRadius={50}
                            outerRadius={80}
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
                        <Legend verticalAlign="bottom" height={36} iconType="circle" />
                    </PieChart>
                </ResponsiveContainer>
            </div>
        </div>
    );
}
