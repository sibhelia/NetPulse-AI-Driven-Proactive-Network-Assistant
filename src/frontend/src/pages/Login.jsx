import React, { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { FaUserShield, FaUserCog } from 'react-icons/fa';
import './Login.css';

const Login = ({ onLogin }) => {
    const [username, setUsername] = useState('');
    const [password, setPassword] = useState('');
    const [role, setRole] = useState('admin'); // admin | field_team
    const [error, setError] = useState('');
    const navigate = useNavigate();

    // Credential'lar
    const credentials = {
        admin: { username: 'admin', password: 'netpulse2026' },
        field_team: { username: 'sahateam', password: 'team2026' }
    };

    const handleSubmit = (e) => {
        e.preventDefault();

        const validCred = credentials[role];

        if (username === validCred.username && password === validCred.password) {
            // Role bilgisini localStorage'a kaydet
            localStorage.setItem('userRole', role);
            onLogin();

            // Role'e göre yönlendir
            if (role === 'admin') {
                navigate('/');
            } else {
                navigate('/field-team');
            }
        } else {
            setError('Kullanıcı adı veya şifre hatalı!');
        }
    };

    return (
        <div className="login-container">
            <div className="login-card">
                <div className="login-header">
                    <img src="/logo.png" alt="NetPulse Logo" className="login-logo" />
                    <h2>Ağ Operasyon Merkezi</h2>
                    <p>Lütfen devam etmek için giriş yapın</p>
                </div>

                {/* Role Seçimi */}
                <div className="role-selector">
                    <button
                        type="button"
                        className={`role-btn ${role === 'admin' ? 'active' : ''}`}
                        onClick={() => setRole('admin')}
                    >
                        <FaUserShield />
                        <span>Admin</span>
                    </button>
                    <button
                        type="button"
                        className={`role-btn ${role === 'field_team' ? 'active' : ''}`}
                        onClick={() => setRole('field_team')}
                    >
                        <FaUserCog />
                        <span>Saha Ekibi</span>
                    </button>
                </div>

                <form onSubmit={handleSubmit} className="login-form">
                    <div className="form-group">
                        <label htmlFor="username">Kullanıcı Adı</label>
                        <input
                            type="text"
                            id="username"
                            value={username}
                            onChange={(e) => setUsername(e.target.value)}
                            placeholder={role === 'admin' ? 'admin' : 'sahateam'}
                            required
                        />
                    </div>

                    <div className="form-group">
                        <label htmlFor="password">Şifre</label>
                        <input
                            type="password"
                            id="password"
                            value={password}
                            onChange={(e) => setPassword(e.target.value)}
                            placeholder="••••••••"
                            required
                        />
                    </div>

                    {error && <div className="error-message">{error}</div>}

                    <button type="submit" className="login-btn">
                        Giriş Yap
                    </button>
                </form>

                <div className="login-footer">
                    <p>© 2026 NetPulse Systems</p>
                </div>
            </div>
        </div>
    );
};

export default Login;
