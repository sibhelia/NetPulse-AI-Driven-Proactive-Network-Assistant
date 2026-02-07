import React, { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import './Login.css';

const Login = ({ onLogin }) => {
    const [username, setUsername] = useState('');
    const [password, setPassword] = useState('');
    const [error, setError] = useState('');
    const navigate = useNavigate();

    const handleSubmit = (e) => {
        e.preventDefault();
        // Simple mock authentication
        if (username === 'admin' && password === '1234') {
            onLogin();
            navigate('/'); // Redirect to Dashboard
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

                <form onSubmit={handleSubmit} className="login-form">
                    <div className="form-group">
                        <label htmlFor="username">Kullanıcı Adı</label>
                        <input
                            type="text"
                            id="username"
                            value={username}
                            onChange={(e) => setUsername(e.target.value)}
                            placeholder="Kullanıcı adınızı girin"
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
