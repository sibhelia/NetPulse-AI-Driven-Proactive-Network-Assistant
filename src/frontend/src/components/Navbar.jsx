import React, { useState, useEffect, useRef } from 'react';
import { Link, useNavigate } from 'react-router-dom';
import './Navbar.css';
import { FaUserCircle, FaSignOutAlt, FaClock, FaCog, FaChevronDown } from 'react-icons/fa';

export default function Navbar({ onLogout }) {
    const [currentTime, setCurrentTime] = useState(new Date());
    const [isDropdownOpen, setIsDropdownOpen] = useState(false);
    const dropdownRef = useRef(null);
    const navigate = useNavigate();

    useEffect(() => {
        const timer = setInterval(() => {
            setCurrentTime(new Date());
        }, 1000);

        // Click outside to close dropdown
        const handleClickOutside = (event) => {
            if (dropdownRef.current && !dropdownRef.current.contains(event.target)) {
                setIsDropdownOpen(false);
            }
        };

        document.addEventListener('mousedown', handleClickOutside);
        return () => {
            clearInterval(timer);
            document.removeEventListener('mousedown', handleClickOutside);
        };
    }, []);

    const formatTime = (date) => {
        return date.toLocaleTimeString('tr-TR', { hour: '2-digit', minute: '2-digit', second: '2-digit' });
    };

    const formatDate = (date) => {
        return date.toLocaleDateString('tr-TR', { day: 'numeric', month: 'long', year: 'numeric' });
    };

    const handleProfileClick = () => {
        navigate('/profile');
        setIsDropdownOpen(false);
    };

    const handleLogoutClick = () => {
        if (onLogout) onLogout();
        navigate('/login');
    };

    return (
        <nav className="navbar">
            <div className="navbar-content">
                {/* LEFT: Brand Logo (Big Heybetli Logo) */}
                <div className="navbar-brand">
                    <Link to="/">
                        <img src="/logo.png" alt="NetPulse" className="logo" />
                    </Link>
                </div>

                {/* RIGHT Container: Stats | Clock | Admin */}
                <div className="navbar-right-container">

                    {/* 1. Live Monitoring Badge (Moved here) */}
                    <div className="stat-badge">
                        <span className="stat-icon">🟢</span>
                        <span className="stat-label">Canlı İzleme</span>
                    </div>

                    <div className="divider"></div>

                    {/* 2. Digital Clock */}
                    <div className="navbar-clock">
                        <FaClock className="clock-icon" />
                        <div className="time-info">
                            <span className="time">{formatTime(currentTime)}</span>
                            <span className="date">{formatDate(currentTime)}</span>
                        </div>
                    </div>

                    <div className="divider"></div>

                    {/* 3. Admin Profile with Dropdown */}
                    <div className="admin-profile-wrapper" ref={dropdownRef}>
                        <div
                            className={`admin-profile ${isDropdownOpen ? 'active' : ''}`}
                            onClick={() => setIsDropdownOpen(!isDropdownOpen)}
                        >
                            <FaUserCircle className="admin-avatar" />
                            <div className="admin-info">
                                <span className="admin-name">Admin</span>
                                <span className="admin-role">Yönetici</span>
                            </div>
                            <FaChevronDown className={`chevron ${isDropdownOpen ? 'rotate' : ''}`} />
                        </div>

                        {/* Dropdown Menu */}
                        {isDropdownOpen && (
                            <div className="admin-dropdown">
                                <div className="dropdown-item" onClick={handleProfileClick}>
                                    <FaCog className="item-icon" />
                                    <span>Profil Ayarları</span>
                                </div>
                                <div className="dropdown-divider"></div>
                                <div className="dropdown-item logout" onClick={handleLogoutClick}>
                                    <FaSignOutAlt className="item-icon" />
                                    <span>Çıkış Yap</span>
                                </div>
                            </div>
                        )}
                    </div>
                </div>
            </div>
        </nav>
    );
}
