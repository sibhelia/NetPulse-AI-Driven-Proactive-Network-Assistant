import { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import './RegionalMap.css';

export default function RegionalMap({ subscribers }) {
    const [hoveredPin, setHoveredPin] = useState(null);
    const navigate = useNavigate();

    // İstanbul mahallelerinin koordinatları (Türkiye haritasında relative pozisyon)
    const locationCoords = {
        'Kadıköy/Moda': { x: 580, y: 320 },
        'Kadıköy/Fenerbahçe': { x: 590, y: 330 },
        'Beşiktaş/Etiler': { x: 540, y: 310 },
        'Beşiktaş/Bebek': { x: 535, y: 305 },
        'Şişli/Mecidiyeköy': { x: 545, y: 315 },
        'Şişli/Nişantaşı': { x: 550, y: 318 },
        'Üsküdar/Çengelköy': { x: 595, y: 315 },
        'Üsküdar/Kuzguncuk': { x: 600, y: 318 },
        'Sarıyer/İstinye': { x: 525, y: 295 },
        'Sarıyer/Tarabya': { x: 520, y: 290 },
        'Bakırköy/Ataköy': { x: 515, y: 335 },
        'Bakırköy/Yeşilköy': { x: 510, y: 340 },
    };

    const getCoords = (location) => {
        return locationCoords[location] || { x: 550, y: 320 };
    };

    if (!subscribers) {
        return <div className="map-loading">Veri bekleniyor...</div>;
    }

    const totalSubscribers = (subscribers.GREEN?.length || 0) + (subscribers.YELLOW?.length || 0) + (subscribers.RED?.length || 0);

    const handlePinClick = (id) => {
        navigate(`/subscriber/${id}`);
    };

    return (
        <div className="regional-map">
            <div className="map-header">
                <h3>🗺️ Türkiye Geneli Ağ Haritası</h3>
                <p>İstanbul bölgesindeki {totalSubscribers} abone izleniyor</p>
            </div>

            <div className="map-container">
                <svg viewBox="0 40 800 400" className="turkey-map">
                    {/* Simplified Turkey Map */}
                    <path
                        d="M 100 250 L 150 200 L 250 180 L 350 170 L 450 160 L 550 180 L 650 200 L 720 220 L 750 250 L 730 300 L 680 340 L 600 360 L 500 370 L 400 360 L 300 350 L 200 330 L 120 300 Z"
                        fill="#E0E0E0"
                        stroke="#999"
                        strokeWidth="2"
                        className="turkey-border"
                    />

                    {/* Istanbul Region Highlight */}
                    <ellipse
                        cx="550"
                        cy="320"
                        rx="80"
                        ry="60"
                        fill="rgba(139, 127, 199, 0.2)"
                        stroke="var(--purple-soft)"
                        strokeWidth="3"
                        strokeDasharray="5,5"
                        className="istanbul-highlight"
                    />
                    <text x="550" y="280" className="region-name">İSTANBUL</text>

                    {/* Location Pins - GREEN */}
                    {subscribers.GREEN?.slice(0, 15).map((sub, idx) => {
                        const coords = getCoords(sub.location);
                        return (
                            <g
                                key={`green-${sub.id}`}
                                onMouseEnter={() => setHoveredPin(sub)}
                                onMouseLeave={() => setHoveredPin(null)}
                                onClick={() => handlePinClick(sub.id)}
                                className="location-pin"
                            >
                                <circle
                                    cx={coords.x + (idx % 3) * 4}
                                    cy={coords.y + (idx % 3) * 4}
                                    r="6"
                                    fill="#4CAF50"
                                    stroke="white"
                                    strokeWidth="2"
                                    className="pin green-pin"
                                />
                            </g>
                        );
                    })}

                    {/* Location Pins - YELLOW */}
                    {subscribers.YELLOW?.map((sub, idx) => {
                        const coords = getCoords(sub.location);
                        return (
                            <g
                                key={`yellow-${sub.id}`}
                                onMouseEnter={() => setHoveredPin(sub)}
                                onMouseLeave={() => setHoveredPin(null)}
                                onClick={() => handlePinClick(sub.id)}
                                className="location-pin"
                            >
                                <circle
                                    cx={coords.x + (idx % 2) * 5}
                                    cy={coords.y + (idx % 2) * 5}
                                    r="7"
                                    fill="#FFC107"
                                    stroke="white"
                                    strokeWidth="2"
                                    className="pin yellow-pin"
                                />
                            </g>
                        );
                    })}

                    {/* Location Pins - RED */}
                    {subscribers.RED?.map((sub, idx) => {
                        const coords = getCoords(sub.location);
                        return (
                            <g
                                key={`red-${sub.id}`}
                                onMouseEnter={() => setHoveredPin(sub)}
                                onMouseLeave={() => setHoveredPin(null)}
                                onClick={() => handlePinClick(sub.id)}
                                className="location-pin"
                            >
                                <circle
                                    cx={coords.x + idx * 6}
                                    cy={coords.y + idx * 6}
                                    r="8"
                                    fill="#F44336"
                                    stroke="white"
                                    strokeWidth="2"
                                    className="pin red-pin"
                                />
                                <text
                                    x={coords.x + idx * 6}
                                    y={coords.y + idx * 6 - 12}
                                    className="alert-icon"
                                >
                                    ⚠️
                                </text>
                            </g>
                        );
                    })}
                </svg>
            </div>

            {/* Hover Tooltip */}
            {hoveredPin && (
                <div className="pin-tooltip">
                    <h4>{hoveredPin.name}</h4>
                    <p>📍 {hoveredPin.location}</p>
                    {/* <p>📦 {hoveredPin.package}</p>  -- package property might not exist on all objects */}
                    <div className="tooltip-action">👉 Detay için tıkla</div>
                </div>
            )}

            {/* Legend */}
            <div className="map-legend">
                <div className="legend-item">
                    <span className="legend-pin green"></span>
                    <span>Sağlıklı ({subscribers.GREEN?.length || 0})</span>
                </div>
                <div className="legend-item">
                    <span className="legend-pin yellow"></span>
                    <span>Riskli ({subscribers.YELLOW?.length || 0})</span>
                </div>
                <div className="legend-item">
                    <span className="legend-pin red"></span>
                    <span>Arızalı ({subscribers.RED?.length || 0})</span>
                </div>
            </div>
        </div>
    );
}
