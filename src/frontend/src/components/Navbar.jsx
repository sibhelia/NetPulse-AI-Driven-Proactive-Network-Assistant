import './Navbar.css';

export default function Navbar() {
    return (
        <nav className="navbar">
            <div className="navbar-content">
                <div className="navbar-brand">
                    <img src="/logo.png" alt="NetPulse" className="logo" />
                </div>
                <div className="navbar-stats">
                    <div className="stat-badge">
                        <span className="stat-icon">🟢</span>
                        <span className="stat-label">Live Monitoring</span>
                    </div>
                </div>
            </div>
        </nav>
    );
}
