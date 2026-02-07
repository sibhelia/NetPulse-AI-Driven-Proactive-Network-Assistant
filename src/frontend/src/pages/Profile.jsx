import React, { useState } from 'react';
import './Profile.css';
import Navbar from '../components/Navbar';
import Footer from '../components/Footer';

const Profile = ({ onLogout }) => {
    const [currentPassword, setCurrentPassword] = useState('');
    const [newPassword, setNewPassword] = useState('');
    const [confirmPassword, setConfirmPassword] = useState('');
    const [message, setMessage] = useState('');

    const handleSave = (e) => {
        e.preventDefault();
        if (newPassword !== confirmPassword) {
            setMessage({ type: 'error', text: 'Yeni şifreler eşleşmiyor!' });
            return;
        }
        // Mock save logic
        setMessage({ type: 'success', text: 'Profil başarıyla güncellendi!' });
        setCurrentPassword('');
        setNewPassword('');
        setConfirmPassword('');
    };

    return (
        <div className="profile-page">
            {/* Pass onLogout to Navbar if needed, or handle in App.jsx */}
            {/* But Navbar is already imported inside App.jsx layout usually. 
                Here we might need to adjust layout. For now, assuming Profile is a protected route.
            */}

            <div className="profile-container">
                <div className="profile-header">
                    <h2>Yönetici Profili</h2>
                    <p>Hesap bilgilerinizi ve güvenlik ayarlarınızı yönetin</p>
                </div>

                <div className="profile-grid">
                    {/* User Info Card */}
                    <div className="profile-card user-info-card">
                        <div className="avatar-section">
                            <div className="large-avatar">AD</div>
                            <h3>Admin User</h3>
                            <span className="role-badge">Sistem Yöneticisi</span>
                        </div>
                        <div className="info-list">
                            <div className="info-item">
                                <span className="label">E-posta</span>
                                <span className="value">admin@netpulse.com</span>
                            </div>
                            <div className="info-item">
                                <span className="label">Son Giriş</span>
                                <span className="value">Az önce</span>
                            </div>
                            <div className="info-item">
                                <span className="label">Yetki Seviyesi</span>
                                <span className="value">Level 5 (Full Access)</span>
                            </div>
                        </div>
                    </div>

                    {/* Security Settings Card */}
                    <div className="profile-card security-card">
                        <h3>Güvenlik Ayarları</h3>
                        <form onSubmit={handleSave} className="security-form">
                            <div className="form-group">
                                <label>Mevcut Şifre</label>
                                <input
                                    type="password"
                                    value={currentPassword}
                                    onChange={(e) => setCurrentPassword(e.target.value)}
                                    placeholder="••••••••"
                                />
                            </div>
                            <div className="form-group">
                                <label>Yeni Şifre</label>
                                <input
                                    type="password"
                                    value={newPassword}
                                    onChange={(e) => setNewPassword(e.target.value)}
                                    placeholder="Yeni şifrenizi girin"
                                />
                            </div>
                            <div className="form-group">
                                <label>Yeni Şifre (Tekrar)</label>
                                <input
                                    type="password"
                                    value={confirmPassword}
                                    onChange={(e) => setConfirmPassword(e.target.value)}
                                    placeholder="Yeni şifrenizi doğrulayın"
                                />
                            </div>

                            {message && (
                                <div className={`message ${message.type}`}>
                                    {message.text}
                                </div>
                            )}

                            <button type="submit" className="save-btn">
                                Değişiklikleri Kaydet
                            </button>
                        </form>
                    </div>
                </div>
            </div>
        </div>
    );
};

export default Profile;
