import './Navbar.css';

export default function Navbar() {
    return (
        <nav className="navbar">
            <div className="container">
                <div className="navbar-content">
                    <div className="navbar-brand">
                        <h1>NetPulse</h1>
                        <span className="navbar-subtitle">Proactive NOC</span>
                    </div>
                    <div className="navbar-stats">
                        <div className="stat-badge">
                            <span className="stat-icon">🟢</span>
                            <span className="stat-label">Monitoring Active</span>
                        </div>
                    </div>
                </div>
            </div>
        </nav>
    );
}
