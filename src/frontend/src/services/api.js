const API_BASE = 'http://localhost:8000';

export const api = {
    // Ana dashboard verisi - Tüm aboneler
    getAllSubscribers: async () => {
        try {
            const res = await fetch(`${API_BASE}/api/scan_network`);
            if (!res.ok) throw new Error('Network response was not ok');
            return await res.json();
        } catch (error) {
            console.error('Error fetching subscribers:', error);
            throw error;
        }
    },

    // Tekil abone detayı (RF + LSTM hybrid)
    getSubscriberDetail: async (subscriberId) => {
        try {
            const res = await fetch(`${API_BASE}/api/simulate/${subscriberId}`);
            if (!res.ok) throw new Error('Subscriber not found');
            return await res.json();
        } catch (error) {
            console.error(`Error fetching subscriber ${subscriberId}:`, error);
            throw error;
        }
    },

    // LSTM trend analizi
    getTrendAnalysis: async (subscriberId) => {
        try {
            const res = await fetch(`${API_BASE}/api/trend/${subscriberId}`);
            if (!res.ok) {
                // 400 = Not enough data, gracefully handle
                if (res.status === 400) {
                    return { error: 'not_enough_data', message: 'Trend analizi için en az 1 saatlik veri gerekli' };
                }
                throw new Error('Trend analysis failed');
            }
            return await res.json();
        } catch (error) {
            console.error(`Error fetching trend for ${subscriberId}:`, error);
            throw error;
        }
    }
};
