import React, { useState, useEffect } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import { api } from '../services/api';
import Footer from '../components/Footer';
import { FaArrowLeft, FaChevronLeft, FaChevronRight } from 'react-icons/fa';
import './SubscriberListPage.css';

const SubscriberListPage = () => {
    const { filter } = useParams(); // 'all', 'green', 'yellow', 'red'
    const navigate = useNavigate();
    const [subscribers, setSubscribers] = useState([]);
    const [loading, setLoading] = useState(true);
    const [error, setError] = useState(null);

    // Pagination State
    const [currentPage, setCurrentPage] = useState(1);
    const itemsPerPage = 5;

    useEffect(() => {
        loadData();
    }, [filter]);

    const loadData = async () => {
        setLoading(true);
        setCurrentPage(1);
        try {
            const result = await api.getAllSubscribers();

            let filteredList = [];
            const upperFilter = filter?.toUpperCase();

            // Helper function to map API lists to flat array with status
            const processList = (list, statusKey) => {
                return (list || []).map(sub => ({
                    ...sub,
                    // Backend returns 'region' (mapped string) and 'plan'. 
                    // Fallbacks are just in case.
                    region: sub.region || 'İstanbul/Merkez',
                    plan: sub.plan || 'Standart Paket',
                    status: statusKey // GREEN, YELLOW, RED
                }));
            };

            if (upperFilter === 'ALL' || !upperFilter) {
                const green = processList(result.lists.GREEN, 'GREEN');
                const yellow = processList(result.lists.YELLOW, 'YELLOW');
                const red = processList(result.lists.RED, 'RED');
                filteredList = [...green, ...yellow, ...red];
            } else {
                filteredList = processList(result.lists[upperFilter], upperFilter);
            }

            filteredList.sort((a, b) => a.id - b.id);
            setSubscribers(filteredList);
            setError(null);
        } catch (err) {
            console.error(err);
            setError('Veri yüklenirken hata oluştu.');
        } finally {
            setLoading(false);
        }
    };

    const getPageTitle = () => {
        switch (filter?.toLowerCase()) {
            case 'green': return 'Sağlıklı Aboneler';
            case 'yellow': return 'Riskli Aboneler';
            case 'red': return 'Arızalı Aboneler';
            default: return 'Tüm Aboneler';
        }
    };

    const getRowClass = (sub) => {
        return '';
    };

    const getStatusLabel = (status) => {
        switch (status) {
            case 'GREEN': return 'Sağlıklı';
            case 'YELLOW': return 'Riskli';
            case 'RED': return 'Arızalı';
            default: return status;
        }
    };

    // Pagination Logic
    const indexOfLastItem = currentPage * itemsPerPage;
    const indexOfFirstItem = indexOfLastItem - itemsPerPage;
    const currentItems = subscribers.slice(indexOfFirstItem, indexOfLastItem);
    const totalPages = Math.ceil(subscribers.length / itemsPerPage);

    const handleNextPage = () => {
        if (currentPage < totalPages) {
            setCurrentPage(prev => prev + 1);
        }
    };

    const handlePrevPage = () => {
        if (currentPage > 1) {
            setCurrentPage(prev => prev - 1);
        }
    };

    return (
        <div className="list-page-wrapper">
            <div className="list-page-content">
                <header className="list-header">
                    <button className="back-btn" onClick={() => navigate('/')} title="Geri Dön">
                        <FaArrowLeft />
                    </button>
                    <h2>{getPageTitle()}</h2>
                </header>

                {loading ? (
                    <div className="loading">Yükleniyor...</div>
                ) : error ? (
                    <div className="error">{error}</div>
                ) : (
                    <div className="table-wrapper">
                        <div className="table-container">
                            <table className="subscriber-table">
                                <thead>
                                    <tr>
                                        <th>Abone No</th>
                                        <th>Ad Soyad</th>
                                        <th>Bölge</th>
                                        <th>Paket</th>
                                        <th>Durum</th>
                                        <th>İşlem</th>
                                    </tr>
                                </thead>
                                <tbody>
                                    {currentItems.map((sub) => (
                                        <tr key={sub.id} className={getRowClass(sub)}>
                                            <td>#{sub.id}</td>
                                            <td>
                                                <div className="user-cell">
                                                    <div className="avatar-placeholder">{sub.name.charAt(0)}</div>
                                                    <span>{sub.name}</span>
                                                </div>
                                            </td>
                                            <td>{sub.region}</td>
                                            <td><span className="plan-badge">{sub.plan}</span></td>
                                            <td>
                                                <span className={`status-badge ${sub.status.toLowerCase()}`}>
                                                    {getStatusLabel(sub.status)}
                                                </span>
                                            </td>
                                            <td>
                                                <button
                                                    className="detail-btn"
                                                    onClick={() => navigate(`/subscriber/${sub.id}`)}
                                                >
                                                    Detay
                                                </button>
                                            </td>
                                        </tr>
                                    ))}
                                    {subscribers.length === 0 && (
                                        <tr>
                                            <td colSpan="6" style={{ textAlign: 'center', padding: '2rem' }}>Kayıt bulunamadı.</td>
                                        </tr>
                                    )}
                                </tbody>
                            </table>
                        </div>

                        {/* Pagination Controls */}
                        {subscribers.length > 0 && (
                            <div className="pagination-controls">
                                <button
                                    className="pagination-btn icon-only"
                                    onClick={handlePrevPage}
                                    disabled={currentPage === 1}
                                    title="Önceki Sayfa"
                                >
                                    <FaChevronLeft />
                                </button>
                                <span className="page-info">
                                    {currentPage} / {totalPages}
                                </span>
                                <button
                                    className="pagination-btn icon-only"
                                    onClick={handleNextPage}
                                    disabled={currentPage === totalPages}
                                    title="Sonraki Sayfa"
                                >
                                    <FaChevronRight />
                                </button>
                            </div>
                        )}
                    </div>
                )}
            </div>
            <Footer />
        </div>
    );
};

export default SubscriberListPage;
