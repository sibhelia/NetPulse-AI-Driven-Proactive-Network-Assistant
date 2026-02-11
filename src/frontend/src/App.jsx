import React, { useState, useEffect } from 'react';
import { BrowserRouter, Routes, Route, Navigate } from 'react-router-dom';
import Navbar from './components/Navbar';
import Footer from './components/Footer';
import Dashboard from './pages/Dashboard';
import SubscriberDetail from './pages/SubscriberDetail';
import SubscriberListPage from './pages/SubscriberListPage';
import FieldTeamDashboard from './pages/FieldTeamDashboard';
import Login from './pages/Login';
import Profile from './pages/Profile';

function App() {
    // Auth State - Initialize from LocalStorage to persist login
    const [isAuthenticated, setIsAuthenticated] = useState(() => {
        return localStorage.getItem('auth') === 'true';
    });

    const handleLogin = () => {
        localStorage.setItem('auth', 'true');
        setIsAuthenticated(true);
    };

    const handleLogout = () => {
        localStorage.removeItem('auth');
        setIsAuthenticated(false);
    };

    // Protected Route Layout Wrapper
    const ProtectedLayout = ({ children }) => {
        if (!isAuthenticated) {
            return <Navigate to="/login" replace />;
        }
        return (
            <div className="app">
                <Navbar onLogout={handleLogout} />
                <main className="main-content">
                    {children}
                </main>
                <Footer />
            </div>
        );
    };

    return (
        <BrowserRouter>
            <Routes>
                {/* Public Route */}
                {/* If already logged in, redirect Login page to Dashboard */}
                <Route
                    path="/login"
                    element={isAuthenticated ? <Navigate to="/" replace /> : <Login onLogin={handleLogin} />}
                />

                {/* Protected Routes */}
                <Route
                    path="/"
                    element={
                        <ProtectedLayout>
                            <Dashboard />
                        </ProtectedLayout>
                    }
                />
                <Route
                    path="/subscriber/:id"
                    element={
                        <ProtectedLayout>
                            <SubscriberDetail />
                        </ProtectedLayout>
                    }
                />
                <Route
                    path="/list/:filter"
                    element={
                        <ProtectedLayout>
                            <SubscriberListPage />
                        </ProtectedLayout>
                    }
                />
                <Route
                    path="/profile"
                    element={
                        <ProtectedLayout>
                            <Profile onLogout={handleLogout} />
                        </ProtectedLayout>
                    }
                />
                <Route
                    path="/field-team"
                    element={
                        <ProtectedLayout>
                            <FieldTeamDashboard />
                        </ProtectedLayout>
                    }
                />

                {/* Redirect any unknown route to login */}
                <Route path="*" element={<Navigate to="/login" replace />} />
            </Routes>
        </BrowserRouter>
    );
}

export default App;
