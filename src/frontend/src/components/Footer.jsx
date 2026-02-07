import React from 'react';
import './Footer.css';
import { FaGithub, FaLinkedin, FaTwitter } from 'react-icons/fa';

const Footer = () => {
    const currentYear = new Date().getFullYear();

    return (
        <footer className="footer">
            <div className="footer-content">
                <div className="footer-left">
                    <p>© {currentYear} <span className="brand-highlight">NetPulse</span>. Tüm hakları saklıdır.</p>
                </div>

                <div className="footer-center">
                    <a href="#" className="footer-link">Destek</a>
                    <span className="separator">•</span>
                    <a href="#" className="footer-link">Gizlilik Politikası</a>
                    <span className="separator">•</span>
                    <a href="#" className="footer-link">İletişim</a>
                </div>

                <div className="footer-right">
                    <div className="social-icons">
                        <FaGithub className="social-icon" />
                        <FaLinkedin className="social-icon" />
                        <FaTwitter className="social-icon" />
                    </div>
                    <span className="version">v1.0.3</span>
                </div>
            </div>
        </footer>
    );
};

export default Footer;
